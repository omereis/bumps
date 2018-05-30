celery multi stopwait w1 -A proj -l info


docker run -itd --link redis-server --link rabbit-server --link oe_celery --name celery_client ubuntu:16.04
Celery('tasks', backend='amqp',broker='amqp://<user>:<password>@<ip>/<vhost>')
app = Celery('proj', broker='amqp://rabbit-server', backend='redis://redis-server', include=['proj.tasks'])