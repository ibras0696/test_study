from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from middlewares import api_header
from routers import router

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:8000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.add_middleware(api_header.AppHeaderMiddleware)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Главная",
            "username": "тест",
            "dct": {1: "test"},
            "lst": [1, 2, 3, 4],
            "tpl": (1, 2, 3)
        },
    )


@app.get('/test', response_class=HTMLResponse)
async def tst(request: Request):
    
    return templates.TemplateResponse(
        request=request,
        name="test.html",
        context={
            "lol": "LOOOL"
        }
    )



app.include_router(router=router)
