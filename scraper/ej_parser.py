import re
from typing import List, Any, Dict, Callable

import attr
import requests
from bs4 import BeautifulSoup

from scraper import config, utils

EJUDGE_PR_FILTER = r'status==pr'
EJUDGE_SUBMISSION_ID_FILTER = r'id=={}'


@attr.s(auto_attribs=True)
class EjColumn:
    ej_name: str
    name: str
    xform: Callable[[str], Any] = attr.ib(default=lambda x: x)


COLUMNS = [
    # seems like ejudge can add some non-digit symbols at the end of run id
    EjColumn(ej_name='Run ID', name='rid', xform=lambda s: int(re.match(r'^\d+', s).group())),
    EjColumn(ej_name='User name', name='login'),
    EjColumn(ej_name='Problem', name='problem'),
    EjColumn(ej_name='Result', name='verdict'),
]

COLUMNS_EJ_NAME_MAPPING = {col.ej_name: col for col in COLUMNS}


class ContestParser:
    def __init__(self, contest_id: int, last_rid: int = -1):
        self.contest_id = contest_id
        self.last_rid = last_rid
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": config.PROXY_AUTH_TOKEN
        })

    def parse_submissions_table(self, content: bytes) -> List[Dict[str, Any]]:
        parser = BeautifulSoup(content, 'lxml')
        submissions_table = parser.find('table', attrs={
            'class': 'b1',
        })
        table_headers, *table_rows = submissions_table.find_all('tr')
        column_header = [header.text.strip() for header in table_headers]

        parsed_submissions = []
        for row in table_rows:
            cols = [column.text.strip() for column in row.find_all('td')]

            submission = dict()
            for col_ind, col_value in enumerate(cols):
                column = COLUMNS_EJ_NAME_MAPPING.get(column_header[col_ind], None)
                if column:
                    submission[column.name] = column.xform(col_value)
            submission['cid'] = self.contest_id
            parsed_submissions.append(submission)

        return parsed_submissions

    def parse_all_new_pr(self) -> List[Dict[str, Any]]:
        all_pr_submissions_url = utils.build_newjudge_url(self.contest_id,
                                                          EJUDGE_PR_FILTER,
                                                          self.last_rid + 1)
        ej_response = self._session.get(all_pr_submissions_url)
        if ej_response.status_code != 200:
            return []
        all_pr_submissions = self.parse_submissions_table(ej_response.content)
        all_pr_submissions = [sub for sub in all_pr_submissions if sub['rid'] > self.last_rid]
        if not all_pr_submissions:
            return []
        for submission in all_pr_submissions:
            submission['link'] = utils.build_view_run_url(submission['cid'], submission['rid'])
        self.last_rid = max((submission['rid'] for submission in all_pr_submissions))
        return all_pr_submissions

    def track_submissions_verdict_modification(self, rid_list: List[int]) -> List[int]:
        pass
