import os


def getenv_boolean(var_name, default_value=False):
    result = default_value
    env_value = os.getenv(var_name)
    if env_value is not None:
        result = env_value.upper() in ("TRUE", "1")
    return result


DEFAULT_PAGE_SIZE = 100
PAGE_SIZE_LIMIT = 300

# API_PREFIX = "/market"
API_PREFIX = "/xxx"

SECRET_KEY = os.getenvb(b"SECRET_KEY")
if not SECRET_KEY:
  SECRET_KEY = os.urandom(32)
#SECRET_KEY = os.urandom(32)

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8  # 60 minutes * 24 hours * 8 days = 8 days

SERVER_NAME = os.getenv("SERVER_NAME")
SERVER_HOST = os.getenv("SERVER_HOST")
# a string of origins separated by commas, e.g:
# "http://localhost, http://localhost:8080, http://local.dockertoolbox.tiangolo.com"
# BACKEND_CORS_ORIGINS = os.getenv("BACKEND_CORS_ORIGINS")
BACKEND_CORS_ORIGINS = "*"
# PROJECT_NAME = os.getenv("PROJECT_NAME")
PROJECT_NAME = "market"

SMTP_TLS = getenv_boolean("SMTP_TLS", True)
SMTP_PORT = None
_SMTP_PORT = os.getenv("SMTP_PORT")
if _SMTP_PORT is not None:
    SMTP_PORT = int(_SMTP_PORT)
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAILS_FROM_EMAIL = os.getenv("EMAILS_FROM_EMAIL")
EMAILS_FROM_NAME = PROJECT_NAME
EMAIL_RESET_TOKEN_EXPIRE_HOURS = 48
EMAIL_TEMPLATES_DIR = "/app/app/email-templates/build"
EMAILS_ENABLED = SMTP_HOST and SMTP_PORT and EMAILS_FROM_EMAIL

# FIRST_SUPERUSER = os.getenv("FIRST_SUPERUSER")
# FIRST_SUPERUSER_PASSWORD = os.getenv("FIRST_SUPERUSER_PASSWORD")
FIRST_SUPERUSER = "admin@aq.cn"
FIRST_SUPERUSER_UUID = r"87d7eb5382e411ea865f53e889a17c68"
# Aa.12345
FIRST_SUPERUSER_PASSWORD = (
    r"$2b$12$zfR1nq8T0KMQ6MZj8tAoIO9te4JEozG2.0CE53oBLIpgodABoRpiG"
)

PAY_PARAMS = {
    "wx": {
        "app_id": "",
        "mch_id": "",
        "mch_key": "",
        "notify_url": "",
        "key": "",
        "cert": "",
        "sess": "",
    }
}

USERS_OPEN_REGISTRATION = getenv_boolean("USERS_OPEN_REGISTRATION")

EMAIL_TEST_USER = "test@example.com"

MARKET_ID = 1
VERIFY_CODE_TIMEOUT = 180  # 秒超时时间
SMS_LIMIT_TIME = 10  # 秒超时时间
SMS_VERIFY_CODE_TIMEOUT = 300  # 秒超时时间

MONGODB_MIN_POOL_SIZE = 0
MONGODB_MAX_POOL_SIZE = 100
MONGO_SERVER = "mongodb://192.168.0.115:27017"

REDIS_URL = "redis://:123456@localhost:6379/0?encoding=utf-8"


DB_CONFIGS = {
    "connections": {
        "market": {
            # "engine": "tortoise.backends.sqlite",
            # "credentials": {"file_path": "s.db"},
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": "localhost",
                "port": "5432",
                "user": "market",
                #"user": "postgres",
                "password": "market.12345",
                #"password": "123456",
                "database": "market",
            },
        },
        "qpweb": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": "192.168.0.215",
                "port": "3306",
                "user": "root",
                "password": "123456",
                "database": "wk_aq",
            },
        },
    },
    "apps": {
        "market": {"models": ["market.models"], "default_connection": "market"},
        # "qplatform": {"default_connection": "qplatform"},
    },
}
