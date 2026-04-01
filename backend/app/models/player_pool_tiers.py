import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .picks import Pick
    from .pool_tiers import PoolTier


# Shared properties
class PlayerPoolTierBase(SQLModel):
    player_tournament_id: uuid.UUID = Field(
        foreign_key="app.player_tournament.id", nullable=False, ondelete="CASCADE"
    )
    pool_tier_id: uuid.UUID = Field(
        foreign_key="app.pool_tier.id", nullable=False, ondelete="CASCADE"
    )


# Properties to receive via API on creation
class PlayerPoolTierCreate(PlayerPoolTierBase):
    pass


# Properties to receive via API on deletion
class PlayerPoolTierDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class PlayerPoolTierUpdate(SQLModel):
    pool_tier_id: uuid.UUID | None = Field(default=None)
    # No need to update player_tournament_id since it should be immutable after creation


# Database model
class PlayerPoolTier(PlayerPoolTierBase, TimestampsMixin, table=True):
    __tablename__ = "player_pool_tier"
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    pool_tier: "PoolTier" = Relationship(back_populates="player_pool_tiers")
    picks: list["Pick"] = Relationship(
        back_populates="player_pool_tier", cascade_delete=True
    )
