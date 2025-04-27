from flask import Blueprint, render_template, request, jsonify
import ollama
import sqlite3
from datetime import datetime

# Create a blueprint for Gemma
gemma_bp = Blueprint('gemma', __name__)

# Database setup
DB_PATH = "instance/chat_sessions.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT,
                start_time TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                sender TEXT,
                message TEXT,
                timestamp TEXT,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        """)
        conn.commit()

# Initialize the database
init_db()

# Route to render the Gemma chat page
@gemma_bp.route('/gemma_chat')
def gemma_chat_page():
    return render_template('gemma.html')

# Route to start a new chat session
@gemma_bp.route('/start_session', methods=['POST'])
def start_session():
    session_name = request.json.get("session_name", f"Session {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO sessions (session_name, start_time) VALUES (?, ?)", (session_name, start_time))
        session_id = c.lastrowid
        conn.commit()
    return jsonify({"session_id": session_id, "session_name": session_name, "start_time": start_time})

# Route to handle user messages
@gemma_bp.route('/gemma_chat_api', methods=['POST'])
def gemma_chat_api():
    session_id = request.json.get("session_id")
    user_message = request.json.get("message")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # If no session, create a new one
    if not session_id:
        session_name = f"Session {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO sessions (session_name, start_time) VALUES (?, ?)", (session_name, timestamp))
            session_id = c.lastrowid
            conn.commit()

    # Fetch previous messages for context
    messages_for_context = []
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT sender, message
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """, (session_id,))
        messages = c.fetchall()
        for sender, message in messages:
            messages_for_context.append({"role": "user" if sender == "user" else "assistant", "content": message})

    messages_for_context.append({"role": "user", "content": user_message})

    try:
        # Ollama API call with context
        response = ollama.chat(
            model="gemma3:4b",
            messages=messages_for_context
        )
        print(f"Ollama Response: {response}")

        if hasattr(response, "message") and hasattr(response.message, "content"):
            bot_response = response.message.content
        else:
            bot_response = "Sorry, I couldn't process that."

        # Save both user and bot messages to the database
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO messages (session_id, sender, message, timestamp) VALUES (?, ?, ?, ?)",
                      (session_id, "user", user_message, timestamp))
            c.execute("INSERT INTO messages (session_id, sender, message, timestamp) VALUES (?, ?, ?, ?)",
                      (session_id, "bot", bot_response, timestamp))
            conn.commit()

    except Exception as e:
        print(f"Error with Ollama API: {e}")
        bot_response = f"Error: {str(e)}"

    return jsonify({"response": bot_response, "session_id": session_id})

# Route to fetch session history
@gemma_bp.route('/get_sessions', methods=['GET'])
def get_sessions():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, session_name, start_time FROM sessions ORDER BY start_time DESC")
        sessions = [{"id": row[0], "session_name": row[1], "start_time": row[2]} for row in c.fetchall()]
    return jsonify(sessions)

# Route to fetch messages of a session
@gemma_bp.route('/get_session_messages/<int:session_id>', methods=['GET'])
def get_session_messages(session_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT sender, message, timestamp
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """, (session_id,))
        messages = [{"sender": row[0], "message": row[1], "timestamp": row[2]} for row in c.fetchall()]
    return jsonify(messages)

# Route to delete a session and its messages
@gemma_bp.route('/delete_session/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        c.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
    return jsonify({"message": "Session deleted successfully"})

# Route to reset the current session
@gemma_bp.route('/reset_session/<int:session_id>', methods=['POST'])
def reset_session(session_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.commit()
    return jsonify({"message": "Session reset successfully", "session_id": session_id})