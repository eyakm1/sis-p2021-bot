from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from bot.messaging import generate_markup, edit
from bot.bot_class import dp
from bot.bot_class import bot_instance


@dp.callback_query_handler()
async def button_callback(call: CallbackQuery):
    assigned_text = "\n\nПроверяет @"
    assigned_by_me_text = assigned_text + call.from_user.username
    if assigned_by_me_text in call.message.text:
        # unassign
        text = call.message.text.replace(assigned_by_me_text, "")
        button_text = "\U00002705 Сейчас проверю"
    elif assigned_text in call.message.text:
        # unassign forbidden
        await call.answer("Вы не можете отменить статус "
                          "проверки этим человеком", show_alert=True)
        return
    else:
        # assign
        text = call.message.text + assigned_by_me_text
        button_text = "\U0000274C Больше не проверяю"
    markup = generate_markup(button_text)
    await edit(bot_instance, call.message.chat.id,
               call.message.message_id, text, markup=markup)
