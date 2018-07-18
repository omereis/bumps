from flask import Flask, render_template
from flask_nav import Nav
from flask_nav.elements import Navbar, Subgroup, View, Link, Text, Separator

app = Flask (__name__)
nav = Nav (app)

nav.register_element ('my_navbar', Navbar('thenav', View('Home Page', 'index'),
                    View('Item One', 'item', item='Aradnik'),
                    Link ('Yahoo!', 'http://www.yahoo.com'),
                    Separator(),
                    Text('Plain text example')),
                    Subgroup ('my_subgroup',
                        View ('Item Two', 'item', 'Subgroup Item'))
                    )

@app.route('/')
def index():
    return render_template ('index.html')

@app.route('/item/<item>')
def item(item):
    return '<h1>The Item Page!!!<br>The item is {}.'.format(item)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')