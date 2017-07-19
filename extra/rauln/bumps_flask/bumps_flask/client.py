from __future__ import print_function
import sys
from json import dumps, loads
from requests import post, get
from requests.cookies import RequestsCookieJar
# import .api
# from bumps import FitDriver

if len(sys.argv) > 1:
    HOST = sys.argv[1]
else:
    HOST = 'http://localhost:5000'  # DEBUG


class Connection(object):
    def __init__(self, host=HOST):
        self.endpoint = host + '/api/'
        self.jar = RequestsCookieJar()
        self.headers = None
        self.uid = None

        r = self.login()

        if r is True:
            print('Logged in as token {}!'.format(self.uid))

        else:
            print('Error connecting, server returned: ', r)

    def login(self):
        '''
        Connects to the web service, the UID and
        saves the JWT in a cookie (or a header).
        Returns true for a succesful connection,
        false otherwise.
        '''
        r = post(self.endpoint + 'register')
        try:
            self.uid = r.json()['uid']
            self.jar.set(
                'access_token_cookie',
                r.cookies['access_token_cookie'],
                domain=HOST)

        except Exception as e:
            return e

        return True


    def logout(self):
        '''
        Disconnect from the web service,
        clear cookies (or headers).
        Return true for a succesful disconnect,
        false otherwise
        '''

        r = get(self.endpoint + 'logout', params={'redirect': 0})
        return r.json()


    def get_job(self, job_id=None, _format=None):
        '''
        Returns jobs given a job_id
        Formats available = json (default), html
        '''

        self.job_id = job_id
        self._format = _format

        resource = 'jobs'

        if self.job_id:
            if self._format:
                resource += '/{}.{}'.format(self.job_id, self._format)
            else:
                resource += '/{}'.format(self.job_id)
        else:
            if self._format:
                resource += '.{}'.format(self._format)

        r = get(self.endpoint + resource, cookies=self.jar)
        return r.json()


    # def format_slurm_commands(ntasks=, ):

    def post_job(self, job_file, bumps_cmds, slurm_cmds, queue='slurm'):
        '''
        Posts a job file in the current working
        directory to the server and return the
        server's response
        '''

        r = post(self.endpoint + 'jobs',
                    files={'file': open(job_file, 'rb')},
                    data={
                        'bumps_commands': dumps(bumps_cmds),
                        'slurm_commands': dumps(slurm_cmds),
                        'user': self.uid,
                        'queue': queue},
                    cookies=self.jar)
        print(r.text)

    def current_user(self):
        return self.uid

    def get_user(self):
        pass

    def post_user(self):
        pass

    def list_jobs(self):
        r = get(self.endpoint + 'jobs')
        return r.json()

    def get_job_info(self, job_id):
        pass

    def get_job_status(self, job_id):
        pass

    def get_job_results(self, job_id):
        pass

    def stop_job(self, job_id):
        pass

    def delete_job(self, job_id):
        pass
