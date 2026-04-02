import uuid
from typing import TYPE_CHECKING

from pydantic import NonNegativeInt
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .courses import Course
    from .player_holes import PlayerHole


# Shared properties
class CourseHoleBase(SQLModel):
    course_id: uuid.UUID = Field(foreign_key="app.course.id", ondelete="CASCADE")
    hole_number: NonNegativeInt = Field(le=18)
    par: NonNegativeInt


# Properties to receive via API on creation
class CourseHoleCreate(CourseHoleBase):
    pass


# Properties to receive via API on deletion
class CourseHoleDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class CourseHoleUpdate(SQLModel):
    par: NonNegativeInt  # Par is the only updatable field for a course hole, as hole number and course association should be immutable after creation


# Database model
class CourseHole(CourseHoleBase, TimestampsMixin, table=True):
    __tablename__ = "course_hole"
    __table_args__ = (
        UniqueConstraint("course_id", "hole_number", name="uq_course_hole_number"),
        {"schema": "app"},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    course: "Course" = Relationship(back_populates="holes")

    player_holes: list["PlayerHole"] = Relationship(
        back_populates="course_hole", cascade_delete=True
    )
