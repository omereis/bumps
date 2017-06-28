import os, datetime

class Config(object):
    MAX_CONTENT_LENGHT = 16 * 1024 * 1024  # 16MB
    SECRET_KEY = os.urandom(24)


class ProductionConfig(Config):
    # JWT_PRIVATE_KEY =
    # JWT_PUBLIC_KEY =
    # JWT_ALGORITHM =
    # JWT_SESSION_COOKIE =
    # JWT_COOKIE_SECURE = True
    # JWT_COOKIE_CSRF_PROTECT = True
    # UPLOAD_FOLDER = os.path.join(os.getcwd(), '.bumps_folder')

    pass

class DevelopmentConfig(Config):
    UPLOAD_FOLDER = os.path.join(os.getcwd(), '.bumps_folder')
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    WTF_CSRF_ENABLED = False
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_SESSION_COOKIE = True
    JWT_TOKEN_LOCATION = 'cookies'
    JWT_ACCESS_COOKIE_PATH = '/'
    # JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(seconds=5)
    # JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(minutes=5)
