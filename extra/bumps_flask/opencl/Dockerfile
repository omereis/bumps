# Using the latest long-term-support Ubuntu OS
FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
    apt-utils \
    unzip \
    tar \
    xz-utils \
    alien \
    beignet-opencl-icd \
    clinfo \
    ;

# Install Intel OpenCL drivers
# based on the Intel OpenCL installation instructions and the Intel docker file
# in https://github.com/chihchun/opencl-docker
#ADD http://registrationcenter-download.intel.com/akdlm/irc_nas/11396/SRB5.0_linux64.zip /tmp/intel-opencl-driver
ARG INTEL_DRIVER
RUN mkdir -p /tmp/opencl-driver-intel
COPY $INTEL_DRIVER /tmp/opencl-driver-intel/$INTEL_DRIVER
WORKDIR /tmp/opencl-driver-intel
# SRB 5 uses a zip file; older drivers use .tgz
RUN echo INTEL_DRIVER is $INTEL_DRIVER; \
    if echo $INTEL_DRIVER | grep -q "[.]zip$"; then \
        unzip $INTEL_DRIVER; \
        mkdir fakeroot; \
        for f in intel-opencl-*.tar.xz; do tar -C fakeroot -Jxvf $f; done; \
        cp -R fakeroot/* /; \
        ldconfig; \
    else \
        tar -xzf $INTEL_DRIVER; \
        for i in $(basename $INTEL_DRIVER .tgz)/rpm/*.rpm; do alien --to-deb $i; done; \
        dpkg -i *.deb; \
        rm -rf $INTEL_DRIVER $(basename $INTEL_DRIVER .tgz) *.deb; \
        mkdir -p /etc/OpenCL/vendors; \
        echo /opt/intel/*/lib64/libintelocl.so > /etc/OpenCL/vendors/intel.icd; \
    fi;

# Install AMD Radeon drivers
ARG AMD_DRIVER
RUN mkdir -p /tmp/opencl-driver-amd
COPY $AMD_DRIVER /tmp/opencl-driver-amd/$AMD_DRIVER
WORKDIR /tmp/opencl-driver-amd
RUN echo AMD_DRIVER is $AMD_DRIVER; \
    tar -Jxvf $AMD_DRIVER; \
    rm $AMD_DRIVER; \
    cd amdgpu-pro-*; \
    ./amdgpu-install; \
    apt-get install opencl-amdgpu-pro -y;

#RUN apt-get install -y alien

# Install NVidia OpenCL drivers
# In order to run against nvidia GPU need the docker-ce package:
#   https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce
# then the nvidia-docker2 package:
#   https://github.com/NVIDIA/nvidia-docker
# The commands to compose the nvidia opencl configuration come from
# the nvidia docker containers in opencl/runtime/Dockerfile at:
#   https://gitlab.com/nvidia/opencl
# These are also hosted on docker hub and can be used as the base container:
#   https://hub.docker.com/r/nvidia/opencl/
RUN mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

RUN rm -f /etc/OpenCL/vendors/mesa.icd

CMD clinfo
