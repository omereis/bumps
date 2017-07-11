import os
import datetime

### DEBUG
MAX_CONTENT_LENGHT = 16 * 1024 * 1024  # 16MB
SECRET_KEY = os.urandom(24)
UPLOAD_FOLDER = os.path.join(os.getcwd(), '.bumps_folder')
REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
WTF_CSRF_ENABLED = False
JWT_COOKIE_CSRF_PROTECT = False
JWT_SESSION_COOKIE = True
JWT_TOKEN_LOCATION = 'cookies'
JWT_ACCESS_COOKIE_PATH = '/'
JWT_BLACKLIST_ENABLED = True
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(seconds=30)
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(minutes=2)
# JWT_PRIVATE_KEY =
# JWT_PUBLIC_KEY =
# JWT_ALGORITHM =
# JWT_SESSION_COOKIE =
# JWT_COOKIE_SECURE = True
# JWT_COOKIE_CSRF_PROTECT = True
