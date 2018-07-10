docker container rm -f oe_bumps
docker container rm -f bumps_gui
rem docker build --rm -t bumps_base -f Dockerfile.bumps .
docker build --rm -t bumps_gui -f Dockerfile.bumps .
rem docker build --rm -t oe_bumps -f Dockerfile_bumps.oe .
docker run -d -it --link redis-server --link rabbit-server -e "BACKEND_SERVER=ncnr-r9nano" -e "BROKER_SERVER=ncnr-r9nano" -p 5000:5000 -h bumps_gui --name bumps_gui bumps_gui
rem docker run -d -it --link redis-server --link rabbit-server -e "BACKEND_SERVER=redis-server" -e "BROKER_SERVER=rabbit-server" -p 5000:5000 -h bumps_gui --name bumps_gui bumps_gui
rem docker exec -i -t oe_bumps "bash"
docker exec -i -t bumps_gui "bash"

