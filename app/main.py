from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

users = {
    1: {
        'username': 'test',
        'email': 'test@test.yes',
        'age': 20
    }
}

class UserCreate(BaseModel):
    username: str
    email: str
    age: int


@app.delete('/users')
async def create_user(user_data: UserCreate
                      ) -> dict[str, str | dict]:
    tl = len(users) + 1
    users[tl] = {
        'username': user_data.username,
        'email': user_data.email,
        'age': user_data.age
    }
    return {"status": 'ok', 'data': users}

@app.get('/users')
async def get_users() -> dict:
    return users














# users = {
#     1: {'name': 'ibragim', 'age': 21},
#     2: {'name': 'Islam', 'age': 19},
#     3: {'name': 'Timur', 'age': 20}
# }


# @app.get("/users/{user_id}")
# async def get_user(user_id: int) -> dict:
#     r = users.get(user_id)
#     if not r:
#         raise HTTPException(status_code=404, detail="user not found")
    
#     return {"user": user_id, "name": r}
#     # return {"user_id": user_id}

# # http://127.0.0.1:8000/user/age?min_age=10&max_age=20
# @app.get("/user/age")
# async def list_users(
#     min_age: int = 10,
#     max_age: int = 20
#     ) -> dict:
#     d = {
#         key: value for key, value in users.items() 
#         if min_age <= value['age'] <= max_age
#     }
#     return d

