# pylint: disable=E0401,C0411
# this import should be first
import orm_setup as _

import logging
import time
import os

import requests
import pathlib

from common.models.models import Contest
from scraper import config
from scraper.ej_parser import ContestParser

API_SUBMISSIONS_POST_URL = str(pathlib.PurePosixPath(config.API_BASE_URL, 'submissions'))

# Logging setup

os.makedirs(config.LOGS_DIR, exist_ok=True)

logging.basicConfig(format=config.LOGS_FORMAT, level=logging.INFO)
logger_file_handler = logging.handlers.TimedRotatingFileHandler(
    os.path.join(config.LOGS_DIR, 'scraper.log'),
    encoding="utf-8", when="h", interval=config.LOG_FILE_UPDATE_INTERVAL_HOURS,
    backupCount=config.LOGS_BACKUP_FILE_COUNT)
logger_file_handler.setFormatter(logging.Formatter(config.LOGS_FORMAT))
logging.getLogger().addHandler(logger_file_handler)


def main():
    session = requests.Session()
    if config.CERTIFICATE_PATH and config.CERTIFICATE_KEY_PATH:
        logging.info('Using certificate')
        logging.info('Cert path: %s', config.CERTIFICATE_PATH)
        logging.info('Key path: %s', config.CERTIFICATE_KEY_PATH)
        session.cert = (config.CERTIFICATE_PATH, config.CERTIFICATE_KEY_PATH)
    while True:
        try:
            for contest in Contest.objects.all():
                logging.info("Scraping contest %d", contest.cid)
                parser = ContestParser(contest.cid, contest.last_run_id)
                new_pr_submissions = parser.parse_all_new_pr()
                if len(new_pr_submissions) == 0:
                    continue
                response = session.post(API_SUBMISSIONS_POST_URL, json=new_pr_submissions)
                if response.status_code != 200:
                    logging.warning("Send new PR submissions to TLM failed for contest %d",
                                    contest.cid)
                    continue
                contest.last_run_id = parser.last_rid
                contest.save()
        # pylint: disable=W0703
        # here we should ignore any exception
        except Exception as err:
            logging.exception(err)
        time.sleep(config.SCRAPE_INTERVAL_SECONDS)


if __name__ == '__main__':
    main()
