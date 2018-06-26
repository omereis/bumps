docker pull omereis/bumps
docker pull redis:latest
docker run --name bumps_redis -d redis
docker run -d --link bumps_redis -p 5000:5000 omereis/bumps