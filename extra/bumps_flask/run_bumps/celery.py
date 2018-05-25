from __future__ import absolute_import, unicode_literals
from celery import Celery

try:
    BACKEND_SERVER=os.environ['BACKEND_SERVER']
except:
    BACKEND_SERVER='bumps_redis'

try:
    BROKER_SERVER=os.environ['BROKER_SERVER']
except:
    BROKER_SERVER='rabbit-server'

app = Celery('bumps_runner',
             broker='amqp://' + BROKER_SERVER,
             backend='redis://' + BACKEND_SERVER)
#             include=['tasks'])
#             broker='amqp://rabbit-server',
#            backend='redis://redis-server')

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()
