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