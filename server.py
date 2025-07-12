from flask import Flask, request, send_from_directory, jsonify, redirect, url_for, render_template_string, session
from werkzeug.utils import secure_filename
import os, json
from PIL import Image
import io

UPLOAD_FOLDER = 'w'
GALLERY_JSON = 'gallery.json'
ADMIN_PASSWORD = 's3cret2024'  # Задай свой пароль
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Для сессий
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_gallery():
    if not os.path.exists(GALLERY_JSON):
        return []
    with open(GALLERY_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_gallery(data):
    with open(GALLERY_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/w/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/gallery.json')
def serve_gallery_json():
    return send_from_directory('.', GALLERY_JSON)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return send_from_directory('.', 'admin.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return 'Wrong password', 401
    return render_template_string('''
        <form method="post">
            <input type="password" name="password" placeholder="Password">
            <button type="submit">Login</button>
        </form>
    ''')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    files = request.files.getlist('file')
    captions = request.form.getlist('caption')
    if not files:
        return jsonify({'error': 'No file'}), 400
    gallery = load_gallery()
    responses = []
    for idx, file in enumerate(files):
        if file and allowed_file(file.filename):
            # Convert to webp
            try:
                img = Image.open(file.stream)
                webp_io = io.BytesIO()
                img.save(webp_io, format='WEBP')
                webp_io.seek(0)
                # Use .webp extension
                base = secure_filename(file.filename.rsplit('.', 1)[0])
                filename = f"{base}.webp"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                with open(filepath, 'wb') as f_out:
                    f_out.write(webp_io.read())
                # Add to gallery.json
                caption = captions[idx] if idx < len(captions) else ''
                gallery.append({'src': f'w/{filename}', 'caption': caption})
                responses.append({'file': filename, 'success': True})
            except Exception as e:
                responses.append({'file': file.filename, 'success': False, 'error': str(e)})
        else:
            responses.append({'file': file.filename, 'success': False, 'error': 'Invalid file'})
    save_gallery(gallery)
    return jsonify({'results': responses})

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True) 