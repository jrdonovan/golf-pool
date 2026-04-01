import uuid
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .picks import Pick
    from .pools import Pool


# Shared properties
class SubmissionBase(SQLModel):
    name: str = Field(max_length=255)
    pool_id: uuid.UUID = Field(
        foreign_key="app.pool.id", nullable=False, ondelete="CASCADE"
    )
    submitter_name: str = Field(max_length=255, nullable=False)
    submitter_email: EmailStr = Field(max_length=255, nullable=False)
    total_score: float = Field(default=0)
    tiebreaker_strokes: int | None = Field(default=None, nullable=True)


# Properties to receive via API on creation
class SubmissionCreate(SubmissionBase):
    pass


# Properties to receive via API on deletion
class SubmissionDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class SubmissionUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    user_id: uuid.UUID | None = Field(default=None)
    total_score: float | None = Field(default=None)
    tiebreaker_strokes: int | None = Field(default=None)


# Database model
class Submission(SubmissionBase, TimestampsMixin, table=True):
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    pool: "Pool" = Relationship(back_populates="submissions")
    picks: list["Pick"] = Relationship(back_populates="submission", cascade_delete=True)
