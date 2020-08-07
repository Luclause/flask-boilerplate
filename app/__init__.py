from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

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

from app import routes