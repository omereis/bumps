
image ?= opencl_$(USER)
IMAGE ?= $(image)

# Intel OpenCL 2.0
#INTEL_DRIVER = SRB5.0_linux64.zip
#INTEL_DRIVER_URL = http://registrationcenter-download.intel.com/akdlm/irc_nas/11396/$(INTEL_DRIVER)

# Intel OpenCL 1.2 16.1.2
#INTEL_DRIVER = opencl_runtime_16.1.2_x64_rh_6.4.0.37.tgz
#INTEL_DRIVER_URL = http://registrationcenter-download.intel.com/akdlm/irc_nas/12556/$(INTEL_DRIVER)

# Intel OpenCL 1.2 16.1.1
INTEL_DRIVER = opencl_runtime_16.1.1_x64_ubuntu_6.4.0.25.tgz
INTEL_DRIVER_URL = http://registrationcenter-download.intel.com/akdlm/irc_nas/9019/$(INTEL_DRIVER)

# AMDGPU-PRO
# TODO: this should be replaced by the ROCm drivers...
#AMD_DRIVER = amdgpu-pro-17.40-492261.tar.xz
AMD_DRIVER = amdgpu-pro-18.10-572953.tar.xz
AMD_DRIVER_URL = http://www2.ati.com/drivers/linux/ubuntu/$(AMD_DRIVER)
AMD_OPTS = --device=/dev/kfd --device=/dev/dri --group-add video

# Nvidia
NVIDIA_OPTS = --runtime=nvidia

RUN_OPTS = $(AMD_OPTS)

.PHONY: stop build run clean fetch 

all: build run

stop:
	# Stop the container if it is running
	-docker container ls | grep -q $(IMAGE) && docker stop -t 0 $(IMAGE)
	# Remove the container if it exists
	-docker container ls -a | grep -q $(IMAGE) && docker container rm $(IMAGE)

clean: stop
	# Remove the image if it exists
	-docker image ls | grep -q $(IMAGE) && docker image rm $(IMAGE)

build: $(INTEL_DRIVER)
	# Build or update the image ("make clean build" to build without cache)
	docker build . -t $(IMAGE) --build-arg INTEL_DRIVER=$(INTEL_DRIVER) \
		--build-arg AMD_DRIVER=$(AMD_DRIVER)

run: stop
	# Run the container
	docker run $(RUN_OPTS) --name $(IMAGE) $(IMAGE)

bash: stop
	# Run the container interactive
	docker run $(RUN_OPTS) --interactive --tty --name $(IMAGE) $(IMAGE) bash

attach:
	# Attach to running container
	docker exec --interactive --tty $(IMAGE) bash

fetch: $(AMD_DRIVER) $(INTEL_DRIVER)

$(AMD_DRIVER):
	wget $(AMD_DRIVER_URL)

$(INTEL_DRIVER):
	wget $(INTEL_DRIVER_URL)
