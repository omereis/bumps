from flask import Flask, render_template
# initialize Flask
app = Flask(__name__)

@app.route('/')
def index():
    """Serve the index HTML"""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
