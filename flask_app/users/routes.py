from flask import render_template, url_for, redirect, request, Blueprint, session
from flask_login import login_user, current_user, logout_user, login_required

from flask_app import db, bcrypt
from flask_app.models import User, Question
from flask_app.users.forms import RegistrationForm, LoginForm, UpdateUsernameForm, UpdateEmailForm, UpdatePasswordForm

import qrcode
import qrcode.image.svg as svg
import pyotp

from io import BytesIO

users = Blueprint("users", __name__)

@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        db.session.add(user)
        db.session.commit()
        session['reg_username'] = user.username

        return redirect(url_for('users.tfa'))

    return render_template('register.html', form=form)

@users.route("/tfa")
def tfa():
    if 'reg_username' not in session:
        return redirect(url_for('main.index'))

    headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0' # Expire immediately, so browser has to reverify everytime
    }

    return render_template('tfa.html'), headers

@users.route("/qr_code")
def qr_code():
    if 'reg_username' not in session:
        return redirect(url_for('main.index'))

    user = User.query.filter_by(username=session['reg_username']).first()
    session.pop('reg_username')
    img = qrcode.make(user.get_auth_uri(), image_factory=svg.SvgPathImage)
    stream = BytesIO()
    img.save(stream)

    headers = {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0' # Expire immediately, so browser has to reverify everytime
    }

    return stream.getvalue(), headers

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print(user)

        if user is not None and bcrypt.check_password_hash(user.password, form.password.data) and form.otp.data == pyotp.TOTP(user.otp_secret).now():
            login_user(user)
            return redirect(url_for('main.user_detail', username=form.username.data))

    return render_template('login.html', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    userForm = UpdateUsernameForm()
    emailForm = UpdateEmailForm()
    passwordForm = UpdatePasswordForm()
    print(request.form)
    if request.method == 'POST':
        if userForm.validate_on_submit():
            current_user.username = userForm.username.data
            db.session.commit()
            return redirect(url_for('main.user_detail', username=current_user.username))
        elif emailForm.is_submitted() and emailForm.validate_on_submit():
            current_user.email = emailForm.email.data
            db.session.commit()
            return redirect(url_for('main.user_detail', username=current_user.username))
        elif passwordForm.is_submitted() and passwordForm.validate_on_submit():
            hashed = bcrypt.generate_password_hash(passwordForm.password.data).decode('utf-8')
            user = User.query.filter_by(username=current_user.username).first()
            user.password = hashed
            db.session.commit()
            logout_user()
            return redirect(url_for('users.login'))

    userForm.username.data = current_user.username
    emailForm.email.data = current_user.email
    return render_template('account.html', title='Account', userForm=userForm, emailForm=emailForm, passwordForm=passwordForm)
