import uuid
from datetime import date
from typing import TYPE_CHECKING

from pydantic import PositiveInt
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .player_rounds import PlayerRound
    from .tournaments import Tournament


# Shared properties
class TournamentRoundBase(SQLModel):
    tournament_id: uuid.UUID = Field(
        foreign_key="app.tournament.id", ondelete="CASCADE"
    )
    round_number: PositiveInt = Field(le=4)
    scheduled_date: date


# Properties to receive via API on creation
class TournamentRoundCreate(TournamentRoundBase):
    pass


# Properties to receive via API on deletion
class TournamentRoundDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class TournamentRoundUpdate(SQLModel):
    scheduled_date: date


# Database model
class TournamentRound(TournamentRoundBase, TimestampsMixin, table=True):
    __tablename__ = "tournament_round"
    __table_args__ = (
        UniqueConstraint(
            "tournament_id",
            "round_number",
            name="uq_tournament_round",
        ),
        {"schema": "app"},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    tournament: "Tournament" = Relationship(back_populates="tournament_rounds")

    player_rounds: list["PlayerRound"] = Relationship(back_populates="tournament_round")
