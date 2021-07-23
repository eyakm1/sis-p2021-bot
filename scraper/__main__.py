# pylint: disable=E0401,C0411
# this import should be first
import orm_setup as _

import logging
import time

import requests

from common.models.models import Contest
from scraper.config import (
    API_SUBMISSIONS_POST_URL,
    CERTIFICATE_KEY_PATH,
    CERTIFICATE_PATH,
    SCRAPE_INTERVAL_SECONDS,
)
from scraper.ej_parser import ContestParser


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
