bumps_flask
===========

Introduction
------------

A remote processing service for *bumps* using a batch queue on a *Flask* server with a *Redis* database.
Queueing and scheduling is currently provided by *slurm*.


Installation
------------

**Docker Install**

Install an official *Redis* image first::

    $ docker pull redis:latest

Then, simply run::

    $ docker build . -t bumps_flask

from the directory containing the *Dockerfile* for *bumps_flask* on your server.

Running the server
-----------------

Now that there is a *Docker* image for the server installed, it can be daemonized and linked to *Redis* as follows::

    $ docker run --name bumps_redis -d redis
    $ docker run --link bumps_redis -p 5000:5000 bumps_flask

This should start a *gunicorn* server accessible from ``http://0.0.0.0:5000``.

**WARNING**

This is a development configuration and has a lot of security flaws.
For example, *Redis* is installed but not properly secured. It uses legacy *Docker*
commands such as *--link*. Since we are testing file uploads,
the Unix user which runs the server has root privileges. It also starts *Flask* with debug mode on.
Do **not** install this for production servers.


To-Do
-----

[W]
    Working on it

[X]
    DONE! (maybe)

[ ]
    GET TO WORK!

- Todo
    - [W] Generalize the service to allow for other bumps commands
    - [ ] Generalize the service to allow for generic queues (priority: support for slurm)
        - [W] Dockerize a slurm cluster for linking with bumps_flask
    - [W] Implement client interface for connecting to remote work server
        - [W] Implement the remaining REST interface
    - [X] Implement generic Slurm script generator from web service form values
        - [X] Allow for downloading of result files
        - [X] Generate unique job ids for organization and DB usage
    - [X] Implement calling bumps for running and saving of fits
        - [X] Implement MPLD3 html results page for generated graphs
    - [ ] Implement secure redirect back to caller (http://flask.pocoo.org/snippets/63/)
    - [ ] Implement unit testing
    - [X] Fix serializing lists in redis
    - [X] Implement logout
    - [X] Implement JWT token refresh for users to log back in with their UID
        - [X] Fix landing page auth issue (expired token)
    - [X] Implement redis database
    - [X] Implement file handling
