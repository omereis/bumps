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
        return {key: self.hget(_hash, key) for key in self.db.hkeys(_hash)}

    def hset(self, _hash, key, value):
        '''
        Attempt to set value to an existing json serialized
        key list in _hash. If the list is empty, then initialize
        it with the current value
        '''

        # Catch the first pass where the list is not json
        try:
            key_list = self.hget(_hash, key)
            key_list.append(value)
            self.db.hset(_hash, key, dumps(key_list))
        except BaseException:
            self.db.hset(_hash, key, dumps([]))

    def hincr(self, _hash, key, n):
        self.db.hincrby(_hash, key, n)

    def hkeys(self, _hash):
        return self.db.hkeys(_hash)

    ##################
    # String commands
    ##################

    def set(self, key, value, expiration=None):
        if expiration:
            self.db.set(key, value, expiration)
        else:
            self.db.set(key, value)

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

    def ping(self):
        return self.db.ping()

    def get_all(self):
        return self.db.scan(0)[1]

    def get_jobs(self):
        return self.db.hkeys('jobs')

    def get_users(self):
        return self.db.hkeys('users')

    def flushall(self):  # DEV
        self.db.flushall()


class BumpsJob(object):
    '''
    Possible job status: PENDING, ACTIVE, CANCEL, COMPLETE, ERROR
    '''

    def __init__(self, _id=None, name='', origin='', date=None, start=None, stop=None,
                 priority=0.0, notify='', status='PENDING'):

        self._id = _id
        self.name = name
        self.origin = origin
        self.date = date
        self.start = start
        self.stop = stop
        self.priority = priority
        self.notify = notify
        self.status = status
