from flask import session
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    RadioField,
    TextAreaField,
    HiddenField
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user

from flask_app.models import User

class QuestionForm(FlaskForm):
    question = StringField("Question:", validators=[DataRequired(), Length(min=1, max=100)])
    details = TextAreaField("Details:", validators=[Length(min=1)])
    submit = SubmitField("Submit Question!")
    
class UpdateQuestionForm(FlaskForm):
    question = TextAreaField("Question:", validators=[Length(min=1)])
    details = TextAreaField("Details:", validators=[Length(min=1)])
    submit = SubmitField("Update Question")

class AnswerForm(FlaskForm):
    answer = TextAreaField("Answer:", validators=[Length(min=1)])
    submit = SubmitField("Submit Answer")
    
class UpdateAnswerForm(FlaskForm):
    answer = TextAreaField("Answer:", validators=[Length(min=1)])
    submit = SubmitField("Update Answer")

class CommentForm(FlaskForm):
    comment = TextAreaField("Comment:", validators=[Length(min=1)])
    answerID = HiddenField("answerID")
    submit = SubmitField("Submit Comment")
