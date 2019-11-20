docker container rm -f redis-server
docker container rm -f rabbit-server

docker pull rabbitmq:latest
docker pull redis:latest


docker run -d --name redis-server redis
docker run -d --name rabbit-server rabbitmq
