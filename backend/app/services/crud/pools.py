import uuid
from typing import Any

from sqlmodel import Session, select

from app.models.pools import Pool, PoolCreate, PoolDelete, PoolStatus, PoolUpdate
from app.services.crud.tournaments import get_tournament


def get_pool(*, session: Session, pool_id: uuid.UUID) -> Pool | None:
    statement = select(Pool).where(Pool.id == pool_id)
    return session.exec(statement).first()


def get_pool_by_name_and_tournament(
    *, session: Session, name: str, tournament_id: uuid.UUID
) -> Pool | None:
    statement = select(Pool).where(
        Pool.name == name,
        Pool.tournament_id == tournament_id,
    )
    return session.exec(statement).first()


def list_pools(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    tournament_id: uuid.UUID | None = None,
    status: PoolStatus | None = None,
) -> list[Pool]:
    statement = select(Pool)

    if tournament_id:
        statement = statement.where(Pool.tournament_id == tournament_id)
    if status:
        statement = statement.where(Pool.status == status)

    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement).all())


def create_pool(*, session: Session, pool_in: PoolCreate) -> Pool:
    db_tournament = get_tournament(session=session, tournament_id=pool_in.tournament_id)
    if not db_tournament:
        raise ValueError(f"Tournament {pool_in.tournament_id} not found")

    existing_pool = get_pool_by_name_and_tournament(
        session=session,
        name=pool_in.name,
        tournament_id=pool_in.tournament_id,
    )
    if existing_pool:
        raise ValueError(
            f"Pool '{pool_in.name}' already exists for tournament {pool_in.tournament_id}"
        )

    db_pool = Pool.model_validate(pool_in)
    session.add(db_pool)
    session.commit()
    session.refresh(db_pool)
    return db_pool


def update_pool(*, session: Session, pool_id: uuid.UUID, pool_in: PoolUpdate) -> Pool:
    db_pool = get_pool(session=session, pool_id=pool_id)
    if not db_pool:
        raise ValueError("Pool not found")

    update_data = pool_in.model_dump(exclude_unset=True)
    if not update_data:
        raise ValueError("No data provided for update")

    new_name = update_data.get("name")
    if new_name and new_name != db_pool.name:
        conflict_pool = get_pool_by_name_and_tournament(
            session=session,
            name=new_name,
            tournament_id=db_pool.tournament_id,
        )
        if conflict_pool and conflict_pool.id != db_pool.id:
            raise ValueError(
                f"Pool '{new_name}' already exists for tournament {db_pool.tournament_id}"
            )

    db_pool.sqlmodel_update(update_data)
    session.add(db_pool)
    session.commit()
    session.refresh(db_pool)
    return db_pool


def delete_pool(*, session: Session, pool_in: PoolDelete) -> Any:
    db_pool = get_pool(session=session, pool_id=pool_in.id)
    if not db_pool:
        raise ValueError("Pool not found")
    session.delete(db_pool)
    session.commit()
    return {"ok": True}
