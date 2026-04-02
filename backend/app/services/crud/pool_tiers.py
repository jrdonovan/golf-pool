import uuid
from typing import Any

from sqlmodel import Session, select

from app.models.player_pool_tiers import (
    PlayerPoolTier,
    PlayerPoolTierCreate,
    PlayerPoolTierDelete,
    PlayerPoolTierUpdate,
)
from app.models.player_tournaments import PlayerTournament
from app.models.pool_tiers import (
    PoolTier,
    PoolTierCreate,
    PoolTierDelete,
    PoolTierUpdate,
)
from app.services.crud.pools import get_pool


def get_pool_tier(*, session: Session, tier_id: uuid.UUID) -> PoolTier | None:
    statement = select(PoolTier).where(PoolTier.id == tier_id)
    return session.exec(statement).first()


def get_pool_tier_by_name_and_pool(
    *, session: Session, name: str, pool_id: uuid.UUID
) -> PoolTier | None:
    statement = select(PoolTier).where(
        PoolTier.name == name, PoolTier.pool_id == pool_id
    )
    return session.exec(statement).first()


def list_pool_tiers(
    *, session: Session, pool_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[PoolTier]:
    statement = (
        select(PoolTier).where(PoolTier.pool_id == pool_id).offset(skip).limit(limit)
    )
    return list(session.exec(statement).all())


def create_pool_tier(*, session: Session, pool_tier_in: PoolTierCreate) -> PoolTier:
    db_pool = get_pool(session=session, pool_id=pool_tier_in.pool_id)
    if not db_pool:
        raise ValueError(f"Pool {pool_tier_in.pool_id} not found")

    existing_tier = get_pool_tier_by_name_and_pool(
        session=session,
        name=pool_tier_in.name,
        pool_id=pool_tier_in.pool_id,
    )
    if existing_tier:
        raise ValueError(
            f"Pool tier '{pool_tier_in.name}' already exists for pool {pool_tier_in.pool_id}"
        )

    db_tier = PoolTier.model_validate(pool_tier_in)
    session.add(db_tier)
    session.commit()
    session.refresh(db_tier)
    return db_tier


def update_pool_tier(
    *, session: Session, tier_id: uuid.UUID, pool_tier_in: PoolTierUpdate
) -> PoolTier:
    db_tier = get_pool_tier(session=session, tier_id=tier_id)
    if not db_tier:
        raise ValueError("Pool tier not found")

    update_data = pool_tier_in.model_dump(exclude_unset=True)
    if not update_data:
        raise ValueError("No data provided for update")

    new_name = update_data.get("name")
    if new_name and new_name != db_tier.name:
        conflict_tier = get_pool_tier_by_name_and_pool(
            session=session,
            name=new_name,
            pool_id=db_tier.pool_id,
        )
        if conflict_tier and conflict_tier.id != db_tier.id:
            raise ValueError(
                f"Pool tier '{new_name}' already exists for pool {db_tier.pool_id}"
            )

    db_tier.sqlmodel_update(update_data)
    session.add(db_tier)
    session.commit()
    session.refresh(db_tier)
    return db_tier


def delete_pool_tier(*, session: Session, tier_in: PoolTierDelete) -> Any:
    db_tier = get_pool_tier(session=session, tier_id=tier_in.id)
    if not db_tier:
        raise ValueError("Pool tier not found")
    session.delete(db_tier)
    session.commit()
    return {"ok": True}


def get_player_pool_tier(
    *, session: Session, player_pool_tier_id: uuid.UUID
) -> PlayerPoolTier | None:
    statement = select(PlayerPoolTier).where(PlayerPoolTier.id == player_pool_tier_id)
    return session.exec(statement).first()


def get_player_pool_tier_by_keys(
    *, session: Session, player_tournament_id: uuid.UUID, pool_tier_id: uuid.UUID
) -> PlayerPoolTier | None:
    statement = select(PlayerPoolTier).where(
        PlayerPoolTier.player_tournament_id == player_tournament_id,
        PlayerPoolTier.pool_tier_id == pool_tier_id,
    )
    return session.exec(statement).first()


def create_player_pool_tier(
    *, session: Session, player_pool_tier_in: PlayerPoolTierCreate
) -> PlayerPoolTier:
    db_tier = get_pool_tier(session=session, tier_id=player_pool_tier_in.pool_tier_id)
    if not db_tier:
        raise ValueError(f"Pool tier {player_pool_tier_in.pool_tier_id} not found")

    db_player_tournament = session.get(
        PlayerTournament, player_pool_tier_in.player_tournament_id
    )
    if not db_player_tournament:
        raise ValueError(
            f"Player tournament {player_pool_tier_in.player_tournament_id} not found"
        )

    db_pool = get_pool(session=session, pool_id=db_tier.pool_id)
    if not db_pool:
        raise ValueError(f"Pool {db_tier.pool_id} not found")

    if db_pool.tournament_id != db_player_tournament.tournament_id:
        raise ValueError(
            "Player tournament and pool tier must belong to the same tournament"
        )

    existing = get_player_pool_tier_by_keys(
        session=session,
        player_tournament_id=player_pool_tier_in.player_tournament_id,
        pool_tier_id=player_pool_tier_in.pool_tier_id,
    )
    if existing:
        raise ValueError("Player pool tier already exists")

    db_player_pool_tier = PlayerPoolTier.model_validate(player_pool_tier_in)
    session.add(db_player_pool_tier)
    session.commit()
    session.refresh(db_player_pool_tier)
    return db_player_pool_tier


def get_or_create_player_pool_tier(
    *, session: Session, player_tournament_id: uuid.UUID, pool_tier_id: uuid.UUID
) -> PlayerPoolTier:
    existing = get_player_pool_tier_by_keys(
        session=session,
        player_tournament_id=player_tournament_id,
        pool_tier_id=pool_tier_id,
    )
    if existing:
        return existing

    db_tier = get_pool_tier(session=session, tier_id=pool_tier_id)
    if not db_tier:
        raise ValueError(f"Pool tier {pool_tier_id} not found")

    db_player_tournament = session.get(PlayerTournament, player_tournament_id)
    if not db_player_tournament:
        raise ValueError(f"Player tournament {player_tournament_id} not found")

    db_pool = get_pool(session=session, pool_id=db_tier.pool_id)
    if not db_pool:
        raise ValueError(f"Pool {db_tier.pool_id} not found")

    if db_pool.tournament_id != db_player_tournament.tournament_id:
        raise ValueError(
            "Player tournament and pool tier must belong to the same tournament"
        )

    db_player_pool_tier = PlayerPoolTier.model_validate(
        PlayerPoolTierCreate(
            player_tournament_id=player_tournament_id,
            pool_tier_id=pool_tier_id,
        )
    )
    session.add(db_player_pool_tier)
    session.flush()
    return db_player_pool_tier


def update_player_pool_tier(
    *,
    session: Session,
    player_pool_tier_id: uuid.UUID,
    player_pool_tier_in: PlayerPoolTierUpdate,
) -> PlayerPoolTier:
    db_player_pool_tier = get_player_pool_tier(
        session=session, player_pool_tier_id=player_pool_tier_id
    )
    if not db_player_pool_tier:
        raise ValueError("Player pool tier not found")

    db_tier = get_pool_tier(session=session, tier_id=player_pool_tier_in.pool_tier_id)
    if not db_tier:
        raise ValueError(f"Pool tier {player_pool_tier_in.pool_tier_id} not found")

    db_player_tournament = session.get(
        PlayerTournament, db_player_pool_tier.player_tournament_id
    )
    if not db_player_tournament:
        raise ValueError(
            f"Player tournament {db_player_pool_tier.player_tournament_id} not found"
        )

    db_pool = get_pool(session=session, pool_id=db_tier.pool_id)
    if not db_pool:
        raise ValueError(f"Pool {db_tier.pool_id} not found")

    if db_pool.tournament_id != db_player_tournament.tournament_id:
        raise ValueError(
            "Player tournament and pool tier must belong to the same tournament"
        )

    conflict = get_player_pool_tier_by_keys(
        session=session,
        player_tournament_id=db_player_pool_tier.player_tournament_id,
        pool_tier_id=player_pool_tier_in.pool_tier_id,
    )
    if conflict and conflict.id != db_player_pool_tier.id:
        raise ValueError("Player pool tier already exists")

    db_player_pool_tier.sqlmodel_update(player_pool_tier_in.model_dump())
    session.add(db_player_pool_tier)
    session.commit()
    session.refresh(db_player_pool_tier)
    return db_player_pool_tier


def delete_player_pool_tier(*, session: Session, tier_in: PlayerPoolTierDelete) -> Any:
    db_player_pool_tier = get_player_pool_tier(
        session=session, player_pool_tier_id=tier_in.id
    )
    if not db_player_pool_tier:
        raise ValueError("Player pool tier not found")
    session.delete(db_player_pool_tier)
    session.commit()
    return {"ok": True}
