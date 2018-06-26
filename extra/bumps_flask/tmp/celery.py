from __future__ import absolute_import, unicode_literals
from celery import Celery

appCelery = Celery('bumps', broker='amqp://rabbit-server', backend='redis://redis-server')
#app = Celery('bumps', broker='amqp://rabbit-server', backend='redis://p858547') works
#app = Celery('bumps', broker='amqp://p858547', backend='redis://p858547') doesn't work

# Optional configuration, see the application user guide.
appCelery.conf.update(result_expires=3600,)

#if __name__ == '__main__':
#app.start()
if __name__ == '__main__':
    appCelery.start()
    f = open("oe_debug.txt", "a+")
    f.write("app started\n")
    f.close()
