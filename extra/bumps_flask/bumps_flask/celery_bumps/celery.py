from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
from .oe_debug import print_debug

def get_env_value (env_var, default_value):
    try:
        env_value = os.environ[env_var]
    except:
        env_value = default_value
    return env_value

backend_url = "redis://" + get_env_value ('BACKEND_SERVER', 'ncnr-r9nano')
broker_url   = "amqp://" + get_env_value ('BROKER_SERVER', 'ncnr-r9nano')
app = Celery('bumps', broker=broker_url, backend=backend_url)
#app = Celery('bumps', broker='amqp://ncnr-r9nano', backend=backend_url)
#app = Celery('bumps', broker='amqp://ncnr-r9nano', backend='redis://ncnr-r9nano')

#app = Celery('bumps', broker='amqp://rabbit-server', backend='redis://redis-server')
#app = Celery('bumps', broker='amqp://rabbit-server', backend='redis://p858547') works
#app = Celery('bumps', broker='amqp://p858547', backend='redis://p858547') doesn't work

# Optional configuration, see the application user guide.
app.conf.update(result_expires=3600,)

if __name__ == '__main__':
    app.start()
