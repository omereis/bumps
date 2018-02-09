docker pull redis:latest
docker build . -t bumps
docker run --name bumps_redis -d redis
docker run -d --link bumps_redis -p 5000:5000 bumps