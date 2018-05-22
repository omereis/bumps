from __future__ import absolute_import, unicode_literals
from celery import Celery
from . import app

try:
    REDIS_SERVER=os.environ['REDIS_SERVER']
except:
    REDIS_SERVER='bumps_redis'

try:
    f = open("oe_debug.txt", "a+")
    f.write("\n")
    f.write("'REDIS_SERVER'=" + REDIS_SERVER + "\n")
    f.close()
except Exception as excp:
    print ("Error: " + str(excp.args))

app.config['BROKER_URL']  = 'amqp://rabbit-server'
app.config['BACKEND_URL'] = 'redis://' + REDIS_SERVER

celery = Celery(app.name, broker=app.config['BROKER_URL'], backend=app.config['BACKEND_URL'])
celery.conf.update(app.config)
#appCelery = Celery('bumps',
#             broker='amqp://rabbit-server',
#             backend='redis://' + REDIS_SERVER,
#             backend='redis://redis-server',
#             include=['bumps_flask.run_job'])
try:
    f = open("oe_debug.txt", "a+")
    f.write("\n")
    f.write("Celery created" + "\n")
    f.close()
except Exception as excp:
    print ("Error: " + str(excp.args))

if __name__ == '__main__':
    celery.start()
    
@celery.task
def add(n1, n2)
    return (n1 + n2)