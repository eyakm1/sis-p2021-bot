# pylint: disable=E0401,C0411
# this import should be first
import orm_setup as _

import logging
import time
import os

import requests
from common.models.models import Contest
from scraper import config, utils
from scraper.ej_parser import ContestParser

# Logging setup

os.makedirs(config.LOGS_DIR, exist_ok=True)

logging.basicConfig(format=config.LOGS_FORMAT, level=logging.INFO)
logger_file_handler = logging.handlers.TimedRotatingFileHandler(
    os.path.join(config.LOGS_DIR, 'scraper.log'),
    encoding="utf-8", when="h", interval=config.LOG_FILE_UPDATE_INTERVAL_HOURS,
    backupCount=config.LOGS_BACKUP_FILE_COUNT)
logger_file_handler.setFormatter(logging.Formatter(config.LOGS_FORMAT))
logging.getLogger().addHandler(logger_file_handler)


def get_new_pr(parser: ContestParser, session: requests.Session) -> None:
    logging.info("Scraping contest %d", parser.contest_id)
    new_pr_submissions = parser.parse_all_new_pr()
    if len(new_pr_submissions) == 0:
        return
    response = session.post(utils.build_api_url('submissions'),
                            json=new_pr_submissions)
    if response.status_code != 200:
        logging.warning("Send new PR submissions to TLM failed for contest %d",
                        parser.contest_id)


def track_contest_pr_submissions_verdict_change(parser: ContestParser, session: requests.Session) \
        -> None:
    # get all PR's of contest
    logging.info("Tracking PR submissions of contest %d", parser.contest_id)
    tracking_pr_submissions_url = utils.build_api_url('contests',
                                                      f'{parser.contest_id}',
                                                      'submissions')
    response = session.get(tracking_pr_submissions_url)
    if response.status_code != 200:
        logging.warning("Failed to get PR submissions for contest %d", parser.contest_id)
        return

    # parse them in Parser object
    tracking_pr_submissions = response.json()
    rid_internal_id_map = {run['rid']: run['submission_id'] for run in tracking_pr_submissions}
    all_tracking_rids = [run['rid'] for run in tracking_pr_submissions]
    changed_verdict_submissions = parser.track_submissions_verdict_modification(all_tracking_rids)

    # Send them to TLM
    for submission_rid in changed_verdict_submissions:
        response = session.put(utils.build_api_url('submissions',
                                                   f'{rid_internal_id_map[submission_rid]}',
                                                   'status'),
                               json='closed')
        if response.status_code != 200:
            logging.warning("Send change submission cid: %d rid: %d status failed",
                            parser.contest_id,
                            submission_rid)


def main():
    session = requests.Session()
    if config.CERTIFICATE_PATH and config.CERTIFICATE_KEY_PATH:
        logging.info('Using certificate')
        logging.info('Cert path: %s', config.CERTIFICATE_PATH)
        logging.info('Key path: %s', config.CERTIFICATE_KEY_PATH)
        session.cert = (config.CERTIFICATE_PATH, config.CERTIFICATE_KEY_PATH)
    while True:
        try:
            all_contest_resp = session.get(utils.build_api_url('contests'))
            all_contest_id = all_contest_resp.json()
            for contest_id in all_contest_id:
                contest, _ = Contest.objects.get_or_create(cid=contest_id)
                parser = ContestParser(contest.cid, contest.last_run_id)

                get_new_pr(parser, session)
                contest.last_run_id = parser.last_rid
                contest.save()

                track_contest_pr_submissions_verdict_change(parser, session)
        # pylint: disable=W0703
        # here we should ignore any exception
        except Exception as err:
            logging.exception(err)
        time.sleep(config.SCRAPE_INTERVAL_SECONDS)


if __name__ == '__main__':
    main()
