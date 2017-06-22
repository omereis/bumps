import json, random, datetime, uuid
from flask import jsonify, url_for, redirect
from flask import request as flask_request
from flask_restful import Resource, Api, abort
from flask_jwt_extended import create_access_token
from bumps_flask import app, redis_store, redis_dummy, jwt

# Set RESTful API using flask_restful
api = Api(app)


def create_user_token():
    '''
    Generates a user access token for identification
    '''

    return str(uuid.uuid4())


def register_token(user_token):
    '''
    Generates a resource token for accessing bumps functionality
    based on available resources, priority (...)

    todo: check resources before providing token
    todo: implement an existing, secure token generator
    '''
    jwt_token = create_access_token(identity=user_token)

    # Create the dummy db with key=user_token, value=[user_jobs]
    redis_dummy[user_token] = []
    return jwt_token


class Register(Resource):
    '''
    Assigns JWT token on a per-user_token basis
    User is then expected to send the JWT with each subsequent API call
    (Cookie and/or header based approach?)
    '''
    def post(self):
        # post_data = flask_request.get_json()
        # # Check to see if current user_token is already in DB?
        # user_token = post_data.get('user_token')
        pass

    def get(self):
        pass


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
        if user_token not in redis_dummy.keys():
            abort(404, message="Token {} does not exist".format(user_token))
        return jsonify({user_token: redis_dummy[user_token]})

    def delete(self, user_token, job_id):
        '''
        Deletes a specific job_id for a given user_token
        '''
        del redis_dummy[user_token][job_id]
        return '', 204

    def put(self, user_token, job_id):
        '''
        Updates a job given a token endpoint user_token and the specific job_id
        '''
        redis_dummy[user_token].append(job_id)
        return jsonify({user_token: job_id}), 201


class JobList(Resource):
    def get(self, _format='json'):
        if not _format or _format == 'html':
            return 'You chose HTML.'
        return jsonify(redis_dummy)

    def post(self):
        json_data = flask_request.get_json()
        user_token = json_data['token']
        if user_token not in redis_dummy.keys():
            abort(404, message="Token {} does not exist".format(user_token))
        job_id = json_data['job']
        redis_dummy[user_token].append(job_id)
        return '', 201


@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    '''
    Function wrapped with the ability to add JSON-serializable
    claims to the headers of the soon-to-be-created JWT token
    '''

    return json.dumps({
        'iat': str(datetime.datetime.utcnow()),
        'exp': str(datetime.datetime.utcnow() + datetime.timedelta(minutes=5)),
        'extra_headers': ''
    })


# api.add_resource(resource_tokens, '/token_gen')
# api.add_resource(Register, '/authorize')
api.add_resource(JobList, '/api/jobs', '/api/jobs.<string:_format>')
api.add_resource(Jobs, '/api/jobs/<user_token>')
# api.add_resource(BumpsJob, 'api/bumps')  # DEBUG
