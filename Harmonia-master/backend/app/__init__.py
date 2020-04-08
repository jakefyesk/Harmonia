from app.config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__,
            static_url_path='',
            static_folder='assets',
            template_folder='templates')
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

def save_and_commit(item):
	db.session.add(item)
	db.session.commit()
db.save = save_and_commit

from app import routes, models
