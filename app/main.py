import asyncio

from core.db import AsyncSessionLocal

from crud import post
from crud import user_profile
from crud import user
from crud import tst
from crud import tst_data
 

import models  # Важно: импортируем модели, чтобы metadata их увидела


async def main() -> None:
    async with AsyncSessionLocal() as session:
        print('-' * 100)
        # user_new = await user.create_user(session, 'ibra', "ibras@", 'ibragim', 21)
        # print(user_new)
        # profile = await user_profile.create_profile(session, 1, "Что то обомне ", "https://crm.py-it.ru")
        # print(profile)
        from pprint import pprint as p
        r1 = await tst_data.seed_test_data(session=session)
        r2 = await tst.get_users_profiles_posts(session=session)
        p(r2)
        # print(r2)
        print('-' * 100)

    # user_1 = await user.get_user_by_id(session, 1)
    # print('_' * 100)
    #
    # print(f"ID: {user_1.id}"
    #       f"\nUsername: {user_1.username}"
    #       f"\nEmail: {user_1.email}"
    #       f"\nFull Name: {user_1.full_name}"
    #       f"\nAge: {user_1.age}"
    #       f"\nIs Active: {user_1.is_active}"
    #       f"\nCreated At: {user_1.created_at}")
    #
    # print('_' * 100)

    print("Таблицы созданы.")


if __name__ == "__main__":
    asyncio.run(main())
