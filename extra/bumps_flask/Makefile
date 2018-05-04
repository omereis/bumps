
host ?= 0.0.0.0
port ?= 5000
image ?= bumps_$(USER)

HOST ?= $(host)
PORT ?= $(port)
IMAGE ?= $(image)

# Specify the type of gpu (amd, nvidia, intel).
# This defines the run options needed for the docker container to access the
# GPU resources on the (Linux) host.  The nvidia container needs a special
# nvidia runtime installed, which depends on the docker-ce package from docker
# rather than the base docker package in debian/ubuntu.
# Note: Intel beignet gets confused by multiple cards... may need relabel
# the card and renderer as shown in the comment below.  This option can be
# specified using RUN_OPTS="..." on the call to Make.
NVIDIA_OPTS = --runtime=nvidia
AMD_OPTS = --device=/dev/kfd --device=/dev/dri --group-add video
INTEL_OPTS = --device=/dev/dri
#INTEL_OPTS = --device=/dev/dri/card1:/dev/dri/card0 --device=/dev/dri/renderD129:/dev/dri/renderD128
gpu ?= none
ifeq ($(gpu), amd)
	RUN_OPTS = $(AMD_OPTS)
else ifeq ($(gpu), nvidia)
	RUN_OPTS = $(NVIDIA_OPTS)
else ifeq ($(gpu), intel)
	RUN_OPTS = $(INTEL_OPTS)
endif

.PHONY: stop clean build run build-redis run-redis

all: build run 

stop:
	# Stop the container if it is running
	-docker container ls | grep -q $(IMAGE) && docker stop -t 0 $(IMAGE)
	# Remove the container if it exists
	-docker container ls -a | grep -q $(IMAGE) && docker container rm $(IMAGE)

clean: stop
	# Remove the image if it exists
	-docker image ls | grep -q $(IMAGE) && docker image rm $(IMAGE)

build: build-redis
	# Build or update the image ("make clean build" to build without cache)
	docker build . -t $(IMAGE)

run: stop run-redis
	# Start the container and connect it to redis
	# Note: make sure the selected port is accessible via the firewall
	docker run $(RUN_OPTS) -d --link bumps_redis -e PORT=$(PORT) -e HOST=$(HOST) -p $(PORT):$(PORT) --name $(IMAGE) $(IMAGE)

bash: stop
	# Run the container interactive
	docker run $(RUN_OPTS) --interactive --tty --name $(IMAGE) $(IMAGE) bash

attach:
	# Attach to a running container
	docker exec --interactive --tty $(IMAGE) bash

build-redis:
    # Grab the latest redis image
	docker pull redis:latest

run-redis:
	# Start the redis container if it is not already started
	-docker ps | grep -q bumps_redis || docker run --name bumps_redis -d redis
