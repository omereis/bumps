docker container rm -f bumps_gui
docker build . -t bumps_gui
docker run --name bumps_redis -d redis
docker run -p 5000:5000 --link bumps_redis -d --name bumps_gui bumps_gui
docker exec -i -t bumps_gui "bash"
rem docker exec -i -t bumps_redis "redis-cli"
rem bumps cf1.py --batch --stepmon --burn=100 --steps=100 --store=./cf1_results --fit=newton
rem apt-get install python-numpy python-scipy python-matplotlib
bumps cf1.py --batch --stepmon --burn=100 --steps=100 --store=cf1_results --fit=newton
