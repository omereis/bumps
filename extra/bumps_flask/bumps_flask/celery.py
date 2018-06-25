from __future__ import absolute_import, unicode_literals
from celery import Celery

app = Celery('bumps', broker='amqp://rabbit-server', backend='redis://redis-server')
#app = Celery('bumps', broker='amqp://rabbit-server', backend='redis://p858547') works
#app = Celery('bumps', broker='amqp://p858547', backend='redis://p858547') doesn't work

# Optional configuration, see the application user guide.
app.conf.update(result_expires=3600,)

#if __name__ == '__main__':
#    app.start()
