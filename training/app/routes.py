# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, Response
import os
import cv2
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models import users, save_users
from app.simple_facerec import SimpleFacerec
import time
from io import BytesIO
from flask import Response

bp = Blueprint('auth', __name__)
bp.config = {
    'UPLOAD_FOLDER': 'app/static/uploads'
}

sfr = SimpleFacerec()
sfr.load_encoding_images("app/static/uploads")

print(f"Loaded {len(sfr.known_face_encodings)} face encodings.")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if the profile picture is provided
        if 'profile_picture' not in request.files:
            return 'No file part'
        file = request.files['profile_picture']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            # Use the username as the filename
            ext = file.filename.rsplit('.', 1)[1].lower()  # Extract the file extension
            filename = secure_filename(f"{username}.{ext}")  # Combine username and extension
            filepath = os.path.join(bp.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            profile_picture_path = 'uploads/' + filename  # Save relative path for later use

        # Check if the email is already registered
        if email in users:
            return 'Email already registered'
        
        # Save user details
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        users[email] = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'profile_picture': profile_picture_path
        }
        save_users(users)  # Save immediately after a new registration
        #users = load_users()  # Reload updated data if needed
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


@bp.route('/camera', methods=['GET'])
def camera():
    return render_template('camera.html')

def generate_frames():
    cap = cv2.VideoCapture(2)  # Try accessing camera at index 2

    if not cap.isOpened():  # Fallback to index 0
        print("Camera index 2 not available. Trying index 0.")
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():  # If still not available, exit
        print("Error: No accessible camera found.")
        return

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Error: Unable to capture video frame.")
            break

        # Detect Faces
        face_locations, face_names = sfr.detect_known_faces(frame)
        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
            # Annotate frame
            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

        # Encode frame to JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            print("Error: Failed to encode frame.")
            continue

        # Send to browser
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

    cap.release()


@bp.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')