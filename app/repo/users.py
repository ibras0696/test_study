from sqlalchemy.ext.asyncio import AsyncSession
from core.models.user import User




class User:
    def __init__(self,session:AsyncSession):
        self.session=session


        async def create(
                self,
                user_id:int,
                name:str,
                email:str,):
            user=User(id=user_id,name=name,email=email)
            self.session.add(user)
            await self.session.flush()
            return user
        

        
        async def get_user_by_id(user_id:int):
            user=self.session.select(User).where(User.id==user_id)
            return user.scalar_one_or_none()
        

        

            

        
        


   



