import asyncio
import re
from typing import Optional

import aiogram
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.logger import get_logger
from bot.submission import Submission

notification_logger = get_logger("notifications")


def prepare_for_hashtag(s: str, prefix: str = '') -> str:
    if s.isdigit() or s == '':
        return prefix + s
    replaced = re.sub(r'\W', '_', s)  # replace non-alphanumeric symbols with _
    return re.sub(r'_+', '_', replaced)  # merge consequent underscores


def generate_markup(button_text: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(button_text, callback_data="-"))
    return markup


def generate_message(submission: Submission) -> str:
    return f"#{prepare_for_hashtag(str(submission.cid), 'c')}, " \
           f"#{prepare_for_hashtag(submission.problem, 'p')}, " \
           f"#{prepare_for_hashtag(submission.login, 'u')}, " \
           f"{submission.link}"


async def send(bot: aiogram.Bot, chat_id: int, message: str, markup: InlineKeyboardMarkup = None) \
        -> Optional[int]:
    try:
        notification_logger.debug("Sending message: %d to group", chat_id)
        result = await bot.send_message(chat_id, message, reply_markup=markup)
        return result.message_id
    except aiogram.exceptions.TelegramAPIError as err:
        notification_logger.error("Message not sent: %s", str(err))
        return None
    except asyncio.TimeoutError:
        return None


async def edit(bot: aiogram.Bot, chat_id: int, message_id: int,
               text: str, markup: InlineKeyboardMarkup = None) \
        -> Optional[int]:
    try:
        notification_logger.debug("Editing message %d in chat %d", message_id, chat_id)
        result = await bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
        return result.message_id
    except aiogram.exceptions.TelegramAPIError as err:
        notification_logger.error("Message not edited: %s", str(err))
        return None
    except asyncio.TimeoutError:
        return None


async def send_to_channel(bot: aiogram.Bot, submission: Submission, chat_id: int) -> Optional[int]:
    markup = generate_markup("\U00002705 Сейчас проверю")
    message = generate_message(submission)
    return await send(bot, chat_id, message, markup)


async def delete_message(bot: aiogram.Bot, chat_id: int, message_id: int) -> bool:
    try:
        notification_logger.debug("Deleting message with id %d from chat %d",
                                  message_id, chat_id)
        await bot.delete_message(chat_id, message_id)
    except aiogram.exceptions.TelegramAPIError as err:
        notification_logger.error("Message not deleted: %s", str(err))
        return False
    except asyncio.TimeoutError:
        return False
    return True
