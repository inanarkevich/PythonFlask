from flask import Flask
import os
app = Flask(__name__)

app.secret_key = os.urandom(9)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fintracker.db'

from fintracker.models import db
db.init_app(app)

import fintracker.routes

