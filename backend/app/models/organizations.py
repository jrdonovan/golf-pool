import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .tournaments import Tournament


# Shared properties
class OrganizationBase(SQLModel):
    name: str = Field(unique=True, max_length=255)
    external_id: int | None = Field(default=None, nullable=True, unique=True)


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
class Organization(OrganizationBase, TimestampsMixin, table=True):
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    tournaments: list["Tournament"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
