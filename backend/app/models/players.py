import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.utils import get_datetime_utc

if TYPE_CHECKING:
    from .player_tournaments import PlayerTournament


# Shared properties
class PlayerBase(SQLModel):
    first_name: str = Field(max_length=255, nullable=False)
    last_name: str = Field(max_length=255, nullable=False)
    country: str | None = Field(default=None, max_length=255, nullable=True)
    is_amateur: bool | None = Field(default=None, nullable=True)
    birth_date: datetime | None = Field(default=None, nullable=True)
    world_ranking: int | None = Field(default=None, nullable=True)
    external_id: int | None = Field(default=None, nullable=True)


# Properties to receive via API on creation
class PlayerCreate(PlayerBase):
    pass


# Properties to receive via API on deletion
class PlayerDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class PlayerUpdate(SQLModel):
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    country: str | None = Field(default=None, max_length=255)
    is_amateur: bool | None = Field(default=None)
    birth_date: datetime | None = Field(default=None)
    world_ranking: int | None = Field(default=None)
    external_id: int | None = Field(default=None)


# Database model
class Player(PlayerBase, table=True):
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(sa_type=DateTime(timezone=True))  # type: ignore

    player_tournaments: list["PlayerTournament"] = Relationship(
        back_populates="player", cascade_delete=True
    )
