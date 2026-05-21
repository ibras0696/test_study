from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr

from routers import router

app = FastAPI()

app.include_router(router=router)