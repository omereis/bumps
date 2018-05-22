docker pull redis:latest
docker build . -t bumps
docker run --name bumps_redis -d redis
docker run -d --link bumps_redis -p 5000:5000 bumps
docker run --link bumps_redis -p 5000:5000 --name oe_bumps oe_bumps