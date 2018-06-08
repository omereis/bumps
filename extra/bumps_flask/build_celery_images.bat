docker build --rm -t oe_bumps_worker -f Dockerfile_bumps_worker.oe .
docker build --rm -t oe_bumps -f Dockerfile_bumps.oe .
rem lower
docker build --rm -t oe_flower  -f flower\Dockerfile_flower.oe .
rem cd ..

docker run -h oe_flower --name oe_flower --link redis-server --link rabbit-server -it -d -p 5555:5555 oe_flower
