from app import app, redis_store, redis_dummy

class User(object):
    def __init__(self, user_token=None):
        self.user_token = user_token


class BumpsJob(object):
    def __init__(self, id=None, name='', origin='', start=None, stop=None,
                 priority=0.0, notify='', status='PENDING', location=''):

        self.id = id
        self.name = name
        self.origin = origin
        self.start = start
        self.stop = stop
        self.priority = priority
        self.notify = notify
        self.status = status
        self.location = location

    def report_status(self):
        pass
