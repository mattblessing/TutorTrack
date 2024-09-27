from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_login import LoginManager
from tutortrack.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    from tutortrack.users.routes import users
    from tutortrack.other.routes import other
    from tutortrack.account.routes import account
    from tutortrack.sessions.routes import sessions
    from tutortrack.topics.routes import topics
    from tutortrack.results.routes import results
    from tutortrack.reports.routes import reports

    app.register_blueprint(users)
    app.register_blueprint(other)
    app.register_blueprint(account)
    app.register_blueprint(sessions)
    app.register_blueprint(topics)
    app.register_blueprint(results)
    app.register_blueprint(reports)

    return app
