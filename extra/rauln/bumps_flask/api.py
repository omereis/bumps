#!/usr/bin/env python
import json, random
from flask import jsonify
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse, abort
from bumps_flask import app, redis_store, redis_dummy

# Set RESTful API using flask_restful
api = Api(app)

def generate_user_token():
    '''
    Generates a resource access token for logging in
    '''
    candidate = ''.join([random.choice('aeiou12345') for i in xrange(5)])
    return candidate

class resource_tokens(Resource):
    def get(self):
        login_token = generate_user_token()
        return json.dumps({'token_id': login_token})

class Jobs(Resource):
    def get(self, user_token):
        if not user_token in redis_dummy.keys():
            abort(404, message="User token {} does not exist".format(user_token))
        return json.dumps({user_token:redis_dummy[user_token]})

    def delete(self, user_token, job_id):
        del redis_dummy[user_token][job_id]
        return '', 204

    def put(self, user_token, job_id):
        redis_dummy[user_token].append(job_id)
        return json.dumps({user_token:job_id}), 201

class JobList(Resource):
    def get(self):
        return redis_dummy

    def post(self):
        user_token = flask_request.form['token']
        if not user_token in redis_dummy.keys():
            abort(404, message="User token {} does not exist".format(user_token))
        job_id = flask_request.form['job_id']
        redis_dummy[user_token].append(job_id)


api.add_resource(resource_tokens, '/token_gen')
api.add_resource(JobList, '/jobs')
api.add_resource(Jobs, '/jobs/<user_token>')
