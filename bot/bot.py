import threading
from time import sleep
import orm_setup as _
from bot_class import bot
# pylint: disable=unused-import
import callback
# pylint: disable=unused-import
import commands
import config


def bot_polling():
    bot.infinity_polling()


def process_updates():
    while True:
        bot.process_waiting()
        bot.delete_messages()
        sleep(config.POLL_INTERVAL_SECONDS)


t1 = threading.Thread(target=bot_polling)
t2 = threading.Thread(target=process_updates)
t1.start()
t2.start()
t1.join()
t2.join()
