from aiogram.types import CallbackQuery

from bot.bot_class import dp
from bot.bot_class import bot_instance


@dp.callback_query_handler()
async def button_callback(call: CallbackQuery):
    if len(call.data.split()) != 2:
        raise ValueError(f"Invalid callback data sent: {call.data}")
    verb, subject = call.data.split()
    if verb != "assigned":
        raise ValueError(f"Invalid callback data sent: {call.data}")
    else:
        pass
