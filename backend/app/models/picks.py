import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.utils import get_datetime_utc

if TYPE_CHECKING:
    from .player_pool_tiers import PlayerPoolTier
    from .submissions import Submission


# Shared properties
class PickBase(SQLModel):
    submission_id: uuid.UUID = Field(foreign_key="app.submission.id")
    player_pool_tier_id: uuid.UUID = Field(foreign_key="app.player_pool_tier.id")


# Properties to receive via API on creation
class PickCreate(PickBase):
    pass


# Properties to receive via API on deletion
class PickDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class PickUpdate(SQLModel):
    player_pool_tier_id: uuid.UUID


# Database model
class Pick(PickBase, table=True):
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(sa_type=DateTime(timezone=True))  # type: ignore

    submission: "Submission" = Relationship(back_populates="picks")
    player_pool_tier: "PlayerPoolTier" = Relationship(back_populates="picks")
