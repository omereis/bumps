docker container rm -f redis-server
docker container rm -f rabbit-server

docker run -d --name redis-server redis:latest
docker run -d --name rabbit-server rabbitmq:latest
