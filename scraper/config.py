import os

EJUDGE_NEW_JUDGE_URL = os.getenv('EJUDGE_NEW_JUDGE_URL', r"http://ejudge.lksh.ru/ej/new-judge")
EJUDGE_PR_FILTER = r"status==pr"
PROXY_AUTH_TOKEN = os.getenv('PROXY_AUTH_TOKEN', '')
API_SUBMISSIONS_POST_URL = os.getenv('API_BASE', '') + '/submissions'
SCRAPE_INTERVAL_SECONDS = float(os.getenv('SCRAPE_INTERVAL_SECONDS', '300'))
CERTIFICATE_PATH = os.getenv('SCRAPER_CERTIFICATE_PATH', '')
CERTIFICATE_KEY_PATH = os.getenv('SCRAPER_CERTIFICATE_KEY_PATH', '')

SUBMISSION_FIELDS_EJUDGE_NAMES = {
    'Run ID': 'rid',
    'User name': 'login',
    'Problem': 'problem',
}

LOG_FILE_UPDATE_INTERVAL_HOURS = 1
LOGS_BACKUP_FILE_COUNT = 24 * 7
LOGS_DIR = 'logs/scraper'
LOGS_FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
