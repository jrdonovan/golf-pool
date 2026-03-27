import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.utils import get_datetime_utc

if TYPE_CHECKING:
    from .pool_tiers import PoolTier
    from .tournaments import Tournament


class PoolStatus(StrEnum):
    not_started = "Not Started"
    in_progress = "In Progress"
    complete = "Complete"
    closed = "Closed"


# Shared properties
class PoolBase(SQLModel):
    name: str = Field(max_length=255)
    entry_fee: float | None = Field(default=None, nullable=True)
    status: PoolStatus = Field(default=PoolStatus.not_started)


# Properties to receive via API on creation
class PoolCreate(PoolBase):
    pass


# Properties to receive via API on deletion
class PoolDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class PoolUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    entry_fee: float | None = Field(default=None)
    status: PoolStatus | None = Field(default=None)


# Database model
class Pool(PoolBase, table=True):
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tournament_id: uuid.UUID = Field(
        foreign_key="app.tournament.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(sa_type=DateTime(timezone=True))  # type: ignore

    tournament: "Tournament" = Relationship(back_populates="pools")

    tiers: list["PoolTier"] = Relationship(back_populates="pool", cascade_delete=True)
