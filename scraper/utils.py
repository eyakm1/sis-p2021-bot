import pathlib
import urllib.parse
from typing import Collection, Any, Generator

from scraper import config


def build_newjudge_url(contest_id: int, query_filter: str, first_rid: int = 0) -> str:
    """
    Build ejudge query URL which will be parsed
    :param contest_id: id of scraping contest
    :param query_filter: submissions filter in ejudge internal format
    :param first_rid: first run id which will be returned by ejudge
    :return: ejudge query URL
    """
    parse_url = urllib.parse.urlparse(config.EJUDGE_PROXY_BASE_URL)
    query_params = urllib.parse.urlencode(
        {
            'contest_id': contest_id,
            'filter_expr': query_filter,
            # ejudge is dumb
            'filter_last_run': first_rid,
        }
    )
    parse_url = parse_url._replace(query=query_params)
    new_path = str(pathlib.PurePosixPath(parse_url.path, 'new-judge'))
    parse_url = parse_url._replace(path=new_path)
    return parse_url.geturl()


def build_view_run_url(contest_id: int, run_id: int) -> str:
    """
    Build ejudge URL to judge submission
    :param contest_id: contest id of submission
    :param run_id: Contest run id of submission
    :return: ejudge URL
    """
    parse_url = urllib.parse.urlparse(config.EJUDGE_PROXY_BASE_URL)
    new_path = str(pathlib.PurePosixPath(parse_url.path, f'c{contest_id}', f'r{run_id}'))
    parse_url = parse_url._replace(path=new_path)
    return parse_url.geturl()


def build_api_url(*path: str) -> str:
    api_submissions_url_parse = urllib.parse.urlparse(config.API_BASE_URL)
    api_submissions_path = str(pathlib.PurePosixPath(api_submissions_url_parse.path, *path))
    api_submissions_url_parse = api_submissions_url_parse._replace(path=api_submissions_path)
    return api_submissions_url_parse.geturl()


def batcher(seq: Collection[Any], batch_size: int) -> Generator[Collection[Any], None, None]:
    """
    Simple sequence batcher
    :param seq: Sequence
    :param batch_size: Batch size
    :return: Generator of batches
    """
    for pos in range(0, len(seq), batch_size):
        yield seq[pos:pos + batch_size]
