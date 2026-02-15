from aiogram import Router
from .help import router as help_router
from .start import router as start_router
from .namaz import router as namaz_router

router = Router()

router.include_routers(help_router, start_router, namaz_router)
