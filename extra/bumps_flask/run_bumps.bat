rem set FLASK_APP=bumps_flask
rem flask run
rem test
docker pull redis:latest
docker build . -t bumps
docker run --name bumps_redis -d redis
rem docker run --link bumps_redis -p 5000:5000 bumps
docker run -p 5000:5000 --link bumps_redis -d --name bumps_gui bumps
docker exec -i -t bumps_gui "bash"

