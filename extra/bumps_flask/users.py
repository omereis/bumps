from flask import Flask, render_template, redirect, url_for, request, session, flash
from sql_db import bumps_sql
from oe_debug import print_debug
#------------------------------------------------------------------------------
TABLE_USERS    = 't_bumps_users'
FIELD_USERNAME = 'username'
FIELD_PASSWORD = 'password'
#------------------------------------------------------------------------------
class BumpsUser (object):
    username = None
    password = None
    db = None
#------------------------------------------------------------------------------
    def username_exists (self, username):
        username_exists = False
        try:
            db = self.connect_to_db()
            db.free_result()
            strSql = "select count(*) from %s where %s='%s';" % (TABLE_USERS, FIELD_USERNAME, username)
            res = db.run_sql (strSql, get_results=True)
            print_debug ("users.py, username_exists:\nstr(res): %s" % str(res))
            username_exists = res[0][0] > 0
            print_debug ("users.py, username_exists:\nusername_exists" % str(username_exists))
        except Exception as e:
            print_debug ("users.py, username_exists exceiption:\n%s" % str(e))
        return username_exists
#------------------------------------------------------------------------------
    def connect_to_db(self):
        if not self.db:
            self.db = bumps_sql()
            self.db.connect_to_db()
        return self.db
#------------------------------------------------------------------------------
    def add_user(self, username, password):
        user_added = False
        try:
            db = self.connect_to_db()
            strSql = "insert into %s (%s,%s) values ('%s','%s');" % \
                    (TABLE_USERS, FIELD_USERNAME, FIELD_PASSWORD, username, password)
            print_debug ("users.py, add_user\nstrSql: '%s'" % strSql)
            db.run_sql (strSql, get_results=False)
            user_added = True
        except Exception as e:
            print_debug ("users.py, username_exists exceiption:\n%s" % str(e))
        return user_added
#------------------------------------------------------------------------------
