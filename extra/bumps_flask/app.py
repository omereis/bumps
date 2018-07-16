# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
import mysql
from mysql.connector import MySQLConnection, Error
from oe_debug import print_debug
from users import BumpsUser
#------------------------------------------------------------------------------
# create the application object
app = Flask(__name__)
app.secret_key = 'secret_key'
#------------------------------------------------------------------------------
def connect_to_db():
    conn = None
    try:
        conn = mysql.connector.connect(host='ncnr-r9nano.campus.nist.gov', database='lite', \
                                        user='discover',password='flask')
    except Error as e:
        print(e)
    return conn 
#------------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def wrap (*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Login required')
            return redirect(url_for('login'))
    return wrap
#------------------------------------------------------------------------------
def logout_required(f):
    @wraps(f)
    def wrap (*args, **kwargs):
        if 'logged_in' not in session:
            return f(*args, **kwargs)
        else:
            flash('Login required')
            return redirect(url_for('login'))
    return wrap
#------------------------------------------------------------------------------
@app.route('/')
@login_required
def home():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("select * from posts;")
    posts = [dict(title=row[0],description=row[1]) for row in cursor.fetchall()]
    conn.close()
    return render_template('index.html', posts=posts)  # render a template
#------------------------------------------------------------------------------
@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')  # render a template
#------------------------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
#@login_required
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = BumpsUser()
        if user.username_exists (username):
            print_debug ("app.py, register\nusername exists")
        else:
            print_debug ("app.py, register\nusername doesn't exists")
            user.add_user(username,password)
            return render_template('login.html', username=username)
    return render_template('register.html')  # render a template
#------------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            session['username']  = 'admin'
            flash ('Just logged in :-)')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)
#------------------------------------------------------------------------------
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash ('Just logged out :-(')
    return redirect(url_for('welcome'))
#------------------------------------------------------------------------------
@app.before_first_request
def on_start():
    print("on_start")
    session.clear()
#------------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        session.pop('logged_in', None)
    except Exception as e:
        print("Exception: " + str(e))
    app.run(debug=True, host='0.0.0.0')

