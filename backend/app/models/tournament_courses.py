import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .courses import Course
    from .player_rounds import PlayerRound
    from .tournaments import Tournament


# Shared properties
class TournamentCourseBase(SQLModel):
    tournament_id: uuid.UUID = Field(
        foreign_key="app.tournament.id", ondelete="CASCADE"
    )
    course_id: uuid.UUID = Field(foreign_key="app.course.id", ondelete="CASCADE")


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
class TournamentCourse(TournamentCourseBase, TimestampsMixin, table=True):
    __tablename__ = "tournament_course"
    __table_args__ = (
        UniqueConstraint(
            "tournament_id",
            "course_id",
            name="uq_tournament_course",
        ),
        {"schema": "app"},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    tournament: "Tournament" = Relationship(back_populates="tournament_courses")
    course: "Course" = Relationship(back_populates="tournament_courses")
    player_rounds: list["PlayerRound"] = Relationship(
        back_populates="tournament_course"
    )
