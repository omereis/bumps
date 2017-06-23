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
        -   [ ] Get back to using lists or other composite type (currently str())
    - [ ] Implement unit testing
    - [ ] **Backend work!!**
    - [ ] Implement logout (revoke JWT?)
    - [W] Implement JWT token refresh for users who log back in with their UID
        - [ ] Fix landing page auth issue (expired token)
