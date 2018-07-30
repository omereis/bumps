docker pull redis:latest
docker pull rabbitmq:latest
docker container rm -f rabbit-server
docker container rm -f redis-server
docker run -d --name redis-server -p 6379:6379 redis
docker run -d --name rabbit-server -p 5671:5671 -p 5672:5672 rabbitmq
