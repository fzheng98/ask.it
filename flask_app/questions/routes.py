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
from flask_app.questions.forms import QuestionForm, AnswerForm, CommentForm, UpdateQuestionForm, UpdateAnswerForm

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


@questions.route("/questions/<question_id>", methods=["GET", "POST"])
def question_detail(question_id):
    answer_form = AnswerForm()
    comment_form = CommentForm()

    question = Question.query.filter_by(id=question_id).first()

    if answer_form.validate_on_submit():
        answer = Answer(
            answer=answer_form.answer.data,
            author=current_user,
            question=question,
            user_id=current_user.id
        )

        db.session.add(answer)
        db.session.commit()

        return redirect(request.path)

    if comment_form.validate_on_submit():
        answer = Answer.query.filter_by(id=comment_form.answerID.data).first()
        comment = Comment(
            comment=comment_form.comment.data,
            author=current_user,
            answer=answer,
            user_id=current_user.id
        )

        db.session.add(comment)
        db.session.commit()

        return redirect(request.path)

    answers = question.answers[::-1]
    num_answers = len(answers)
    user_answered = None
    if (current_user.is_authenticated):
        user_answered = any(answer.author.username == current_user.username for answer in answers)
    comments = []
    for answer in answers:
        comments.append(answer.comments[::-1])

    return render_template(
        "question_detail.html",
        question=question,
        answers_bundle=zip(answers, comments),
        num_answers=num_answers,
        answer_form=answer_form,
        comment_form=comment_form,
        user_answered=user_answered
    )


@questions.route("/update_question/<question_id>", methods=["GET", "POST"])
def update_question(question_id):
    form = UpdateQuestionForm()

    question = Question.query.filter_by(id=question_id).first()

    if form.validate_on_submit():
        question.question = form.question.data
        question.details = form.details.data
        db.session.commit()

        return redirect(url_for("questions.question_detail", question_id=question_id))

    return render_template("update_question.html", form=form, question=question)


@questions.route("/update_answer/<answer_id>", methods=["GET", "POST"])
def update_answer(answer_id):
    form = UpdateAnswerForm()

    answer = Answer.query.filter_by(id=answer_id).first()
    question = Question.query.filter_by(id=answer.question_id).first()

    if form.validate_on_submit():
        answer.answer = form.answer.data
        db.session.commit()

        return redirect(url_for("questions.question_detail", question_id=answer.question_id))

    return render_template("update_answer.html", form=form, question=question, answer=answer)
    