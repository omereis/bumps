docker container rm -f  oe_bumps_worker
docker build --rm -t oe_bumps_worker -f Dockerfile_bumps_worker.oe .
docker run -d -it --link redis-server --link rabbit-server -h oe_bumps_worker --name oe_bumps_worker oe_bumps_worker
docker exec -it oe_bumps_worker bash