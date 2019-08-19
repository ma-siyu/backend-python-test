from flask import Flask, g
import sqlite3
from flask_sqlalchemy import SQLAlchemy

# configuration
DATABASE = '/tmp/alayatodo.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
GOOGLE_RECAPTCHA_SITE_KEY = '6Le9xbMUAAAAAKXbIMF9fxtGaYFreySrAz03rUEr'
GOOGLE_RECAPTCHA_SECRET_KEY = '6Le9xbMUAAAAAIFJC8Meiil671U289dlONMS_hwC'

app = Flask(__name__)
app.config.from_object(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/alayatodo.db"

db = SQLAlchemy(app)
with app.app_context():
    import alayatodo.views
    db.create_all()


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    db.session.commit()
    db.session.close()
