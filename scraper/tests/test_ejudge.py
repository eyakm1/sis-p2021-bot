from unittest.mock import Mock, patch

import requests

import scraper
from scraper import ej_parser, utils


def test_non_200_ejudge_status_code():
    with patch.object(requests.Session, 'get', return_value=Mock(content='', status_code=500)):
        parser = ej_parser.ContestParser(contest_id=1)
        pr_submissions = parser.parse_all_new_pr()
        assert pr_submissions == []


def test_many_users_with_symbols_after_run_id():
    mock_cfg = Mock(EJUDGE_PROXY_BASE_URL='example.com')
    with patch.object(scraper, 'config', mock_cfg), \
            patch.object(ej_parser, 'config', mock_cfg), \
            patch.object(utils, 'config', mock_cfg), \
            open('scraper/tests/ej_table_many_pr_with_symbols_after_run_id.html', 'rb') \
                    as table_html, \
            patch.object(requests.Session, 'get', return_value=Mock(content=table_html.read(),
                                                                    status_code=200)):
        parser = ej_parser.ContestParser(contest_id=1)
        pr_submissions = parser.parse_all_new_pr()
        assert pr_submissions == [
            {'login': 'abishev', 'problem': 'B', 'rid': 5,
             'cid': 1, 'verdict': 'Pending review', 'link': 'example.com/c1/r5'},
            {'login': 'abishev', 'problem': 'A', 'rid': 4,
             'cid': 1, 'verdict': 'Pending review', 'link': 'example.com/c1/r4'},
            {'login': 'ejudge', 'problem': 'B', 'rid': 3,
             'cid': 1, 'verdict': 'Pending review', 'link': 'example.com/c1/r3'},
            {'login': 'ejudge', 'problem': 'A', 'rid': 1,
             'cid': 1, 'verdict': 'Pending review', 'link': 'example.com/c1/r1'},
            {'login': 'ejudge', 'problem': 'A', 'rid': 0,
             'cid': 1, 'verdict': 'Pending review', 'link': 'example.com/c1/r0'}
        ]
        assert parser.last_rid == 5


def test_change_status():
    with open('scraper/tests/ej_table_ok_symbols_after_run_id.html', 'rb') \
            as table_html, \
            patch.object(requests.Session, 'get', return_value=Mock(content=table_html.read(),
                                                                    status_code=200)):
        parser = ej_parser.ContestParser(contest_id=1)
        changed_verdict_submissions = \
            parser.track_submissions_verdict_modification([5, 4, 3, 2, 1, 0])
        assert changed_verdict_submissions == [5, 4, 3, 0]


def test_no_submissions():
    with open('scraper/tests/ej_table_many_pr_with_symbols_after_run_id.html', 'rb') \
            as table_html, patch.object(requests.Session, 'get',
                                        return_value=Mock(content=table_html.read(),
                                                          status_code=200)):
        parser = ej_parser.ContestParser(contest_id=1, last_rid=5)
        pr_submissions = parser.parse_all_new_pr()
        assert pr_submissions == []
        assert parser.last_rid == 5


def test_batcher():
    arr = [1, 2, 3, 4, 5]
    arr_batched = list(utils.batcher(arr, 2))
    assert arr_batched == [[1, 2], [3, 4], [5]]

    arr_batched = list(utils.batcher(arr, 3))
    assert arr_batched == [[1, 2, 3], [4, 5]]

    arr_batched = list(utils.batcher(arr, 5))
    assert arr_batched == [[1, 2, 3, 4, 5]]

    arr_batched = list(utils.batcher(arr, 10))
    assert arr_batched == [[1, 2, 3, 4, 5]]
