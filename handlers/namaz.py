from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from test_study.bd.time_namza import get_times
import logging

router = Router()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.message(Command('namaz'))
async def time_command(message: Message):

    logger.info(f"Пользователь {message.from_user.id} запросил время намаза")

    try:

        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

        prayer_times_text = get_times()
        prayer_times_dict = ""
        for prayer, time in prayer_times_text.items():
            prayer_times_dict += f"🕌 *{prayer}*: {time}\n"

        await message.answer(
            prayer_times_dict,
            parse_mode="Markdown"
        )

        logger.info("Сообщение отправлено успешно")

    except Exception as e:
        error_msg = f"Ошибка в боте: {str(e)}"
        logger.error(error_msg)
        await message.answer(error_msg)