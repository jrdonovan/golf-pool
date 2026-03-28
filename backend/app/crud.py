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
from .models.tournaments import (
    Tournament,
    TournamentCreate,
    TournamentDelete,
    TournamentStatus,
    TournamentUpdate,
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


###### Tournament Methods ######
def get_tournament(*, session: Session, tournament_id: uuid.UUID) -> Tournament | None:
    statement = select(Tournament).where(Tournament.id == tournament_id)
    session_tournament = session.exec(statement).first()
    return session_tournament


def get_tournament_by_external_id(
    *, session: Session, external_id: int
) -> Tournament | None:
    statement = select(Tournament).where(Tournament.external_id == external_id)
    session_tournament = session.exec(statement).first()
    return session_tournament


def list_tournaments(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    organization_id: uuid.UUID | None = None,
    status: TournamentStatus | None = None,
) -> list[Tournament]:
    statement = select(Tournament)

    if organization_id:
        statement = statement.where(Tournament.organization_id == organization_id)
    if status:
        statement = statement.where(Tournament.status == status)

    statement = statement.offset(skip).limit(limit)
    session_tournaments = list(session.exec(statement).all())
    return session_tournaments


def create_tournament(
    *, session: Session, tournament_in: TournamentCreate
) -> Tournament:
    organization = get_organization(
        session=session, organization_id=tournament_in.organization_id
    )
    if not organization:
        raise ValueError(f"Organization {tournament_in.organization_id} not found")

    if tournament_in.start_date > tournament_in.end_date:
        raise ValueError("start_date cannot be after end_date")

    if tournament_in.external_id is not None:
        existing_tournament = get_tournament_by_external_id(
            session=session, external_id=tournament_in.external_id
        )
        if existing_tournament:
            raise ValueError("Tournament with this external_id already exists")

    db_obj = Tournament.model_validate(tournament_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_tournament(
    *,
    session: Session,
    tournament_id: uuid.UUID,
    update_vals: TournamentUpdate,
) -> Tournament:
    db_tournament = get_tournament(session=session, tournament_id=tournament_id)
    if not db_tournament:
        raise ValueError("Tournament not found")

    tournament_data = update_vals.model_dump(exclude_unset=True)
    if not tournament_data:
        raise ValueError("No data provided for update")

    if "organization_id" in tournament_data:
        # Ignore if organization_id is being updated to the same value
        if tournament_data["organization_id"] == db_tournament.organization_id:
            del tournament_data["organization_id"]
        else:
            organization = get_organization(
                session=session, organization_id=tournament_data["organization_id"]
            )
            if not organization:
                raise ValueError(
                    f"Organization {tournament_data['organization_id']} not found"
                )

    if "external_id" in tournament_data:
        # Ignore if external_id is being updated to the same value
        if tournament_data["external_id"] == db_tournament.external_id:
            del tournament_data["external_id"]
        elif tournament_data["external_id"] is not None:
            existing_tournament = get_tournament_by_external_id(
                session=session, external_id=tournament_data["external_id"]
            )
            if existing_tournament:
                raise ValueError("Tournament with this external_id already exists")

    start_date = tournament_data.get("start_date", db_tournament.start_date)
    end_date = tournament_data.get("end_date", db_tournament.end_date)
    if start_date > end_date:
        raise ValueError("start_date cannot be after end_date")

    db_tournament.sqlmodel_update(tournament_data)
    session.add(db_tournament)
    session.commit()
    session.refresh(db_tournament)
    return db_tournament


def delete_tournament(*, session: Session, tournament_in: TournamentDelete) -> Any:
    db_tournament = get_tournament(session=session, tournament_id=tournament_in.id)
    if not db_tournament:
        raise ValueError("Tournament not found")
    session.delete(db_tournament)
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
