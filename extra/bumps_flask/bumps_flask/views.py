from flask import Flask, render_template, request
import os, json, datetime

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

from .oe_debug import print_debug
#------------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    '''
    '''
    return render_template('bumps_mp_gui.html')
#------------------------------------------------------------------------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    print_debug("views.py, dashboard")
    return render_template('dashboard.html',id=17)
#------------------------------------------------------------------------------
@app.route('/onsendfitjob')
def on_send_fit_job():
    res = {}
    try:
        res = request.args['message']
        print(f'res:\n---------------\n{res}\n-------------------\n')
        print(f'type(res): {type(res)}')
        cm = json.loads(res)
        print(f'cm = {cm}')
        print(f'type(cm): {type(cm)}')
        for key in cm.keys():
            print(f'\t{key}:\t{cm[key]}')
    except Exception as e:
        print (f'run time error in on_send_fit_job: {e}')
    return json.dumps(res)
#------------------------------------------------------------------------------
