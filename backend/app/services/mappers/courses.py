import uuid

from app.models.course_holes import CourseHoleCreate
from app.models.courses import CourseCreate, CourseUpdate
from app.services.live_golf_data import CourseData, HoleData


class CourseMapperFactory:
    @staticmethod
    def create_from_course_data(incoming_data: CourseData) -> CourseCreate:
        return CourseCreate(
            live_golf_data_id=incoming_data.courseId,
            name=incoming_data.courseName,
            city=incoming_data.location.city,
            state=incoming_data.location.state,
            country=incoming_data.location.country,
            par_front_nine=incoming_data.parFrontNine,
            par_back_nine=incoming_data.parBackNine,
            par_total=incoming_data.parTotal,
        )

    @staticmethod
    def update_from_course_data(incoming_data: CourseData) -> CourseUpdate:
        return CourseUpdate(
            name=incoming_data.courseName,
            city=incoming_data.location.city,
            state=incoming_data.location.state,
            country=incoming_data.location.country,
            par_front_nine=incoming_data.parFrontNine,
            par_back_nine=incoming_data.parBackNine,
            par_total=incoming_data.parTotal,
        )

    @staticmethod
    def create_hole(
        incoming_data: HoleData, *, course_id: uuid.UUID
    ) -> CourseHoleCreate:
        return CourseHoleCreate(
            course_id=course_id, hole_number=incoming_data.holeId, par=incoming_data.par
        )
