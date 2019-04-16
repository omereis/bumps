""" source:
https://secdevops.ai/weekend-project-part-2-turning-flask-into-a-real-time-websocket-server-using-flask-socketio-ab6b45f1d896
"""
from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, emit
# from codenames import game

# initialize Flask
app = Flask(__name__)
socketio = SocketIO(app)
ROOMS = {} # dict to track active rooms

@app.route('/')
def index():
    """Serve the index HTML"""
    return render_template('index.html')

@socketio.on('create')
def on_create(data):
    """Create a game lobby"""
#    gm = game.Info(
#        size=data['size'],
#        teams=data['teams'],
#        dictionary=data['dictionary'])
#    room = gm.game_id
    ROOMS[room] = gm
    join_room(room)
    emit('join_room', {'room': room})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=4000)

