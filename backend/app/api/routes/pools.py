import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.models.player_pool_tiers import (
    PlayerPoolTier,
    PlayerPoolTierCreate,
    PlayerPoolTierDelete,
    PlayerPoolTierUpdate,
)
from app.models.pool_tiers import (
    PoolTier,
    PoolTierCreate,
    PoolTierDelete,
    PoolTierUpdate,
)
from app.models.pools import Pool, PoolCreate, PoolDelete, PoolStatus, PoolUpdate
from app.services.crud.pool_tiers import (
    create_player_pool_tier,
    create_pool_tier,
    delete_player_pool_tier,
    get_player_pool_tier,
    list_pool_tiers,
    update_player_pool_tier,
)
from app.services.crud.pool_tiers import delete_pool_tier as delete_pool_tier_record
from app.services.crud.pool_tiers import update_pool_tier as update_pool_tier_record
from app.services.crud.pools import (
    create_pool,
    delete_pool,
    get_pool,
    list_pools,
    update_pool,
)

router = APIRouter(prefix="/pools", tags=["pools"])


@router.get("/", response_model=list[Pool])
async def read_pools(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    tournament_id: uuid.UUID | None = None,
    status: PoolStatus | None = None,
):
    pools = list_pools(
        session=session,
        skip=skip,
        limit=limit,
        tournament_id=tournament_id,
        status=status,
    )
    return pools


@router.get("/{pool_id}", response_model=Pool)
async def read_pool(pool_id: uuid.UUID, session: SessionDep):
    pool = get_pool(session=session, pool_id=pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    return pool


@router.post("/", response_model=Pool)
async def create_pool_route(*, session: SessionDep, pool_in: PoolCreate):
    try:
        return create_pool(session=session, pool_in=pool_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{pool_id}", response_model=Pool)
async def update_pool_route(
    *, session: SessionDep, pool_id: uuid.UUID, pool_in: PoolUpdate
):
    try:
        return update_pool(session=session, pool_id=pool_id, pool_in=pool_in)
    except ValueError as e:
        detail = str(e)
        if detail == "Pool not found":
            raise HTTPException(status_code=404, detail=detail)
        raise HTTPException(status_code=400, detail=detail)


@router.delete("/{pool_id}")
async def delete_pool_route(*, session: SessionDep, pool_id: uuid.UUID) -> Any:
    try:
        return delete_pool(session=session, pool_in=PoolDelete(id=pool_id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{pool_id}/tiers", response_model=list[PoolTier])
async def read_pool_tiers(pool_id: uuid.UUID, session: SessionDep):
    pool = get_pool(session=session, pool_id=pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    return list_pool_tiers(session=session, pool_id=pool_id)


@router.post("/{pool_id}/tiers", response_model=list[PoolTier])
async def create_pool_tiers(
    pool_id: uuid.UUID, session: SessionDep, pool_tiers_in: list[PoolTierCreate]
):
    pool = get_pool(session=session, pool_id=pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")

    created_tiers: list[PoolTier] = []
    for tier_in in pool_tiers_in:
        try:
            created_tiers.append(
                create_pool_tier(
                    session=session,
                    pool_tier_in=PoolTierCreate(
                        name=tier_in.name,
                        description=tier_in.description,
                        pool_id=pool_id,
                    ),
                )
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return created_tiers


@router.patch("/{pool_id}/tiers/{tier_id}", response_model=PoolTier)
async def update_pool_tier_route(
    pool_id: uuid.UUID,
    tier_id: uuid.UUID,
    session: SessionDep,
    pool_tier_in: PoolTierUpdate,
):
    pool = get_pool(session=session, pool_id=pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")

    try:
        return update_pool_tier_record(
            session=session, tier_id=tier_id, pool_tier_in=pool_tier_in
        )
    except ValueError as e:
        detail = str(e)
        if detail == "Pool tier not found":
            raise HTTPException(status_code=404, detail=detail)
        raise HTTPException(status_code=400, detail=detail)


@router.delete("/{pool_id}/tiers/{tier_id}")
async def delete_pool_tier_route(
    pool_id: uuid.UUID, tier_id: uuid.UUID, session: SessionDep
) -> Any:
    pool = get_pool(session=session, pool_id=pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")

    try:
        return delete_pool_tier_record(
            session=session, tier_in=PoolTierDelete(id=tier_id)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/tiers/{tier_id}/player-pool-tiers", response_model=PlayerPoolTier)
async def create_player_pool_tier_route(
    tier_id: uuid.UUID,
    session: SessionDep,
    player_pool_tier_in: PlayerPoolTierCreate,
):
    if player_pool_tier_in.pool_tier_id != tier_id:
        raise HTTPException(
            status_code=400,
            detail="Path tier_id must match body pool_tier_id",
        )

    try:
        return create_player_pool_tier(
            session=session, player_pool_tier_in=player_pool_tier_in
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/player-pool-tiers/{player_pool_tier_id}", response_model=PlayerPoolTier)
async def update_player_pool_tier_route(
    player_pool_tier_id: uuid.UUID,
    session: SessionDep,
    player_pool_tier_in: PlayerPoolTierUpdate,
):
    try:
        return update_player_pool_tier(
            session=session,
            player_pool_tier_id=player_pool_tier_id,
            player_pool_tier_in=player_pool_tier_in,
        )
    except ValueError as e:
        detail = str(e)
        if detail == "Player pool tier not found":
            raise HTTPException(status_code=404, detail=detail)
        raise HTTPException(status_code=400, detail=detail)


@router.delete("/player-pool-tiers/{player_pool_tier_id}")
async def delete_player_pool_tier_route(
    player_pool_tier_id: uuid.UUID,
    session: SessionDep,
) -> Any:
    db_player_pool_tier = get_player_pool_tier(
        session=session, player_pool_tier_id=player_pool_tier_id
    )
    if not db_player_pool_tier:
        raise HTTPException(status_code=404, detail="Player pool tier not found")

    try:
        return delete_player_pool_tier(
            session=session,
            tier_in=PlayerPoolTierDelete(id=player_pool_tier_id),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
