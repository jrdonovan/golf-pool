import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.models.submissions import Submission, SubmissionDelete
from app.services.crud.submissions import (
    SubmissionWithPicksCreate,
    create_submission_with_picks,
    delete_submission,
    get_submission,
    list_submissions,
)

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.get("/", response_model=list[Submission])
async def read_submissions(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    pool_id: uuid.UUID | None = None,
):
    return list_submissions(session=session, skip=skip, limit=limit, pool_id=pool_id)


@router.get("/{submission_id}", response_model=Submission)
async def read_submission(submission_id: uuid.UUID, session: SessionDep):
    submission = get_submission(session=session, submission_id=submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.post("/", response_model=Submission)
async def create_submission_route(
    *, session: SessionDep, submission_in: SubmissionWithPicksCreate
):
    try:
        return create_submission_with_picks(
            session=session, submission_in=submission_in
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{submission_id}")
async def delete_submission_route(
    *, session: SessionDep, submission_id: uuid.UUID
) -> Any:
    try:
        return delete_submission(
            session=session, submission_in=SubmissionDelete(id=submission_id)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
