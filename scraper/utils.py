import urllib.parse
from typing import List, Dict

from bs4 import Tag

from scraper.config import (
    EJUDGE_NEW_JUDGE_URL,
    SUBMISSION_FIELDS_EJUDGE_NAMES,
)


def build_newjudge_url(contest_id: int, query_filter: str, first_rid: int = 0) -> str:
    """
    Build ejudge query URL which will be parsed
    :param contest_id: id of scraping contest
    :param query_filter: submissions filter in ejudge internal format
    :param first_rid: first run id which will be returned by ejudge
    :return: ejudge query URL
    """
    parse_url = urllib.parse.urlparse(EJUDGE_NEW_JUDGE_URL)
    query_params = urllib.parse.urlencode(
        {
            'contest_id': contest_id,
            'filter_expr': query_filter,
            # ejudge is dumb
            'filter_last_run': first_rid,
        }
    )
    parse_url = parse_url._replace(query=query_params)
    url = urllib.parse.urlunparse(parse_url)
    return url


def build_column_field_mapping(header_col: List[Tag]) -> Dict[str, int]:
    header_col = [ele.text.strip() for ele in header_col]
    column_field_mapping = dict()
    for column, column_header in enumerate(header_col):
        submission_field = SUBMISSION_FIELDS_EJUDGE_NAMES.get(column_header, None)
        if submission_field:
            column_field_mapping[submission_field] = column
    return column_field_mapping
