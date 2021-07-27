from bot.bot_class import bot_instance

def assigned_callback(submission_id: int, assignee: int) -> bool:
    return bot_instance.change_assignee(submission_id, assignee) and \
           bot_instance.change_status(submission_id, "assigned")

def snoozed_callback(submission_id: int) -> bool:
    return bot_instance.snooze(submission_id)

def closed_callback(submission_id: int) -> bool:
    return bot_instance.change_status(submission_id, "closed")

def unassigned_callback(submission_id: int) -> bool:
    return bot_instance.change_status(submission_id, "unassigned")

@bot_instance.callback_query_handler(func=lambda call: True)
def button_callback(call):
    if len(call.data.split()) != 2:
        raise ValueError(f"Invalid callback data sent: {call.data}")
    verb, subject = call.data.split()
    if verb == "assigned":
        assigned_callback(int(subject), call.from_user.id)
    elif verb == "closed":
        closed_callback(int(subject))
    elif verb == "snoozed":
        snoozed_callback(int(subject))
    elif verb == "unassigned":
        unassigned_callback(int(subject))
    else:
        raise ValueError(f"Unknown callback verb: {verb}")
