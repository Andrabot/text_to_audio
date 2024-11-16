from functools import wraps
from flask import session, redirect, url_for, flash

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'admin':
            flash("You do not have permission to access this page.")
            return redirect(url_for('home'))  # Halaman home jika akses ditolak
        return f(*args, **kwargs)
    return decorated_function
