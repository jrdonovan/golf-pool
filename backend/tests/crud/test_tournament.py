import uuid
from datetime import date, timedelta

from sqlmodel import Session

from app import crud
from app.models.organizations import OrganizationCreate
from app.models.tournaments import (
    Tournament,
    TournamentCreate,
    TournamentDelete,
    TournamentStatus,
    TournamentUpdate,
)
from tests.utils.utils import random_lower_string


def _create_organization(db: Session):
    return crud.create_organization(
        session=db,
        organization_in=OrganizationCreate(
            name=f"org-{random_lower_string()}",
            external_id=abs(hash(random_lower_string())) % 1_000_000_000,
        ),
    )


def _build_tournament_input(
    organization_id: uuid.UUID, *, external_id: int | None = None
):
    today = date.today()
    return TournamentCreate(
        name=f"tournament-{random_lower_string()}",
        organization_id=organization_id,
        purse=1_000_000,
        format="stroke",
        status=TournamentStatus.not_started,
        start_date=today,
        end_date=today + timedelta(days=3),
        timezone="America/New_York",
        external_id=external_id,
    )


def test_create_tournament(db: Session) -> None:
    organization = _create_organization(db)
    tournament_in = _build_tournament_input(
        organization.id,
        external_id=abs(hash(random_lower_string())) % 1_000_000_000,
    )

    tournament = crud.create_tournament(session=db, tournament_in=tournament_in)

    assert tournament.name == tournament_in.name
    assert tournament.organization_id == organization.id
    assert tournament.external_id == tournament_in.external_id


def test_create_tournament_invalid_organization(db: Session) -> None:
    tournament_in = _build_tournament_input(
        uuid.uuid4(),
        external_id=abs(hash(random_lower_string())) % 1_000_000_000,
    )

    try:
        crud.create_tournament(session=db, tournament_in=tournament_in)
        raise AssertionError("Expected ValueError for missing organization")
    except ValueError as e:
        assert "not found" in str(e)


def test_create_tournament_invalid_date_range(db: Session) -> None:
    organization = _create_organization(db)
    today = date.today()
    tournament_in = TournamentCreate(
        name=f"tournament-{random_lower_string()}",
        organization_id=organization.id,
        purse=500000,
        format="stroke",
        status=TournamentStatus.not_started,
        start_date=today + timedelta(days=2),
        end_date=today,
        timezone="America/New_York",
        external_id=abs(hash(random_lower_string())) % 1_000_000_000,
    )

    try:
        crud.create_tournament(session=db, tournament_in=tournament_in)
        raise AssertionError("Expected ValueError for invalid date range")
    except ValueError as e:
        assert str(e) == "start_date cannot be after end_date"


def test_create_tournament_duplicate_external_id(db: Session) -> None:
    organization = _create_organization(db)
    external_id = abs(hash(random_lower_string())) % 1_000_000_000
    tournament_in = _build_tournament_input(organization.id, external_id=external_id)

    crud.create_tournament(session=db, tournament_in=tournament_in)

    try:
        duplicate_in = _build_tournament_input(organization.id, external_id=external_id)
        crud.create_tournament(session=db, tournament_in=duplicate_in)
        raise AssertionError("Expected ValueError for duplicate external_id")
    except ValueError as e:
        assert str(e) == "Tournament with this external_id already exists"


def test_get_tournament(db: Session) -> None:
    organization = _create_organization(db)
    tournament_in = _build_tournament_input(
        organization.id,
        external_id=abs(hash(random_lower_string())) % 1_000_000_000,
    )
    created = crud.create_tournament(session=db, tournament_in=tournament_in)

    retrieved = crud.get_tournament(session=db, tournament_id=created.id)

    assert retrieved
    assert retrieved.id == created.id
    assert retrieved.name == created.name


def test_get_tournament_by_external_id(db: Session) -> None:
    organization = _create_organization(db)
    external_id = abs(hash(random_lower_string())) % 1_000_000_000
    tournament_in = _build_tournament_input(organization.id, external_id=external_id)
    created = crud.create_tournament(session=db, tournament_in=tournament_in)

    retrieved = crud.get_tournament_by_external_id(session=db, external_id=external_id)

    assert retrieved
    assert retrieved.id == created.id
    assert retrieved.external_id == external_id


def test_list_tournaments_filtered(db: Session) -> None:
    organization_1 = _create_organization(db)
    organization_2 = _create_organization(db)

    first = _build_tournament_input(
        organization_1.id,
        external_id=abs(hash(random_lower_string())) % 1_000_000_000,
    )
    second = _build_tournament_input(
        organization_2.id,
        external_id=abs(hash(random_lower_string())) % 1_000_000_000,
    )
    second.status = TournamentStatus.complete

    first_created = crud.create_tournament(session=db, tournament_in=first)
    second_created = crud.create_tournament(session=db, tournament_in=second)

    org_1_tournaments = crud.list_tournaments(
        session=db, organization_id=organization_1.id
    )
    complete_tournaments = crud.list_tournaments(
        session=db, status=TournamentStatus.complete
    )

    assert any(t.id == first_created.id for t in org_1_tournaments)
    assert all(t.organization_id == organization_1.id for t in org_1_tournaments)
    assert any(t.id == second_created.id for t in complete_tournaments)
    assert all(t.status == TournamentStatus.complete for t in complete_tournaments)


def test_update_tournament(db: Session) -> None:
    organization = _create_organization(db)
    tournament_in = _build_tournament_input(
        organization.id,
        external_id=abs(hash(random_lower_string())) % 1_000_000_000,
    )
    created = crud.create_tournament(session=db, tournament_in=tournament_in)

    updated = crud.update_tournament(
        session=db,
        tournament_id=created.id,
        update_vals=TournamentUpdate(
            name=f"updated-{random_lower_string()}",
            status=TournamentStatus.in_progress,
        ),
    )

    assert updated.id == created.id
    assert updated.name.startswith("updated-")
    assert updated.status == TournamentStatus.in_progress


def test_update_tournament_invalid_date_range(db: Session) -> None:
    organization = _create_organization(db)
    tournament_in = _build_tournament_input(
        organization.id,
        external_id=abs(hash(random_lower_string())) % 1_000_000_000,
    )
    created = crud.create_tournament(session=db, tournament_in=tournament_in)

    try:
        crud.update_tournament(
            session=db,
            tournament_id=created.id,
            update_vals=TournamentUpdate(
                start_date=date.today() + timedelta(days=10),
                end_date=date.today(),
            ),
        )
        raise AssertionError("Expected ValueError for invalid date range")
    except ValueError as e:
        assert str(e) == "start_date cannot be after end_date"


def test_delete_tournament(db: Session) -> None:
    organization = _create_organization(db)
    tournament_in = _build_tournament_input(
        organization.id,
        external_id=abs(hash(random_lower_string())) % 1_000_000_000,
    )
    created = crud.create_tournament(session=db, tournament_in=tournament_in)

    crud.delete_tournament(session=db, tournament_in=TournamentDelete(id=created.id))

    deleted = db.get(Tournament, created.id)
    assert deleted is None
