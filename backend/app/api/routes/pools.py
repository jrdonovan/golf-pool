import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.models.pools import Pool, PoolCreate, PoolDelete, PoolStatus, PoolUpdate
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
