import asyncio
import logging

from aiogram import Dispatcher, Bot
from config import BOT_TOKEN
from handlers import router

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Выход')
