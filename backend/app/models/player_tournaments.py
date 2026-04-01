import uuid
from typing import TYPE_CHECKING

from pydantic import NonNegativeInt, PositiveInt
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .player_rounds import PlayerRound
    from .players import Player
    from .tournaments import Tournament


# Shared properties
class PlayerTournamentBase(SQLModel):
    player_id: uuid.UUID = Field(foreign_key="app.player.id", ondelete="CASCADE")
    tournament_id: uuid.UUID = Field(
        foreign_key="app.tournament.id", ondelete="CASCADE"
    )
    position: PositiveInt | None = Field(default=None)
    total_score: int | None = Field(default=None)
    strokes: NonNegativeInt | None = Field(default=None)
    missed_cut: bool = Field(default=False)
    withdrawn: bool = Field(default=False)
    disqualified: bool = Field(default=False)
    points: float = Field(default=0)


# Properties to receive via API on creation
class PlayerTournamentCreate(PlayerTournamentBase):
    pass


# Properties to receive via API on deletion
class PlayerTournamentDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class PlayerTournamentUpdate(SQLModel):
    position: PositiveInt | None = Field(default=None)
    total_score: int | None = Field(default=None)
    strokes: NonNegativeInt | None = Field(default=None)
    missed_cut: bool | None = Field(default=None)
    withdrawn: bool | None = Field(default=None)
    disqualified: bool | None = Field(default=None)
    points: float | None = Field(default=None)


# Database model
class PlayerTournament(PlayerTournamentBase, TimestampsMixin, table=True):
    __tablename__ = "player_tournament"
    __table_args__ = (
        UniqueConstraint(
            "player_id",
            "tournament_id",
            name="uq_player_tournament",
        ),
        {"schema": "app"},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    player: "Player" = Relationship(back_populates="player_tournaments")

    tournament: "Tournament" = Relationship(back_populates="player_tournaments")

    player_rounds: list["PlayerRound"] = Relationship(
        back_populates="player_tournament"
    )
