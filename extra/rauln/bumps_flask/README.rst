bumps_flask
===========

Introduction
------------

A remote processing service for *bumps* using a batch queue on a *Flask* server with a *Redis* database.
Queue service TBD (looking at Celery, slurm, torque, RQ).


Installation
------------

** Docker Install **

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

This should start a *gunicorn* server accessible from *0.0.0.0:5000*.

** WARNING **

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

-  Tweaks and improvements
    - [X] Implement actual redis database
    - [X] Fix serializing lists in redis
    - [ ] Implement logout (revoke JWT?)
    - [ ] Implement JWT token refresh for users who log back in with their UID
        - [X] Fix landing page auth issue (expired token)
    - [ ] Implement secure redirect back to caller (http://flask.pocoo.org/snippets/63/)

- Milestones
    - [X] Implement file handling
    - [W] Implement generic Slurm script generator from web service form values
        - [ ] Associate FitProblems to users
        - [W] Generate unique job ids for organization and DB usage
    - [W] Implement client interface for connecting to remote work server
        - [W] Implement the remaining REST interface
    - [ ] Implement unit testing
    - [ ] etc
