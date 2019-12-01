docker container rm -f bumps_redis
docker build --rm -f bumps_redis.dockerfile -t bumps_redis .

docker run -it -d --name bumps_redis bumps_redis
docker exec -i -t bumps_redis bash
