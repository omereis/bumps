import sys
from flask import Flask
from flask_redis import FlaskRedis
from flask_jwt_extended import JWTManager
from flask_restful  import Api
from flask_rq2 import RQ
from .database import Database

# Set app
app = Flask(__name__, instance_relative_config=True)

# Set app configs
app.config.from_object('config')
app.config.from_pyfile('config.py', silent=True)

# Set JWT Manager
jwt = JWTManager(app)

# Set RESTful API
api = Api(app)

# Set redis
redis = FlaskRedis(app)

# Set Redis db
rdb = Database(redis)

# Set queue
rqueue = RQ(app)  # DEBUG


try:
    rdb.ping()
except:
    print("WARNING: Redis isn't running. try `/etc/init.d/redis-server restart`")
    sys.exit(1)

# Import the Flask views after instancing the app
import bumps_flask.views
