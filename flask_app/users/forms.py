from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user

from flask_app.models import User
from flask_app import db, bcrypt

import pyotp
import re

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    confirm_password = PasswordField("Comfirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username is taken')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email is taken')

    def validate_password(self, password):
        errors = ""
        if not len(password.data) >= 6 and len(password.data) <= 20:
            errors += "Password must be between 6 and 20 characters long. "
        if not re.search("[!\"#$%&\\'()*+\\,\\-\\.\\/:;<=>?@\\[\\]\\^_`{\\|}\\\]{1,}", password.data):
            errors += "Password must include at least 1 symbol. "
        if not re.search("[a-z]{1,}", password.data):
            errors += "\nPassword must include at least 1 lowercase letter. "
        if not re.search("[A-Z]{1,}", password.data):
            errors +="Password must include at least 1 uppercase letter. "
        if not re.search("[0-9]{1,}", password.data):
            errors += "Password must include at least 1 number. "
        if len(errors) > 0:
            raise ValidationError(errors)

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    otp = StringField("Authenticator Code", validators=[DataRequired(), Length(min=6,max=6)])
    submit = SubmitField("Login")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError("That username does not exist in our database.")
        if user.confirmed == False:
            raise ValidationError("Account has not been confirmed. Check your email to confirm your account.")


class UpdateUsernameForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    submit = SubmitField("Update", _name="usernameUpdate")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username is taken')

class UpdateEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField("Update", _name="emailUpdate")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email is taken')

class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm New Password", validators=[DataRequired(), EqualTo("new_password")])
    submit = SubmitField("Update", _name="passwordUpdate")

    def validate_old_password(self, old_password):
        if not bcrypt.check_password_hash(current_user.password, old_password.data):
            raise ValidationError('Current password is incorrect.')

    def validate_new_password(self, new_password):
        errors = ""
        if not len(new_password.data) >= 6 and len(new_password.data) <= 20:
            errors += "Password must be between 6 and 20 characters long. "
        if not re.search("[!\"#$%&\\'()*+\\,\\-\\.\\/:;<=>?@\\[\\]\\^_`{\\|}\\\]{1,}", new_password.data):
            errors += "Password must include at least 1 symbol. "
        if not re.search("[a-z]{1,}", new_password.data):
            errors += "\nPassword must include at least 1 lowercase letter. "
        if not re.search("[A-Z]{1,}", new_password.data):
            errors +="Password must include at least 1 uppercase letter. "
        if not re.search("[0-9]{1,}", new_password.data):
            errors += "Password must include at least 1 number. "
        if len(errors) > 0:
            raise ValidationError(errors)
