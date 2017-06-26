import json, random, datetime, uuid
import msgpack as msg
from flask import jsonify, url_for, redirect, render_template
from flask import request as flask_request
from flask_restful import Resource, Api, abort
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required
from bumps_flask import app, rdb, jwt

# Set RESTful API using flask_restful
api = Api(app)

def create_user_token():
    '''
    Generates a user access token for identification
    '''

    return str(uuid.uuid4())


def register_token(user_token, auth_token, refresh_token=False):
    '''
    Generates a resource token for accessing bumps functionality
    based on available resources, priority (...)

    todo: check resources before providing token
    todo: implement an existing, secure token generator
    '''

    if auth_token:
        jwt_id = create_access_token(identity=user_token)
        rdb.set('user_tokens', user_token, json.dumps(''))
        return jwt_id

    if refresh_token:
        refresh_id = create_refresh_token(identity=user_token)
        return refresh_id

    return Exception


# Move this to database.py?
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
        if not rdb.exists('user_tokens', user_token):
            abort(404, message="Token {} does not exist".format(user_token))
        return jsonify({user_token: rdb.get('user_tokens', user_token)})

    def delete(self, user_token, job_id):
        '''
        Deletes a specific job_id for a given user_token
        '''
        # redis_store.hdel()
        return '', 204

    def put(self, user_token, job_id):
        '''
        Updates a job given a token endpoint user_token and the specific job_id
        '''
        # redis_store.hset('user_tokens', user_token, ...)
        return jsonify({user_token: job_id}), 201


class JobList(Resource):
    def get(self, _hash='user_tokens', _format='json'):
        if not _format or _format == 'html':
            return ', '.join([rdb.get(_hash, user_token) for user_token in rdb.get_all(_hash).values()])
        return jsonify(rdb.get_all(_hash))


    def post(self):
        json_data = flask_request.get_json()
        user_token = json_data['token']
        if not rdb.exists('user_tokens', user_token):
            abort(404, message="Token {} does not exist".format(user_token))
        job_id = json_data['job']
        rdb.set('user_tokens', user_token, job_id)
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
