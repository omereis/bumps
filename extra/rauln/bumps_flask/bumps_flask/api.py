import json
import random
import datetime
import uuid
import os
from werkzeug.utils import secure_filename
from flask import jsonify, url_for, redirect, render_template
from flask import request as flask_request
from flask_restful import Resource, Api, abort
from flask_jwt_extended import create_access_token, create_refresh_token

from .database import User, BumpsJob
from . import app, rdb, jwt


# Set RESTful API using flask_restful
api = Api(app)


def create_user_token():
    '''
    Generates a user access token for identification
    '''

    return str(uuid.uuid4()).split('-')[0]


def register_token(user_token):
    '''
    Generates a resource token for accessing bumps functionality
    based on available resources, priority (...)

    todo: check resources before providing token
    todo: implement an existing, secure token generator
    '''


    jwt_id = create_access_token(identity=user_token)
    user = User(user_token=user_token)
    rdb.hset('users', user_token, json.dumps(user.__dict__))
    return jwt_id


def setup_job(user, data=None, filename=None, _file=None):
    # Convenient variable
    folder = os.path.join(
        app.config.get('UPLOAD_FOLDER'),
        'fit_problems',
        user)

    # Make sure the upload folder exists beforehand
    if not os.path.exists(folder):
        os.makedirs(folder)

    # If an upload file was provided...
    if _file:
        # Get the file form data
        f = _file
        filename = _file.filename
        # Sanitize the filename
        filename = secure_filename(filename)
        # Save the uploaded file
        f.save(os.path.join(folder, filename))

    else:
        # Sanitize the filename
        filename = secure_filename(filename)
        # Create the file to prepare it for the queue
        with open(os.path.join(folder, filename), 'w') as f:
            f.write(data)

    return os.path.join(folder, filename)


def process_request_form(request):
    response = {'missing_keys': [], 'slurm': {}, 'cli': {}, 'line': {}}
    for form in request:

        if 'optimizer' == form:
            response['cli']['fit'] = request[form]['fitter']

        elif 'steps' == form:
            response['cli']['steps'] = request[form]['steps']

        elif 'email' == form and request[form]:
            response['slurm']['--mail-user'] = request[form]

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

        # Catch the line-fitting related variables here
        elif 'line' == form:
            response['line']['x'] = [
                int(float(i)) for i in request[form]['x'].strip().split(',')]
            response['line']['y'] = [
                float(i) for i in request[form]['y'].strip().split(',')]
            response['line']['dy'] = [
                float(i) for i in request[form]['dy'].strip().split(',')]
            response['line']['m'] = request[form]['m']
            response['line']['b'] = request[form]['b']

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
    def get(self, job_id=None, _format='json'):
        if job_id:
            if _format == 'html':
                return '''{}'''.format(rbd.hget('jobs', job_id))

            return jsonify(rdb.hget('jobs', job_id))

        else:
            if _format == 'html':
                return '''{}'''.format(rbd.get_jobs())

            return jsonify(rdb.get_jobs())

    def post(self):
        json_data = flask_request.get_json()
        try:
            job = BumpsJob(
                _id=random.randint(0, 100),  # Debug
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


class Users(Resource):
    def get(self, user_id=None, _format='json'):
        if user_id:
            if _format == 'html':
                return '''{}'''.format(rdb.hget('users', user_id))

            return jsonify(rdb.hget('users', user_id))

        else:
            if _format == 'html':
                return '''{}'''.format(rdb.get_users())

            return jsonify(rdb.get_users())

    def post(self):
        json_data = flask_request.get_json()
        try:
            user = User (user_token=json_data['user_token'])
        except KeyError:
            return make_response(json.dumps({'error':'not a proper job definition'}), 400)

        rdb.hset('users', user_token, json.dumps(user.get_job()))


@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    '''
    Function wrapped with the ability to add JSON-serializable
    claims to the headers of the soon-to-be-created JWT token
    '''

    return json.dumps({
        'iat': str(datetime.datetime.utcnow()),
        'exp': str(datetime.datetime.utcnow() + datetime.timedelta(minutes=0, seconds=10)),
        'extra_headers': ''
    })


api.add_resource(Jobs, '/api/jobs', '/api/jobs.<string:_format>', '/api/jobs/<int:job_id>.<string:_format>')
api.add_resource(Users, '/api/users', '/api/users.<string:_format>', '/api/users/<string:user_id>.<string:_format>')
