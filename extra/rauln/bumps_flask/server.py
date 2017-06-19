#!/usr/bin/env python

from __future__ import print_function
import os, requests, random
from flask import Flask, url_for, render_template, redirect, send_from_directory, flash
from flask import request as flask_request
from werkzeug.utils import secure_filename

from bumps_flask import app, redis_store, redis_dummy
from bumps_flask.api import api, generate_user_token


# Set the allowed file upload extensions
ALLOWED_EXT = set(['txt', 'pdf', 'png'])

def allowed_file(filename):
    '''
    Boolean function which checks to see if POSTed file is allowed based on extension
    '''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    '''
    Function which handles file uploads to the server.
    Checks for the existance of a pre-defined upload folder and creates one if not found.
    '''
    if flask_request.method == 'POST':
        _file = flask_request.files['file']
        if _file and allowed_file(_file.filename):
            filename = secure_filename(_file.filename)
            if not os.path.exists(app.config.get('UPLOAD_FOLDER')):
                os.mkdir(app.config.get('UPLOAD_FOLDER'))
            _file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))

@app.route('/uploaded_file/<filename>')
def uploaded_file(filename):
    '''
    Sends a previously uploaded file to the browser
    '''
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/login', methods=['GET', 'POST'])
def login(id=None, valid=False, user_jobs=None):
    '''
    Validates a resource token and assigns a JWT token
    for expiration, authentication (...)
    '''
    if flask_request.method == 'POST':
        t = flask_request.form['token']
        if t in redis_dummy:
            return render_template('service.html', id=t, valid=True, user_jobs = redis_dummy[t])
        else:
            return render_template('service.html', id=t, valid=False)


@app.route('/register', methods=['GET', 'POST'])
def tokenizer(token=None):
    '''
    Generates a resource token for accessing bumps functionality
    based on available resources, priority (...)
    '''
    login = generate_user_token()
    redis_dummy[login] = []
    return render_template('tokenizer.html', token=login)

@app.route('/submit', methods=['POST'])
def submit_job(job=None):
    return render_template('fit.html', job=job)

@app.route('/')
def index():
    return render_template('index.html')
