from unittest.mock import Mock, patch
import requests
from scraper import ej_parser


def test_non_200_ejudge_status_code():
    with patch.object(requests.Session, 'get', return_value=Mock(content='', status_code=500)):
        parser = ej_parser.ContestParser(contest_id=1)
        pr_submissions = parser.parse_all_new_pr()
        assert pr_submissions == []


def test_many_users_with_symbols_after_run_id():
    with open('scraper/tests/ej_table_many_pr_with_symbols_after_run_id.html', 'rb') \
            as table_html, patch.object(requests.Session, 'get',
                                        return_value=Mock(content=table_html.read(),
                                                          status_code=200)):
        parser = ej_parser.ContestParser(contest_id=1)
        pr_submissions = parser.parse_all_new_pr()
        assert pr_submissions == [{'login': 'abishev', 'problem': 'B', 'rid': 5, 'cid': 1},
                                  {'login': 'abishev', 'problem': 'A', 'rid': 4, 'cid': 1},
                                  {'login': 'ejudge', 'problem': 'B', 'rid': 3, 'cid': 1},
                                  {'login': 'ejudge', 'problem': 'A', 'rid': 1, 'cid': 1},
                                  {'login': 'ejudge', 'problem': 'A', 'rid': 0, 'cid': 1}]
        assert parser.last_rid == 5


def test_no_submissions():
    with open('scraper/tests/ej_table_many_pr_with_symbols_after_run_id.html', 'rb') \
            as table_html, patch.object(requests.Session, 'get',
                                        return_value=Mock(content=table_html.read(),
                                                          status_code=200)):
        parser = ej_parser.ContestParser(contest_id=1, last_rid=5)
        pr_submissions = parser.parse_all_new_pr()
        assert pr_submissions == []
        assert parser.last_rid == 5
