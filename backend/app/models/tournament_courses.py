import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.utils import get_datetime_utc

if TYPE_CHECKING:
    from .courses import Course
    from .tournaments import Tournament


# Shared properties
class TournamentCourseBase(SQLModel):
    tournament_id: uuid.UUID = Field(
        foreign_key="app.tournament.id", nullable=False, ondelete="CASCADE"
    )
    course_id: uuid.UUID = Field(
        foreign_key="app.course.id", nullable=False, ondelete="CASCADE"
    )


# Properties to receive via API on creation
class TournamentCourseCreate(TournamentCourseBase):
    pass


# Properties to receive via API on deletion
class TournamentCourseDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class TournamentCourseUpdate(SQLModel):
    course_id: uuid.UUID


# Database model
class TournamentCourse(TournamentCourseBase, table=True):
    __tablename__ = "tournament_course"
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(sa_type=DateTime(timezone=True))  # type: ignore

    tournament: "Tournament" = Relationship(back_populates="tournament_courses")
    course: "Course" = Relationship(back_populates="tournament_courses")
