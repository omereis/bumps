from json import dumps, loads
from requests import post, get
from requests.cookies import RequestsCookieJar
# import .api

HOST = 'http://localhost:5000'  # DEBUG

class Connection(object):
    def __init__(self, host=None):
        self.endpoint = HOST
        self.jar = RequestsCookieJar()
        self.headers = None
        self.uid = None

    def connect(self):
        r = post(HOST + '/register')
        try:
            self.uid = r.json()['uid']
            self.jar.set('access_token_cookie', r.cookies['access_token_cookie'], domain=HOST)
        except:
            return False

        return True


    def get_job(self, jod_id=None, _format=None):
        resource = 'jobs'

        if job_id:
            if _format:
                resource += '/{}.{}'.format(job_id, _format)
            else:
                resource += '/{}'.format(jod_id)
        else:
            if _format:
                resource += '.{}'.format(_format)

        return loads(get(endpoint + resource, cookies=self.jar))


    def post_job(self, job):
        r = post(HOST + '/jobs', json=job, cookies=self.jar)
        return r.json()


    def get_user(self):
        pass


    def post_user(self):
        pass


    def list_jobs(self):
        pass


    def get_job_info(self, jobid):
        pass


    def get_job_status(self, jobid):
        pass


    def get_job_results(self, jobid):
        pass


    def wait_for_job(self):
        pass


    def stop_job(self, jobid):
        pass

        
    def delete_job(self, jobid):
        pass
