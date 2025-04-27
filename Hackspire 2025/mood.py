from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import os
from datetime import datetime
from flask import current_app

mood_bp = Blueprint('mood', __name__)

def get_mood_db_path():
    return os.path.join(current_app.instance_path, 'mood_journal.db')

def init_mood_db():
    mood_db_path = get_mood_db_path()
    os.makedirs(current_app.instance_path, exist_ok=True)
    with sqlite3.connect(mood_db_path) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS mood_entries
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      date_time TEXT,
                      mood TEXT,
                      notes TEXT)''')
        conn.commit()

@mood_bp.route('/mood')
def mood_journal():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    entries = view_entries()
    return render_template('mood.html', entries=entries)

@mood_bp.route('/save_mood', methods=['POST'])
def save_mood():
    if 'user' not in session:
        return redirect(url_for('login.html'))
    mood = request.form.get('mood')
    notes = request.form.get('notes', '')
    save_entry(mood, notes)
    flash("Mood saved successfully!", "success")
    return redirect(url_for('mood.mood_journal'))

@mood_bp.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    if 'user' not in session:
        return redirect(url_for('login.html'))
    delete_entry_from_db(entry_id)
    flash("Mood entry deleted successfully!", "success")
    return redirect(url_for('mood.mood_journal'))

@mood_bp.route('/view_entry/<int:id>')
def view_entry(id):
    mood_db_path = get_mood_db_path()
    with sqlite3.connect(mood_db_path) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM mood_entries WHERE id = ?", (id,))
        entry = c.fetchone()
    if entry:
        return jsonify({
            'id': entry[0],
            'date_time': entry[1],
            'mood': entry[2],
            'notes': entry[3]
        })
    return jsonify({'error': 'Entry not found'}), 404

def save_entry(mood, notes):
    mood_db_path = get_mood_db_path()
    with sqlite3.connect(mood_db_path) as conn:
        c = conn.cursor()
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO mood_entries (date_time, mood, notes) VALUES (?, ?, ?)",
                  (date_str, mood, notes))
        conn.commit()

def view_entries():
    mood_db_path = get_mood_db_path()
    with sqlite3.connect(mood_db_path) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM mood_entries ORDER BY date_time DESC")
        return c.fetchall()

def delete_entry_from_db(entry_id):
    mood_db_path = get_mood_db_path()
    with sqlite3.connect(mood_db_path) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM mood_entries WHERE id = ?", (entry_id,))
        conn.commit()
