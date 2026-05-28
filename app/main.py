from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI(debug=True, title="Сайт")



# html_test = "./templates/index.html"
# html = None
# with open(f"{html_test}", "r", encoding="utf-8") as f:
#     html = f.read()

@app.get("/")
async def main() -> dict[str, int]:
    return {"ok": 2}

@app.post("/")
async def main_post() -> dict[str, int]:
    return {"ok status": 200}


# @app.get("/home", response_class=HTMLResponse)
# async def home():
#     return html

"""
https://workspace.google.com/intl/ru/gmail/?search=ponchik URL
https PROTOCOL 2  SSL -https / http 

workspace.google.com SUB DOMEN/DNS
google.com DOMEN/DNs
DOMEN /intl/ru/gmail ENDPOINT
QUERY PARAMETS ?search=ponchik

http://127.0.0.1:8000
"""