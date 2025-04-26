from flask import Flask, render_template, request, redirect, url_for, jsonify
from collections import defaultdict
import random

app = Flask(__name__)

# In-memory storage
rooms = defaultdict(list)
public_rooms = set()

# Helper to generate random usernames
def generate_username():
    adjectives = ["Happy", "Calm", "Brave", "Bright", "Gentle"]
    nouns = ["Sun", "River", "Tree", "Sky", "Star"]
    return random.choice(adjectives) + random.choice(nouns) + str(random.randint(100, 999))

# Home page
@app.route('/')
def home():
    return render_template('home.html', rooms=public_rooms)

# Create a new community
@app.route('/create_room', methods=['POST'])
def create_room():
    room_name = request.form['room_name'].strip()
    if room_name:
        public_rooms.add(room_name)
    return redirect(url_for('home'))

# Enter a community room
@app.route('/room/<room_name>')
def room(room_name):
    username = generate_username()
    return render_template('room.html', room_name=room_name, username=username)

# Send a message
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    room = data['room']
    username = data['username']
    message = data['message']
    rooms[room].append({'username': username, 'message': message})
    return jsonify({'status': 'Message received'})

# Get all messages of a room
@app.route('/get_messages/<room_name>')
def get_messages(room_name):
    return jsonify(rooms[room_name])

if __name__ == '__main__':
    app.run(debug=True)
