from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
from flask_login import UserMixin


db = SQLAlchemy()

class User(UserMixin, db.Model):
  __tablename__ = 'users'
  user_id = db.Column(db.Integer, primary_key = True)
  first_name = db.Column(db.String(100))
  last_name = db.Column(db.String(100))
  email = db.Column(db.String(120), unique=True)
  password_hash = db.Column(db.String(54))
  username = db.Column(db.String(100))
  
  def __init__(self, first_name, last_name, email, password, username):
    self.first_name = first_name.title()
    self.last_name = last_name.title()
    self.email = email.lower()
    self.set_password(password)
    self.username = username.lower()
    
  def set_password(self, password):
    self.password_hash = generate_password_hash(password)
  
  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

class City (db.Model):
  __tablename__ = 'addresses'
  address_id = db.Column(db.Integer, primary_key = True)
  city = db.Column(db.String(35)) 
  
  def __init__(self, city):
        self.city = city
  
  def __str__(self):
      return self.city
  
  
  
class Category(db.Model):
    __tablename__ = 'category_types'
    category_id = db.Column(db.Integer, primary_key = True)
    category = db.Column(db.String(35))
    
    def __init__(self, category):
        self.category = category
    
    def __str__(self):
        return self.category
    

    
class Transaction (db.Model):
    __tablename__ = 'transactions'
    transaction_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer)
    category_id = db.Column(db.Integer)
    sum_amount = db.Column(db.Numeric(35))
    date = db.Column(db.Date)
    

    

  
  
