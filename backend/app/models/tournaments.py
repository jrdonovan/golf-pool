import uuid
from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import PositiveInt
from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.utils import get_datetime_utc

if TYPE_CHECKING:
    from .organizations import Organization
    from .player_tournaments import PlayerTournament
    from .pools import Pool
    from .tournament_courses import TournamentCourse
    from .tournament_rounds import TournamentRound


class TournamentStatus(StrEnum):
    not_started = "Not Started"
    in_progress = "In Progress"
    complete = "Complete"
    official = "Official"


# Shared properties
class TournamentBase(SQLModel):
    name: str = Field(max_length=255)
    organization_id: uuid.UUID = Field(
        foreign_key="app.organization.id", nullable=False, ondelete="CASCADE"
    )
    purse: PositiveInt | None = Field(default=None, nullable=True)
    format: str | None = Field(default="stroke")
    status: TournamentStatus = Field(
        default=TournamentStatus.not_started,
        sa_type=SQLEnum(TournamentStatus, schema="app", name="tournamentstatus"),  # type: ignore
    )
    start_date: date
    end_date: date
    timezone: str | None = Field(default=None, max_length=255, nullable=True)
    external_id: int | None = Field(default=None, nullable=True, unique=True)


# Properties to receive via API on creation
class TournamentCreate(TournamentBase):
    pass


# Properties to receive via API on deletion
class TournamentDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class TournamentUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    purse: PositiveInt | None = Field(default=None)
    format: str | None = Field(default=None)
    status: TournamentStatus | None = Field(default=None)
    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)
    timezone: str | None = Field(default=None, max_length=255)
    external_id: int | None = Field(default=None, nullable=True)


# Database model
class Tournament(TournamentBase, table=True):
    __table_args__ = (
        UniqueConstraint(
            "name", "organization_id", "start_date", name="uq_tournament_name_org_start"
        ),
        {"schema": "app"},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(sa_type=DateTime(timezone=True))  # type: ignore

    organization: "Organization" = Relationship(back_populates="tournaments")

    pools: list["Pool"] = Relationship(back_populates="tournament", cascade_delete=True)

    player_tournaments: list["PlayerTournament"] = Relationship(
        back_populates="tournament", cascade_delete=True
    )

    tournament_courses: list["TournamentCourse"] = Relationship(
        back_populates="tournament", cascade_delete=True
    )

    tournament_rounds: list["TournamentRound"] = Relationship(
        back_populates="tournament", cascade_delete=True
    )


class TournamentPublic(TournamentBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime | None
    updated_at: datetime | None


class TournamentsPublic(TournamentBase):
    data: list[TournamentPublic]
