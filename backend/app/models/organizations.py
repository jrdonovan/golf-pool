import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.utils import get_datetime_utc

if TYPE_CHECKING:
    from .tournaments import Tournament


# Shared properties
class OrganizationBase(SQLModel):
    name: str = Field(unique=True, max_length=255)
    external_id: int | None = Field(default=None, nullable=True)


# Properties to receive via API on creation
class OrganizationCreate(OrganizationBase):
    pass


# Properties to receive via API on deletion
class OrganizationDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class OrganizationUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    external_id: int | None = None


# Database model
class Organization(OrganizationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(sa_type=DateTime(timezone=True))  # type: ignore

    tournaments: list["Tournament"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
