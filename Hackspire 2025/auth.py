from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt

db = SQLAlchemy()

auth_bp = Blueprint('auth', __name__)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user'] = user.name
            session['email'] = user.email
            flash("Login successful!", "success")
            return redirect(url_for('homepage'))  # Redirect to the home page
        else:
            flash("Invalid email or password.", "danger")
    return render_template('login.html', title="Login")

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for('auth.login'))

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login.html'))
    return render_template('login.html', title="Register")

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('email', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('homepage'))
