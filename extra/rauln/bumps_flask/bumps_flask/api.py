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
from . import app, rdb, jwt

# Set RESTful API using flask_restful
api = Api(app)


def create_user_token():
    '''
    Generates a user access token for identification
    '''

    return str(uuid.uuid4()).split('-')[0]


def register_token(user_token, auth_token, refresh_token=False):
    '''
    Generates a resource token for accessing bumps functionality
    based on available resources, priority (...)

    todo: check resources before providing token
    todo: implement an existing, secure token generator
    '''

    if auth_token:
        jwt_id = create_access_token(identity=user_token)
        rdb.sadd('users', user_token)
        return jwt_id

    if refresh_token:
        refresh_id = create_refresh_token(identity=user_token)
        return refresh_id

    return Exception


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

    rdb.hset(user, 'job_files', filename)
    rdb.hincr(user, 'job_n', 1)

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
    Things jobs should be able to do:
        Be submitted
        Be deleted
        Check their status
        Print their information
        Stop their work
    '''

    def get(self, user_token):
        '''
        Returns the jobs associated with the specified user_token
        '''
        if not rdb.sismember('users', user_token):
            abort(404, message="Token {} does not exist".format(user_token))
        return jsonify({user_token: rdb.hget(user_token, 'jobs')})

    def delete(self, user_token, job_id):
        '''
        Deletes a specific job_id for a given user_token
        '''
        return '', 204

    def put(self, user_token, job_id):
        '''
        Updates a job given a token endpoint user_token and the specific job_id
        '''
        # return jsonify({user_token: job_id}), 201


class JobList(Resource):
    def get(self, _format='json'):

        r_dict = {}
        for user in rdb.get_jobs():
            r_dict[user] = rdb.hget(user, 'job_n')

        if _format == 'html':
            return '''{}'''.format(r_dict)
        return jsonify(r_dict)

    def post(self):
        json_data = flask_request.get_json()
        user_token = json_data['token']
        if not rdb.sismember('users', user_token):
            abort(404, message="Token {} does not exist".format(user_token))
        job_id = json_data['job']
        redb.hset(user_token, 'jobs', job_id)
        return '', 201


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


api.add_resource(JobList, '/api/jobs', '/api/jobs.<string:_format>')
api.add_resource(Jobs, '/api/jobs/<user_token>')
