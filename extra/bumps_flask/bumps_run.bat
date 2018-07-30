docker container rm -f bumps_gui
docker build --rm -t bumps_gui -f Dockerfile.bumps .
rem docker run -d -it --link redis-server --link rabbit-server -e "BACKEND_SERVER=ncnr-r9nano" -e "BROKER_SERVER=ncnr-r9nano" -p 5000:5000 -h bumps_gui --name bumps_gui bumps_gui

docker run -d -it --link redis-server --link rabbit-server --env BROKER_SERVER=rabbit-server --env BACKEND_SERVER=redis-server -p 5000:5000 -h bumps_gui --name bumps_gui bumps_gui
docker exec -i -t bumps_gui "bash"

rem docker run --link redis-server --link rabbit-server -e "BACKEND_SERVER=ncnr-r9nano" -e "BROKER_SERVER=ncnr-r9nano" -p 5000:5000 -h bumps_gui --name bumps_gui bumps_gui
