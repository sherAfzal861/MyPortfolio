from flask_sqlalchemy import SQLAlchemy
import os
# from app import app
from datetime import datetime  # Correct import
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sitemap import Sitemap

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogs.db'
app.config['SECRET_KEY'] = '6c78454fef445a51e505526d54882af0a2198ec09cf465b0'
app.config['SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS'] = True
ext = Sitemap(app=app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize the database
with app.app_context():
    db.create_all()
