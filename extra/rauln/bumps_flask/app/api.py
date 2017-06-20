import json
import random
from flask import request as flask_request
from flask_restful import Resource, Api, abort
from app import app, redis_store, redis_dummy, auth

# Set RESTful API using flask_restful
api = Api(app)


def generate_user_token():
    '''
    Generates a resource access token for logging in
    '''
    candidate = ''.join([random.choice('aeiou12345') for i in xrange(5)])
    return candidate


# class resource_tokens(Resource):
#     def get(self):
#         login_token = generate_user_token()
#         return json.dumps({'token_id': login_token})


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
        return json.dumps({user_token: redis_dummy[user_token]})

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
        return json.dumps({user_token: job_id}), 201


class JobList(Resource):
    def get(self):
        return [[job for job in redis_dummy[token]] for token in redis_dummy.keys()]

    def post(self):
        user_token = flask_request.form['token']
        if user_token not in redis_dummy.keys():
            abort(404, message="Token {} does not exist".format(user_token))
        job_id = flask_request.form['job_id']
        redis_dummy[user_token].append(job_id)


# api.add_resource(resource_tokens, '/token_gen')
api.add_resource(JobList, '/jobs')
api.add_resource(Jobs, '/jobs/<user_token>')
