import uuid
from typing import TYPE_CHECKING

from pydantic import NonNegativeInt
from sqlmodel import Field, Relationship, SQLModel

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .course_holes import CourseHole
    from .tournament_courses import TournamentCourse


# Shared properties
class CourseBase(SQLModel):
    live_golf_data_id: str = Field(unique=True)
    name: str
    city: str | None = Field(default=None)
    state: str | None = Field(default=None)
    country: str | None = Field(default=None)
    par_front_nine: NonNegativeInt | None = Field(default=None)
    par_back_nine: NonNegativeInt | None = Field(default=None)
    par_total: NonNegativeInt | None = Field(default=None)
    yardage_front_nine: NonNegativeInt | None = Field(default=None)
    yardage_back_nine: NonNegativeInt | None = Field(default=None)
    yardage_total: NonNegativeInt | None = Field(default=None)


# Properties to receive via API on creation
class CourseCreate(CourseBase):
    pass


# Properties to receive via API on deletion
class CourseDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class CourseUpdate(SQLModel):
    name: str | None = Field(default=None)
    city: str | None = Field(default=None)
    state: str | None = Field(default=None)
    country: str | None = Field(default=None)
    par_front_nine: NonNegativeInt | None = Field(default=None)
    par_back_nine: NonNegativeInt | None = Field(default=None)
    par_total: NonNegativeInt | None = Field(default=None)
    yardage_front_nine: NonNegativeInt | None = Field(default=None)
    yardage_back_nine: NonNegativeInt | None = Field(default=None)
    yardage_total: NonNegativeInt | None = Field(default=None)


# Database model
class Course(CourseBase, TimestampsMixin, table=True):
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    holes: list["CourseHole"] = Relationship(
        back_populates="course", cascade_delete=True
    )

    tournament_courses: list["TournamentCourse"] = Relationship(
        back_populates="course", cascade_delete=True
    )
