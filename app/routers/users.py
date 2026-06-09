from fastapi import APIRouter, HTTPException, Header, Cookie
from starlette import status
from schemas.users import UserCreate,UserEmail,UserName
from core.db import DB_DEPS
from services.users import UserServise
from core.deps import get_user_service





router = APIRouter(prefix="/users", tags=["users"])















