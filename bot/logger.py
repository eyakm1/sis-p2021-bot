import logging
import os
import telebot
from config import LOG_FILE_UPDATE_INTERVAL_HOURS, LOGS_BACKUP_FILE_COUNT

os.makedirs("logs", exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    return personalize_logger(logger, name)


def personalize_logger(logger: logging.Logger, name: str) -> logging.Logger:
    os.makedirs(f"logs/{name}", exist_ok=True)
    logger.setLevel(logging.DEBUG)
    logger_file_handler = logging.handlers.TimedRotatingFileHandler(
        f"logs/{name}/{name}.log",
        encoding="utf-8", when="h", interval=LOG_FILE_UPDATE_INTERVAL_HOURS,
        backupCount=LOGS_BACKUP_FILE_COUNT)
    logging_formatter = logging.Formatter("%(levelname)s %(asctime)s - %(message)s")
    logger_file_handler.setFormatter(logging_formatter)
    logger.addHandler(logger_file_handler)
    return logger


telebot_logger = telebot.logger
telebot_logger = personalize_logger(telebot_logger, "telebot")
