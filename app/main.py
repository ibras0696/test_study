from fastapi import FastAPI

app = FastAPI()


users = {
    1: 'ibragim',
    2: 'Islam',
    3: 'Timur'
}


@app.get("/api/v1/")
async def root() -> dict[str, str]:
    return {"message": "FastApi work"}


@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    r = users.get(user_id)
    if not r:
        return {"message": "user not found", "status": 404}
    
    return {"user": user_id, "name": r}
    # return {"user_id": user_id}


@app.get("/user")
async def user() -> dict[str, int]:
    return {
        "user_1": 1,
        "user_2": 2,
        "user_3": 3
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
async def get_version() -> dict[str, str]:
    return {"version": "0.1.0"}