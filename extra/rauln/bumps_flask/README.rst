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
    - [ ] Implement unit testing
    - [ ] Implement logout (revoke JWT?)
    - [ ] Implement JWT token refresh for users who log back in with their UID
        - [X] Fix landing page auth issue (expired token)
    - [W] Implement secure redirect back to caller (http://flask.pocoo.org/snippets/63/)

- Milestones
    - [W] Implement file handling (tempdirs, filenames based on jobids)
    - [W] Implement generic Slurm script generator from web service form values
        - [W] Associate FitProblems to users
    - [ ] Implement client interface for connecting to remote work server
        - [ ] Implement the remaining REST interface
    - [ ] etc
