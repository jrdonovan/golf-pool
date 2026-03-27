import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.utils import get_datetime_utc

if TYPE_CHECKING:
    from .course_holes import CourseHole


# Shared properties
class CourseBase(SQLModel):
    external_id: int | None = Field(default=None, nullable=True)
    name: str = Field(max_length=255)
    city: str = Field(max_length=255)
    state: str = Field(max_length=255)
    country: str = Field(max_length=255)
    par_front_nine: int | None = Field(default=None)
    par_back_nine: int | None = Field(default=None)
    par_total: int | None = Field(default=None)
    yardage_front_nine: int | None = Field(default=None)
    yardage_back_nine: int | None = Field(default=None)
    yardage_total: int | None = Field(default=None)


# Properties to receive via API on creation
class CourseCreate(CourseBase):
    pass


# Properties to receive via API on deletion
class CourseDelete(SQLModel):
    id: uuid.UUID


# Properties to receive via API on update
class CourseUpdate(SQLModel):
    external_id: int | None = Field(default=None, nullable=True)
    name: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=255)
    state: str | None = Field(default=None, max_length=255)
    country: str | None = Field(default=None, max_length=255)
    par_front_nine: int | None = Field(default=None)
    par_back_nine: int | None = Field(default=None)
    par_total: int | None = Field(default=None)
    yardage_front_nine: int | None = Field(default=None)
    yardage_back_nine: int | None = Field(default=None)
    yardage_total: int | None = Field(default=None)


# Database model
class Course(CourseBase, table=True):
    __table_args__ = {"schema": "app"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(sa_type=DateTime(timezone=True))  # type: ignore

    holes: list["CourseHole"] = Relationship(
        back_populates="course", cascade_delete=True
    )
