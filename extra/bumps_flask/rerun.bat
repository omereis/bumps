docker container rm -f oe_bumps
docker build --rm -t oe_bumps -f Dockerfile_bumps.oe .
docker run -d --link redis-server --link rabbit-server -e "BACKEND_SERVER=redis-server" -p 5000:5000 --name oe_bumps oe_bumps
docker exec -i -t oe_bumps "bash"
rem docker exec -i -t bumps_redis "redis-cli"
rem bumps cf1.py --batch --stepmon --burn=100 --steps=100 --store=./cf1_results --fit=newton
rem apt-get install python-numpy python-scipy python-matplotlib
rem bumps cf1.py --batch --stepmon --burn=100 --steps=100 --store=cf1_results --fit=newton
