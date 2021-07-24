from common.models.models import Contest
from bot.bot_class import bot_instance
from bot.messaging import send


@bot_instance.message_handler(commands=["subscribe"])
def subscribe(message):
    try:
        cid = str(int(message.text.split()[1]))
    except (ValueError, IndexError):
        send(bot_instance, message.chat.id,
             "Неверный формат команды!\nВведите: /subscribe <contest_id>")
        return
    chat_id = message.chat.id
    contest = Contest.objects.filter(cid=cid).first()
    if contest:
        contest_chat = contest.chat_id
        send(bot_instance, message.chat.id,
             f"Этот контест уже был "
             f"привязан к {'этому' if contest_chat == message.chat.id else 'другому'} чату")
        return
    Contest.objects.create(cid=cid, chat_id=chat_id)
    send(bot_instance, message.chat.id, "Контест успешно добавлен!")
