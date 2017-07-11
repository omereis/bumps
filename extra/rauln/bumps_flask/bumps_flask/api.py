import json
import random
import datetime
import uuid
import os
from flask import jsonify, url_for, redirect, render_template, make_response
from flask import request as flask_request
from flask_restful import Resource, Api, abort
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, jwt_required, get_jti)

from .database import BumpsJob
from .file_handler import build_slurm_script
from . import app, rdb, jwt


# Set RESTful API using flask_restful
api = Api(app)


def create_user_token():
    '''
    Generates a user id for identification.
    Works basically like a username
    '''

    return str(uuid.uuid4())[:6]


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


    # If there is not already a list, it means there is a NoneType
    if type(rdb.hget('users', user_token)) != type([]):
        rdb.hset('users', user_token, [])

    return make_response(jsonify(refresh_token=refresh_token, access_token=access_token), 201)

def add_job(user, job):
    rdb.hset('users', user, job)  # DEBUG


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
            response['cli']['steps'] = request[form]['steps']

        elif 'email' == form and request[form]['email']:
            print('Email: ', request[form]['email'])
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
                    response['slurm']['jobname'] = request[form][key]

                elif 'n_cores' == key:
                    response['slurm']['--ntasks'] = request[form][key]

                elif 'mem_per_core' == key:
                    response['slurm']['--mem-per-cpu'] = request[form][key]

                elif 'mem_unit' == key:
                    response['slurm']['mem_unit'] = request[form][key]

                elif 'walltime' == key:
                    response['slurm']['--time'] = request[form][key]

                else:
                    response['missing_keys'].append(key)

    return response


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
    @jwt_required
    def get(self, job_id=None, _format='.json'):
        if job_id:
            if _format == '.html':
                return '''{}'''.format(rdb.hget('jobs', job_id))

            return jsonify(rdb.hget('jobs', job_id))

        else:
            if _format == '.html':
                return '''{}'''.format(rdb.get_jobs())

            return jsonify(rdb.get_jobs())

    def post(self):
        json_data = flask_request.get_json()
        try:
            job = BumpsJob(
                _id=random.randint(0, 100),  # DEBUG
                name=json_data['name'],
                origin=flask_request.remote_addr,
                date=str(datetime.datetime.utcnow()),
                #priority = get_priority(),
                #notify= get_notify(),?
                )

        except KeyError:
            return make_response(json.dumps({'error':'not a proper job definition'}), 400)

        rdb.hset('jobs', _id, json.dumps(job.__dict__))

        return jsonify({'job_data': job.__dict__})


    def delete(self, job_id):
        pass


class Users(Resource):
    def get(self, user_id=None, _format='.json'):
        if user_id:
            if _format == '.html':
                return '''{}'''.format(rdb.hget('users', user_id))

            return jsonify(rdb.hget('users', user_id))

        else:
            if _format == '.html':
                return '''{}'''.format(rdb.get_users())

            return jsonify(rdb.get_users())

    def post(self):
        # Add jobs to users
        json_data = flask_request.get_json()
        try:
            user = User(user_token=json_data['user_token'])
        except KeyError:
            return make_response(json.dumps({'error':'not a proper job definition'}), 400)

        rdb.hset('users', user_token, json.dumps(user.get_job()))

# @jwt.user_claims_loader
# def add_claims_to_jwt(identity):
#     '''
#     Function wrapped with the ability to add JSON-serializable
#     claims to the headers of the soon-to-be-created JWT token
#     '''
#
#     return json.dumps({
#         'iat': str(datetime.datetime.utcnow()),
#         'exp': str(datetime.datetime.utcnow() + datetime.timedelta(minutes=0, seconds=10)),
#         'extra_headers': ''
#     })


api.add_resource(Jobs, '/api/jobs', '/api/jobs<string:_format>', '/api/jobs/<string:job_id><string:_format>')
api.add_resource(Users, '/api/users', '/api/users<string:_format>', '/api/users/<string:user_id><string:_format>')
