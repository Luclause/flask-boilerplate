import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Flask secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-sauce'

    # Location of the SQLite DB
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

    # Disable signalling to application on DB updates
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Error logging
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMIN = ['somesnorkshit@gmail.com']

    # APP Settings
    POSTS_PER_PAGE = 3

    # Languages
    LANGUAGES = ['en', 'es']
    
    # Microsoft Translator Key
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')