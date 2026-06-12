from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app.models.user import User
from app import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))
        flash('Username atau password salah!', 'error')
    return render_template('login.html')

@auth.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email    = request.form.get('email')
    password = request.form.get('password')
    
    # Check if username or email already exists
    if User.query.filter((User.username == username) | (User.email == email)).first():
        flash('Username atau email sudah terdaftar!', 'error')
        return redirect(url_for('auth.login'))
        
    try:
        user = User(username=username, email=email, role='user')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registrasi berhasil! Silakan masuk.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Terjadi kesalahan saat registrasi. Silakan coba lagi.', 'error')
        
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.landing'))