from os import environ
from flask import Flask
from flask_redis import FlaskRedis
from flask_jwt_extended import JWTManager
from .database import Database

# Set app
app = Flask(__name__)

# Set JWT Manager
jwt = JWTManager(app)

# Set Redis db
rdb = Database(FlaskRedis(app))

# Not working currently (just hangs)
try:
    rdb.ping()
except:
    print("Redis isn't running. try `/etc/init.d/redis-server restart`")
    exit(0)

# Set app configs
if environ.get('BUMPS_FLASK_DEV', '0') == '1':
    app.config.from_object('config.DevelopmentConfig')
    # rdb.flushall()  # DANGER!!
else:
    app.config.from_object('config.ProductionConfig')

# Import the Flask views after instancing the app
import bumps_flask.views
