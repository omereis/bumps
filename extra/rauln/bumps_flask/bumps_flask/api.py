import json
import random
import datetime
import uuid
import os
from flask import jsonify, url_for, redirect, render_template, \
    make_response, send_from_directory, abort
from flask import request as flask_request
from flask_restful import Resource, abort
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, jwt_required, get_jti,
    get_raw_jwt, unset_jwt_cookies)

from . import app, rdb, jwt, api
from .file_handler import setup_files

# def check_available_resources():
#     pass

# def create_user_token(resources):
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

def create_auth_token(user_token):
    '''
    Creates a JWT token given a UID
    '''

    jwt_token = create_access_token(identity=user_token)

    # Use the token ID for blacklisting purposes
    access_jti = get_jti(encoded_token=jwt_token)
    # Mark the token as not blacklisted
    rdb.set(access_jti, 'false', app.config.get('JWT_ACCESS_TOKEN_EXPIRES'))

    return jwt_token


def register_token(user_token):
    '''
    Generates a resource token for accessing bumps functionality
    based on available resources, priority (...)

    todo: check resources before providing token
    '''

    # Create both the auth and refresh tokens
    access_token = create_auth_token(user_token)
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


# TODO: Clean up
def process_request_form(request):
    '''
    Parser function for posteed webforms coming
    from 'form.py'
    '''
    response = {'missing_keys': [], 'slurm': {}, 'cli': {}}
    for form in request:
        if 'optimizer' == form:
            response['cli']['fit'] = request[form]['fitter']

        elif 'steps' == form:
            if request[form]['steps']:
                response['cli']['steps'] = request[form]['steps']

        elif 'email' == form and request[form]['email']:
            response['slurm']['--mail-user'] = request[form]['email']

        # Catch the slurm related variables here
        elif 'slurm' == form:
            for key in request[form]:
                # Check if the optional parameters are actually there, else
                # don't include them
                if 'limit_node' == key and request[form][key]:
                    response['slurm']['limit_node'] = request[form][key]

                elif 'n_gpus' == key and request[form][key]:
                    response['slurm']['n_gpus'] = request[form][key]

                elif 'jobname' == key and request[form][key]:
                    response['slurm']['job-name'] = request[form][key]

                elif 'n_cores' == key:
                    response['slurm']['--ntasks'] = request[form][key]

                elif 'mem_per_core' == key:
                    response['slurm']['--mem-per-cpu'] = request[form][key]

                elif 'mem_unit' == key:
                    response['slurm']['mem_unit'] = request[form][key]

                elif 'walltime' == key:
                    response['slurm']['--time'] = str(request[form][key].time)

                else:
                    response['missing_keys'].append(key)

    return response

##### RESTful Interface
def format_response(request, _format):
    if _format == '.html':
        return render_template('results.html', data=request)

    elif _format == '.json':
        return jsonify(request)

    else:
        abort(400)


class Jobs(Resource):
    '''
    Post a job, get a job!
    Things jobs should be able to do:
        Be submitted
        Be deleted
        Check their status
        Print their information
        Stop their work
    '''

    def get(self, user_id=None, job_id=None, _format='.json'):
        # request = flask_request.get_json()
        # if user_id != get_jwt_identity():
        #     abort(404)
        if not user_id:
            return make_response(format_response(rdb.get_jobs(), _format))

        if not job_id:
            return make_response(
                format_response(
                    rdb.hget(
                        'users',
                        user_id),
                    _format))

        return make_response(format_response(
                rdb.hget(user_id, job_id), _format))

    # TODO: Implement POSTing jobs
    def post(self):
        request = flask_request.get_json()

        _file = request['file']

        # Build job directory
        _dir = os.path.join(app.config.get('UPLOAD_FOLDER'),
                            'fit_problems', request['user'], 'job' + job_id)

        job_data = {
            'user': request['user'],
            '_id': str(rdb.hlen(request['user']) + 1),
            'directory': _dir,
            'origin': flask_request.remote_addr,
            'status': 'PENDING'
        }

        queue = job_data['queue']

        setup_files(job_data, queue,
                    )

        add_job(bumps_payload)

    def delete(self, job_id):
        pass


class Users(Resource):
    def get(self, user_id=None, job_id=None, _file=None, _format='.json'):
        # Work with a specific user's info
        if user_id:
            # Get current user's specific job
            if job_id:
                _dir = os.path.join(app.config.get('UPLOAD_FOLDER'),
                                    'fit_problems', user_id,
                                    'job{}'.format(job_id), 'results')
                if not os.path.exists(_dir):
                    return abort(404)

                # Download a generated result file
                if _file:
                    print('Sending ' + _file + ' from ' + _dir)
                    return send_from_directory(_dir, _file, as_attachment=True)

                # View an html results graph
                else:
                    if _format == '.html':
                        filebase = rdb.hget(user_id, job_id)['filebase']
                        return send_from_directory(
                            _dir, '{}-model.html'.format(filebase))

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

    # TODO: Implement POSTing (creating) users
    def post(self):
        # # Add jobs to users
        # json_data = flask_request.get_json()
        # try:
        #     user = User(user_token=json_data['user_token'])
        # except KeyError:
        #     return make_response(json.dumps(
        #         {'error': 'not a proper job definition'}), 400)
        #
        # add_job(json_data)
        pass


# TODO: Change from string format to UUID format
api.add_resource(Jobs,
                 '/api/jobs',
                 '/api/jobs/<string:user_id><string:_format>',
                 '/api/jobs/<string:user_id>/job<int:job_id><string:_format>',
                 '/api/jobs<string:_format>')


# TODO: Change from string format to UUID format
api.add_resource(Users,
                 '/api/users',
                 '/api/users<string:_format>',
                 '/api/users/<string:user_id><string:_format>',
                 '/api/users/<string:user_id>/job<int:job_id><string:_format>',
                 '/api/users/<string:user_id>/job<int:job_id>/<string:_file>'
                 )
