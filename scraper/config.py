import os

# All urls are processed with pathlib so it doesn't matter whether they end with slash or not

EJUDGE_PROXY_BASE_URL = os.getenv('EJUDGE_PROXY_BASE_URL',
                                  default='https://ejudge.p.lksh.ru/ej/')
PROXY_AUTH_TOKEN = os.getenv('PROXY_AUTH_TOKEN', default='')
API_BASE_URL = os.getenv('API_BASE_URL', default='http://127.0.0.1:8000/')
CERTIFICATE_PATH = os.getenv('SCRAPER_CERTIFICATE_PATH', default='')
CERTIFICATE_KEY_PATH = os.getenv('SCRAPER_CERTIFICATE_KEY_PATH', default='')
SCRAPE_INTERVAL_SECONDS = float(os.getenv('SCRAPE_INTERVAL_SECONDS', '300'))

LOG_FILE_UPDATE_INTERVAL_HOURS = 1
LOGS_BACKUP_FILE_COUNT = 24 * 7
LOGS_DIR = 'logs/scraper'
LOGS_FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
