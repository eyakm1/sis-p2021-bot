from typing import Optional
from telebot.types import Message
from bot.bot_class import bot_instance
from bot.messaging import send


def get_cid_from_argument(message: Message) -> Optional[int]:
    try:
        return int(message.text.split()[1])
    except (ValueError, IndexError):
        return None


@bot_instance.message_handler(commands=["subscribe"])
def subscribe_command(message: Message) -> None:
    cid = get_cid_from_argument(message)
    if not cid:
        send(bot_instance, message.chat.id,
             "Неверный формат команды!\nВведите: /subscribe <contest_id>")
        return

    chat_id = message.chat.id
    if message.chat.type == "private":
        send(bot_instance, chat_id, "Нельзя подписывать личный чат на контест")
        return

    result_code, result_message = bot_instance.subscribe(cid, chat_id)
    if result_code == 200:
        send(bot_instance, chat_id, "Контест успешно добавлен!")
    elif result_code == 400:
        send(bot_instance, chat_id, result_message)
    else:
        send(bot_instance, chat_id, "Произошла неизвестная ошибка")


@bot_instance.message_handler(commands=["unsubscribe"])
def unsubscribe_command(message: Message) -> None:
    cid = get_cid_from_argument(message)
    if not cid:
        send(bot_instance, message.chat.id,
             "Неверный формат команды!\nВведите: /unsubscribe <contest_id>")
        return

    chat_id = message.chat.id
    result_code, result_message = bot_instance.unsubscribe(cid, chat_id)
    if result_code == 200:
        send(bot_instance, chat_id, "Вы успешно отписались от контеста!")
    elif result_code == 400:
        send(bot_instance, chat_id, result_message)
    else:
        send(bot_instance, chat_id, "Произошла неизвестная ошибка")


@bot_instance.message_handler(commands=["unsubscribe_all"])
def unsubscribe_all_command(message: Message) -> None:
    chat_id = message.chat.id
    result_code, result_message = bot_instance.unsubscribe_all(chat_id)
    if result_code == 200:
        send(bot_instance, chat_id, "Вы успешно отписались от всех контестов!")
    elif result_code == 400:
        send(bot_instance, chat_id, result_message)
    else:
        send(bot_instance, chat_id, "Произошла неизвестная ошибка")
