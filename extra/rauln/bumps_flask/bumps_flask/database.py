from json import loads, dumps


class Database(object):
    '''
    A redis class for performing the neeeded
    operations on a hash structure
    '''

    def __init__(self, redis_db):
        self.db = redis_db

    ##################
    # Hash commands
    ##################
    def hexists(self, key, value):
        return self.db.hexists(key, value)

    def hget(self, _hash, key):
        if self.db.hget(_hash, key):
            return loads(self.db.hget(_hash, key))

        return None

    def hget_all(self, _hash):
        return {key: self.get(_hash, key) for key in self.db.hkeys(_hash)}

    def hset(self, _hash, key, value):
        '''
        Attempt to set value to an existing json serialized
        key list in _hash. If the list is empty, then initialize
        it with the current value
        '''

        key_list = self.hget(_hash, key)
        if key_list:
            key_list.append(value)
            self.db.hset(_hash, key, dumps(key_list))
        else:
            self.db.hset(_hash, key, dumps([value]))

    def hincr(self, _hash, key, n):
        self.db.hincrby(_hash, key, n)

    ##################
    # String commands
    ##################

    def exists(self, key):
        return self.db.exists(key)

    def get(self, key):
        return self.db.get(key)

    ##################
    # Set commands
    ##################

    def sadd(self, _set, value):
        return self.db.sadd(_set, value)

    def sismember(self, _set, value):
        return self.db.sismember(_set, value)

    ##################
    # Admin
    ##################

    def get_all(self):
        return self.db.scan(0)[1]

    def get_jobs(self):
        r_list = []
        for db in self.get_all():
            if 'users' not in db:
                r_list.append(db)
        return r_list

    def flushall(self):  # DEV
        self.db.flushall()


class User(object):
    def __init__(self, user_token=None, jobs=[]):
        self.user_token = user_token
        self.jobs = jobs


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
