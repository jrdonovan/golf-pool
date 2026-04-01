import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.utils import TimestampsMixin

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
class Pick(PickBase, TimestampsMixin, table=True):
    __table_args__ = (
        UniqueConstraint(
            "submission_id",
            "player_pool_tier_id",
            name="uq_submission_player_pool_tier",
        ),
        {"schema": "app"},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    submission: "Submission" = Relationship(back_populates="picks")
    player_pool_tier: "PlayerPoolTier" = Relationship(back_populates="picks")
