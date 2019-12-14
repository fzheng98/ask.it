from datetime import datetime
from flask_app import db, login_manager
from flask_login import UserMixin

import pyotp

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    otp_secret = db.Column(db.String(16), nullable=False)

    questions = db.relationship("Question", backref="author", lazy=True)
    answers = db.relationship("Answer", backref="author", lazy=True)
    comments = db.relationship("Comment", backref="author", lazy=True)
        
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # self.otp_secret = base64.b32encode(os.urandom(10)).decode()
        self.otp_secret = pyotp.random_base32()
    
    def get_auth_uri(self):
        servicer = 'Ask.it'

        return ('otpauth://totp/{0}:{1}?secret={2}&issuer={0}'.format(
            servicer, self.username, self.otp_secret
        ))
    
    def verify_totp(self, token):
        totp_client = pyotp.TOTP(self.otp_secret)
        return totp_client.verify(token)

    def __repr__(self):
        return "User('%s', '%s')" % (self.username, self.email)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    answer = db.relationship("Answer", backref="question", lazy=True)
    comments = db.relationship("Comment", backref="question", lazy=True)

    def __repr__(self):
        return "Question: '%s'" % self.question
        
class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)

    def __repr__(self):
        return "Answer: '%s'" % self.answer


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)

    def __repr__(self):
        return 'Comment created by "%s" for "%s"' % (
            self.author.username,
            self.question.question,
        )
