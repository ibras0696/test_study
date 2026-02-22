from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command('help'))
async def help_command(message: Message):
    await message.answer('Я тебе помогаю, скажи спасибо')
