rem set FLASK_APP=bumps_flask
rem flask run
rem test
docker pull giovtorres/docker-centos7-slurm:latest
docker pull redis:latest
docker build . -t bumps_gui
docker run --name bumps_redis -d redis
rem docker run --link bumps_redis -p 5000:5000 bumps
docker run -p 5000:5000 --link bumps_redis -d --name bumps_gui bumps_gui
rem docker run -it -h ernie giovtorres/docker-centos7-slurm:latest
docker exec -i -t bumps_gui "bash"
docker exec -i -t bumps_redis "redis-cli"
