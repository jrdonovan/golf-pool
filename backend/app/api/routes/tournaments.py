import uuid

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.models.tournaments import Tournament
from app.services.crud.organizations import get_org
from app.services.crud.tournaments import (
    get_tournament,
    import_tournament_details,
    list_tournaments,
    upsert_tournament_from_schedule,
)
from app.services.live_golf_data import LiveGolfData

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


@router.get("/", response_model=list[Tournament])
async def read_tournaments(session: SessionDep, skip: int = 0, limit: int = 100):
    tournaments = list_tournaments(session=session, skip=skip, limit=limit)
    return tournaments


@router.get("/import")
async def import_tournaments(session: SessionDep, year: int, org_id: uuid.UUID):
    # Validate that org_id exists
    db_org = get_org(session=session, org_id=org_id)
    if not db_org:
        raise HTTPException(
            status_code=404, detail=f"Organization with id {org_id} not found."
        )

    client = LiveGolfData()
    schedule_data = client.get_schedule(org_id=db_org.live_golf_data_id, year=year)

    created_count = 0
    updated_count = 0
    unchanged_count = 0
    skipped_count = 0

    for incoming_tournament in schedule_data.schedule:
        _, result = upsert_tournament_from_schedule(
            session=session,
            organization_id=db_org.id,
            year=year,
            incoming_data=incoming_tournament,
        )

        if result == "created":
            created_count += 1
        elif result == "updated":
            updated_count += 1
        elif result == "unchanged":
            unchanged_count += 1
        else:
            skipped_count += 1

    session.commit()

    return {
        "message": "Tournaments import complete",
        "org_id": str(org_id),
        "year": year,
        "created": created_count,
        "updated": updated_count,
        "unchanged": unchanged_count,
        "skipped": skipped_count,
        "total_received": len(schedule_data.schedule),
    }


@router.get("/import-details")
async def import_tournament_details_route(
    session: SessionDep, tourn_id: uuid.UUID, year: int
):
    """
    Fetches full tournament details from the external API and upserts into:
    tournaments, courses, course_holes, tournament_courses, players, player_tournaments.
    """
    # Validate that existing tournament exists in db
    db_tournament = get_tournament(session=session, tournament_id=tourn_id)
    if not db_tournament:
        raise HTTPException(
            status_code=404, detail=f"Tournament with id {tourn_id} not found."
        )

    lgd_client = LiveGolfData()
    try:
        lgd_tournament = lgd_client.get_tournament(
            org_id=db_tournament.organization.live_golf_data_id,
            tourn_id=db_tournament.live_golf_data_id,
            year=year,
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=404, detail=str(e)
        )  # Update this to dynamically determine status code based on server response

    results = []
    summary = import_tournament_details(
        session=session,
        organization_id=db_tournament.organization.id,
        incoming_data=lgd_tournament,
    )
    results.append(summary)

    session.commit()

    return {
        "message": "Tournament details import complete",
        "org_id": str(db_tournament.organization.id),
        "tourn_id": tourn_id,
        "year": year,
        "results": results,
    }
