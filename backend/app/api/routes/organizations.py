from fastapi import APIRouter
from sqlmodel import select

from app import crud
from app.api.deps import SessionDep
from app.models.organizations import Organization
from app.services.live_golf_data import LiveGolfData

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/", response_model=list[Organization])
async def read_organizations(session: SessionDep, skip: int = 0, limit: int = 100):
    organizations = crud.list_organizations(session=session, skip=skip, limit=limit)
    return organizations


@router.post("/import")
async def import_organizations(session: SessionDep):
    client = LiveGolfData()
    incoming_organizations = client.get_organizations()

    created_count = 0
    updated_count = 0
    unchanged_count = 0
    skipped_count = 0

    for incoming_org in incoming_organizations:
        try:
            external_id = int(incoming_org.orgId)
        except (TypeError, ValueError):
            skipped_count += 1
            continue

        db_org = crud.get_organization_by_external_id(
            session=session, external_id=external_id
        )

        if db_org is None:
            session.add(
                Organization(name=incoming_org.orgName, external_id=external_id)
            )
            created_count += 1
            continue

        update_data: dict[str, str] = {}
        if db_org.name != incoming_org.orgName:
            conflicting_name_org = session.exec(
                select(Organization).where(Organization.name == incoming_org.orgName)
            ).first()
            if conflicting_name_org and conflicting_name_org.id != db_org.id:
                skipped_count += 1
                continue
            update_data["name"] = incoming_org.orgName

        if update_data:
            db_org.sqlmodel_update(update_data)
            session.add(db_org)
            updated_count += 1
        else:
            unchanged_count += 1

    session.commit()

    return {
        "message": "Organizations import complete",
        "created": created_count,
        "updated": updated_count,
        "unchanged": unchanged_count,
        "skipped": skipped_count,
        "total_received": len(incoming_organizations),
    }
