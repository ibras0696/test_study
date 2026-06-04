from sqlalchemy.ext.asyncio import AsyncSession
from core.models.user import User




class User:
    def __init__(self,session:AsyncSession):
        self.session=session


        async def create(
        self,
        user_id: int,
        name: str,
        email: str,
        hashed_password:str):
            
         user=User(id=user_id, name=name, email=email,hashed_password=hashed_password)
         self.session.add(user)
         self.session.flush()
         return user



    async def get_user_by_id(self,user_id:int):
        user=self.session.select(User).where(User.id==user_id)
        return user.scalar_one_or_none()


    async def update_email(self, user_id:int, new_email:str):
        user=await get_user_by_id(id)

        if user == None:
            return None

        User.email=new_email
        self.session.flush()
        return user

    async def update_password(self,user_id:id,new_password:str):
        user=await get_user_by_id(user_id)
        if user == None:
            return None

        User.hashed_password=new_password
        self.session.flush()
        return user
