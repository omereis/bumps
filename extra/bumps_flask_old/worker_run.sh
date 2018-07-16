#!/bin/bash
echo "Welcome"
#ls $1
if [ $# -eq 0 ]
  then
    WORKER_NAME="lynux_bumps_worker"
else
  WORKER_NAME=$1
fi
echo "WORKER NAME: " $WORKER_NAME
docker container rm -f  "%worker_name%"
docker build --rm -t bumps_worker -f Dockerfile__worker.bumps .
docker run -d -it --link redis-server --link rabbit-server -h $WORKER_NAME --name $WORKER_NAME --env BROKER_SERVER=ncnr-r9nano --env BACKEND_SERVER=ncnr-r9nano bumps_worker 
echo "Worker " $WORKER_NAME " is running"
echo "That's it"

