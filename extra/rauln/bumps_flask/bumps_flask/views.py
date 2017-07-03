import os
import requests
import random
import datetime
import json

from flask import url_for, render_template, redirect, \
    send_from_directory, make_response, flash

from flask import request as flask_request

from flask_jwt_extended import jwt_required, jwt_optional,\
    get_jwt_identity, get_jwt_claims, jwt_refresh_token_required,\
    set_access_cookies

from . import app, rdb, jwt
from .api import api, create_user_token, register_token, \
    process_request_form, setup_job

from .forms import TokenForm, LineForm, OptimizerForm, UploadForm, FitForm
from .slurm_handler import build_slurm_script, line_handler

USERS_H = 'user_tokens'  # DEBUG


@app.route('/')
@jwt_optional
def index():
    '''
    View for the main landing page. Works as a simple authentication page.
    User can request a new UID(), which will also assign to him/her a
    JWT token which must be sent in every subsequent request to the
    server in order to maintain a "session".
    '''

    # Will return None if the current user does not have a JWT (cookie/header)
    jwt_id = get_jwt_identity()

    # The user already has a valid JWT, let them move along
    if jwt_id:
        return redirect(url_for('dashboard'))

    # Get the WTForm and validate the user token, move them along
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
    View for the user's dashboard. They can see their
    running/completed/pending jobs and submit new jobs if
    possible based on their assigned resources.
    '''
    user_token = get_jwt_identity()
    user_data = rdb.hget('users', user_token)
    # Zip together job numbers and job files if possible to display in template
    # if rdb.hget(user_token, 'job_n'):
    #     user_jobs = [i for i in xrange(int(rdb.hget(user_token, 'job_n')))]
    #     zipped = zip(user_jobs, user_scripts)

    # else:
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
    jwt_token = register_token(user_token)
    response = make_response(
        render_template('tokenizer.html', token=user_token))
    set_access_cookies(response, jwt_token)
    return response


@app.route('/api/fit', methods=['GET', 'POST'])
@jwt_required
def fit_job(results=False):
    '''
    '''
    form = FitForm()
    if form.validate_on_submit():
        payload = (process_request_form(form.data))
        dest = setup_job(user=get_jwt_identity(), data='',
                         filename=get_jwt_identity() + '.sh')
        build_slurm_script(dest, payload['slurm'])
        line_handler(dest, payload['line'])  # DEBUG
        return render_template('service.html', data=payload, results=True)

    return render_template('service.html', form=form)


@app.route('/api/results', methods=['GET', 'POST'])
def display_results():
    '''
    '''
    # run_script(build_script(payload))
    print(flask_request.form)
    return render_template('results.html',
                           payload=flask_request.form.get('payload'))


@app.route('/api/upload', methods=['GET', 'POST'])
@jwt_required
def upload():
    '''
    Function which handles file uploads to the server.
    '''

    form = UploadForm()
    if form.validate_on_submit():
        setup_job(user=get_jwt_identity(), _file=form.script.data)  # DEBUG
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
        response = make_response(redirect(url_for('tokenizer')))
        unset_jwt_cookies(response)
        return response

    return render_template('error.html', reason=error), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    '''
    Function to call when a revoked token accesses a protected endpoint
    '''

    return render_template(
        'error.html', reason='Your token has been revoked.'), 401
