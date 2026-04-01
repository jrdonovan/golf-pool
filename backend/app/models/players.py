import uuid
from typing import TYPE_CHECKING

from pydantic import PastDate, PositiveInt
from sqlalchemy import DATE
from sqlmodel import Field, Relationship, SQLModel

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .player_tournaments import PlayerTournament


# Shared properties
class PlayerBase(SQLModel):
    live_golf_data_id: str = Field(unique=True)
    first_name: str
    last_name: str
    country: str | None = Field(default=None)
    is_amateur: bool | None = Field(default=False)
    birth_date: PastDate | None = Field(default=None, sa_type=DATE)
    world_ranking: PositiveInt | None = Field(default=None)


# Properties to receive via API on creation
class PlayerCreate(PlayerBase):
    pass


# Properties to receive via API on deletion
class PlayerDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class PlayerUpdate(SQLModel):
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    country: str | None = Field(default=None)
    is_amateur: bool | None = Field(default=None)
    birth_date: PastDate | None = Field(default=None)
    world_ranking: PositiveInt | None = Field(default=None)


# Database model
class Player(PlayerBase, TimestampsMixin, table=True):
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    player_tournaments: list["PlayerTournament"] = Relationship(
        back_populates="player", cascade_delete=True
    )
