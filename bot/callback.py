from typing import Optional

from telebot.types import Message

from bot.bot_class import bot_instance
from bot.messaging import delete_message


def process_callback(call_data: str, message: Message, assignee: Optional[int] = None):
    status, submission_id = call_data.split()
    if delete_message(bot_instance, message.chat.id, message.id):
        bot_instance.change_status(int(submission_id), status, assignee)
        bot_instance.confirm_delete(int(submission_id))


@bot_instance.callback_query_handler(func=lambda call: True)
def button_callback(call):
    if call.data.startswith("assigned"):
        assignee = call.from_user.id
        process_callback(call.data, call.message, assignee)
    else:
        process_callback(call.data, call.message)
