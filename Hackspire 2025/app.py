from flask import Flask, render_template, redirect, url_for
from auth import auth_bp, db
from mood import mood_bp, init_mood_db
# from chatbot import chatbot_bp
from gemma import gemma_bp  # Import the Gemma blueprint
from recomm import recomm_bp
from commu import commu_bp
import os

app = Flask(__name__)
app.secret_key = 'secret_key'

# Ensure the instance folder exists
if not os.path.exists('instance'):
    os.makedirs('instance')

# Use an absolute path for the database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.abspath('instance/database.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(mood_bp)
# app.register_blueprint(chatbot_bp)
app.register_blueprint(gemma_bp)  # Register the Gemma blueprint
app.register_blueprint(recomm_bp)  # Register the recomm page bluprint
app.register_blueprint(commu_bp)  # Register the commu page bluprint

# Landing page route
@app.route('/')
def landing_page():
    return render_template('landingpage.html')

# Homepage route
@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

# Setup databases
with app.app_context():
    db.create_all()  # Creates tables for `auth` (User model)
    init_mood_db()   # Initializes the mood journal database

if __name__ == '__main__':
    app.run(debug=True)
