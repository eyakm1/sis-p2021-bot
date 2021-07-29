import asyncio
import logging
import sys
from aiogram import executor, exceptions
# pylint: disable=unused-import
import bot.callback
# pylint: disable=unused-import
import bot.commands
from bot import config
from bot.bot_class import bot_instance, dp

# heartbeat_counter is not a constant
# pylint: disable=invalid-name
heartbeat_counter = 0

logging.basicConfig(level=logging.INFO)

FLOOD_LIMIT_TIMEOUT_SECONDS = 60


async def process_updates():
    while True:
        try:
            await bot_instance.process_waiting()
            await bot_instance.delete_messages()
        except exceptions.RetryAfter:
            logging.warning("We got throttled")
            # default flood timeout
            await asyncio.sleep(FLOOD_LIMIT_TIMEOUT_SECONDS)

        # heartbeat_counter is not a constant
        # pylint: disable=invalid-name
        # pylint: disable=global-statement
        global heartbeat_counter
        heartbeat_counter += 1

        await asyncio.sleep(config.POLL_INTERVAL_SECONDS)


async def heartbeat_check():
    last_heartbeat = heartbeat_counter
    while True:
        await asyncio.sleep(config.HEARTBEAT_INTERVAL_SECONDS)
        if heartbeat_counter == last_heartbeat:
            logging.error("Bot shows no signs of life")
            sys.exit(1)
        last_heartbeat = heartbeat_counter


if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(process_updates())
    event_loop.create_task(heartbeat_check())

    executor.start_polling(dp, loop=event_loop)
