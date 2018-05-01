
host ?= 0.0.0.0
port ?= 5000
image ?= bumps_$(USER)

HOST ?= $(host)
PORT ?= $(port)
IMAGE ?= $(image)

.PHONY: build run clean distclean

all: build run clean build-redis run-redis

clean:
	# Stop the container if it is running
	-docker container ls | grep -q $(IMAGE) && docker stop -t 0 $(IMAGE)
	# Remove the container if it exists
	-docker container ls -a | grep -q $(IMAGE) && docker container rm $(IMAGE)
	# Remove the image if it exists
	-docker image ls | grep -q $(IMAGE) && docker image rm $(IMAGE)

build: build-redis
	# Build or update the image ("make clean build" to build without cache)
	docker build . -t $(IMAGE)

run: run-redis
	# Stop the container if it is running
	-docker container ls | grep -q $(IMAGE) && docker stop -t 0 $(IMAGE)
	# Remove the container if it exists
	-docker container ls -a | grep -q $(IMAGE) && docker container rm $(IMAGE)
	# Start the container and connect it to redis
	# Note: make sure the selected port is accessible via the firewall
	docker run -d --link bumps_redis -e PORT=$(PORT) -e HOST=$(HOST) -p $(PORT):$(PORT) --name $(IMAGE) $(IMAGE)

build-redis:
    # Grab the latest redis image
	docker pull redis:latest

run-redis:
	# Start the redis container if it is not already started
	-docker ps | grep -q bumps_redis || docker run --name bumps_redis -d redis
