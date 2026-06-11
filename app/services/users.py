from core.models.user import User
from repo.users import UserRepo


class UserServise:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    async def create_user(
        self,
        name: str,
        email: str,
        hashed_password: str,
    ) -> User:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name is empty")
        if not isinstance(email, str) or not email.strip():
            raise ValueError("email is empty")
        if not isinstance(hashed_password, str) or not hashed_password.strip():
            raise ValueError("hashed_password is empty")

        user = await self.repo.user_create(
            name=name,
            email=email,
            hashed_password=hashed_password,
        )
        await self.repo.session.commit()
        return user

    async def get_users(self) -> list[User]:
        return await self.repo.get_users()

    async def get_user(self, user_id: int) -> User | None:
        if not isinstance(user_id, int):
            raise TypeError("user_id is int")

        return await self.repo.get_user_by_id(id=user_id)

    async def update_email(self, user_id: int, new_email: str) -> User | None:
        if not isinstance(user_id, int):
            raise TypeError("user_id is int")
        if not isinstance(new_email, str) or not new_email.strip():
            raise ValueError("new_email is empty")

        user = await self.repo.update_email(id=user_id, new_email=new_email)
        if user is None:
            return None

        await self.repo.session.commit()
        return user

    async def update_name(self, user_id: int, new_name: str) -> User | None:
        if not isinstance(user_id, int):
            raise TypeError("user_id is int")
        if not isinstance(new_name, str) or not new_name.strip():
            raise ValueError("new_name is empty")

        user = await self.repo.update_name(id=user_id, new_name=new_name)
        if user is None:
            return None

        await self.repo.session.commit()
        return user

    async def update_password(self, user_id: int, new_password: str) -> User | None:
        if not isinstance(user_id, int):
            raise TypeError("user_id is int")
        if not isinstance(new_password, str) or not new_password.strip():
            raise ValueError("new_password is empty")

        user = await self.repo.update_password(id=user_id, new_password=new_password)
        if user is None:
            return None

        await self.repo.session.commit()
        return user

    async def user_delete(self, user_id: int) -> bool:
        if not isinstance(user_id, int):
            raise TypeError("user_id is int")

        deleted = await self.repo.user_delete(id=user_id)
        if not deleted:
            return False

        await self.repo.session.commit()
        return True

