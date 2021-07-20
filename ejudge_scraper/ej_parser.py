from typing import List
from bs4 import BeautifulSoup
import requests
from utils import build_newjudge_url, build_column_field_mapping
import config


class ContestParser:
    def __init__(self, contest_id: int, last_rid: int = -1):
        self.contest_id = contest_id
        self.last_rid = last_rid
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": config.PROXY_AUTH_TOKEN
        })

    def parse_table(self, content: bytes):
        parser = BeautifulSoup(content, 'lxml')
        submissions_table = parser.find('table', attrs={
            'class': 'b1',
        })
        table_headers, *table_rows = submissions_table.find_all('tr')
        column_field_mapping = build_column_field_mapping(table_headers)

        all_pr_submissions = []
        for row in table_rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]

            cur_submission = dict()
            # skip last char because ejudge adds hashtag after the Run ID
            cur_submission['rid'] = int(cols[column_field_mapping['rid']][:-1])
            cur_submission['login'] = cols[column_field_mapping['login']]
            cur_submission['problem'] = cols[column_field_mapping['problem']]
            cur_submission['cid'] = self.contest_id
            all_pr_submissions.append(cur_submission)
            self.last_rid = max(self.last_rid, cur_submission['rid'])
        return all_pr_submissions

    def parse_all_new_pr(self):
        all_pr_submissions_url = build_newjudge_url(self.contest_id,
                                                    config.EJUDGE_PR_FILTER, self.last_rid + 1)
        ej_response = self._session.get(all_pr_submissions_url)
        if ej_response.status_code != 200:
            return []
        return self.parse_table(ej_response.content)

    def track_submission_verdict_modification(self, rid: List[int]):
        pass
