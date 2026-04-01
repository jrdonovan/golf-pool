import uuid
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .picks import Pick
    from .pools import Pool


# Shared properties
class SubmissionBase(SQLModel):
    name: str
    pool_id: uuid.UUID = Field(foreign_key="app.pool.id", ondelete="CASCADE")
    submitter_name: str
    submitter_email: EmailStr
    total_score: float = Field(default=0)
    tiebreaker_strokes: int


# Properties to receive via API on creation
class SubmissionCreate(SubmissionBase):
    pass


# Properties to receive via API on deletion
class SubmissionDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class SubmissionUpdate(SQLModel):
    name: str | None = Field(default=None)
    total_score: float | None = Field(default=None)
    tiebreaker_strokes: int | None = Field(default=None)


# Database model
class Submission(SubmissionBase, TimestampsMixin, table=True):
    __table_args__ = (
        UniqueConstraint(
            "name",
            "pool_id",
            name="uq_submissions_name_pool_id_key",
        ),
        {"schema": "app"},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    pool: "Pool" = Relationship(back_populates="submissions")
    picks: list["Pick"] = Relationship(back_populates="submission", cascade_delete=True)
