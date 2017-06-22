from __future__ import print_function
import os
import requests
import random
import datetime
from flask import url_for, render_template, redirect,\
    send_from_directory, make_response
from flask import request as flask_request
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, create_access_token,\
    get_jwt_identity, get_jwt_claims, set_access_cookies

from bumps_flask import app, redis_store, redis_dummy, jwt
from bumps_flask.api import api, redis_dummy, generate_user_token


# Set the allowed file upload extensions
ALLOWED_EXT = ('xml')

# Testing user_tokens and JWT tokens,
# make a simple map between them to keep track for now
token_map = {}

def allowed_file(filename):
    '''
    Boolean function which checks to see if POSTed file is allowed
    based on extension
    '''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


@app.route('/api/upload', methods=['POST'])
@jwt_required
def upload_file():
    '''
    Function which handles file uploads to the server.
    Checks for the existance of a pre-defined upload folder and creates one if not found.
    '''
    file_to_upload = flask_request.files['file']
    if file_to_upload and allowed_file(file_to_upload.filename):
        # Parse the filename to make sure it is safe
        filename = secure_filename(file_to_upload.filename)
        # Create the upload folder if it does not exist yet
        if not os.path.exists(app.config.get('UPLOAD_FOLDER')):
            os.mkdir(app.config.get('UPLOAD_FOLDER'))
        # Finally, save the uploaded file in the upload folder
        file_to_upload.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('submit_job'))
    return 'Error uploading file... Make sure you are uploading a .xml file.'


@app.route('/api/uploaded_file/<filename>')
@jwt_required
def uploaded_file(filename):
    '''
    Sends a previously uploaded file to the browser
    '''
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/dashboard', methods=['GET', 'POST'])
@jwt_required
def login():
    '''
    Validates a resource token and assigns a JWT token
    for expiration, authentication (...)

    todo: Cleanup
          Move api operations to api module
    '''
    global token_map  # DEBUG

    if flask_request.method == 'POST':
        t = flask_request.form['token']
        if t in redis_dummy:
            print(get_jwt_claims())
            return render_template('service.html', id=t, valid=True,
                user_jobs=redis_dummy[t], user_jwt=token_map[t])
        else:
            return render_template('service.html', id=t, valid=False)
    else:
        t = get_jwt_identity()
        if t in redis_dummy:
            return render_template('service.html', id=t, valid=True,
                user_jobs=redis_dummy[t], user_jwt=token_map[t])
        else:
            return render_template('service.html', id=t, valid=False)


@app.route('/auth_token', methods=['GET'])
def tokenizer():
    '''
    Generates a resource token for accessing bumps functionality
    based on available resources, priority (...)

    todo: check resources before providing token
    todo: implement an existing, secure token generator
    '''
    login_token = generate_user_token()
    jwt_token = create_access_token(identity=login_token)

    # Create the dummy db with key=user_token, value=[user_jobs]
    redis_dummy[login_token] = []
    # Create the dummy db with key=user_token, value=jwt_token
    token_map[login_token] = jwt_token
    # Build the response, create the cookie and send it
    r = make_response(render_template('tokenizer.html', token=login_token))
    set_access_cookies(r, jwt_token)
    return r


@app.route('/api/submit', methods=['GET', 'POST'])
@jwt_required
def submit_job(job=None, submitted=False):
    return render_template('fit.html', job=job, submitted=submitted)


@app.route('/')
def index():
    return render_template('index.html')
