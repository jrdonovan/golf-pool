import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .pool_tiers import PoolTier
    from .submissions import Submission
    from .tournaments import Tournament


class PoolStatus(StrEnum):
    not_started = "Not Started"
    in_progress = "In Progress"
    complete = "Complete"
    closed = "Closed"


# Shared properties
class PoolBase(SQLModel):
    name: str
    entry_fee: float | None = Field(default=None)
    status: PoolStatus = Field(
        default=PoolStatus.not_started,
        sa_type=SQLEnum(PoolStatus, schema="app", name="poolstatus"),  # type: ignore
    )
    tournament_id: uuid.UUID = Field(
        foreign_key="app.tournament.id", ondelete="CASCADE"
    )


# Properties to receive via API on creation
class PoolCreate(PoolBase):
    pass


# Properties to receive via API on deletion
class PoolDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class PoolUpdate(SQLModel):
    name: str | None = Field(default=None)
    entry_fee: float | None = Field(default=None)
    status: PoolStatus | None = Field(default=None)


# Database model
class Pool(PoolBase, TimestampsMixin, table=True):
    __table_args__ = (
        UniqueConstraint(
            "name",
            "tournament_id",
            name="uq_name_tournament",
        ),
        {"schema": "app"},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    tournament: "Tournament" = Relationship(back_populates="pools")

    tiers: list["PoolTier"] = Relationship(back_populates="pool", cascade_delete=True)

    submissions: list["Submission"] = Relationship(
        back_populates="pool", cascade_delete=True
    )
