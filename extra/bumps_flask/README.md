bumps_flask
===========


![](http://i.imgur.com/80bX1Tu.gif)


Introduction
------------

A remote processing service for *bumps* using a batch queue on a *Flask* server with a *Redis* database. Includes a simple web page interface.

Queueing and scheduling handled by *slurm*.


Installation
------------

**Docker Install**

Install an official *Redis* image first:

    $ docker pull redis:latest

Then, simply run::

    $ docker build . -t bumps_flask

from the directory containing the *Dockerfile* for *bumps_flask* on your server.

**Docker Configure**

On linux systems DNS lookup was failing, so you may need to find
the DNS IP addresses with::

    $ nmcli dev show | grep 'IP4.DNS'

and add them to docker using the following in /etc/docker/daemon.json::

    {
        "dns": ["first ip", "second ip"],
        ...
    }

You may need to force a docker daemon restart before this works:

    $ sudo pkill docker

Note that the nvidia runtime configuration is also in /etc/docker/daemon.json
so you may need some fiddling after installing it.

**NVidia**

In order to get a working NVidia container you need to install the nvidia
runtime into your host docker configuration.  This can be done using
the nvidia-docker2 package from the NVidia PPA (perosnal package archive).  
See the following for details:

    https://github.com/NVIDIA/nvidia-docker

As of this writing the nvidia-docker2 package depends on the docker-ce package 
from the docker PPA, so you may need to install that as well:

    https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce

The docker run command reuires and additional argument "--runtime=nvidia" to
connect the container to the hardware.

The Dockerfile for NVidia is relatively simple; presumably the bulk of the
configuration work is hidden in the NVidia runtime.

Note: probably need to set up the NVidia drivers on the host before any other
step, and probably needs to be done using the propriety drivers from NVidia.
The test machine was already set up so the specifics are not included here.

**AMD Radeon**

Similar to NVidia, the AMD drivers must be installed on the host in order
to run GPGPU from a docker container.  The open source ROCm drivers did not
work as of this writing, so the amdgpu-pro drivers were used instead.  The
makefile might not fetch the appropriate drivers (wget does not seem to
behave the same way as clicking the HTML link), and you may have to download
them by hand.  The AMD drivers need a few startup options as well:

    --device=/dev/kfd --device=/dev/dri --group-add video

This last argument (group-add video) should be done as part of the container
configuration, but isn't at the moment.

**Intel**

The intel drivers are included in the container.  The CPU device shows up on
a machine with Intel CPU.  Haven't tested with GPU.


Running the server
------------------

Now that there is a *Docker* image for the server installed, it can be daemonized and linked to *Redis* as follows:

    $ docker run --name bumps_redis -d redis
    $ docker run --link bumps_redis -p 5000:5000 bumps_flask

(May need to add flags for access to the GPU hardware, as listed in the
installation section.)

This should start a *gunicorn* server accessible from ``http://0.0.0.0:5000``.

**WARNING**

This is a development configuration and has a lot of security flaws.
For example, *Redis* is installed but not properly secured. It uses legacy *Docker*
commands such as *--link*. Since we are testing file uploads,
the Unix user which runs the server has root privileges. It also starts *Flask* with debug mode on.

Do **not** install this for production servers.


To-Do
-----
- Todo List
    - [ ] Generalize the service to allow for other bumps commands
    - [ ] Generalize the service to allow for generic queues (priority: support for slurm)
    - [x] Implement generic Slurm script generator from web service form values
        - [x] Allow for downloading of result files
        - [x] Generate unique job ids for organization and DB usage
    - [x] Implement calling bumps for running and saving of fits
        - [x] Implement MPLD3 html results page for generated graphs
    - [ ] Implement secure redirect back to caller (http://flask.pocoo.org/snippets/63/)
    - [ ] Implement unit testing
    - [x] Fix serializing lists in redis
    - [x] Implement logout
    - [x] Implement JWT token refresh for users to log back in with their UID
        - [x] Fix landing page auth issue (expired token)
    - [x] Implement redis database
    - [x] Implement file handling
