# pylint: disable=E0401,C0411
# this import should be first
import orm_setup as _

from common_models.models import Contest
from ej_parser import ContestParser
import json
import requests
import config
import time

if __name__ == '__main__':
    while True:
        try:
            for contest in Contest.objects.all():
                parser = ContestParser(contest.cid, contest.last_run_id)
                new_pr_submissions = parser.parse_all_new_pr()
                if len(new_pr_submissions) == 0:
                    continue
                json_submissions = json.dumps(new_pr_submissions)
                response = requests.post(config.API_SUBMISSIONS_POST_URL, data=json_submissions)
                if response.status_code != 200:
                    continue
                contest.last_run_id = parser.last_rid
                contest.save()
        # pylint: disable=W0703
        # here we should ignore any exception
        except Exception:
            print('Dead')
        time.sleep(config.SCRAPE_INTERVAL_SECONDS)
