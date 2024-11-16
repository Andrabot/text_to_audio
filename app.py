from flask import Flask, render_template, request, redirect, url_for, session, flash
from gtts import gTTS
import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = 'secretkey'
AUDIO_FOLDER = 'static/audio'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Fungsi koneksi ke database
def get_db_connection():
    conn = sqlite3.connect('user_data.db')
    conn.row_factory = sqlite3.Row
    return conn

# Fungsi untuk memeriksa ekstensi file yang diperbolehkan
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Decorator untuk akses admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'admin':
            flash("You do not have permission to access this page.")
            return redirect(url_for('home'))  # Halaman home jika akses ditolak
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    limit_left = 5
    if 'user_id' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        limit_left = max(0, 5 - user['usage_count']) if user['payment_status'] == "approved" else 0
        conn.close()
    return render_template('index.html', limit_left=limit_left, username=session.get('username'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, 'user'))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists.")
            return redirect(url_for('register'))
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_role'] = user['role']  # Simpan peran pengguna ke sesi
            return redirect(url_for('home'))
        else:
            flash("Login failed. Check your username and password.")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/convert', methods=['POST'])
def convert():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    text = request.form['text']
    language = request.form['language']
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if user['usage_count'] >= 5 or user['payment_status'] != "approved":
        return redirect(url_for('purchase_license'))

    tts = gTTS(text=text, lang=language)
    audio_file = os.path.join(AUDIO_FOLDER, f'output_audio_{user_id}.mp3')
    tts.save(audio_file)
    cursor.execute('UPDATE users SET usage_count = usage_count + 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return render_template('index.html', audio_file=f'audio/output_audio_{user_id}.mp3')

@app.route('/purchase_license', methods=['GET', 'POST'])
def purchase_license():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        license_type = request.form['license_type']
        payment_method = request.form['payment_method']
        file = request.files['payment_proof']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            user_id = session['user_id']
            conn = get_db_connection()
            cursor = conn.cursor()

            new_expiry = datetime.now() + (timedelta(weeks=1) if license_type == 'weekly' else timedelta(weeks=4))
            cursor.execute('''
                UPDATE users 
                SET license_expiry = ?, usage_count = 0, payment_method = ?, payment_proof = ?, payment_status = 'pending'
                WHERE id = ?
            ''', (new_expiry.strftime('%Y-%m-%d'), payment_method, file_path, user_id))

            conn.commit()
            conn.close()
            flash("Pembayaran berhasil diunggah. Menunggu konfirmasi.")
            return redirect(url_for('home'))
        else:
            flash("File tidak valid. Silakan upload bukti pembayaran dalam format PNG, JPG, JPEG, atau PDF.")
            return redirect(url_for('purchase_license'))
    
    return render_template('purchase.html')

@app.route('/admin/verify_payments')
@admin_required
def verify_payments():
    print("User Role in session:", session.get('user_role'))  # Memeriksa role di sesi
    conn = get_db_connection()
    payments = conn.execute('SELECT * FROM users WHERE payment_status = "pending"').fetchall()
    conn.close()
    return render_template('verify_payments.html', payments=payments)

@app.route('/admin/approve_payment/<int:user_id>', methods=['POST'])
@admin_required
def approve_payment(user_id):
    conn = get_db_connection()
    conn.execute('UPDATE users SET payment_status = "approved", usage_count = 0 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    flash("Pembayaran disetujui.")
    return redirect(url_for('verify_payments'))

if __name__ == '__main__':
    app.run(debug=True)
