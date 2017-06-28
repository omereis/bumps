from json import loads, dumps
# from msgpack import loads, dumps


class Database(object):
    '''
    A redis class for performing the neeeded
    operations on a hash structure
    '''

    def __init__(self, redis_db):
        self.db = redis_db

    def hexists(self, key, value):
        return self.db.hexists(key, value)

    def exists(self, key):
        return self.db.exists(key)

    def hget(self, _hash, key):
        return loads(self.db.hget(_hash, key))

    def get(self, key):
        return self.db.get(key)

    def hget_all(self, _hash):
        return {key: self.get(_hash, key) for key in self.db.hkeys(_hash)}

    def get_all(self):
        return self.db.scan(0)[1]


    def hset(self, _hash, key, value):
        '''
        Attempt to set :value: to an existing :key: in :_hash:,
        and if catching a KeyError exception then start a new :_hash:
        '''

        try:
            value_str = self.get(_hash, key)
            value_str = value_str + ', {}'.format(value)
            self.db.hset(_hash, key, dumps(value_str))
        except Exception as e:
            print('Exception', e)
            self.db.hset(_hash, key, dumps(value))

    def flushall(self):
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
