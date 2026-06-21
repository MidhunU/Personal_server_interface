import os
import sys
import socket
import math
import datetime
import shutil
import subprocess
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'antigravity-local-transfer-secret-key-1337'

# Configure Upload Folder to target Android Gallery
# Tries the Termux symlink path first, then absolute Android Pictures directory, then local fallback
ANDROID_PATHS = [
    os.path.expanduser('~/storage/pictures/FlaskServerUploads'),
    '/storage/emulated/0/Pictures/FlaskServerUploads'
]

UPLOAD_FOLDER = None
for path in ANDROID_PATHS:
    try:
        os.makedirs(path, exist_ok=True)
        UPLOAD_FOLDER = path
        break
    except Exception:
        continue

if not UPLOAD_FOLDER:
    # Fallback to local workspace uploads directory if target Android path is inaccessible (e.g., during Windows dev)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set 1GB Max file size limit
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024

def get_local_ip():
    """Retrieve the primary local IP address of the server."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def format_size(size_bytes):
    """Format file size in human readable string."""
    if size_bytes == 0:
        return "0 Bytes"
    size_name = ("Bytes", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def get_file_icon(filename):
    """Return appropriate emoji icon based on file extension."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
        return '📦'
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']:
        return '🖼️'
    elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.webm', '.flv']:
        return '🎬'
    elif ext in ['.mp3', '.wav', '.ogg', '.flac', '.m4a']:
        return '🎵'
    elif ext in ['.pdf']:
        return '📕'
    elif ext in ['.txt', '.md', '.rtf', '.log']:
        return '📄'
    elif ext in ['.doc', '.docx', '.odt']:
        return '📝'
    elif ext in ['.xls', '.xlsx', '.ods', '.csv']:
        return '📊'
    elif ext in ['.ppt', '.pptx']:
        return '🎭'
    elif ext in ['.html', '.css', '.js', '.py', '.json', '.sh', '.bat', '.cmd', '.c', '.cpp', '.java']:
        return '💻'
    return '📄'

def get_files_list():
    """Scan upload folder and return metadata for all files."""
    files = []
    if not os.path.exists(UPLOAD_FOLDER):
        return files
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            files.append({
                'name': filename,
                'size': stat.st_size,
                'formatted_size': format_size(stat.st_size),
                'mtime': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'icon': get_file_icon(filename)
            })
    # Sort files by modification time, newest first
    files.sort(key=lambda x: x['mtime'], reverse=True)
    return files

@app.route('/')
def index():
    files_list = get_files_list()
    total_files = len(files_list)
    total_bytes = sum(f['size'] for f in files_list)
    total_size_str = format_size(total_bytes)
    
    return render_template(
        'index.html',
        files=files_list,
        total_files=total_files,
        total_size=total_size_str,
        ip_address=get_local_ip()
    )

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        flash('Invalid upload request format.', 'error')
        return redirect(url_for('index'))
    
    files = request.files.getlist('files')
    uploaded_count = 0
    errors = []
    
    for file in files:
        if file.filename == '':
            continue
        if file:
            filename = secure_filename(file.filename)
            if not filename:
                filename = f"uploaded_file_{int(datetime.datetime.now().timestamp())}"
            
            # Resolve duplicate names
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                filename = f"{base}({counter}){ext}"
                counter += 1
                
            try:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_count += 1
                
                # Trigger Android media scan if running under Termux, making it appear in gallery instantly
                try:
                    if shutil.which('termux-media-scan'):
                        subprocess.run(['termux-media-scan', filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
            except Exception as e:
                errors.append(f"Error saving {file.filename}: {str(e)}")
                
    if uploaded_count > 0:
        flash(f'Successfully uploaded {uploaded_count} file(s).', 'success')
    if errors:
        for err in errors:
            flash(err, 'error')
            
    if uploaded_count == 0 and not errors:
        flash('No files selected for upload.', 'warning')
        
    return redirect(url_for('index'))

@app.route('/download/<path:filename>')
def download_file(filename):
    safe_filename = secure_filename(os.path.basename(filename))
    return send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename, as_attachment=True)

@app.route('/delete/<path:filename>', methods=['POST'])
def delete_file(filename):
    safe_filename = secure_filename(os.path.basename(filename))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    
    if os.path.exists(filepath) and os.path.isfile(filepath):
        try:
            os.remove(filepath)
            flash(f'File "{safe_filename}" successfully deleted.', 'success')
        except Exception as e:
            flash(f'Error deleting file: {str(e)}', 'error')
    else:
        flash('File not found or already deleted.', 'error')
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    local_ip = get_local_ip()
    print("=" * 60)
    print("           ANTIGRAVITY LOCAL SHARE SERVER STARTED           ")
    print("=" * 60)
    print(f"Local Access:   http://localhost:5000")
    print(f"Network Access: http://{local_ip}:5000")
    print("=" * 60)
    print("Press Ctrl+C to stop the server.")
    print("-" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
