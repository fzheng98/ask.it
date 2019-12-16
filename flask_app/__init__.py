from logging.config import dictConfig

from flask import Flask, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_mail import Mail

csp = {
    "default-src": [
        "'self'",
    ],
    'img-src': '*',
    'script-src': ['https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js',
                    'https://code.jquery.com/jquery-3.3.1.slim.min.js',
                    'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js'],
    'style-src': ["'self'",'custom.css', 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css']
}

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

talisman = Talisman()
mail = Mail()
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "users.login"


def create_app():
    app = Flask(__name__)
    app.config[
        "SECRET_KEY"
    ] = b"0)\x08\xe3\xc9\xc8\x83\xb8\xf1\xda\xdb\xd7\xb3\x0eT\x17"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.update(
        MAIL_SERVER = 'smtp.gmail.com',
    	MAIL_PORT = 465,
        MAIL_USE_SSL = True,
        MAIL_USERNAME = 'ask.itsender@gmail.com',
        MAIL_PASSWORD = 'CMSC388JProject',
        MAIL_DEFAULT_SENDER = 'ask.itsender@gmail.com'
    )

    talisman.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from flask_app.main.routes import main
    from flask_app.users.routes import users
    from flask_app.questions.routes import questions

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(questions)

    with app.app_context():
        db.create_all()

    talisman.content_security_policy = csp
    talisman.content_security_policy_report_uri = "/csp_error_handling"

    return app
