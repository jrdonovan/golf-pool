import uuid
from typing import TYPE_CHECKING

from sqlmodel import Session, select

from app.models.course_holes import CourseHole, CourseHoleCreate
from app.models.courses import Course, CourseCreate, CourseUpdate
from app.models.tournament_courses import TournamentCourse, TournamentCourseCreate
from app.services.mappers.courses import CourseMapperFactory

if TYPE_CHECKING:
    from app.services.live_golf_data import CourseData


def get_course_by_live_golf_data_id(
    *, session: Session, live_golf_data_id: str
) -> Course | None:
    statement = select(Course).where(Course.live_golf_data_id == live_golf_data_id)
    return session.exec(statement).first()


def get_course_hole(
    *, session: Session, course_id: uuid.UUID, hole_number: int
) -> CourseHole | None:
    statement = select(CourseHole).where(
        CourseHole.course_id == course_id, CourseHole.hole_number == hole_number
    )
    return session.exec(statement).first()


def get_tournament_course(
    *, session: Session, tournament_id: uuid.UUID, course_id: uuid.UUID
) -> TournamentCourse | None:
    statement = select(TournamentCourse).where(
        TournamentCourse.tournament_id == tournament_id,
        TournamentCourse.course_id == course_id,
    )
    return session.exec(statement).first()


def _upsert_course(
    *, session: Session, course_create: CourseCreate, course_update: CourseUpdate
) -> tuple[Course, str]:
    db_course = get_course_by_live_golf_data_id(
        session=session, live_golf_data_id=course_create.live_golf_data_id
    )

    if db_course is None:
        db_course = Course.model_validate(course_create)
        session.add(db_course)
        return db_course, "created"

    changed_data = {
        key: value
        for key, value in course_update.model_dump(exclude_unset=True).items()
        if getattr(db_course, key) != value
    }

    if changed_data:
        db_course.sqlmodel_update(changed_data)
        session.add(db_course)
        return db_course, "updated"

    return db_course, "unchanged"


def upsert_course_hole(
    *, session: Session, hole_create: CourseHoleCreate
) -> tuple[CourseHole, str]:
    db_hole = get_course_hole(
        session=session,
        course_id=hole_create.course_id,
        hole_number=hole_create.hole_number,
    )

    if db_hole is None:
        db_hole = CourseHole.model_validate(hole_create)
        session.add(db_hole)
        return db_hole, "created"

    if db_hole.par != hole_create.par:
        db_hole.par = hole_create.par
        session.add(db_hole)
        return db_hole, "updated"

    return db_hole, "unchanged"


def upsert_course_from_data(
    *, session: Session, incoming_data: "CourseData"
) -> tuple[Course, str]:
    course_create = CourseMapperFactory.create_from_course_data(incoming_data)
    course_update = CourseMapperFactory.update_from_course_data(incoming_data)
    db_course, result = _upsert_course(
        session=session, course_create=course_create, course_update=course_update
    )

    # We need the course ID to be set before upserting holes, so flush if newly created
    if result == "created":
        session.flush()

    for hole_data in incoming_data.holes:
        hole_create = CourseMapperFactory.create_hole(hole_data, course_id=db_course.id)
        upsert_course_hole(session=session, hole_create=hole_create)

    return db_course, result


def upsert_tournament_course(
    *, session: Session, tournament_id: uuid.UUID, course_id: uuid.UUID
) -> tuple[TournamentCourse, str]:
    db_tc = get_tournament_course(
        session=session, tournament_id=tournament_id, course_id=course_id
    )

    if db_tc is None:
        db_tc = TournamentCourse.model_validate(
            TournamentCourseCreate(tournament_id=tournament_id, course_id=course_id)
        )
        session.add(db_tc)
        return db_tc, "created"

    return db_tc, "unchanged"
