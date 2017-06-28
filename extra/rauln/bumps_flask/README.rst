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
    - [ ] Fix serializing lists in redis (using msgpack)
        -    [X] Get back to using lists or other composite type
    - [ ] Implement unit testing
    - [ ] **Backend work!!**
    - [ ] Implement logout (revoke JWT?)
    - [W] Implement JWT token refresh for users who log back in with their UID
        - [X] Fix landing page auth issue (expired token)
    - [W] Implement secure redirect back to caller (http://flask.pocoo.org/snippets/63/)
    - [W] Associate FitProblem scripts to job_n (consider that jobs may not finish in order appended...)
