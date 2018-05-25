docker pull redis:latest
docker pull rabbitmq:latest
docker build --rm -t oe_bumps -f Dockerfile_bumps.oe .
rem docker run --name bumps_redis -d redis
docker run --name redis-server -d redis
rem docker run -d --link bumps_redis -p 5000:5000 bumps_gui
docker run -d -e RABBITMQ_NODENAME=my-rabbit -p 22 --name rabbit-server rabbitmq
docker run -d --link redis-server -e REDIS_SERVER="redis-server" --link  rabbit-server -p 5000:5000 --name oe_bumps oe_bumps
docker run -d --link redis-server --link rabbit-server -e "BACKEND_SERVER=redis-server" -p 5000:5000 --name oe_bumps oe_bumps


rem docker run -d --name bumps_gui --link redis-server -p 5000:5000 bumps

rem bumps cf1.py --batch --stepmon --burn=100 --steps=100 --store=/home/root/celery/bumps/results --fit=newton
rem bumps cf1.py --batch --stepmon --burn=100 --steps=100 --store=/tmp/test/result --fit=newton

