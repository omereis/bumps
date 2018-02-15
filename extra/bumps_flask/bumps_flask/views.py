import os
import json
import datetime

from flask import (
    url_for, render_template, redirect,
    make_response, flash, jsonify)

from flask import request as flask_request

from flask_jwt_extended import (
    jwt_required, jwt_optional, get_raw_jwt,
    get_jwt_identity, get_jwt_claims, set_access_cookies,
    jwt_refresh_token_required, set_refresh_cookies, unset_jwt_cookies)

from . import app, rdb, jwt, api
from .api import (
    create_user_token, register_token, disconnect,
    process_request_form, add_job, create_auth_token)

from .forms import TokenForm, OptimizerForm, UploadForm, FitForm
from .file_handler import setup_files, update_job_info, search_results, zip_files


@app.route('/', methods=['GET', 'POST'])
@jwt_optional
def index():
    '''
    View for the main landing page. Works as a simple authentication page.
    User can request a new UID (user token), which will also assign to them a
    JWT auth token that must be sent in every subsequent request to the
    server in order to maintain a sort of session.
    '''

    # Will return None if the current user does not have a JWT (cookie/header)
    jwt_id = get_jwt_identity()

    # The user already has a valid JWT, let them move along
    if jwt_id:
        return redirect(url_for('dashboard'))

    # Get the WTForm and validate the user token, move them along
    form = TokenForm()
#    try:
#        f = open('debug.txt', 'a')
#        f.write("form: " + str(form))
#        f.write("form.token: " + str(form.token))
#    finally:
#        f.close()

    if form.validate_on_submit():
        user_token = form.data['token']
        # Get the auth and refresh tokens from the api
        resp = json.loads(register_token(user_token).get_data())  # POST/GET
        jwt_token = resp['access_token']
        refresh_token = resp['refresh_token']

        # Prepare a redirect for a successful login
        response = make_response(redirect(url_for('dashboard')))

        # Bundle the JWT cookies into the response object
        set_access_cookies(response, jwt_token)
        set_refresh_cookies(response, refresh_token)
        flash('Logged in!')
        return response

    # If the user does not yet have a JWT token and has not filled the form,
    # display the main login page
    else:
        if form.errors:
            flash('Error: {}'.format(''.join(form.errors['token'])))

        return render_template('index.html', form=form)


@app.route('/api/dashboard', methods=['GET', 'POST'])
@jwt_required
def dashboard():
    '''
    View for the user's dashboard. They can see their
    running/completed/pending jobs and submit new jobs if
    possible based on their assigned resources. Users can
    retrieve the results of their finished jobs.
    '''

    # Retrieve the UID
    user_token = get_jwt_identity()

    update_job_info(user_token)  # DEBUG (Polling job status here)  # POST/GET

    # Get the database info for the current user
    user_jobs = rdb.hvals(user_token)

    files = {}
    for job in user_jobs:
        if job['status'] == 'COMPLETED':
            files[job['_id']] = search_results(job['directory'])
            zip_files(job['directory'], files[job['_id']])

    try:
#            import datetime
        f = open('debug.txt', 'a')
        f.write("\ndashboard():\tChange time: " + str(datetime.datetime.now()) + "\n")
        f.write("id=" + str(user_token) + "\n")
    finally:
        f.close()
    return render_template(
        'dashboard.html',
        id=user_token,
        jobs=user_jobs,
        files=files)


@app.route('/api/register', methods=['GET', 'POST'])
def tokenizer():
    '''
    View for showing the user their unique ID, which they should remember
    in order to refresh their JWT authentication.
    Uses the API to create a unique user_token which is
    then associated to an authentication JWT
    and saved as a cookie or in a header by the client
    '''

    # TODO: Check available resources here
    # Create a UID
    user_token = create_user_token()

    # Associate an auth JWT and a refresh JWT to the UID
    try :
#        rt = register_token(user_token)
        x = register_token(user_token).get_data()
        resp = json.loads(x)
#        resp = json.loads(register_token(user_token).get_data())
        jwt_token = resp['access_token']
        refresh_token = resp['refresh_token']
    except Exception as excp:
        print ("Error: " + str(excp.args))

    # Working with the client interface
    if flask_request.method == 'POST':
        try:
#            import datetime
            f = open('debug.txt', 'a')
            f.write("\nFunction tokenizer()\tChange time: " + str(datetime.datetime.now()) + "\n")
            f.write("POST request\n")
        finally:
            f.close()
        response = jsonify(
            uid=user_token,
            auth_token=jwt_token,
            refresh_token=refresh_token)

    # Working with the web page interface
    else:
        # Build the response object to a template
        response = make_response(
            render_template('tokenizer.html', token=user_token))

    # Bundle the JWT cookies into the response object
    try:
#            import datetime
        f = open('debug.txt', 'a')
        f.write("\nFunction tokenizer()\tChange time: " + str(datetime.datetime.now()) + "\n")
        f.write("flask_request.method=" + str(flask_request.method) + "\n")
    finally:
        f.close()
    set_access_cookies(response, jwt_token)
    set_refresh_cookies(response, refresh_token)
    return response


@app.route('/api/fit', methods=['GET', 'POST'])
@jwt_required
def fit_job(results=False):
    '''
    Page for displaying the forms related to building
    a FitProblem as described in the bumps docs. This
    function validates the forms and sets up the job
    by working with the API functions.
    '''

    form = FitForm()
    if form.validate_on_submit():
        # Parse through the form data
        form_data = (process_request_form(form.data))

        # Assuming the UIDs are unique enough, a job_id
        # can be an incremental integer associated with a UID.
        job_id = str(rdb.hlen(get_jwt_identity()) + 1)

        # Build job directory
        _dir = os.path.join(app.config.get('UPLOAD_FOLDER'),
                            'fit_problems', get_jwt_identity(), 'job' + job_id)

        # TODO: Get queue here
        # queue = 'rq'

        # TODO: Add extra keys from form_data
        bumps_payload = {
            'user': get_jwt_identity(),
            '_id': job_id,
            'origin': flask_request.remote_addr,
            'directory': _dir,
            'status': 'PENDING',
            'submitted': datetime.datetime.now().strftime('%c')
        }

        # Use the parsed data to set up the job related files
        # and build a BumpsJob (json serialized dict)
        try:
#            import datetime
            f = open('debug.txt', 'a')
            f.write("\nfit_job, Before calling 'setup_files':\tChange time: " + str(datetime.datetime.now()) + "\n")
        finally:
            f.close()
        bumps_payload = setup_files(bumps_payload, form_data,
                                    form.upload.data['script'])

        add_job(bumps_payload)
        flash('Job submitted successfully.')
        return redirect(url_for('dashboard'))

    return render_template('service.html', form=form)


@app.route('/refresh')
@jwt_refresh_token_required
def refresh():
    '''
    Refreshes a user's access token if they hold
    a valid refresh token
    '''
    jwt_token = create_auth_token(get_jwt_identity())

    resp = make_response(redirect(url_for('dashboard')))
    set_access_cookies(resp, jwt_token)
    flash('Token refreshed successfully!')
    return resp


@app.route('/api/web/logout')
@jwt_required
def logout():
    # Get the JWT identifier and set logged_out to 'true' in DB
    jti = get_raw_jwt()['jti']
    rdb.set(jti, 'true', app.config.get('JWT_ACCESS_TOKEN_EXPIRES'))

    resp = make_response(redirect(url_for('index')))
    unset_jwt_cookies(resp)

    flash('Logged out successfully!')
    return resp


# The following functions define the responses for JWT callbacks

@jwt.token_in_blacklist_loader
def token_in_blacklist_callback(decrypted_token):
    jti = decrypted_token['jti']
    entry = rdb.get(jti)
    if entry is None:
        return True
    return entry == 'true'


@jwt.expired_token_loader
def expired_token_callback():
    '''
    Function to call when an expired token accesses a protected endpoint
    '''
    return render_template(
        'error.html', reason="Expired token", expired=True), 401


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
        response = make_response(redirect(url_for('index')))
        unset_jwt_cookies(response)
        flash('Invalid token detected, redirected to the frontpage.')
        return response

    return render_template('error.html', reason=error), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    '''
    Function to call when a revoked token accesses a protected endpoint
    '''

    return render_template(
        'error.html', reason='You are not logged in!'), 401
