from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLite DB
db = SQLAlchemy(app)

# Initialize Migration engine
migrate = Migrate(app, db)

# Initialize Login Manager
login = LoginManager(app)
login.login_view = 'login'

# Logging errors to Admins through SMTP
if not app.debug:
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

from app import routes, models, errors