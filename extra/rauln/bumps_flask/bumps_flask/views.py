import json

from flask import (
    url_for, render_template, redirect,
    send_from_directory, make_response,
    flash, jsonify)

from flask import request as flask_request

from flask_jwt_extended import (
    jwt_required, jwt_optional, get_jti, get_raw_jwt,
    get_jwt_identity, get_jwt_claims, set_access_cookies,
    jwt_refresh_token_required, set_refresh_cookies, unset_jwt_cookies)

from . import app, rdb, jwt
from .api import (
    api, create_user_token, register_token,
    process_request_form, add_job, create_auth_token)

from .forms import TokenForm, OptimizerForm, UploadForm, FitForm
from .file_handler import setup_job


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

    if form.validate_on_submit():
        user_token = form.data['token']
        # Get the auth and refresh tokens from the api
        resp = json.loads(register_token(user_token).get_data())
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
    possible based on their assigned resources.
    '''

    # Retrieve the UID
    user_token = get_jwt_identity()
    # Get the database info for the current user
    user_data = rdb.hget('users', user_token)
    return render_template('dashboard.html', id=user_token, jobs=user_data)


@app.route('/register', methods=['GET', 'POST'])
def tokenizer():
    '''
    View for showing the user their unique ID, which they should remember
    in order to refresh their JWT authentication.
    Uses the API to create a unique user_token which is
    then associated to an authentication JWT
    and saved as a cookie by the client
    '''

    # Create a UID
    user_token = create_user_token()
    # Associate an auth JWT and a refresh JWT to the UID
    resp = json.loads(register_token(user_token).get_data())
    jwt_token = resp['access_token']
    refresh_token = resp['refresh_token']

    # Working with the client interface
    if flask_request.method == 'POST':
        response = jsonify(uid=user_token, auth_token=jwt_token, refresh_token=refresh_token)

    # Working with the web page interface
    else:
        # Build the response object to a template
        response = make_response(
            render_template('tokenizer.html', token=user_token))

    # Bundle the JWT cookies into the response object
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

        # Use the parsed data to set up a job and related files
        job_id = setup_job(user=get_jwt_identity(),
                _input=form_data, _file=form.upload.data['script'])  # DEBUG

        add_job(get_jwt_identity(), job_id)  # DEBUG

        flash('Job submitted successfully.')
        return redirect(url_for('dashboard'))

    return render_template('service.html', form=form)


# @app.route('/api/uploaded_file/<filename>')
# @jwt_required
# def uploaded_file(filename):
#     '''
#     Sends a previously uploaded file to the browser
#     '''
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


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


@app.route('/logout', methods=['GET', 'POST','DELETE'])
@jwt_required
def logout():
    '''
    Blacklists the user's refresh token
    and unsets the cookies/removes the headers
    '''

    jti = get_raw_jwt()['jti']
    rdb.set(jti, 'true', app.config.get('JWT_ACCESS_TOKEN_EXPIRES'))

    resp = make_response(redirect(url_for('index')))
    unset_jwt_cookies(resp)
    flash('Logged out successfully!')
    return resp


########## The following functions define the responses for JWT auth failure. ##########

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
    return render_template('error.html', reason="Expired token", expired=True), 401


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
