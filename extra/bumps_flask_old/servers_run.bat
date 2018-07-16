docker pull redis:latest
docker pull rabbitmq:latest
docker container rm -f rabbit-server
docker container rm -f redis-server
docker run -d --name redis-server redis
docker run -d --name rabbit-server rabbitmq
