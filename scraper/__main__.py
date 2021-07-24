# pylint: disable=E0401,C0411
# this import should be first
import orm_setup as _

import logging
import time
import os

import requests

from common.models.models import Contest
from scraper.config import (
    API_SUBMISSIONS_POST_URL,
    CERTIFICATE_KEY_PATH,
    CERTIFICATE_PATH,
    SCRAPE_INTERVAL_SECONDS,
    LOG_FILE_UPDATE_INTERVAL_HOURS,
    LOGS_BACKUP_FILE_COUNT, LOGS_DIR, LOGS_FORMAT,
)
from scraper.ej_parser import ContestParser

os.makedirs(LOGS_DIR, exist_ok=True)

logging.basicConfig(format=LOGS_FORMAT, level=logging.INFO)
logger_file_handler = logging.handlers.TimedRotatingFileHandler(
    os.path.join(LOGS_DIR, 'scraper.log'),
    encoding="utf-8", when="h", interval=LOG_FILE_UPDATE_INTERVAL_HOURS,
    backupCount=LOGS_BACKUP_FILE_COUNT)
logger_file_handler.setFormatter(logging.Formatter(LOGS_FORMAT))
logging.getLogger().addHandler(logger_file_handler)


def main():
    session = requests.Session()
    if CERTIFICATE_PATH and CERTIFICATE_KEY_PATH:
        logging.info('Using certificate')
        logging.info('Cert path: %s', CERTIFICATE_PATH)
        logging.info('Key path: %s', CERTIFICATE_KEY_PATH)
        session.cert = (CERTIFICATE_PATH, CERTIFICATE_KEY_PATH)
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
                    continue
                contest.last_run_id = parser.last_rid
                contest.save()
        # pylint: disable=W0703
        # here we should ignore any exception
        except Exception as err:
            logging.exception(err)
        time.sleep(SCRAPE_INTERVAL_SECONDS)


if __name__ == '__main__':
    main()
