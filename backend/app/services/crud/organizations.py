import uuid
from typing import TYPE_CHECKING, Any

from sqlmodel import Session, select

from app.models.organizations import Organization, OrganizationDelete
from app.services.mappers.organizations import OrganizationMapperFactory

if TYPE_CHECKING:
    from app.services.live_golf_data import OrganizationData


def get_org(*, session: Session, org_id: uuid.UUID) -> Organization | None:
    statement = select(Organization).where(Organization.id == org_id)
    return session.exec(statement).first()


def get_org_by_live_golf_data_id(
    *, session: Session, live_golf_data_id: str
) -> Organization | None:
    statement = select(Organization).where(
        Organization.live_golf_data_id == live_golf_data_id
    )
    return session.exec(statement).first()


def upsert_org(
    *, session: Session, live_golf_data_id: str, incoming_data: "OrganizationData"
) -> tuple[Organization, str]:
    if not live_golf_data_id:
        raise ValueError("Organization live_golf_data_id is required for upsert")

    db_org = get_org_by_live_golf_data_id(
        session=session, live_golf_data_id=live_golf_data_id
    )

    if db_org is None:
        create_obj = OrganizationMapperFactory.create_model(incoming_data)
        db_org = Organization.model_validate(create_obj)
        session.add(db_org)
        return db_org, "created"

    update_org = OrganizationMapperFactory.update_model(incoming_data)
    update_data = update_org.model_dump(exclude_unset=True)
    changed_data = {
        key: value
        for key, value in update_data.items()
        if getattr(db_org, key) != value
    }

    if changed_data:
        db_org.sqlmodel_update(changed_data)
        session.add(db_org)
        session.refresh(db_org)

    return db_org, "updated" if changed_data else "unchanged"


def list_orgs(
    *, session: Session, skip: int = 0, limit: int = 100
) -> list[Organization]:
    statement = select(Organization).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def delete_org(*, session: Session, organization_in: OrganizationDelete) -> Any:
    db_organization = get_org(session=session, org_id=organization_in.id)
    if not db_organization:
        raise ValueError("Organization not found")
    session.delete(db_organization)
    session.commit()
    return {"ok": True}
