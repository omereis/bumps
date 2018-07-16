docker container rm -f  oe_bumps_worker
docker build --rm -t bumps_worker -f Dockerfile_bumps_worker.oe .
docker run -d -it --link redis-server --link rabbit-server -h r9_bumps_worker --name r9_bumps_worker --env BROKER_SERVER=ncnr-r9nano --env BACKEND_SERVER=ncnr-r9nano bumps_worker
docker exec -it r9_bumps_worker bash
