from flask import Flask, render_template, request, redirect, url_for, jsonify , Blueprint
from collections import defaultdict
import random
import sqlite3

DB_PATH = "instance/communities.db"

# Initialize the database
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS communities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        conn.commit()

# Call the function to initialize the database
init_db()

commu_bp = Blueprint('commu', __name__)

# In-memory storage
rooms = defaultdict(list)
public_rooms = set()

# Helper to generate random usernames
def generate_username():
    adjectives = ["Happy", "Calm", "Brave", "Bright", "Gentle"]
    nouns = ["Sun", "River", "Tree", "Sky", "Star"]
    return random.choice(adjectives) + random.choice(nouns) + str(random.randint(100, 999))

# Home page
@commu_bp.route('/commu')
def community():
    return render_template('commu.html', rooms=get_all_communities())

# Create a new community
@commu_bp.route('/create_room', methods=['POST'])
def create_room():
    room_name = request.form['room_name'].strip()
    if room_name:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO communities (name) VALUES (?)", (room_name,))
                conn.commit()
                return redirect(url_for('commu.community'))
            except sqlite3.IntegrityError:
                # Community already exists
                return render_template('commu.html', rooms=get_all_communities(), error=f"Community '{room_name}' already exists.")
    return redirect(url_for('commu.community'))

# Join a community
@commu_bp.route('/join_room', methods=['POST'])
def join_room():
    room_name = request.form['room_name'].strip()
    if room_name:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT name FROM communities WHERE name = ?", (room_name,))
            result = c.fetchone()
            if result:
                # Community exists, redirect to the room
                return redirect(url_for('commu.room', room_name=room_name))
            else:
                # Community does not exist
                return render_template('commu.html', rooms=get_all_communities(), error=f"Community '{room_name}' does not exist. You can create it.")
    return redirect(url_for('commu.community'))

# Helper function to get all communities
def get_all_communities():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM communities")
        return [row[0] for row in c.fetchall()]

# Enter a community room
@commu_bp.route('/room/<room_name>')
def room(room_name):
    username = generate_username()
    return render_template('room.html', room_name=room_name, username=username)

# Send a message
@commu_bp.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    room = data['room']
    username = data['username']
    message = data['message']
    rooms[room].append({'username': username, 'message': message})
    return jsonify({'status': 'Message received'})

# Get all messages of a room
@commu_bp.route('/get_messages/<room_name>')
def get_messages(room_name):
    return jsonify(rooms[room_name])

# Delete a community
@commu_bp.route('/delete_room/<room_name>', methods=['POST'])
def delete_room(room_name):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM communities WHERE name = ?", (room_name,))
        conn.commit()
    return redirect(url_for('commu.community'))
