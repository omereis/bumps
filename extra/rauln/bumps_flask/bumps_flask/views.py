from flask import url_for, render_template, redirect, \
    send_from_directory, make_response, flash, jsonify
from flask import request as flask_request

from flask_jwt_extended import jwt_required, jwt_optional,\
    get_jwt_identity, get_jwt_claims, set_access_cookies

from . import app, rdb, jwt
from .api import api, create_user_token, register_token, process_request_form
from .forms import TokenForm, OptimizerForm, UploadForm, FitForm
from .file_handler import setup_job


@app.route('/')
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

    # Retrieve the UID
    user_token = get_jwt_identity()
    # Get the database info for the current user
    user_data = rdb.hget('users', user_token)
    return render_template('dashboard.html', id=user_token, jobs=user_data[0]['jobs'])


@app.route('/register', methods=['GET', 'POST'])
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
    # Associate an auth JWT to the UID
    jwt_token = register_token(user_token)

    # Working with the client interface
    if flask_request.method == 'POST':
        response = jsonify({'uid': user_token})

    # Working with the web page interface
    else:
        # Build the response object to a template
        response = make_response(
            render_template('tokenizer.html', token=user_token))

    # Bundle the JWT cookie into the response object
    set_access_cookies(response, jwt_token)
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
        setup_job(user=get_jwt_identity(), _input=form_data, _file=form.upload.data['script'])
        # Display the results
        return render_template('service.html', data=form_data, results=True)

    return render_template('service.html', form=form)


@app.route('/api/upload', methods=['GET', 'POST'])
@jwt_required
def upload():
    '''
    Function which handles file uploads to the server.
    '''

    form = UploadForm()
    if form.validate_on_submit():
        form_data = process_request_form(form.script.data)
        setup_job(user=get_jwt_identity(), _data=form_data)
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


########## The following functions define the responses for JWT auth failure. ##########

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
