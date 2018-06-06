docker pull redis:latest
docker pull rabbitmq:latest
docker build --rm -t oe_bumps -f Dockerfile_bumps.oe .
docker run --name redis-server -d redis
docker run -d --name rabbit-server rabbitmqdocker run -d --name rabbit-server rabbitmq
docker run -d -e RABBITMQ_NODENAME=my-rabbit -p 22 --name rabbit-server rabbitmq
docker run -d --link redis-server --link rabbit-server -e "BACKEND_SERVER=redis-server" -p 5000:5000 --name oe_bumps oe_bumps

rem Worker(s)
rem docker build --rm -t oe_bumps_worker -f Dockerfile_bumps_worker.oe .
rem docker run -d -it --link redis-server --link rabbit-server -h oe_bumps_worker --name oe_bumps_worker oe_bumps_worker
rem docker run -d -it --link redis-server --link rabbit-server -h oe_bumps_worker2 --name oe_bumps_worker2 oe_bumps_worker

rem docker run -d --name bumps_gui --link redis-server -p 5000:5000 bumps

rem bumps cf1.py --batch --stepmon --burn=100 --steps=100 --store=/home/root/celery/bumps/results --fit=newton
rem bumps cf1.py --batch --stepmon --burn=100 --steps=100 --store=/tmp/test/result --fit=newton

