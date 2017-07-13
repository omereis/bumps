import os
import datetime
from tempfile import gettempdir


SECRET_KEY = os.urandom(24) # Set a secret key here
MAX_CONTENT_LENGHT = 8 * 1024 * 1024  # 8MB
UPLOAD_FOLDER = os.path.join(gettempdir(), 'bumps_flask')
REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

WTF_CSRF_ENABLED = True

JWT_TOKEN_LOCATION = 'cookies'
JWT_COOKIE_CSRF_PROTECT = True
JWT_COOKIE_SECURE = True
JWT_SESSION_COOKIE = True
JWT_ACCESS_COOKIE_PATH = '/'

JWT_BLACKLIST_ENABLED = True
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(weeks=1)

# JWT_PRIVATE_KEY =
# JWT_PUBLIC_KEY =
# JWT_ALGORITHM =
