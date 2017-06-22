import os
import sys
from collections import defaultdict
from flask import Flask
from flask_redis import FlaskRedis
from flask_jwt_extended import JWTManager

UPLOAD_FOLDER = os.path.join(os.getcwd(), '.bumps_folder')

app = Flask(__name__)

# Set app variables
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGHT'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] = os.urandom(24)
app.config['JWT_TOKEN_LOCATION'] = 'cookies'  # Option for users who do not accept cookies will be requiered
app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
# app.config[JWT_PRIVATE_KEY]
# app.config[JWT_PUBLIC_KEY]
# app.config[JWT_ALGORITHM]
# app.config['JWT_SESSION_COOKIE'] = False  # Keep cookies alive for now

# The following should be true in production
app.config['JWT_COOKIE_SECURE'] = False  # DEBUG
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # DEBUG


# Set JWT Manager
jwt = JWTManager(app)

# A dictionary with a list of Job types (status, ...)
redis_dummy = defaultdict(list)  # DEBUG

# Set Redis
REDIS_URL = 'redis://localhost:6379'
redis_store = FlaskRedis(app)

# Import the Flask views after instancing the app
import bumps_flask.views
