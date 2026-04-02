import uuid
from typing import TYPE_CHECKING, Any

from sqlmodel import Session, select

from app.models.tournaments import (
    Tournament,
    TournamentCreate,
    TournamentDelete,
    TournamentStatus,
    TournamentUpdate,
)
from app.services.crud.courses import upsert_course_from_data, upsert_tournament_course
from app.services.crud.organizations import get_org
from app.services.crud.players import (
    upsert_player_from_tournament_data,
    upsert_player_tournament,
)
from app.services.mappers.tournaments import TournamentMapperFactory

if TYPE_CHECKING:
    from app.services.live_golf_data import ScheduleTournamentData, TournamentData


def get_tournament(*, session: Session, tournament_id: uuid.UUID) -> Tournament | None:
    statement = select(Tournament).where(Tournament.id == tournament_id)
    return session.exec(statement).first()


def get_tournament_by_live_golf_data_id_and_year(
    *, session: Session, live_golf_data_id: str, year: int
) -> Tournament | None:
    statement = select(Tournament).where(
        Tournament.live_golf_data_id == live_golf_data_id,
        Tournament.year == year,
    )
    return session.exec(statement).first()


def _upsert_tournament(
    *,
    session: Session,
    tournament_create: TournamentCreate,
    tournament_update: TournamentUpdate,
) -> tuple[Tournament, str]:
    live_golf_data_id = tournament_create.live_golf_data_id
    year = tournament_create.year

    if not live_golf_data_id:
        raise ValueError("Tournament live_golf_data_id is required for upsert")

    db_tournament = get_tournament_by_live_golf_data_id_and_year(
        session=session, live_golf_data_id=live_golf_data_id, year=year
    )

    if db_tournament is None:
        db_tournament = Tournament.model_validate(tournament_create)
        session.add(db_tournament)
        return db_tournament, "created"

    validated_update_data = tournament_update.model_dump(exclude_unset=True)

    changed_data = {
        key: value
        for key, value in validated_update_data.items()
        if getattr(db_tournament, key) != value
    }

    if changed_data:
        db_tournament.sqlmodel_update(changed_data)
        session.add(db_tournament)
        return db_tournament, "updated"

    return db_tournament, "unchanged"


def upsert_tournament_from_schedule(
    *,
    session: Session,
    organization_id: uuid.UUID,
    year: int,
    incoming_data: "ScheduleTournamentData",
) -> tuple[Tournament, str]:
    tournament_create = TournamentMapperFactory.create_from_schedule(
        incoming_data, organization_id=organization_id, year=year
    )
    tournament_update = TournamentMapperFactory.update_from_schedule(incoming_data)
    return _upsert_tournament(
        session=session,
        tournament_create=tournament_create,
        tournament_update=tournament_update,
    )


def upsert_tournament_from_details(
    *, session: Session, organization_id: uuid.UUID, incoming_data: "TournamentData"
) -> tuple[Tournament, str]:
    tournament_create = TournamentMapperFactory.create_from_tournament_data(
        incoming_data, organization_id=organization_id
    )
    tournament_update = TournamentMapperFactory.update_from_tournament_data(
        incoming_data
    )
    return _upsert_tournament(
        session=session,
        tournament_create=tournament_create,
        tournament_update=tournament_update,
    )


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
    return list(session.exec(statement).all())


def update_tournament(
    *, session: Session, tournament_id: uuid.UUID, update_vals: TournamentUpdate
) -> Tournament:
    db_tournament = get_tournament(session=session, tournament_id=tournament_id)
    if not db_tournament:
        raise ValueError("Tournament not found")

    update_values = update_vals.model_dump(exclude_unset=True)
    if not update_values:
        raise ValueError("No data provided for update")

    if "organization_id" in update_values:
        if update_values["organization_id"] == db_tournament.organization_id:
            del update_values["organization_id"]
        else:
            organization = get_org(
                session=session, org_id=update_values["organization_id"]
            )
            if not organization:
                raise ValueError(
                    f"Organization {update_values['organization_id']} not found"
                )

    start_date = update_values.get("start_date", db_tournament.start_date)
    end_date = update_values.get("end_date", db_tournament.end_date)
    if start_date > end_date:
        raise ValueError("start_date cannot be after end_date")

    db_tournament.sqlmodel_update(update_values)
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


def import_tournament_details(
    *,
    session: Session,
    organization_id: uuid.UUID,
    incoming_data: "TournamentData",
) -> dict:
    """
    Orchestrates a full upsert from a TournamentData API response into:
    tournaments, courses, course_holes, tournament_courses, players, player_tournaments.
    Does NOT commit — caller is responsible for session.commit().
    """
    db_tournament, t_result = upsert_tournament_from_details(
        session=session, organization_id=organization_id, incoming_data=incoming_data
    )

    # Need the tournament PK before linking courses/players
    session.flush()

    courses_created = courses_updated = courses_unchanged = 0
    for course_data in incoming_data.courses:
        db_course, c_result = upsert_course_from_data(
            session=session, incoming_data=course_data
        )
        # flush so course.id is populated before linking
        session.flush()
        upsert_tournament_course(
            session=session,
            tournament_id=db_tournament.id,
            course_id=db_course.id,
        )
        if c_result == "created":
            courses_created += 1
        elif c_result == "updated":
            courses_updated += 1
        else:
            courses_unchanged += 1

    players_created = players_updated = players_unchanged = 0
    for player_data in incoming_data.players:
        db_player, p_result = upsert_player_from_tournament_data(
            session=session, incoming_data=player_data
        )
        session.flush()
        upsert_player_tournament(
            session=session,
            player_id=db_player.id,
            tournament_id=db_tournament.id,
        )
        if p_result == "created":
            players_created += 1
        elif p_result == "updated":
            players_updated += 1
        else:
            players_unchanged += 1

    return {
        "tournament": t_result,
        "courses": {
            "created": courses_created,
            "updated": courses_updated,
            "unchanged": courses_unchanged,
            "total": len(incoming_data.courses),
        },
        "players": {
            "created": players_created,
            "updated": players_updated,
            "unchanged": players_unchanged,
            "total": len(incoming_data.players),
        },
    }
