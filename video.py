from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Set up upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route to upload videos
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        video = request.files['video']
        name = request.form['name']
        category = request.form['category']
        
        # Check if a file was uploaded and if the file is allowed
        if video and allowed_file(video.filename):
            filename = secure_filename(video.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            video.save(file_path)
            
            # Get current time and date for the upload time
            upload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Insert video data into the database
            conn = get_db_connection()
            conn.execute('INSERT INTO videos (name, category, upload_time, file_path) VALUES (?, ?, ?, ?)',
                         (name, category, upload_time, file_path))
            conn.commit()
            conn.close()
            
            return redirect(url_for('view_videos'))
    return render_template('upload.html')

# Route to view all uploaded videos
@app.route('/videos')
def view_videos():
    conn = get_db_connection()
    videos = conn.execute('SELECT * FROM videos').fetchall()
    conn.close()
    return render_template('view_video.html', videos=videos)

# Route to view a single video
@app.route('/video/<int:video_id>')
def video_details(video_id):
    conn = get_db_connection()
    video = conn.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()
    conn.close()
    if video:
        return render_template('video_details.html', video=video)
    else:
        return "Video not found!", 404

if __name__ == '__main__':
    app.run(debug=True)
