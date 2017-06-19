import os
from flask import Flask
from flask_redis import FlaskRedis
from collections import defaultdict

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'bumps_folder')


app = Flask(__name__)

# Set app variables
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGHT'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] = os.urandom(24)
app.config['WTF_CSRF_ENABLED'] = True



# A dictionary with a list of Job types (status, ...)
redis_dummy = defaultdict(list)

# Set Redis
REDIS_URL = 'redis://localhost:6379'
redis_store = FlaskRedis(app)

import bumps_flask.server
