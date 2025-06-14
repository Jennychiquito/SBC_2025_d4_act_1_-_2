from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'jen123'

# Upload folder for profile pictures
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------------------ Models ------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    birthday = db.Column(db.String(50))
    address = db.Column(db.String(255))
    photo = db.Column(db.String(255), default='default.png')

# ------------------ Helper Functions ------------------
def register_user(username, password, name, birthday, address, photo):
    if User.query.filter_by(username=username).first():
        return False
    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password, name=name, birthday=birthday, address=address, photo=photo)
    db.session.add(user)
    db.session.commit()
    return True

def check_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

# ------------------ Routes ------------------
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        birthday = request.form['birthday']
        address = request.form['address']

        # handle photo upload
        file = request.files['photo']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(photo_path)
        else:
            filename = 'default.png'

        if register_user(username, password, name, birthday, address, filename):
            session['username'] = username
            return redirect(url_for('profile'))
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
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password!')
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('User not found.')
        return redirect(url_for('login'))

    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

# ------------------ Main ------------------
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
