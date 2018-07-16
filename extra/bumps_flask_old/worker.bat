docker container rm -f oe_worker
docker build --rm -t oe_bumps_worker -f Dockerfile__worker.debug .
rem docker run -d -it --link redis-server --link rabbit-server -h oe_worker --name oe_worker --env BROKER_SERVER=ncnr-r9nano --env BACKEND_SERVER=ncnr-r9nano oe_bumps_worker
docker run -d -it --link redis-server --link rabbit-server -h oe_worker --name oe_worker --env BROKER_SERVER=rabbit-server --env BACKEND_SERVER=redis-server oe_bumps_worker
docker exec -it oe_worker bash 
rem celery -A bumps_flask.celery_bumps worker -E -l info