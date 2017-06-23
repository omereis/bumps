import os

class Config(object):
    MAX_CONTENT_LENGHT = 16 * 1024 * 1024  # 16MB
    SECRET_KEY = os.urandom(24)


class ProductionConfig(Config):
    # JWT_PRIVATE_KEY =
    # JWT_PUBLIC_KEY =
    # JWT_ALGORITHM =
    # JWT_SESSION_COOKIE =
    pass


class DevelopmentConfig(Config):
    UPLOAD_FOLDER = os.path.join(os.getcwd(), '.bumps_folder')
    REDIS_URL = 'redis://localhost:6379'
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_SESSION_COOKIE = False
    JWT_TOKEN_LOCATION = 'cookies'
    JWT_ACCESS_COOKIE_PATH = '/'
