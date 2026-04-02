from fastapi import APIRouter

from app.api.deps import SessionDep
from app.models.organizations import Organization
from app.services.crud.organizations import list_orgs, upsert_org
from app.services.live_golf_data import LiveGolfData

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/", response_model=list[Organization])
async def read_organizations(session: SessionDep, skip: int = 0, limit: int = 100):
    organizations = list_orgs(session=session, skip=skip, limit=limit)
    return organizations


@router.get("/import")
async def import_organizations(session: SessionDep):
    client = LiveGolfData()
    imported_orgs = client.get_organizations()

    created_count = 0
    updated_count = 0
    unchanged_count = 0

    for imported_org in imported_orgs:
        db_org, result = upsert_org(
            session=session,
            live_golf_data_id=imported_org.orgId,
            incoming_data=imported_org,
        )
        if result == "created":
            created_count += 1
        elif result == "updated":
            updated_count += 1
        else:
            unchanged_count += 1
    session.commit()

    return {
        "message": "Organizations import complete",
        "created": created_count,
        "updated": updated_count,
        "unchanged": unchanged_count,
        "total_received": len(imported_orgs),
    }
