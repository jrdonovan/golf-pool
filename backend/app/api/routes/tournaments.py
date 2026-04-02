import uuid

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.models.tournaments import Tournament
from app.services.crud.organizations import get_org
from app.services.crud.tournaments import (
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
