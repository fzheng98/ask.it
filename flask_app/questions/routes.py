from flask import (
    render_template,
    url_for,
    redirect,
    request,
    Blueprint,
    session,
    current_app,
)
from flask_login import login_user, current_user, logout_user, login_required

from flask_app import db, bcrypt
from flask_app.models import User, Question, Answer, Comment
from flask_app.questions.forms import QuestionForm, AnswerForm


questions = Blueprint("questions", __name__)

@questions.route("/ask_question", methods=["GET", "POST"])
@login_required
def ask_question():
    form = QuestionForm()

    if form.validate_on_submit():

        question = Question(
            question=form.question.data,
            details=form.details.data,
            author=current_user,
        )

        db.session.add(question)
        db.session.commit()

        return redirect(url_for("main.index"))

    return render_template("ask_question.html", title="Ask a Question", form=form)
    

@questions.route("/questions/<question>", methods=["GET", "POST"])
def question_detail(question):
    form = AnswerForm()

    question = Question.query.filter_by(question=question).first()

    if form.validate_on_submit():
        comment = Comment(content=form.text.data, author=current_user, question=question)

        db.session.add(comment)
        db.session.commit()

        return redirect(request.path)

    answer = question.answer
    comments = question.comments[::-1]

    return render_template("question_detail.html", question=question, answer=answer, comments=comments, form=form)
