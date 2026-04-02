import uuid
from typing import TYPE_CHECKING

from sqlmodel import Session, select

from app.models.player_tournaments import PlayerTournament, PlayerTournamentCreate
from app.models.players import Player, PlayerCreate, PlayerUpdate
from app.services.mappers.players import PlayerMapperFactory

if TYPE_CHECKING:
    from app.services.live_golf_data import TournamentPlayerData


def get_player_by_live_golf_data_id(
    *, session: Session, live_golf_data_id: str
) -> Player | None:
    statement = select(Player).where(Player.live_golf_data_id == live_golf_data_id)
    return session.exec(statement).first()


def get_player_tournament(
    *, session: Session, player_id: uuid.UUID, tournament_id: uuid.UUID
) -> PlayerTournament | None:
    statement = select(PlayerTournament).where(
        PlayerTournament.player_id == player_id,
        PlayerTournament.tournament_id == tournament_id,
    )
    return session.exec(statement).first()


def _upsert_player(
    *,
    session: Session,
    player_create: PlayerCreate,
    player_update: PlayerUpdate,
) -> tuple[Player, str]:
    db_player = get_player_by_live_golf_data_id(
        session=session, live_golf_data_id=player_create.live_golf_data_id
    )

    if db_player is None:
        db_player = Player.model_validate(player_create)
        session.add(db_player)
        return db_player, "created"

    changed_data = {
        key: value
        for key, value in player_update.model_dump(exclude_unset=True).items()
        if getattr(db_player, key) != value
    }

    if changed_data:
        db_player.sqlmodel_update(changed_data)
        session.add(db_player)
        return db_player, "updated"

    return db_player, "unchanged"


def upsert_player_from_tournament_data(
    *, session: Session, incoming_data: "TournamentPlayerData"
) -> tuple[Player, str]:
    player_create = PlayerMapperFactory.create_from_tournament_player(incoming_data)
    player_update = PlayerMapperFactory.update_from_tournament_player(incoming_data)
    return _upsert_player(
        session=session, player_create=player_create, player_update=player_update
    )


def upsert_player_tournament(
    *, session: Session, player_id: uuid.UUID, tournament_id: uuid.UUID
) -> tuple[PlayerTournament, str]:
    db_pt = get_player_tournament(
        session=session, player_id=player_id, tournament_id=tournament_id
    )

    if db_pt is None:
        db_pt = PlayerTournament.model_validate(
            PlayerTournamentCreate(player_id=player_id, tournament_id=tournament_id)
        )
        session.add(db_pt)
        return db_pt, "created"

    return db_pt, "unchanged"
