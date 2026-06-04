from fastapi import APIRouter

from .posts import router as posts
from .users import router as users

router = APIRouter(prefix="/api")

router.include_router(posts)
router.include_router(users)
