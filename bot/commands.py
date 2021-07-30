from typing import Optional
from aiogram.types import Message
from bot.bot_class import bot_instance, dp
from bot.messaging import send


def get_cid_from_argument(message: Message) -> Optional[int]:
    try:
        return int(message.text.split()[1])
    except (ValueError, IndexError):
        return None


@dp.message_handler(commands=["subscribe"])
async def subscribe_command(message: Message) -> None:
    cid = get_cid_from_argument(message)
    if not cid:
        await send(bot_instance, message.chat.id,
                   "Неверный формат команды!\nВведите: /subscribe <contest_id>")
        return

    chat_id = message.chat.id
    if message.chat.type == "private":
        await send(bot_instance, chat_id, "Нельзя подписывать личный чат на контест")
        return

    result_code = await bot_instance.subscribe(cid, chat_id)
    response_dict = {200: "Контест успешно добавлен!",
                     403: "Другой чат подписан на этот контест",
                     409: "Этот чат уже подписан на данный контест"}
    response_text = response_dict.get(result_code, "Ошибка")
    await send(bot_instance, chat_id, response_text)


@dp.message_handler(commands=["unsubscribe"])
async def unsubscribe_command(message: Message) -> None:
    cid = get_cid_from_argument(message)
    if not cid:
        await send(bot_instance, message.chat.id,
                   "Неверный формат команды!\nВведите: /unsubscribe <contest_id>")
        return

    chat_id = message.chat.id
    result_code = await bot_instance.unsubscribe(cid, chat_id)
    response_dict = {200: "Вы успешно отписались от контеста!",
                     404: "Вы не подписаны на данный контест"}
    response_text = response_dict.get(result_code, "Ошибка")
    await send(bot_instance, chat_id, response_text)


@dp.message_handler(commands=["unsubscribe_all"])
async def unsubscribe_all_command(message: Message) -> None:
    chat_id = message.chat.id
    result_code = await bot_instance.unsubscribe_all(chat_id)
    if result_code == 200:
        await send(bot_instance, chat_id, "Вы успешно отписались от всех контестов")
    else:
        await send(bot_instance, chat_id, "Ошибка")
