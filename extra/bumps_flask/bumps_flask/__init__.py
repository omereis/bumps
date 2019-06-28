from flask import Flask, url_for
from flask_redis import FlaskRedis
from flask_jwt_extended import JWTManager
from flask_restful import Api
from .database import Database
import sys, os

try:
    current_dir = os.getcwd()
    os.chdir(current_dir + '/bumps_flask')
    from bumps_flask.get_host_port import get_host_port
    from bumps_flask.bumps_ws_server import main
    print('Websocket server loaded')
    os.chdir(current_dir)
except Exception as e:
    print(f'current directory: {os.getcwd()}')
    print(f'run time error in "__init__": {e}')
print(f'arguments: {sys.argv[1:]}')
host,port = get_host_port()
print(f'host: {host}\nport: {port}')
#------------------------------------------------------------------------------
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

import os
results_dir = f'Results directory: "{os.getcwd()}/{os.environ["FLASK_APP"]}/static"'
#print(f'Results directory: "{os.getcwd()}/{os.environ["FLASK_APP"]}/static"')

# Import the Flask views after instancing the app
import bumps_flask.views
