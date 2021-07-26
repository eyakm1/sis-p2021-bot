import os

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
API_URL = os.getenv('API_BASE', '')
POLL_INTERVAL_SECONDS = float(os.getenv('BOT_POLL_INTERVAL_SECONDS', '1'))
LOG_FILE_UPDATE_INTERVAL_HOURS = 1
LOGS_BACKUP_FILE_COUNT = 24 * 7
CERT_FILE_PATH = os.getenv("BOT_CERT_FILE_PATH", "")
CERT_KEY_FILE_PATH = os.getenv("BOT_CERT_KEY_FILE_PATH", "")
CERT = (CERT_FILE_PATH, CERT_KEY_FILE_PATH)
HEARTBEAT_INTERVAL_SECONDS = 3 * POLL_INTERVAL_SECONDS
