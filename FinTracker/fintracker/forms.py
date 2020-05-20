from flask_wtf import Form
from wtforms.fields import TextField, SubmitField, PasswordField, DateField
from wtforms import validators
from fintracker.models import db, User, City, Category
from wtforms.ext.sqlalchemy.fields import QuerySelectField 


class SignupForm(Form):
  first_name = TextField("First name",  [validators.Required("Please enter your first name.")])
  last_name = TextField("Last name",  [validators.Required("Please enter your last name.")])
  email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
  username = TextField("Username",  [validators.Required("Please enter your user name.")])
  submit = SubmitField("Create account")

  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)

  def validate(self):
    if not Form.validate(self):
      return False
    
    user = User.query.filter_by(email = self.email.data.lower()).first()
    if user:
      self.email.errors.append("That email is already taken")
      return False
    else:
      return True

class SigninForm(Form):
  email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
  submit = SubmitField("Sign In")
  
  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)

  def validate(self):
    if not Form.validate(self):
      return False
    
    user = User.query.filter_by(email = self.email.data).first()
    if user and user.check_password(self.password.data):
      return True
    else:
      self.email.errors.append("Invalid e-mail or password")
      return False


def City_choice():
    return City.query
  
class SearchForm(Form):
    dt_from = DateField('Pick a Date', format="%d/%m/%Y")
    dt_to = DateField('Pick a Date', format="%d/%m/%Y")
    city = QuerySelectField(label='City', query_factory = City_choice, allow_blank=True)
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

def Category_choice():
    return Category.query
    
class AddForm(Form):
    dt=DateField('Date', [validators.Required("Please enter date.")], format="%d/%m/%Y")
    category=QuerySelectField('Category', [validators.Required("Please enter category.")], query_factory = Category_choice, allow_blank=True)
    sum_amount=TextField('Sum', [validators.Required("Please enter category."), validators.Regexp('^(0|[1-9][0-9]*)$', message="Sum field can contain only numbers")])
    submit = SubmitField("Add")
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
    

    
    
    

  

