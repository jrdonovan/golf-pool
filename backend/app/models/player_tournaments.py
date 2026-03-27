import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.utils import get_datetime_utc

if TYPE_CHECKING:
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
class PlayerTournament(PlayerTournamentBase, table=True):
    __tablename__ = "player_tournament"
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(sa_type=DateTime(timezone=True))  # type: ignore

    player: "Player" = Relationship(back_populates="player_tournaments")

    tournament: "Tournament" = Relationship(back_populates="player_tournaments")
