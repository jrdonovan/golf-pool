import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .player_rounds import PlayerRound
    from .players import Player
    from .tournaments import Tournament


# Shared properties
class PlayerTournamentBase(SQLModel):
    player_id: uuid.UUID = Field(
        foreign_key="app.player.id", nullable=False, ondelete="CASCADE"
    )
    tournament_id: uuid.UUID = Field(
        foreign_key="app.tournament.id", nullable=False, ondelete="CASCADE"
    )
    position: int | None = Field(default=None, nullable=True)
    total_score: int | None = Field(default=None, nullable=True)
    missed_cut: bool = Field(default=False)
    withdrawn: bool = Field(default=False)
    points: float = Field(default=0.0)


# Properties to receive via API on creation
class PlayerTournamentCreate(PlayerTournamentBase):
    pass


# Properties to receive via API on deletion
class PlayerTournamentDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class PlayerTournamentUpdate(SQLModel):
    position: int | None = Field(default=None)
    total_score: int | None = Field(default=None)
    missed_cut: bool | None = Field(default=None)
    withdrawn: bool | None = Field(default=None)
    points: float | None = Field(default=None)


# Database model
class PlayerTournament(PlayerTournamentBase, TimestampsMixin, table=True):
    __tablename__ = "player_tournament"
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    player: "Player" = Relationship(back_populates="player_tournaments")

    tournament: "Tournament" = Relationship(back_populates="player_tournaments")

    player_rounds: list["PlayerRound"] = Relationship(
        back_populates="player_tournament"
    )
