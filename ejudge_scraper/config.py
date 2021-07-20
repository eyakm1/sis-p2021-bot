import os

EJUDGE_NEW_JUDGE_URL = r"http://ejudge.lksh.ru/ej/new-judge"
EJUDGE_PR_FILTER = r"status==pr"
PROXY_AUTH_TOKEN = os.getenv('PROXY_AUTH_TOKEN', default='')
API_SUBMISSIONS_POST_URL = os.getenv('API_SUBMISSIONS_POST_URL', default='')
SCRAPE_INTERVAL_SECONDS = 5 * 60

SUBMISSION_FIELDS_EJUDGE_NAMES = {
    'Run ID': 'rid',
    'User name': 'login',
    'Problem': 'problem',
}
