from fastapi import APIRouter

from app.api.routes import (
    login,
    organizations,
    pools,
    private,
    submissions,
    tournaments,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(organizations.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(tournaments.router)
api_router.include_router(pools.router)
api_router.include_router(submissions.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
