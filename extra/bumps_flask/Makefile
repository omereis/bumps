
host ?= 0.0.0.0
port ?= 5000
image ?= bumps_$(USER)

HOST ?= $(host)
PORT ?= $(port)
IMAGE ?= $(image)

.PHONY: build run clean distclean

all: build run

clean:
	# Kill the existing bumps:port container
	-docker container ls -a | grep -q $(IMAGE) && docker container rm $(IMAGE)
	# Kill the existing bumps:port image
	-docker image ls | grep -q $(IMAGE) && docker image rm $(IMAGE)

build:
    # Grab the latest redis
	docker pull redis:latest
	# Build the new bumps:port container
	docker build . -t $(IMAGE)

run:
	# Start redis if it is not already started
	-docker ps | grep -q bumps_redis || docker run --name bumps_redis -d redis
	# Stop the existing bumps:port container
	-docker container ls | grep -q $(IMAGE) && docker stop -t 0 $(IMAGE)
	# Kill the existing bumps:port container
	-docker container ls -a | grep -q $(IMAGE) && docker container rm $(IMAGE)
	# Start redis if it is not already started
	docker run -d --link bumps_redis -e PORT=$(PORT) -e HOST=$(HOST) -p $(PORT):$(PORT) --name $(IMAGE) $(IMAGE)
