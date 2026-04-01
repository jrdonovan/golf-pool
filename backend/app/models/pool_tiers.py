import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .player_pool_tiers import PlayerPoolTier
    from .pools import Pool


# Shared properties
class PoolTierBase(SQLModel):
    name: str
    pool_id: uuid.UUID = Field(foreign_key="app.pool.id", ondelete="CASCADE")
    description: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class PoolTierCreate(PoolTierBase):
    pass


# Properties to receive via API on deletion
class PoolTierDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class PoolTierUpdate(SQLModel):
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)


# Database model
class PoolTier(PoolTierBase, TimestampsMixin, table=True):
    __tablename__ = "pool_tier"
    __table_args__ = (
        UniqueConstraint(
            "name",
            "pool_id",
            name="uq_pool_tiers_name_pool_id_key",
        ),
        {"schema": "app"},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    pool: "Pool" = Relationship(back_populates="tiers")
    player_pool_tiers: list["PlayerPoolTier"] = Relationship(
        back_populates="pool_tier", cascade_delete=True
    )
