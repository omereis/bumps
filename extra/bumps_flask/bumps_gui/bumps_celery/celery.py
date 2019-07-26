from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.signals import task_postrun

app = Celery('bumps_celery',
             broker='amqp://rabbit-server',
             backend='redis://redis-server',
             include=['bumps_celery.tasks'])

def celery_post_run(task, **kwargs):
    print(f'task content:\n{dir(task)}')
#task_postrun.connect(celery_post_run)

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()