from typing import Optional
from aiogram.types import Message
from bot.bot_class import bot_instance, dp
from bot.messaging import send


def get_cid_from_argument(message: Message) -> Optional[int]:
    try:
        return int(message.text.split()[1])
    except (ValueError, IndexError):
        return None


async def send_feedback(success: bool, error_message: str, ok_message: str, chat_id: int) -> None:
    if success:
        await send(bot_instance, chat_id, ok_message)
    elif error_message:
        await send(bot_instance, chat_id, error_message)
    else:
        await send(bot_instance, chat_id, "Произошла неизвестная ошибка. "
                                          "Попробуйте ещё раз")


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

    success, error_message = await bot_instance.subscribe(cid, chat_id)
    await send_feedback(success, error_message, "Контест успешно добавлен!", chat_id)


@dp.message_handler(commands=["unsubscribe"])
async def unsubscribe_command(message: Message) -> None:
    cid = get_cid_from_argument(message)
    if not cid:
        await send(bot_instance, message.chat.id,
                   "Неверный формат команды!\nВведите: /unsubscribe <contest_id>")
        return

    chat_id = message.chat.id
    success, error_message = await bot_instance.unsubscribe(cid, chat_id)
    await send_feedback(success, error_message, "Вы успешно отписались от контеста!", chat_id)


@dp.message_handler(commands=["unsubscribe_all"])
async def unsubscribe_all_command(message: Message) -> None:
    chat_id = message.chat.id
    success, error_message = await bot_instance.unsubscribe_all(chat_id)
    await send_feedback(success, error_message, "Вы успешно отписались от всех контестов!", chat_id)
