docker container rm -f oe_bumps
docker build --rm -t oe_bumps -f Dockerfile_bumps.oe .
rem docker run --link redis-server --link rabbit-server -e "BACKEND_SERVER=redis-server" -p 5000:5000 -h oe_bumps --name oe_bumps oe_bumps
docker run -d -it --link redis-server --link rabbit-server -e "BACKEND_SERVER=redis-server" -p 5000:5000 -h oe_bumps --name oe_bumps oe_bumps
docker exec -i -t oe_bumps "bash"
rem docker exec -i -t bumps_redis "redis-cli"
rem bumps cf1.py --batch --stepmon --burn=100 --steps=100 --store=./cf1_results --fit=newton
rem apt-get install python-numpy python-scipy python-matplotlib
rem bumps cf1.py --batch --stepmon --burn=100 --steps=100 --store=cf1_results --fit=newton
rem docker run --link redis-server --link rabbit-server -e "BACKEND_SERVER=redis-server" -p 5000:5000 --name oe_bumps oe_bumps
rem app = Celery('proj', broker='amqp://rabbit-server', backend='redis://redis-server')


rem docker run -d -it -h oe_bumps --name oe_bumps oe_bumps


