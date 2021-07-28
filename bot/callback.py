from aiogram.types import CallbackQuery

from bot.bot_class import dp
from bot.bot_class import bot_instance


async def assigned_callback(submission_id: int, assignee: int) -> bool:
    return await bot_instance.change_assignee(submission_id, assignee) and \
           await bot_instance.change_status(submission_id, "assigned")


async def snoozed_callback(submission_id: int) -> bool:
    return await bot_instance.snooze(submission_id)


async def closed_callback(submission_id: int) -> bool:
    return await bot_instance.change_status(submission_id, "closed")


async def unassigned_callback(submission_id: int) -> bool:
    return await bot_instance.change_status(submission_id, "unassigned")


@dp.callback_query_handler()
async def button_callback(call: CallbackQuery):
    if len(call.data.split()) != 2:
        raise ValueError(f"Invalid callback data sent: {call.data}")
    verb, subject = call.data.split()
    if verb == "assigned":
        await assigned_callback(int(subject), call.from_user.id)
    elif verb == "closed":
        await closed_callback(int(subject))
    elif verb == "snoozed":
        await snoozed_callback(int(subject))
    elif verb == "unassigned":
        await unassigned_callback(int(subject))
    else:
        raise ValueError(f"Unknown callback verb: {verb}")
