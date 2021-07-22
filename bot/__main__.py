import threading
from time import sleep

import orm_setup as _
# pylint: disable=unused-import
import bot.callback
# pylint: disable=unused-import
import bot.commands
import bot.config as config
from bot.bot_class import bot_instance


def bot_polling():
    bot_instance.infinity_polling()


def process_updates():
    while True:
        bot_instance.process_waiting()
        bot_instance.delete_messages()
        sleep(config.POLL_INTERVAL_SECONDS)


t1 = threading.Thread(target=bot_polling)
t2 = threading.Thread(target=process_updates)
t1.start()
t2.start()
t1.join()
t2.join()
