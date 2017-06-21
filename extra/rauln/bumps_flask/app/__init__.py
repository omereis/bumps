import os
import sys
from collections import defaultdict
from flask import Flask, jsonify, url_for, render_template,\
 redirect, send_from_directory
from flask_redis import FlaskRedis
from flask_jwt_extended import JWTManager

UPLOAD_FOLDER = os.path.join(os.getcwd(), '.bumps_folder')

app = Flask(__name__)

# Set app variables
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGHT'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] = os.urandom(24)

# Set JWT Manager
jwt = JWTManager(app)

# A dictionary with a list of Job types (status, ...)
redis_dummy = defaultdict(list)

# Set Redis
REDIS_URL = 'redis://localhost:6379'
redis_store = FlaskRedis(app)

# Import the Flask views after instancing the app
import app.server
