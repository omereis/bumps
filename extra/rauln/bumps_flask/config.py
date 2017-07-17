import os
import datetime
from tempfile import gettempdir

# TODO: Fix cookies so they work when options are True

SECRET_KEY = os.urandom(24) # Set a secret key here
MAX_CONTENT_LENGHT = 8 * 1024 * 1024  # 8MB
UPLOAD_FOLDER = os.path.join(gettempdir(), 'bumps_flask')
REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://redis:6379')

WTF_CSRF_ENABLED = False

JWT_TOKEN_LOCATION = 'cookies'
JWT_ACCESS_COOKIE_PATH = '/'
JWT_COOKIE_CSRF_PROTECT = False
JWT_COOKIE_SECURE = False
JWT_SESSION_COOKIE = False

JWT_BLACKLIST_ENABLED = True
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(weeks=1)

# JWT_PRIVATE_KEY =
# JWT_PUBLIC_KEY =
# JWT_ALGORITHM =
