from sqlalchemy.ext.asyncio import AsyncSession
from core.models.user import User
from sqlalchemy import select


class UserRepo:

   def __init__(self,session:AsyncSession):
        self.session=session
    
   async def user_create(self, name: str, email: str, hashed_password: str) -> User:
     user=User(name=name,email=email,hashed_password=hashed_password)

     self.session.add(user)
     await self.session.flush()
     return user
    
    
   async def get_users(self) -> list[User]:
       result=await self.session.execute(select(User))
       return list(result.scalars().all())
    
    
   async def get_user_by_id(self, id:int)-> None | User:
       return await self.session.get(User, id)
    
    
   async def get_user_by_email(self, email: str) -> User | None:
      result = await self.session.execute(
         select(User).where(User.email == email)
      )
      return result.scalar_one_or_none()
      
      
   async def update_email(self,id:int,new_email:str)-> User | None:
       user=await self.get_user_by_id(id)
       if user is None:
          return None
       
       user.email=new_email
       await self.session.flush()
       return user

   async def update_name(self,id:int,new_name:str)-> User | None:
       user=await self.get_user_by_id(id)
       if user is None:
          return None
       
       user.name=new_name
       await self.session.flush()
       return user
    
   async def update_password(self,id:int,new_password:str)-> User | None:
       user=await self.get_user_by_id(id)
       if user is None:
          return None
       
       user.hashed_password=new_password
       await self.session.flush()
       return user


   async def user_delete(self,id:int)-> bool:
       user=await self.get_user_by_id(id)
       if user is None:
          return None
       
       await self.session.delete(user)
       await self.session.flush()
       return True       
       
    
