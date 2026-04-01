import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy import Enum as SQLEnum
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .course_holes import CourseHole
    from .player_rounds import PlayerRound


class HoleResult(StrEnum):
    condor = "Condor"
    albatross = "Albatross"
    eagle = "Eagle"
    birdie = "Birdie"
    par = "Par"
    bogey = "Bogey"
    double_bogey = "Double Bogey"
    triple_bogey_or_worse = "Triple Bogey or Worse"


# Shared properties
class PlayerHoleBase(SQLModel):
    player_round_id: uuid.UUID = Field(
        foreign_key="app.player_round.id", ondelete="CASCADE"
    )
    course_hole_id: uuid.UUID = Field(
        foreign_key="app.course_hole.id", ondelete="CASCADE"
    )
    strokes: NonNegativeInt = Field(default=0)
    score_to_par: int = Field(default=0)
    result: HoleResult | None = Field(
        default=None,
        sa_type=SQLEnum(HoleResult, schema="app", name="holeresult"),  # type: ignore
    )
    is_playoff_hole: bool = Field(default=False)
    play_order: PositiveInt


# Properties to receive via API on creation
class PlayerHoleCreate(PlayerHoleBase):
    pass


# Properties to receive via API on deletion
class PlayerHoleDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class PlayerHoleUpdate(SQLModel):
    strokes: NonNegativeInt | None = Field(default=None)
    score_to_par: int | None = Field(default=None)
    result: HoleResult | None = Field(default=None)
    is_playoff_hole: bool | None = Field(default=None)
    play_order: PositiveInt | None = Field(default=None)


# Database model
class PlayerHole(PlayerHoleBase, TimestampsMixin, table=True):
    __tablename__ = "player_hole"
    __table_args__ = (
        UniqueConstraint(
            "player_round_id",
            "course_hole_id",
            "play_order",
            name="uq_player_hole_round_hole_order",
        ),
        {"schema": "app"},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    player_round: "PlayerRound" = Relationship(back_populates="player_holes")

    course_hole: "CourseHole" = Relationship(back_populates="player_holes")
