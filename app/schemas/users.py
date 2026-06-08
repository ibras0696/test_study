from pydantic import BaseModel, EmailStr




class UserCreate(BaseModel):
     name:str
     email:str
     password:str


class UserEmail(BaseModel):
     email:EmailStr


class UserName(BaseModel):
     name:str