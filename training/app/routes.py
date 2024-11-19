from flask import Blueprint, render_template, request, redirect, url_for, session, Response
#import cv2
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from .models import users, save_users
#from .face_recognition_utils import load_known_faces, recognize_faces, draw_labels

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

bp = Blueprint('auth', __name__)
bp.config = {
    'UPLOAD_FOLDER': UPLOAD_FOLDER
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if 'profile_picture' not in request.files:
            return 'No file part'
        file = request.files['profile_picture']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(bp.config['UPLOAD_FOLDER'], filename))
            profile_picture_path = 'uploads/' + filename

        if email in users:
            return 'Email already registered'
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        users[email] = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'profile_picture': profile_picture_path
        }
        save_users(users)

        return redirect(url_for('auth.index'))
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = users.get(email)
        
        if user and check_password_hash(user['password'], password):
            session['user'] = user['username']
            session['profile_picture'] = user['profile_picture']
            return redirect(url_for('auth.dashboard'))
        return 'Login failed'
    return render_template('login.html')

@bp.route('/logout', methods=['GET'])
def logout():
    session.pop('user', None)
    session.pop('profile_picture', None)
    return redirect(url_for('auth.index'))

@bp.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', username=session['user'], profile_picture=session['profile_picture'])
    return redirect(url_for('auth.index'))

