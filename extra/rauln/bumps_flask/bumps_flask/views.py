from __future__ import print_function
import os, requests, random, datetime

from flask import url_for, render_template, redirect, send_from_directory, make_response
from flask import request as flask_request

from werkzeug.utils import secure_filename

from flask_jwt_extended import jwt_required, jwt_optional, get_jwt_identity, get_jwt_claims, set_access_cookies

from bumps_flask import app, redis_store, redis_dummy, jwt
from bumps_flask.api import api, redis_dummy, create_user_token, register_token
from bumps_flask.forms import TokenForm


# Set the allowed file upload extensions
ALLOWED_EXT = ('xml')


@app.route('/')
@jwt_optional
def index(jwt_id=None):
    jwt_id = get_jwt_identity()
    print(jwt_id)
    if jwt_id:
        return render_template('index.html', jwt_id=jwt_id)

    form = TokenForm()
    if form.validate_on_submit():
        user_token = form.token.data
        redirect(url_for('dashboard'), user_token=user_token, jwt_id=jwt_id)

    else:
        return render_template('index.html', form=form)


@app.route('/api/dashboard', methods=['GET', 'POST'])
@jwt_required
def dashboard():
    '''
    Validates a resource token and assigns a JWT token
    for expiration, authentication (...)
    '''
    user_token = get_jwt_identity()
    if user_token in redis_dummy:
        if flask_request.method == 'POST' and user_token == flask_request.form.get('token'):
            return render_template('dashboard.html', id=user_token, valid=True, user_jobs=redis_dummy[user_token])
        elif flask_request.method == 'GET':
            return render_template('dashboard.html', id=user_token, valid=True, user_jobs=redis_dummy[user_token])
        return """That's not your token... (Clear cookies?)"""
    return render_template('dashboard.html', id=user_token, valid=False)


@app.route('/register', methods=['GET'])
def tokenizer():
    '''
    Uses the API to create a unique user_token which is
    then associated to an authorization JWT token
    and saved as a cookie by the client
    '''

    user_token = create_user_token()
    jwt_token = register_token(user_token)
    response = make_response(render_template('tokenizer.html', token=user_token))
    set_access_cookies(response, jwt_token)
    return response


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


@app.route('/api/submit', methods=['GET', 'POST'])
@jwt_required
def submit_job(job=None, submitted=False):
    return render_template('service.html', job=job, submitted=submitted)


def allowed_file(filename):
    '''
    Boolean function which checks to see if POSTed file is allowed
    based on extension
    '''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


# The following functions define the responses for JWT failure.


@jwt.expired_token_loader
def expired_token_callback():
    '''
    Function to call when an invalid token accesses a protected endpoint.
    '''

    return render_template('error.html', reason='Your token has expired.'), 401


@jwt.unauthorized_loader
def unauthorized_token_callback(error):
    '''
    Function to call when a request with no JWT accesses a protected endpoint
    Takes one argument - an error string indicating why the request in unauthorized
    '''

    return render_template('error.html', reason=error), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    '''
    Function to call when an invalid token accesses a protected endpoint
    Takes one argument - an error string indicating why the token is invalid
    '''

    return render_template('error.html', reason=error), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    '''
    Function to call when a revoked token accesses a protected endpoint
    '''

    return render_template('error.html', reason='Your token has been revoked.'), 401
