import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .courses import Course
    from .player_holes import PlayerHole


# Shared properties
class CourseHoleBase(SQLModel):
    course_id: uuid.UUID = Field(
        foreign_key="app.course.id", nullable=False, ondelete="CASCADE"
    )
    hole_number: int = Field(nullable=False)
    par: int = Field(nullable=False)


# Properties to receive via API on creation
class CourseHoleCreate(CourseHoleBase):
    pass


# Properties to receive via API on deletion
class CourseHoleDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class CourseHoleUpdate(SQLModel):
    par: int  # Par is the only updatable field for a course hole, as hole number and course association should be immutable after creation


# Database model
class CourseHole(CourseHoleBase, TimestampsMixin, table=True):
    __tablename__ = "course_hole"
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    course: "Course" = Relationship(back_populates="holes")

    player_holes: list["PlayerHole"] = Relationship(
        back_populates="course_hole", cascade_delete=True
    )
