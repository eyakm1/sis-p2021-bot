import ssl
from bot import config


def get_ssl_context():
    ssl_context = ssl.create_default_context()
    if config.CERT_FILE_PATH and config.CERT_KEY_FILE_PATH:
        ssl_context.load_cert_chain(config.CERT_FILE_PATH, config.CERT_KEY_FILE_PATH)
    return ssl_context
