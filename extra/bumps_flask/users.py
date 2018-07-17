from flask import Flask, render_template, redirect, url_for, request, session, flash
from sql_db import bumps_sql
from oe_debug import print_debug
import hashlib
import base64
#------------------------------------------------------------------------------
TABLE_USERS    = 't_bumps_users'
FIELD_USERNAME = 'username'
FIELD_PASSWORD = 'password'
#------------------------------------------------------------------------------
class BumpsUser (object):
    username = None
    password = None
    db = None
    key = 'bumps_key'
#------------------------------------------------------------------------------
    def username_exists (self, username):
        username_exists = False
        try:
            db = self.connect_to_db()
            db.conn.free_result()
            res = db.run_sql (strSql, get_results=True)
            username_exists = res[0][0] > 0
        except Exception as e:
            print_debug ("users.py, username_exists exceiption:\n%s" % str(e))
        return username_exists
#------------------------------------------------------------------------------
    def connect_to_db(self, buffered=True):
        if not self.db:
            self.db = bumps_sql()
            self.db.connect_to_db(buffered=buffered)
        return self.db
#------------------------------------------------------------------------------
    def hash_pass (self, password):
        db_pass = password
        try:
            db_pass = encode(self.key, password)
        except:
            db_pass = password
        return db_pass
#------------------------------------------------------------------------------
    def add_user(self, username, password):
        user_added = False
        try:
            db = self.connect_to_db()
            db_pass = self.hash_pass (password)
            strSql = "insert into %s (%s,%s) values ('%s','%s');" % \
                    (TABLE_USERS, FIELD_USERNAME, FIELD_PASSWORD, username, db_pass)
#                    (TABLE_USERS, FIELD_USERNAME, FIELD_PASSWORD, username, password)
            print_debug ("users.py, add_user\nstrSql: '%s'" % strSql)
            db.run_sql (strSql, get_results=False)
            user_added = True
        except Exception as e:
            print_debug ("users.py, username_exists exception:\n%s" % str(e))
        return user_added
#------------------------------------------------------------------------------
    def authenticate(self, username, password):
        authenticated = False
        try:
            print_debug ("users.py, authenticate, before connect_to_db")
            db = self.connect_to_db(buffered=True)
            print_debug ("users.py, authenticate, AFTER connect_to_db")
            db.conn.free_result()
            db_pass = self.hash_pass (password)
            strSql = "select count(*) from %s where (%s='%s') and (%s='%s');" % \
                    (TABLE_USERS, FIELD_USERNAME, username, FIELD_PASSWORD, db_pass)
            res = db.run_sql (strSql, get_results=True)
            if res[0][0] > 0:
                authenticated = True
        except Exception as e:
            print_debug ("users.py, authenticate exception:\n%s" % str(e))
        print_debug("users.py, authenticate\nauthenticated: %s" % str(authenticated))
        return authenticated
#------------------------------------------------------------------------------
def encode(key, string):
#
# Source: https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password
#
    encoded_chars = []
    for i in xrange(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return base64.urlsafe_b64encode(encoded_string)
#------------------------------------------------------------------------------
