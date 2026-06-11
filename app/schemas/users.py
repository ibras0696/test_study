from pydantic import BaseModel, EmailStr, Field




class UserCreate(BaseModel):
     name:str
     email:str
     hashed_password:str = Field(min_length=8, max_length=128)


class UserEmail(BaseModel):
     email:EmailStr


class UserName(BaseModel):
     name:str



class UserRead(BaseModel):
      id:int
      name:str
      email:EmailStr

class UserPassword(BaseModel):
     new_password: str = Field(min_length=8, max_length=128)
     