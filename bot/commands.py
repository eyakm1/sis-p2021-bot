from typing import Optional
from aiogram.types import Message
from bot.bot_class import bot_instance, dp
from bot.messaging import send, delete_message, generate_service_message


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
@dp.channel_post_handler(regexp="/subscribe")
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
    text = generate_service_message(message, "subscribe", cid)
    await delete_message(bot_instance, message.chat.id, message.message_id)
    await send_feedback(success, error_message, text, chat_id)


@dp.message_handler(commands=["unsubscribe_all"])
@dp.channel_post_handler(regexp="/unsubscribe_all")
async def unsubscribe_all_command(message: Message) -> None:
    chat_id = message.chat.id
    success, error_message = await bot_instance.unsubscribe_all(chat_id)
    text = generate_service_message(message, "unsubscribe_all")
    await delete_message(bot_instance, message.chat.id, message.message_id)
    await send_feedback(success, error_message, text, chat_id)


@dp.message_handler(commands=["unsubscribe"])
@dp.channel_post_handler(regexp="/unsubscribe")
async def unsubscribe_command(message: Message) -> None:
    cid = get_cid_from_argument(message)
    if not cid:
        await send(bot_instance, message.chat.id,
                   "Неверный формат команды!\nВведите: /unsubscribe <contest_id>")
        return

    chat_id = message.chat.id
    success, error_message = await bot_instance.unsubscribe(cid, chat_id)
    text = generate_service_message(message, "unsubscribe", cid)
    await delete_message(bot_instance, message.chat.id, message.message_id)
    await send_feedback(success, error_message, text, chat_id)
