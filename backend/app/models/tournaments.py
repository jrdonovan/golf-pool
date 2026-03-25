import uuid
from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.utils import get_datetime_utc

if TYPE_CHECKING:
    from .organizations import Organization
    from .pools import Pool


class TournamentStatus(StrEnum):
    not_started = "Not Started"
    in_progress = "In Progress"
    complete = "Complete"
    official = "Official"


# Shared properties
class TournamentBase(SQLModel):
    name: str = Field(max_length=255)
    purse: int | None = Field(default=None, nullable=True)
    format: str | None = Field(default="stroke")
    status: TournamentStatus = Field(default=TournamentStatus.not_started)
    start_date: date
    end_date: date
    timezone: str | None = Field(default=None, max_length=255, nullable=True)
    external_id: int | None = Field(default=None, nullable=True)


# Properties to receive via API on creation
class TournamentCreate(TournamentBase):
    pass


# Properties to receive via API on deletion
class TournamentDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class TournamentUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    purse: int | None = Field(default=None)
    format: str | None = Field(default=None)
    status: TournamentStatus | None = Field(default=None)
    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)
    timezone: str | None = Field(default=None, max_length=255)
    external_id: int | None = Field(default=None, nullable=True)


# Database model
class Tournament(TournamentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(sa_type=DateTime(timezone=True))  # type: ignore

    organization: "Organization" = Relationship(back_populates="tournaments")

    pools: list["Pool"] = Relationship(back_populates="tournament", cascade_delete=True)
