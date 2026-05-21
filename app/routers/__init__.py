from fastapi import APIRouter

from .profile import router as profile
from .users import router as users

router = APIRouter(prefix="/api")

router.include_router(profile)
router.include_router(users)
