# Using the latest long-term-support Ubuntu OS
FROM ubuntu:16.04

# Warning: on linux systems DNS lookup was failing.  Needed to find
# the DNS IP addresses with:
#     nmcli dev show | grep 'IP4.DNS'
# and add them to docker using the following in /etc/docker/daemon.json:
#     {
#         "dns": ["first ip", "second ip"],
#         ...
#     }
# May need to kill the docker daemon before it works:
#     sudo pkill docker
# Note that the nvidia runtime configuration ends up in the same file, so
# you may need some fiddling after installing it.

# Update the apt-get index and then install project dependencies
RUN apt-get update && apt-get install -y \
    iputils-ping    \
    net-tools       \
    build-essential \
    apache2         \
    apache2-dev     \
    libssl-dev      \
    git             \
    vim             \
    libmunge-dev    \
    munge           \
    python          \
    python-dev      \
    python-pip      \
    python-numpy    \
    #python-scipy    \
    python-matplotlib \
    ocl-icd-libopencl1 \
    python-pyopencl \
    clinfo \
    && rm -rf /var/lib/apt/lists/*

# Intel OpenCL
# based on the Intel OpenCL installation instructions and the Intel docker file
# in https://github.com/chihchun/opencl-docker
#RUN apt-get update && apt-get install -y unzip tar xz-utils clinfo
#ADD http://registrationcenter-download.intel.com/akdlm/irc_nas/11396/SRB5.0_linux64.zip /tmp/intel-opencl-driver
#WORKDIR /tmp/intel-opencl-driver
#RUN mkdir -p /tmp/intel-opencl-driver/fakeroot \
#    tar -C fakeroot -Jxf intel-opencl-r5.0*.tar.xz; do tar -C fakeroot -Jxv $f; done \
#    cp -R fakeroot/* / \
#    ldconfig \
#    clinfo

# NVidia OpenCL
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

RUN rm /etc/OpenCL/vendors/mesa.icd

#ADD https://download.schedmd.com/slurm/slurm-17.11.5.tar.bz2 /tmp/slurm.tgz
#RUN apt-get install vim
# Create the home directory for the new app user.
RUN mkdir -p /home/app_user

# Set the home directory to our app user's home.
ENV HOME=/home/app_user

# Set the directory for relative file paths
WORKDIR /home/app_user/bumps_flask/bumps_flask

# Create the folder for the html templates and static assets
RUN mkdir templates/ && mkdir static/

# Install the app dependencies using pip
RUN pip install -U pip
COPY requirements.txt /home/app_user/bumps_flask/
RUN pip install --no-cache-dir -r ../requirements.txt
RUN pip install git+https://github.com/omereis/bumps.git

# Install applications (refl1d, sasview, ...)
RUN pip install periodictable
RUN pip install refl1d
#RUN pip install tinycc  # Don't need tinycc on linux
RUN pip install --no-cache-dir git+https://github.com/sasview/sasmodels.git
RUN pip install git+https://github.com/sasview/sasview.git@ticket-1094-headless

# Include mod_wsgi to run Flask behind Apache in this container
# RUN pip install mod_wsgi

# Copy app files to the container
COPY ./ /home/app_user/bumps_flask

# Create a new user called 'app_user' and set it up on the OS
RUN groupadd -r app_user && useradd --no-log-init -r -g app_user app_user

# Install the application locally
RUN pip install --no-cache-dir -e ..

# Log in with 'app_user' for the rest of the process
# USER app_user

# Set the environment variables for Flask
ENV FLASK_APP=bumps_flask

# Launch the app
# CMD ["mod_wsgi-express", "start-server", "--host", "0.0.0.0", "--port", "5000", "bumps_flask.wsgi"]
# CMD ["gunicorn", "--bind", "${HOST:-0.0.0.0}:${PORT:-5000}", "bumps_flask:app"]
#CMD ["gunicorn", "--bind", "0.0.0.0:5002", "bumps_flask:app"]
CMD gunicorn --bind ${HOST:-0.0.0.0}:${PORT:-5002} bumps_flask:app
