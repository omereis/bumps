docker pull rabbitmq:latest
docker pull redis:latest
docker run -d --name redis-server redis
docker run -d --name rabbit-server rabbitmq
