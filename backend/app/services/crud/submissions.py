import uuid
from typing import Any

from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Session, select

from app.models.picks import Pick, PickCreate
from app.models.submissions import Submission, SubmissionCreate, SubmissionDelete
from app.services.crud.pool_tiers import get_or_create_player_pool_tier, get_pool_tier
from app.services.crud.pools import get_pool


class SubmissionPickInput(BaseModel):
    pool_tier_id: uuid.UUID
    player_tournament_id: uuid.UUID


class SubmissionWithPicksCreate(BaseModel):
    name: str
    pool_id: uuid.UUID
    submitter_name: str
    submitter_email: EmailStr
    tiebreaker_strokes: int
    picks: list[SubmissionPickInput] = Field(default_factory=list)


def get_submission(*, session: Session, submission_id: uuid.UUID) -> Submission | None:
    statement = select(Submission).where(Submission.id == submission_id)
    return session.exec(statement).first()


def get_submission_by_name_and_pool(
    *, session: Session, name: str, pool_id: uuid.UUID
) -> Submission | None:
    statement = select(Submission).where(
        Submission.name == name,
        Submission.pool_id == pool_id,
    )
    return session.exec(statement).first()


def list_submissions(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    pool_id: uuid.UUID | None = None,
) -> list[Submission]:
    statement = select(Submission)
    if pool_id:
        statement = statement.where(Submission.pool_id == pool_id)
    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement).all())


def create_submission_with_picks(
    *, session: Session, submission_in: SubmissionWithPicksCreate
) -> Submission:
    db_pool = get_pool(session=session, pool_id=submission_in.pool_id)
    if not db_pool:
        raise ValueError(f"Pool {submission_in.pool_id} not found")

    existing_submission = get_submission_by_name_and_pool(
        session=session, name=submission_in.name, pool_id=submission_in.pool_id
    )
    if existing_submission:
        raise ValueError(
            f"Submission '{submission_in.name}' already exists for pool {submission_in.pool_id}"
        )

    submission_create = SubmissionCreate(
        name=submission_in.name,
        pool_id=submission_in.pool_id,
        submitter_name=submission_in.submitter_name,
        submitter_email=submission_in.submitter_email,
        tiebreaker_strokes=submission_in.tiebreaker_strokes,
    )
    db_submission = Submission.model_validate(submission_create)
    session.add(db_submission)
    session.flush()

    used_tier_ids: set[uuid.UUID] = set()
    used_player_tournament_ids: set[uuid.UUID] = set()

    for pick in submission_in.picks:
        if pick.pool_tier_id in used_tier_ids:
            raise ValueError(
                f"Duplicate pick for pool tier {pick.pool_tier_id} is not allowed"
            )
        used_tier_ids.add(pick.pool_tier_id)

        if pick.player_tournament_id in used_player_tournament_ids:
            raise ValueError(
                f"Duplicate player_tournament_id {pick.player_tournament_id} is not allowed"
            )
        used_player_tournament_ids.add(pick.player_tournament_id)

        db_pool_tier = get_pool_tier(session=session, tier_id=pick.pool_tier_id)
        if not db_pool_tier:
            raise ValueError(f"Pool tier {pick.pool_tier_id} not found")
        if db_pool_tier.pool_id != submission_in.pool_id:
            raise ValueError(
                f"Pool tier {pick.pool_tier_id} does not belong to pool {submission_in.pool_id}"
            )

        db_player_pool_tier = get_or_create_player_pool_tier(
            session=session,
            pool_tier_id=pick.pool_tier_id,
            player_tournament_id=pick.player_tournament_id,
        )

        db_pick = Pick.model_validate(
            PickCreate(
                submission_id=db_submission.id,
                player_pool_tier_id=db_player_pool_tier.id,
            )
        )
        session.add(db_pick)

    session.commit()
    session.refresh(db_submission)
    return db_submission


def delete_submission(*, session: Session, submission_in: SubmissionDelete) -> Any:
    db_submission = get_submission(session=session, submission_id=submission_in.id)
    if not db_submission:
        raise ValueError("Submission not found")
    session.delete(db_submission)
    session.commit()
    return {"ok": True}
