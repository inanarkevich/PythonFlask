from fintracker import app
from flask import render_template, request, flash, session, url_for, redirect
from fintracker.forms import SignupForm, SigninForm, SearchForm, AddForm
from fintracker.models import db, User, Transaction
from sqlalchemy.sql import text
import datetime



@app.route('/')
@app.route('/signin', methods=['GET', 'POST'])
def signin():
  form = SigninForm()

  if 'email' in session:
    return redirect(url_for('dashboard')) 
      
  if request.method == 'POST' and form.validate():
    
      session['email'] = form.email.data
      return redirect(url_for('dashboard'))
                
  return render_template('signin.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
  form = SignupForm()

  if 'email' in session:
    return redirect(url_for('dashboard')) 
  
  if request.method == 'POST' and form.validate():
   
      newuser = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data, form.username.data)
      db.session.add(newuser)
      db.session.commit()
      
      session['email'] = newuser.email
      return redirect(url_for('dashboard'))
  
  return render_template('signup.html', form=form)



@app.route('/signout')
def signout():

  if 'email' not in session:
    return redirect(url_for('signin'))
    
  session.pop('email', None)
  return redirect(url_for('signin'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    search = SearchForm(request.form)
    user = User.query.filter_by(email = session['email']).first()
    
    #select average values
    sql= """SELECT ROUND(AVG(Income),2) as avg from
(SELECT SUM(tr.sum_amount) as Income from transactions tr 
where tr.category_id in (select c.category_Id from category_types c 
INNER JOIN operation_types op ON op.operation_id=c.operation_id AND op.operation=:operation)
GROUP BY strftime('%m-%Y', Date), user_id)"""
    transactions_inc = db.engine.execute(text(sql), {"operation":'Income'} ).fetchall()
    transactions_exp = db.engine.execute(text(sql), {"operation":'Expenses'} ).fetchall()
    #select values for plot
    sql_plot="""select sum(tr.sum_amount) as summa, c.category as category from transactions tr
INNER JOIN category_types c ON tr.category_id = c.category_id
where tr.category_id in (select c.category_Id from category_types c INNER JOIN operation_types op ON op.operation_id=c.operation_id AND op.operation='Expenses')
GROUP BY c.category"""
    transactions_plot = db.engine.execute(text(sql_plot)).fetchall()

    if 'email' not in session:
      return redirect(url_for('signin'))

    user = User.query.filter_by(email = session['email']).first()

    if user is None:
      return redirect(url_for('signin'))
    

    if request.method == 'POST':
        return search_results(search)
    return render_template('dashboard.html',title='Trends', max=5000, transactions_inc=transactions_inc, transactions_exp=transactions_exp, transactions_plot=transactions_plot, user=user, form=search)



def search_results(search):
    search = SearchForm(request.form)
    user = User.query.filter_by(email = session['email']).first()
    now = datetime.datetime.now()

    
    if not search.dt_from.data:
        search_dt_from = '1900-01-01'
    else: 
        search_dt_from = search.dt_from.data
    
    if not search.dt_to.data:
        search_dt_to = now.strftime("%Y-%m-%d")
    else:
        search_dt_to = search.dt_to.data
    
    if not search.city.data:
        sql= """SELECT ROUND(AVG(Income),2) as avg from
(SELECT SUM(tr.sum_amount) as Income from transactions tr 
where tr.category_id in (select c.category_Id from category_types c INNER JOIN operation_types op ON op.operation_id=c.operation_id AND op.operation=:operation)
AND tr.date BETWEEN :date1 AND :date2
GROUP BY strftime('%m-%Y', Date), user_id)"""
        transactions_inc = db.engine.execute(text(sql), {"operation":'Income', "date1":search_dt_from, "date2":search_dt_to} ).fetchall()
        transactions_exp = db.engine.execute(text(sql), {"operation":'Expenses', "date1":search_dt_from, "date2":search_dt_to} ).fetchall()
        sql_plot="""select sum(tr.sum_amount) as summa, c.category as category from transactions tr
INNER JOIN category_types c ON tr.category_id = c.category_id
where tr.category_id in (select c.category_Id from category_types c INNER JOIN operation_types op ON op.operation_id=c.operation_id AND op.operation='Expenses')
AND tr.date BETWEEN :date1 AND :date2
GROUP BY c.category"""
        transactions_plot = db.engine.execute(text(sql_plot), {"date1":search_dt_from, "date2":search_dt_to}).fetchall()
    else:
        a = str(search.city.data)
        sql= """SELECT ROUND(AVG(Income),2) as avg from
(SELECT SUM(tr.sum_amount) as Income from transactions tr 
where tr.user_id in (SELECT us.user_id FROM users us INNER join addresses ad ON us.address_id=ad.address_id AND ad.city=:city) 
AND tr.category_id in (select c.category_Id from category_types c INNER JOIN operation_types op ON op.operation_id=c.operation_id AND op.operation=:operation)
AND tr.date BETWEEN :date1 AND :date2
GROUP BY strftime('%m-%Y', Date), user_id)"""
        transactions_inc = db.engine.execute(text(sql), {"city":a, "operation":'Income', "date1":search_dt_from, "date2":search_dt_to} ).fetchall()
        transactions_exp = db.engine.execute(text(sql), {"city":a, "operation":'Expenses', "date1":search_dt_from, "date2":search_dt_to} ).fetchall()
    
        sql_plot="""select sum(tr.sum_amount) as summa, c.category as category from transactions tr
INNER JOIN category_types c ON tr.category_id = c.category_id
where tr.category_id in (select c.category_Id from category_types c INNER JOIN operation_types op ON op.operation_id=c.operation_id AND op.operation='Expenses')
AND tr.user_id in (SELECT us.user_id FROM users us INNER join addresses ad ON us.address_id=ad.address_id AND ad.city=:city)
AND tr.date BETWEEN :date1 AND :date2
GROUP BY c.category"""
        transactions_plot = db.engine.execute(text(sql_plot), {"city":a, "operation":'Expenses', "date1":search_dt_from, "date2":search_dt_to}).fetchall()
    
    
    return render_template('dashboard.html', title='Trends', max=5000, transactions_inc=transactions_inc, transactions_exp=transactions_exp, transactions_plot=transactions_plot, user=user, form=search)




@app.route('/tracker', methods=['GET','POST'])
def tracker():
    search = SearchForm(request.form)
    user = User.query.filter_by(email=session['email']).first()
    user_id = user.user_id

    m = """SELECT tr.date as Date, tr.sum_amount as Sum, c.category as Category, o.operation as Operation, tr.transaction_id as Id
FROM transactions as tr
INNER JOIN category_types as c ON tr.category_id = c.category_id
INNER JOIN operation_types as o ON o.operation_id = c.operation_id
WHERE tr.user_id = :user 
ORDER BY tr.date DESC"""

    k = db.engine.execute(text(m), {"user": user_id}).fetchall()

    if 'email' not in session:
        return redirect(url_for('signin'))

    if user is None:
        return redirect(url_for('signin'))
  
    if request.method == 'POST':
       return search_results_tr(search)
    return render_template('tracker.html', k=k, form=search)

def search_results_tr(search):
    search = SearchForm(request.form)
    user = User.query.filter_by(email=session['email']).first()
    user_id = user.user_id
    now = datetime.datetime.now()

    if not search.dt_from.data:
        search_dt_from = '1900-01-01'
    else: 
        search_dt_from = search.dt_from.data
    
    if not search.dt_to.data:
        search_dt_to = now.strftime("%Y-%m-%d")
    else:
        search_dt_to = search.dt_to.data
        
    m = """SELECT tr.date as Date, tr.sum_amount as Sum, c.category as Category, o.operation as Operation, tr.transaction_id as Id
FROM transactions as tr
INNER JOIN category_types as c ON tr.category_id = c.category_id
INNER JOIN operation_types as o ON o.operation_id = c.operation_id
WHERE tr.user_id = :user
AND tr.date BETWEEN :date1 AND :date2 
ORDER BY tr.date DESC"""

    k = db.engine.execute(text(m), {"user": user_id, "date1":search_dt_from, "date2":search_dt_to}).fetchall()
    return render_template('tracker.html', k=k, form=search)



@app.route('/new', methods=['GET', 'POST'])
def new():
    form = AddForm (request.form)
    if request.method == 'POST' and form.validate():
        #save the transaction
        transaction=Transaction()
        save_changes(transaction, form)
        flash ("Transaction is added")
        return redirect ('/tracker')
    return render_template('new.html', form=form)

def save_changes(transaction, form):
    user = User.query.filter_by(email=session['email']).first()
    user_id = user.user_id
    cat_label = str(form.category.data)
    sql_cat = """select category_id from category_types where category = :category"""
    cat_id_query = db.engine.execute(text(sql_cat), {"category": cat_label}).fetchall()
    cat_id = [x[0] for x in cat_id_query][0]

    
    transaction.user_id = user_id
    transaction.category_id = cat_id
    transaction.sum_amount=form.sum_amount.data
    transaction.date=form.dt.data
    
    db.session.add(transaction)
    db.session.commit()
    
@app.route("/delete", methods=["POST"])
def delete():
    Id = request.form.get("Id")
    transaction = Transaction.query.filter_by(transaction_id=Id).first()
    db.session.delete(transaction)
    db.session.commit()
    return redirect("/tracker")