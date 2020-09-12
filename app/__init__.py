from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()

def create_app(config_class=Config):

    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    # Register the error handling blueprint
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # Register the authentication blueprint
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Logging errors to Admins through SMTP
    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            # Set authentication
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

            # Set secure
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()

            # Build mailing arguments
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='noreply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMIN'],
                subject='Microblog Failure',
                credentials=auth,
                secure=secure
            )

            # Log on Error and mail Admins
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # Log errors to a file
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                        backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(app.config['LANGUAGES'])
        # return 'es'

    return app