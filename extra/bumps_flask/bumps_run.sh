#!/bin/bash
echo "Welcome"
ls
echo "removing container"
docker container rm -f bumps_gui
echo "rebuilding image"
docker build --rm -t bumps_gui -f Dockerfile.bumps .
echo "running container"
docker run -d -it --link redis-server --link rabbit-server -e "BACKEND_SERVER=ncnr-r9nano" -e "BROKER_SERVER=ncnr-r9nano" -p 5000:5000 -h bumps_gui --name bumps_gui bumps_gui
echo "Container bumps_gui now running"
echo "That's it"

