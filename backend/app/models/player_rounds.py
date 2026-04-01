import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import NonNegativeInt, PositiveInt
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.utils import TimestampsMixin

if TYPE_CHECKING:
    from .player_holes import PlayerHole
    from .player_tournaments import PlayerTournament
    from .tournament_courses import TournamentCourse
    from .tournament_rounds import TournamentRound


# Shared properties
class PlayerRoundBase(SQLModel):
    player_tournament_id: uuid.UUID = Field(
        foreign_key="app.player_tournament.id", ondelete="CASCADE"
    )
    tournament_round_id: uuid.UUID = Field(
        foreign_key="app.tournament_round.id", ondelete="CASCADE"
    )
    tournament_course_id: uuid.UUID = Field(
        foreign_key="app.tournament_course.id", ondelete="CASCADE"
    )
    tee_time: datetime | None = Field(default=None)
    is_complete: bool = Field(default=False)
    strokes: NonNegativeInt = Field(default=0)
    score_to_par: int = Field(default=0)
    starting_hole: PositiveInt = Field(default=1, le=18)


# Properties to receive via API on creation
class PlayerRoundCreate(PlayerRoundBase):
    pass


# Properties to receive via API on deletion
class PlayerRoundDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class PlayerRoundUpdate(SQLModel):
    tee_time: datetime | None = Field(default=None)
    is_complete: bool | None = Field(default=None)
    strokes: NonNegativeInt | None = Field(default=None)
    score_to_par: int | None = Field(default=None)
    starting_hole: PositiveInt | None = Field(default=None, le=18)


# Database model
class PlayerRound(PlayerRoundBase, TimestampsMixin, table=True):
    __tablename__ = "player_round"
    __table_args__ = (
        UniqueConstraint(
            "player_tournament_id",
            "tournament_course_id",
            "tournament_round_id",
            name="uq_player_course_round",
        ),
        {"schema": "app"},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    player_tournament: "PlayerTournament" = Relationship(back_populates="player_rounds")

    tournament_round: "TournamentRound" = Relationship(back_populates="player_rounds")

    tournament_course: "TournamentCourse" = Relationship(back_populates="player_rounds")

    player_holes: list["PlayerHole"] = Relationship(back_populates="player_round")
