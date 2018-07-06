docker container rm -f  oe_bumps_worker
docker build --rm -t bumps_base -f Dockerfile.bumps .
docker build --rm -t oe_bumps_worker -f Dockerfile_bumps_worker.oe .
rem celery -A bumps_flask.celery_bumps worker -E -l info
rem docker run -d -it --link redis-server --link rabbit-server -h oe_bumps_worker --name oe_bumps_worker oe_bumps_worker
docker run -d -it --link redis-server --link rabbit-server -h oe_bumps_worker --name oe_bumps_worker oe_bumps_worker
docker run -d -it --link redis-server --link rabbit-server -h oe_bumps_worker --name oe_bumps_worker bumps_base
docker run -d -it -h --link redis-server --link rabbit-server oe_bumps_worker --name oe_bumps_worker bumps_base
docker run -d -it --link redis-server --link rabbit-server -h r9_bumps_worker --name r9_bumps_worker bumps_base
docker run -d -it --link redis-server --link rabbit-server -h oe_bumps_worker_w --name oe_bumps_worker_w bumps_base
docker run -d -it -h oe_bumps_worker_w --name oe_bumps_worker_w bumps_base
docker exec -it oe_bumps_worker bash
