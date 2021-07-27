import re
from typing import Optional

from telebot import apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.logger import get_logger
from bot.submission import Submission

notification_logger = get_logger("notifications")


def prepare_for_hashtag(s: str, prefix: str = '') -> str:
    if s.isdigit() or s == '':
        return prefix + s
    replaced = re.sub(r'\W', '_', s)  # replace non-alphanumeric symbols with _
    return re.sub(r'_+', '_', replaced)  # merge consequent underscores


def generate_group_markup(callback_data: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("\U00002705 Взять", callback_data=f"assigned {callback_data}"))
    return markup


def generate_individual_markup(callback_data: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(InlineKeyboardButton("\U000021A9 Вернуть",
                                    callback_data=f"unassigned {callback_data}"))
    markup.add(InlineKeyboardButton("\U000023F0 Отложить",
                                    callback_data=f"snoozed {callback_data}"))
    markup.add(InlineKeyboardButton("\U0000274C Закрыть", callback_data=f"closed {callback_data}"))
    return markup


def generate_message(submission: Submission) -> str:
    return f"#{prepare_for_hashtag(str(submission.cid), 'c')}, " \
           f"#{prepare_for_hashtag(submission.problem, 'p')}, " \
           f"#{prepare_for_hashtag(submission.login, 'u')}, " \
           f"{submission.link}"


def send(bot, chat_id: int, message: str, markup: InlineKeyboardMarkup = None) -> Optional[int]:
    try:
        notification_logger.debug("Sending message: %d to group", chat_id)
        result = bot.send_message(chat_id, message, reply_markup=markup, parse_mode="html")
        return result.message_id
    except apihelper.ApiException as err:
        notification_logger.error("Message not sent: %s", str(err))
        return None


def send_to_group(bot, submission: Submission, chat_id: int) -> Optional[int]:
    markup = generate_group_markup(submission.id)
    message = generate_message(submission)
    return send(bot, chat_id, message, markup)


def send_assigned(bot, submission: Submission, chat_id: int) -> Optional[int]:
    markup = generate_individual_markup(submission.id)
    message = generate_message(submission)
    return send(bot, chat_id, message, markup)


def send_assigned_by_submission_id(bot, message: str, chat_id: int, submission_id: int) \
        -> Optional[int]:
    markup = generate_individual_markup(submission_id)
    return send(bot, chat_id, message, markup)


def delete_message(bot, chat_id: int, message_id: int) -> bool:
    try:
        notification_logger.debug("Deleting message with id %d from chat %d",
                                  message_id, chat_id)
        bot.delete_message(chat_id, message_id)
    except apihelper.ApiException as err:
        notification_logger.error("Message not deleted: %s", str(err))
        return False
    return True
