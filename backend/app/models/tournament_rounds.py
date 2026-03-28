import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.utils import get_datetime_utc

if TYPE_CHECKING:
    from .tournaments import Tournament


# Shared properties
class TournamentRoundBase(SQLModel):
    tournament_id: uuid.UUID = Field(
        foreign_key="app.tournament.id", nullable=False, ondelete="CASCADE"
    )
    round_number: int = Field(nullable=False)
    scheduled_date: date = Field(nullable=False)


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
class TournamentRound(TournamentRoundBase, table=True):
    __tablename__ = "tournament_round"
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(sa_type=DateTime(timezone=True))  # type: ignore

    tournament: "Tournament" = Relationship(back_populates="tournament_rounds")
