import sys
import threading
from time import sleep

import orm_setup as _
# pylint: disable=unused-import
import bot.callback
# pylint: disable=unused-import
import bot.commands
from bot import config
from bot.bot_class import bot_instance
# heartbeat_counter is not a constant
# pylint: disable=invalid-name
heartbeat_counter = 0
mutex = threading.Lock()


def bot_polling():
    bot_instance.infinity_polling()


def process_updates():
    while True:
        bot_instance.process_waiting()
        bot_instance.delete_messages()

        with mutex:
            # heartbeat_counter is not a constant
            # pylint: disable=invalid-name
            # pylint: disable=global-statement
            global heartbeat_counter
            heartbeat_counter += 1

        sleep(config.POLL_INTERVAL_SECONDS)


def heartbeat_check():
    last_heartbeat = heartbeat_counter
    while True:
        sleep(config.HEARTBEAT_INTERVAL_SECONDS)

        with mutex:
            if heartbeat_counter == last_heartbeat:
                sys.exit(1)
            last_heartbeat = heartbeat_counter


t1 = threading.Thread(target=bot_polling)
t2 = threading.Thread(target=process_updates)
t3 = threading.Thread(target=heartbeat_check)
t1.start()
t2.start()
t3.start()
t1.join()
t2.join()
t3.join()
