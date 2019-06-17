from flask import Flask, url_for
from flask_redis import FlaskRedis
from flask_jwt_extended import JWTManager
from flask_restful import Api
from .database import Database

# Set app
app = Flask(__name__, instance_relative_config=True)

# Set app configs
app.config.from_object('config')
app.config.from_pyfile('config.py', silent=True)

from .oe_debug import print_debug

with app.test_request_context():
    print_debug(f'{url_for("static", filename="results")}')

# Set JWT Manager
jwt = JWTManager(app)

# Set RESTful API
api = Api(app)

# Set redis
redis = FlaskRedis(app)

# Set Redis db
rdb = Database(redis)
print("rdb created: " + str(rdb))

# Import the Flask views after instancing the app
import bumps_flask.views
