from __future__ import print_function
import os, requests, random, datetime

from flask import url_for, render_template, redirect, send_from_directory, make_response
from flask import request as flask_request

from werkzeug.utils import secure_filename

from flask_jwt_extended import jwt_required, jwt_optional, get_jwt_identity,\
get_jwt_claims, set_access_cookies, jwt_refresh_token_required

from bumps_flask import app, rdb, jwt
from bumps_flask.api import api, create_user_token, register_token
from bumps_flask.forms import TokenForm, LineForm, OptimizerForm


# Set the allowed file upload extensions
ALLOWED_EXT = ('xml')

USERS_H = 'user_tokens'  # DEBUG


@app.route('/')
@jwt_optional
def index(jwt_id=None):
    '''
    View for the main landing page. Works as a simple authentication page.
    User can request a new UID(), which will also assign to him/her a
    JWT token which must be sent in every subsequent request to the
    server in order to maintain a session.
    '''
    jwt_id = get_jwt_identity()

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
    View for the user's dashboard. They can see their running/completed jobs
    and submit new jobs if possible based on their assigned resources.
    '''
    user_token = get_jwt_identity()
    if rdb.exists(USERS_H, user_token):
        if flask_request.method == 'POST' and user_token == flask_request.form.get('token') or flask_request.method == 'GET':
            return render_template('dashboard.html', id=user_token, valid=True, user_jobs=rdb.get(USERS_H, user_token))
        return """That's not your token... (Clear cookies?)"""  # DEBUG
    return render_template('dashboard.html', id=user_token, valid=False)


@app.route('/register', methods=['GET'])
def tokenizer():
    '''
    View for showing the user their unique ID, which they should store
    in order to refresh their JWT.
    Uses the API to create a unique user_token which is
    then associated to an authorization JWT token
    and saved as a cookie by the client
    '''

    user_token = create_user_token()
    jwt_token = register_token(user_token)
    refresh_token = register_token(user_token, refresh=True)
    response = make_response(render_template('tokenizer.html', token=user_token))
    set_access_cookies(response, jwt_token)
    return response


@app.route('/api/fit', methods=['GET', 'POST'])
@jwt_required
def fit_job(job=None, submitted=False):
    '''
    View
    '''
    l_form = LineForm()
    o_form = OptimizerForm()
    if l_form.validate_on_submit():
        return redirect(url_for('results'))

    return render_template('service.html', job=job, submitted=submitted, l_form=l_form, o_form=o_form)

@app.route('/api/results')
def display_results():
    return render_template('results.html')


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


def allowed_file(filename):
    '''
    Boolean function which checks to see if POSTed file is allowed
    based on extension
    '''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


# The following functions define the responses for JWT auth failure.


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
