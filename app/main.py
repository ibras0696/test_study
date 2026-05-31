import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from alembic.config import Config
from alembic import command

from middlewares import api_header

from routers import router

from core.db import engine


def run_pending_migrations() -> None:
    alembic_cfg = Config(str(Path(__file__).with_name("alembic.ini")))
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(run_pending_migrations)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
