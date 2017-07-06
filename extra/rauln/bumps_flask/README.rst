bumps_flask
===========

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
