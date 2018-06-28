docker container rm -f oe_bumps
docker build --rm -t oe_bumps -f Dockerfile_bumps.oe .
rem docker run --link redis-server --link rabbit-server -e "BACKEND_SERVER=redis-server" -p 5000:5000 -h oe_bumps --name oe_bumps oe_bumps
docker run -d -it --link redis-server --link rabbit-server -e "BACKEND_SERVER=redis-server" -p 5000:5000 -h oe_bumps --name oe_bumps oe_bumps
docker exec -i -t oe_bumps "bash"
