import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.old_models import User, UserCreate, UserUpdate

from .models.organizations import (
    Organization,
    OrganizationCreate,
    OrganizationDelete,
    OrganizationUpdate,
)


###### Organization Methods ######
def get_organization(
    *, session: Session, organization_id: uuid.UUID
) -> Organization | None:
    statement = select(Organization).where(Organization.id == organization_id)
    session_organization = session.exec(statement).first()
    return session_organization


def get_organization_by_name(*, session: Session, name: str) -> Organization | None:
    statement = select(Organization).where(Organization.name == name)
    session_organization = session.exec(statement).first()
    return session_organization


def get_organization_by_external_id(
    *, session: Session, external_id: int
) -> Organization | None:
    statement = select(Organization).where(Organization.external_id == external_id)
    session_organization = session.exec(statement).first()
    return session_organization


def list_organizations(
    *, session: Session, skip: int = 0, limit: int = 100
) -> list[Organization]:
    statement = select(Organization).offset(skip).limit(limit)
    session_organizations = list(session.exec(statement).all())
    return session_organizations


def create_organization(
    *, session: Session, organization_in: OrganizationCreate
) -> Organization:
    existing_organization = get_organization_by_name(
        session=session, name=organization_in.name
    )
    if existing_organization:
        raise ValueError("Organization with this name already exists")

    db_obj = Organization.model_validate(organization_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_organization(
    *,
    session: Session,
    organization_id: uuid.UUID,
    update_vals: OrganizationUpdate,
) -> Organization:
    db_organization = get_organization(session=session, organization_id=organization_id)
    if not db_organization:
        raise ValueError("Organization not found")

    organization_data = update_vals.model_dump(exclude_unset=True)
    if not organization_data:
        raise ValueError("No data provided for update")

    if "name" in organization_data:
        if organization_data["name"] == db_organization.name:
            # If the name is being updated to the same value, we can skip the uniqueness check
            del organization_data["name"]
        else:
            existing_organization = get_organization_by_name(
                session=session, name=organization_data["name"]
            )
            if existing_organization:
                raise ValueError("Organization with this name already exists")

    if "external_id" in organization_data:
        if organization_data["external_id"] == db_organization.external_id:
            # If the external_id is being updated to the same value, we can skip the uniqueness check
            del organization_data["external_id"]
        else:
            existing_organization = get_organization_by_external_id(
                session=session, external_id=organization_data["external_id"]
            )
            if existing_organization:
                raise ValueError("Organization with this external_id already exists")

    db_organization.sqlmodel_update(organization_data)
    session.add(db_organization)
    session.commit()
    session.refresh(db_organization)
    return db_organization


def delete_organization(
    *, session: Session, organization_in: OrganizationDelete
) -> Any:
    db_organization = get_organization(
        session=session, organization_id=organization_in.id
    )
    if not db_organization:
        raise ValueError("Organization not found")
    session.delete(db_organization)
    session.commit()
    return {"ok": True}


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


# Dummy hash to use for timing attack prevention when user is not found
# This is an Argon2 hash of a random password, used to ensure constant-time comparison
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        # Prevent timing attacks by running password verification even when user doesn't exist
        # This ensures the response time is similar whether or not the email exists
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        db_user.hashed_password = updated_password_hash
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user
