from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Хранилище комнат и участников
rooms = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/room/<room_id>')
def room(room_id):
    return render_template('room.html', room_id=room_id)

@app.route('/create-room', methods=['POST'])
def create_room():
    room_id = request.form.get('room_id')
    if room_id not in rooms:
        rooms[room_id] = []
    return redirect(url_for('room', room_id=room_id))

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    if room not in rooms:
        rooms[room] = []
    rooms[room].append(username)
    emit('user_joined', {'username': username, 'users': rooms[room]}, room=room)

@socketio.on('vote')
def handle_vote(data):
    room = data['room']
    username = data['username']
    vote = data['vote']
    emit('vote_update', {'username': username, 'vote': vote}, room=room)

@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    rooms[room].remove(username)
    emit('user_left', {'username': username, 'users': rooms[room]}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
