import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.utils import get_datetime_utc

if TYPE_CHECKING:
    from .player_tournaments import PlayerTournament
    from .tournament_courses import TournamentCourse
    from .tournament_rounds import TournamentRound


# Shared properties
class PlayerRoundBase(SQLModel):
    player_tournament_id: uuid.UUID = Field(
        foreign_key="app.player_tournament.id", nullable=False, ondelete="CASCADE"
    )
    tournament_round_id: uuid.UUID = Field(
        foreign_key="app.tournament_round.id", nullable=False, ondelete="CASCADE"
    )
    tournament_course_id: uuid.UUID = Field(
        foreign_key="app.tournament_course.id", nullable=False, ondelete="CASCADE"
    )
    tee_time: datetime | None = Field(default=None, nullable=True)
    is_complete: bool = Field(default=False)
    strokes: int = Field(default=0)


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
    strokes: int | None = Field(default=None)


# Database model
class PlayerRound(PlayerRoundBase, table=True):
    __tablename__ = "player_round"
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(sa_type=DateTime(timezone=True))  # type: ignore

    player_tournament: "PlayerTournament" = Relationship(back_populates="player_rounds")

    tournament_round: "TournamentRound" = Relationship(back_populates="player_rounds")

    tournament_course: "TournamentCourse" = Relationship(back_populates="player_rounds")
