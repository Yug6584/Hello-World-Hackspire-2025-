from flask import Blueprint, render_template, request
import sqlite3
import os

recomm_bp = Blueprint('recomm', __name__)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'mood_selections.db')

# Initialize DB (Create table if not exists)
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS mood_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood TEXT NOT NULL,
            choice_type TEXT NOT NULL,
            choice_name TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Recommendation Dictionaries (unchanged)
mood_to_song = {
    'happy': {
        'song_name': 'Sunflower - Post Malone',
        'spotify_link': 'https://open.spotify.com/track/3KkXRkHbMCARz0aVfEt68P',
        'album_image': 'https://i.scdn.co/image/ab67616d0000b27391b78b10a3e0f3e14d34b5ef'
    },
    'sad': {
        'song_name': 'Someone Like You - Adele',
        'spotify_link': 'https://open.spotify.com/track/4kflIGfjdZJW4ot2ioixTB',
        'album_image': 'https://i.scdn.co/image/ab67616d0000b2730f7e80440f6d277337b27b8d'
    },
    'angry': {
        'song_name': 'In The End - Linkin Park',
        'spotify_link': 'https://open.spotify.com/track/60a0Rd6pjrkxjPbaKzXjfq',
        'album_image': 'https://i.scdn.co/image/ab67616d0000b27307f2cc2773c8583d08e5d7d3'
    },
    'relaxed': {
        'song_name': 'Better Together - Jack Johnson',
        'spotify_link': 'https://open.spotify.com/track/2NcQnHAgx8icFci3PvK3L7',
        'album_image': 'https://i.scdn.co/image/ab67616d0000b273f62a9e8f3a3c08bf6f52acae'
    }
}

mood_to_movie = {
    'happy': {
        'movie_name': 'The Pursuit of Happyness',
        'imdb_link': 'https://www.imdb.com/title/tt0454921/',
        'poster_image': 'https://res.cloudinary.com/jerrick/image/upload/d_642250b563292b35f27461a7.png,f_jpg,fl_progressive,q_auto,w_1024/611e8b337d0125001f2676dc.jpg'
    },
    'sad': {
        'movie_name': 'The Fault in Our Stars',
        'imdb_link': 'https://www.imdb.com/title/tt2582846/',
        'poster_image': 'https://jorgelcastanos.blog/wp-content/uploads/2014/10/tumblr_n7dyddvoqs1sfevmio1_1280.jpg'
    },
    'angry': {
        'movie_name': 'Joker',
        'imdb_link': 'https://www.imdb.com/title/tt7286456/',
        'poster_image': 'https://wallpapercave.com/wp/wp4606146.jpg'
    },
    'relaxed': {
        'movie_name': 'Forrest Gump',
        'imdb_link': 'https://www.imdb.com/title/tt0109830/',
        'poster_image': 'https://image.tmdb.org/t/p/original/saHP97rTPS5eLmrLQEcANmKrsFl.jpg'
    }
}

mood_to_book = {
    'happy': {
        'book_name': 'The Alchemist by Paulo Coelho',
        'book_link': 'https://www.goodreads.com/book/show/865.The_Alchemist',
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/I/51Z0nLAfLmL.SX320_BO1,204,203,200.jpg'
    },
    'sad': {
        'book_name': 'Tuesdays with Morrie by Mitch Albom',
        'book_link': 'https://www.goodreads.com/book/show/6900.Tuesdays_with_Morrie',
        'cover_image': 'https://media.s-bol.com/BBgo1On32PLJ/534x840.jpg'
    },
    'angry': {
        'book_name': 'The Art of War by Sun Tzu',
        'book_link': 'https://www.goodreads.com/book/show/10534.The_Art_of_War',
        'cover_image': 'https://imgv2-2-f.scribdassets.com/img/word_document/375004467/original/ca16a4c1b1/1577199238?v=1'
    },
    'relaxed': {
        'book_name': 'The Little Prince by Antoine de Saint-Exupéry',
        'book_link': 'https://www.goodreads.com/book/show/157993.The_Little_Prince',
        'cover_image': 'https://alpha.onemorelibrary.com/images/antoine-de-saint-exupery/the-little-prince.jpg'
    }
}

@recomm_bp.route('/recomm', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_mood = request.form['mood']
        song_info = mood_to_song.get(selected_mood)
        movie_info = mood_to_movie.get(selected_mood)
        book_info = mood_to_book.get(selected_mood)

        # Save choices into database with proper timestamps
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('INSERT INTO mood_records (mood, choice_type, choice_name) VALUES (?, ?, ?)', 
                  (selected_mood, 'song', song_info['song_name']))
        c.execute('INSERT INTO mood_records (mood, choice_type, choice_name) VALUES (?, ?, ?)', 
                  (selected_mood, 'movie', movie_info['movie_name']))
        c.execute('INSERT INTO mood_records (mood, choice_type, choice_name) VALUES (?, ?, ?)', 
                  (selected_mood, 'book', book_info['book_name']))

        conn.commit()
        conn.close()

        return render_template('result.html', mood=selected_mood, song_info=song_info, movie_info=movie_info, book_info=book_info)

    return render_template('recomm.html') 
