from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'jen123'

# Configure SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------------------------ Models ------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.String(50))  
    address = db.Column(db.String(255)) 

# ------------------------ Functions ------------------------

def register_user(username, password, name, birthday, address):
    if User.query.filter_by(username=username).first():
        return False
    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password, name=name, age=birthday, address=address)
    db.session.add(user)
    db.session.commit()
    return True

def check_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

# ------------------------ Routes ------------------------

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('login')) 
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        birthday = request.form['birthday']
        address = request.form['address']

        if register_user(username, password, name, birthday, address):
            session['username'] = username
            return redirect(url_for('login'))
        else:
            flash('Username already exists!')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = check_user(username, password)
        if user:
            session['username'] = username
            flash('Login successful!')
            return redirect(url_for('login'))  
            flash('Invalid username or password!')
    return render_template('login.html')

# ------------------------ Main ------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
