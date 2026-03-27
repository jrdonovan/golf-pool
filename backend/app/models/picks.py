import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.utils import get_datetime_utc

if TYPE_CHECKING:
    from .pool_tiers import PoolTier


# Shared properties
class PickBase(SQLModel):
    name: str = Field(unique=True, max_length=255)
    submission_id: uuid.UUID = Field(foreign_key="app.submissions.id")
    pool_tier_id: uuid.UUID = Field(foreign_key="app.pool_tiers.id")


# Properties to receive via API on creation
class PickCreate(PickBase):
    pass


# Properties to receive via API on deletion
class PickDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class PickUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)


# Database model
class Pick(PickBase, table=True):
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(sa_type=DateTime(timezone=True))  # type: ignore

    pool_tier: "PoolTier" = Relationship(back_populates="picks")
