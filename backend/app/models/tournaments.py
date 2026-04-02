import uuid
from datetime import date
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import NonNegativeInt
from pydantic_extra_types.timezone_name import TimeZoneName
from sqlalchemy import Enum as SQLEnum
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.utils import TimestampsMixin

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


class TournamentFormat(StrEnum):
    stroke = "stroke"
    team = "team"
    team_match = "team match"
    stableford = "stableford"


# Shared properties
class TournamentBase(SQLModel):
    name: str = Field(max_length=255)
    organization_id: uuid.UUID = Field(
        foreign_key="app.organization.id", ondelete="CASCADE"
    )
    year: int = Field(ge=1900, le=2100)
    purse: NonNegativeInt | None = Field(default=None)
    format: TournamentFormat | None = Field(
        default=None,
        sa_type=SQLEnum(TournamentFormat, schema="app", name="tournamentformat"),  # type: ignore
    )
    status: TournamentStatus | None = Field(
        default=None,
        sa_type=SQLEnum(TournamentStatus, schema="app", name="tournamentstatus"),  # type: ignore
    )
    start_date: date
    end_date: date
    timezone: TimeZoneName | None = Field(default=None, max_length=255)
    live_golf_data_id: str


# Properties to receive via API on creation
class TournamentCreate(TournamentBase):
    pass


# Properties to receive via API on deletion
class TournamentDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class TournamentUpdate(SQLModel):
    name: str | None = Field(default=None)
    purse: NonNegativeInt | None = Field(default=None)
    format: str | None = Field(default=None)
    status: TournamentStatus | None = Field(default=None)
    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)
    timezone: TimeZoneName | None = Field(default=None)


# Database model
class Tournament(TournamentBase, TimestampsMixin, table=True):
    __table_args__ = (
        UniqueConstraint(
            "name", "organization_id", "year", name="uq_tournament_name_org_year"
        ),
        {"schema": "app"},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

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
