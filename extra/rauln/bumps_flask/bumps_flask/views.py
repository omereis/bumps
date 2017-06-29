import os
import requests
import random
import datetime
import json

from flask import url_for, render_template, redirect, send_from_directory, make_response, flash
from flask import request as flask_request

from werkzeug.utils import secure_filename

from flask_jwt_extended import jwt_required, jwt_optional, get_jwt_identity,\
    get_jwt_claims, jwt_refresh_token_required, set_access_cookies

from bumps_flask import app, rdb, jwt
from bumps_flask.api import api, create_user_token, register_token, process_request_form
from bumps_flask.forms import TokenForm, LineForm, OptimizerForm, UploadForm, FitForm


USERS_H = 'user_tokens'  # DEBUG


@app.route('/')
@jwt_optional
def index():
    '''
    View for the main landing page. Works as a simple authentication page.
    User can request a new UID(), which will also assign to him/her a
    JWT token which must be sent in every subsequent request to the
    server in order to maintain a session.
    '''

    # Will return None if the current user does not have a JWT (cookie/header)
    jwt_id = get_jwt_identity()

    # The user already has a valid JWT, let them move along
    if jwt_id:
        return redirect(url_for('dashboard'))

    # Get the WTForm and validate the user token
    form = TokenForm()
    if form.validate_on_submit():
        redirect(url_for('dashboard'))

    # If the user does not yet have a JWT token and has not filled the form,
    # display they main login page
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
    user_scripts = rdb.hget(user_token, 'model_files')
    if rdb.hget(user_token, 'job_n'):
        user_jobs = [i for i in xrange(int(rdb.hget(user_token, 'job_n')))]
        zipped = zip(user_jobs, user_scripts)

    else:
        zipped = None

    return render_template('dashboard.html', id=user_token, jobs=zipped)


@app.route('/register')
def tokenizer():
    '''
    View for showing the user their unique ID, which they should store
    in order to refresh their JWT.
    Uses the API to create a unique user_token which is
    then associated to an authorization JWT token
    and saved as a cookie by the client
    '''

    # Create a UID
    user_token = create_user_token()
    jwt_token = register_token(user_token, auth_token=True)
    response = make_response(
        render_template(
            'tokenizer.html',
            token=user_token))
    set_access_cookies(response, jwt_token)
    return response


@app.route('/api/fit', methods=['GET', 'POST'])
@jwt_required
def fit_job(results=False):
    '''
    '''
    form = FitForm()
    if form.validate_on_submit():
        # payload = json.loads(process_request_form(form.data))
        payload = form.data
        return render_template(url_for('display_results'), data=payload)

    return render_template('service.html', form=form)


@app.route('/api/results', methods=['GET', 'POST'])
def display_results(data=None):
    '''
    '''

    data = flask_request.form
    # run_script(build_script(payload))

    return render_template('results.html', data=data)


@app.route('/api/upload', methods=['GET', 'POST'])
@jwt_required
def upload():
    '''
    Function which handles file uploads to the server.
    '''

    form = UploadForm()
    if form.validate_on_submit():
        # Convenient variables
        folder = app.config.get('UPLOAD_FOLDER')
        user_token = get_jwt_identity()

        # Get the file form data
        f = form.script.data

        # Sanitize the filename
        filename = secure_filename(f.filename)

        # Convenient variable
        dest = os.path.join(folder, 'fit_problems', user_token)

        # Make sure the upload folder exists beforehand
        if not os.path.exists(dest):
            os.makedirs(dest)

        # Save the uploaded file
        f.save(os.path.join(dest, filename))

        # Process the file, mark it as received and redirect user
        # run_fitjob(dest)
        rdb.hset(user_token, 'model_files', filename)
        rdb.hincr(user_token, 'job_n', 1)
        flash('File uploaded successfully!')
        return redirect(url_for('dashboard'))

    else:
        return render_template('upload.html', form=form)


@app.route('/api/uploaded_file/<filename>')
@jwt_required
def uploaded_file(filename):
    '''
    Sends a previously uploaded file to the browser
    '''
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# @app.route('/api/refresh')
# @jwt_refresh_token_required
# def refresh():
#     form = TokenForm()
#
#     if form.validate_on_submit():
#         if form.token.data == get_jwt_identity():
#             jwt_token = register_token(form.token.data, auth_token=True)
#             response = make_response(render_template(url_for('index')))
#             set_access_cookies(response, jwt_token)
#             return response
#
#         else:
#             render_template('refresh.html', form=form, error=True)
#
#     else:
#         return render_template('refresh.html', form=form, error=False)


# The following functions define the responses for JWT auth failure.

@jwt.expired_token_loader
def expired_token_callback():
    '''
    Function to call when an expired token accesses a protected endpoint
    '''
    return render_template('error.html', reason="Expired token"), 401


@jwt.unauthorized_loader
# @jwt_refresh_token_required
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

    user_token = get_jwt_identity()
    if user_token:
        jwt_token = register_token(user_token, auth_token=True)
        # refresh_token = register_token(user_token, auth_token=False, refresh_token=True)
        response = make_response(redirect(url_for('index')))
        set_access_cookies(response, jwt_token)
        return response

    return render_template('error.html', reason=error), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    '''
    Function to call when a revoked token accesses a protected endpoint
    '''

    return render_template(
        'error.html', reason='Your token has been revoked.'), 401
