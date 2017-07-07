import os
import datetime

### DEBUG
WTF_CSRF_ENABLED = False
JWT_COOKIE_CSRF_PROTECT = False
JWT_SESSION_COOKIE = True
JWT_TOKEN_LOCATION = 'cookies'
JWT_ACCESS_COOKIE_PATH = '/'
MAX_CONTENT_LENGHT = 16 * 1024 * 1024  # 16MB
SECRET_KEY = os.urandom(24)
DEBUG=False
REDIS_URL = os.environ.get('REDIS_URL', 'redis://bumps_redis:6379/0')
UPLOAD_FOLDER = os.path.join(os.getcwd(), '.bumps_folder')
# JWT_PRIVATE_KEY =
# JWT_PUBLIC_KEY =
# JWT_ALGORITHM =
# JWT_SESSION_COOKIE =
# JWT_COOKIE_SECURE = True
# JWT_COOKIE_CSRF_PROTECT = True
