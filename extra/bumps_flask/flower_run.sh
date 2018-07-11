#!/bin/bash
echo "Welcome"
echo "removing container"
docker build --rm -t bumps_flower  -f Dockerfile_flower.bumps .
docker container rm -f bumps_flower
sudo docker run -h bumps_flower --name bumps_flower --link redis-server --link rabbit-server -it -d -p 5555:5555 bumps_flower

echo "That's it"

