from aiogram.types import CallbackQuery
from bot.messaging import generate_markup, edit
from bot.bot_class import dp
from bot.bot_class import bot_instance


@dp.callback_query_handler()
async def button_callback(call: CallbackQuery):
    submission_id = int(call.data)
    assigned_text = f"\n\nПроверяет @"
    assigned_by_me_text = assigned_text + call.from_user.username
    if assigned_by_me_text in call.message.text:
        text = call.message.text.replace(assigned_by_me_text, "")
    elif assigned_text in call.message.text:
        data = call.message.text.split("\n")
        data[-1] = assigned_by_me_text
        text = "\n".join(data)
    else:
        text = call.message.text + assigned_by_me_text
    markup = generate_markup(submission_id)
    await edit(bot_instance, call.message.chat.id,
               call.message.message_id, text,
               markup=markup)
