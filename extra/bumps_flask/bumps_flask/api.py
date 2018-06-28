import os
import json
import uuid
import datetime

from flask import jsonify, render_template, flash, \
    make_response, redirect, url_for, send_from_directory, abort
from flask import request as flask_request

from flask_restful import Resource

from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, jwt_required, get_jti,
    get_raw_jwt, unset_jwt_cookies)

from . import app, rdb, jwt, api
from .file_handler import setup_files, clean_job_files
from .misc import get_celery_queue_names, print_debug, get_results_dir
#------------------------------------------------------------------------------
def create_user_token():
    '''
    Generates a user id for identification.
    Works basically like a username
    '''
    return str(uuid.uuid4())[:6]


@jwt_required
def disconnect():
    '''
    Blacklists the user's refresh token
    and unsets the cookies/removes the headers
    '''

    jti = get_raw_jwt()['jti']
    rdb.set(jti, 'true', app.config.get('JWT_ACCESS_TOKEN_EXPIRES'))

    resp = make_response(jsonify(Disconnected=True), 201)
    unset_jwt_cookies(resp)

    return resp

from .misc import print_debug

def create_auth_token(user_token):
    '''
    Creates a JWT token given a UID
    '''

    jwt_id = get_jwt_identity()
    token_str = str(jwt_id)
    jwt_token = create_access_token(identity=user_token)
    # Use the token ID for blacklisting purposes
    jti = access_jti = get_jti(encoded_token=jwt_token)
    # Mark the token as not blacklisted
    x = app.config.get('JWT_ACCESS_TOKEN_EXPIRES')
    try:
        rdb.set(jti, 'false', x)
#        rdb.set(access_jti, 'false', app.config.get('JWT_ACCESS_TOKEN_EXPIRES'))
    except Exception as excp:
        print ("Error: " + str(excp.args))
    jwt_id = get_jwt_identity()
    token_str = str(jwt_id)
    return jwt_token


def register_token(user_token):
    '''
    Generates a resource token for accessing bumps functionality.

    todo: should be based on available resources, priority (...)
    '''

    # Create both the auth and refresh tokens
    access_token = create_auth_token(user_token)
    print("register_token: access created")
    refresh_token = create_refresh_token(identity=user_token)

    # Use the refresh token ID for blacklisting purposes
    refresh_jti = get_jti(encoded_token=refresh_token)
    # Mark the refresh token as not blacklisted
    rdb.set(refresh_jti, 'false', app.config.get('JWT_REFRESH_TOKEN_EXPIRES'))

    return make_response(
        jsonify(refresh_token=refresh_token, access_token=access_token), 201)


def add_job(bumps_job):
    # Add job to the DB
    rdb.hset(bumps_job['user'], bumps_job['_id'], bumps_job)

from .forms import CeleryQueueForm

def process_request_form(request):
    '''
    Parser function for posted web forms coming
    from 'form.py'. Builds a dictonary for slurm
    commands and another for bumps CLI commands
    '''

    response = {'missing_keys': [], 'slurm': {}, 'cli': {}, 'celery' : {}}

    # Catch the CLI related options here
    for form in request:

        if 'optimizer' == form:
            response['cli']['fit'] = request[form]['fitter']

        elif 'steps' == form:
            if request[form]['steps']:
                response['cli']['steps'] = request[form]['steps']

        elif 'burn' == form:
            if request[form]['burn']:
                response['cli']['burn'] = request[form]['burn']

        elif 'email' == form and request[form]['email']:
            response['slurm']['--mail-user'] = request[form]['email']

        elif 'use_celery' == form:
            try:
                response['celery']['use_celery'] = request[form]['use_celery']
            except Exception as e:
                response['celery']['use_celery'] = False

        # Catch the slurm related variables here
        elif 'slurm' == form:
            for key in request[form]:
                if 'limit_node' == key and request[form][key]:
                    response['slurm']['limit_node'] = request[form][key]

                elif 'n_gpus' == key and request[form][key]:
                    response['slurm']['n_gpus'] = request[form][key]

                elif 'jobname' == key and request[form][key]:
                    response['slurm']['job-name'] = request[form][key].replace(
                        ' ', '_')

                elif 'n_cores' == key:
                    response['slurm']['--ntasks'] = request[form][key]

                elif 'mem_per_core' == key:
                    response['slurm']['--mem-per-cpu'] = request[form][key]

                elif 'mem_unit' == key:
                    response['slurm']['mem_unit'] = request[form][key]

                elif 'walltime' == key:
                    response['slurm']['--time'] = request[form][key].strftime(
                        "%H:%M:%S")

                else:
                    response['missing_keys'].append(key)

    return response


# RESTful Interface
def format_response(request, _format):
    if _format == 'html':
        return render_template('results.html', data=request)

    elif _format == 'json':
        return jsonify(request)

    else:
        abort(400)


class Jobs(Resource):
    '''
    Things jobs should be able to do:
        Be submitted
        Be deleted
        Check their status
        Print their information
        Stop their work
    '''

    @jwt_required
    def get(self, user_id=None, job_id=None, action=None, _format='json'):
        request = flask_request.get_json()

        if user_id != get_jwt_identity():
            abort(404)

        # No user_id given, so return every user's jobs
        if not user_id:
            return make_response(format_response(rdb.get_jobs(), _format))

        # No job_id given, so return the user's jobs
        if not job_id:
            return make_response(
                format_response(
                    rdb.hget('users', user_id), _format))

        # No particular action given, so return the specific user job data
        if not action:
            return make_response(format_response(
                rdb.hget(user_id, job_id), _format))

        # A delete was requested, delete the job record and files
        elif action == 'delete':
            # Check if the user actually has a DB entry
            if not rdb.hexists(user_id, job_id):
                abort(404)

            # Remove the corresponding job entry
            rdb.hdel(user_id, job_id)

            # Delete up the job folder and files
            clean_job_files(user_id, job_id)

            # Return result in specified format
            if _format == 'json':
                return jsonify(Deleted=True)

            else:
                flash('Job successfully deleted.')
                return redirect(url_for('dashboard'))

    def post(self):

        # Get the uploaded file
        _file = flask_request.files.get('file')

        # Get the POSTed data
        request = flask_request.form
        # Get the bumps CLI dict and the slurm command dict
        bumps_cmds = json.loads(request.get('bumps_commands'))
        slurm_cmds = json.loads(request.get('slurm_commands'))

        # Format the cmds for compatability moving forward
        cmds = dict(cli=bumps_cmds, slurm=slurm_cmds)
        # Get the specified queue
        queue = request.get('queue')

        # Assuming the UIDs are unique enough, a job_id
        # can be an incremental integer associated with a UID.
        job_id = str(rdb.hlen(request['user']) + 1)

        # Build job directory
#        _dir = os.path.join(app.config.get('UPLOAD_FOLDER'), 'fit_problems', request['user'], 'job' + job_id)
        _dir = get_results_dir (app.config.get('UPLOAD_FOLDER'), job_id)

        # Build job metadata
        job_data = {
            'user': request['user'],
            '_id': job_id,
            'origin': flask_request.remote_addr,
            'directory': _dir,
            'status': 'PENDING',
            'submitted': datetime.datetime.now().strftime('%c')
        }

        # Setup the job files
        setup_files(job_data, cmds, _file, queue)

        # Add job to redis
        add_job(job_data)

        return jsonify(Submitted=True)


class Users(Resource):
    @jwt_required
    def get(self, user_id=None, job_id=None, _file=None,
            interactive=None, _format='.json'):
        if user_id != get_jwt_identity():
            abort(404)

        # Work with a specific user's info
        if user_id:
            # Get current user's specific job
            if job_id:
                _dir = get_results_dir (app.config.get('UPLOAD_FOLDER'), job_id, True)
#                _dir = os.path.join(app.config.get('UPLOAD_FOLDER'), 'fit_problems', user_id, 'job{}'.format(job_id), 'results')
                if not os.path.exists(_dir):
                    return abort(404)

                if _file:
                    # View an html results graph
                    if interactive:
                        return send_from_directory(_dir, _file)

                    else:
                        # Download a generated result file
                        return send_from_directory(
                            _dir, _file, as_attachment=True)

            # Get current user's info
            else:
                if _format == '.html':
                    return '''{}'''.format(rdb.hvals(user_id))

                return jsonify(rdb.hvals(user_id))

        # Get info from every user
        else:
            if _format == '.html':
                return '''{}'''.format(rdb.get_users())

            return jsonify(rdb.get_users())
#------------------------------------------------------------------------------
#from celery import Celery
#------------------------------------------------------------------------------
from flask_jwt_extended import set_access_cookies, set_refresh_cookies
@app.route('/api/celery', methods=['GET', 'POST'])
def check_celery():
#    if appCeleryBumps == None:
#        appCeleryBumps = Celery('bumps', broker='amqp://rabbit-server', backend='redis://redis-server')
    msgAllQueues = ""
    inspect = None
    try:
        queues = get_celery_queue_names()
        msgAllQueues = ", ".join(queues)
        msg = "Celery imported"
    except Exception as e:
        msg = "Error: " + str(e.args)
        msg1 = "basa"
    flash ("Celery Status: " + msg)
    flash ("Qeues Names: " + msgAllQueues)
    user_token = create_user_token()
    render_template('tokenizer.html')

    # Associate an auth JWT and a refresh JWT to the UID
    try :
        rt = register_token(user_token)
        x = register_token(user_token).get_data()
        resp = json.loads(x)
#        resp = json.loads(register_token(user_token).get_data())
        jwt_token = resp['access_token']
        refresh_token = resp['refresh_token']
    except Exception as excp:
        print ("Error: " + str(excp.args))

    # Working with the client interface
    if flask_request.method == 'POST':
        flash("POST")
        response = jsonify(
            uid=user_token,
            auth_token=jwt_token,
            refresh_token=refresh_token)

    # Working with the web page interface
    else:
        flash("GET")
        # Build the response object to a template
#        response = make_response(
#            render_template('dashboard.html', token=user_token))
        response = make_response(
            render_template('tokenizer.html', token=user_token))

    # Bundle the JWT cookies into the response object
    set_access_cookies(response, jwt_token)
    set_refresh_cookies(response, refresh_token)
    return response
#------------------------------------------------------------------------------
from celery_bumps import tasks
#from celery_bumps import tasks
#import run_cel
#import os
#------------------------------------------------------------------------------
@app.route('/api/celery_test_add', methods=['GET', 'POST'])
def api_celery_add():
    try:
#        if (appCeleryBumps == None):
#            appCeleryBumps = Celery('bumps', broker='amqp://rabbit-server', backend='redis://redis-server')
#        res = tasks.add.delay(4,5)
        print_debug ("Current directory is: " + os.getcwd())
        res = tasks.add(4,5)
        print_debug("add(4,5):" + str(res))
#        run_cel.run_celery_bumps()
        tEnd = tStart = time.time()
        tDelta = tEnd - tStart
        resCelery = tasks.run_bumps1.delay('/home/bumps_user/bumps_flask/test/cf1.py')
        fReady = resCelery.ready()
        while ((fReady == False) and (tDelta < 10)):
            fReady = resCelery.ready()
            tDelta = time.time() - tStart
        if (resCelery.ready()):
            output = str(resCelery.get()) + ", Performance time: " + str(tDelta)
        else:
            output = "Timeout :-("
        print_debug("add.delay(4,5): " + str(resCelery.get()))
    except Exception as e:
        print_debug("Error:\n" + str(e))
    flash ("Results: " + output)
    response = make_response(render_template('tokenizer.html', output=output))
    return (response)
#------------------------------------------------------------------------------
import time
#------------------------------------------------------------------------------
def get_celery_worker_status():
    ERROR_KEY = "ERROR"
    try:
        from celery.task.control import inspect
        insp = inspect()
        d = insp.stats()
        if not d:
            d = { ERROR_KEY: 'No running Celery workers were found.' }
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'
        d = { ERROR_KEY: msg }
    except ImportError as e:
        d = { ERROR_KEY: str(e)}
    return d
    
#------------------------------------------------------------------------------



api.add_resource(
    Jobs,
    '/api/jobs',
    '/api/jobs/<string:user_id><string:_format>',
    '/api/jobs/<string:user_id>/job<int:job_id><string:_format>',
    '/api/jobs/<string:user_id>/job<int:job_id>/<string:action>.<string:_format>',
    '/api/jobs<string:_format>')


api.add_resource(
    Users,
    '/api/users',
    '/api/users<string:_format>',
    '/api/users/<string:user_id><string:_format>',
    '/api/users/<string:user_id>/job<int:job_id><string:_format>',
    '/api/users/<string:user_id>/job<int:job_id>/<string:_file>',
    '/api/users/<string:user_id>/job<int:job_id>/<string:_file>/<string:interactive>')
