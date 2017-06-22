from os import environ
from collections import defaultdict
from flask import Flask
from flask_redis import FlaskRedis
from flask_jwt_extended import JWTManager

# Set app
app = Flask(__name__)

# Set app configs
if environ['BUMPS_FLASK_DEV'] == '1':
    app.config.from_object('config.DevelopmentConfig')
else:
    app.config.from_object('config.ProductionConfig')

# Set JWT Manager
jwt = JWTManager(app)

# A dictionary with a list of Job types (status, ...)
redis_dummy = defaultdict(list)  # DEBUG

# Set Redis
redis_store = FlaskRedis(app)

# Import the Flask views after instancing the app
import bumps_flask.views
