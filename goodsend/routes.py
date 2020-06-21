from goodsend import app, db, Message, mail
from flask import render_template, request, redirect, url_for
from goodsend.forms import UserInfoForm, LoginForm
#import models
# from goodsend.models import Waitlist, Onboarded, check_password_hash, generate_password_hash, Users
from goodsend.models import Users, check_password_hash,  generate_password_hash
from flask_login import login_required,login_user,current_user,logout_user
import os
import stripe

stripe.api_key = os.environ.get('STRIPE_KEY')


#Home Route
@app.route('/data')
@login_required
def home():
    balance = stripe.Balance.retrieve()
    registered = Users.query.all()
    # active = Onboarded.query.all()
    # active_count = 0
    count = 0
    users = 1
    current = current_user.id
    users_before = current - users
    for user in registered:
        count += 1
    # for a in active:
    #     active_count += 1
    return render_template("data.html", balance=balance, count=count, users_before=users_before)

#Register Route
@app.route('/register', methods=['GET','POST'])
def register():
    form = UserInfoForm()
    if request.method == 'POST' and form.validate():
        # Get Information
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        phone_number = form.phone_number.data
        password = form.password.data
        print("\n", first_name, last_name, email,phone_number,password)
        # Create an instance of User
        user = Users(first_name,last_name,email, phone_number, password)
        # Open and insert into waitlist
        db.session.add(user)
        # Save info into database
        db.session.commit()
        #Email service funnel for new users
        msg = Message(f'{email} has signed up!', recipients=[email, 'goodsendtest1@gmail.com'])
        msg.body =('Another user has signed up')
        msg.html = ('<h1> Welcome to Goodsend! </h1>' '<p> Thank you for signing up! </p>')
        mail.send(msg)
    return render_template('register.html',form = form)

#Login
@app.route('/login', methods = ['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        if form.email.data == "insert_email_address_here" and form.password.data == "password_here":
            return redirect(url_for('admin.index'))
        else:
            logged_user = Users.query.filter(Users.email == email).first()
            if logged_user and check_password_hash(logged_user.password, password):
                login_user(logged_user)
                print("logged in")
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login'))

    return render_template('login.html',form = form)

#Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/update/<int:user_id>',methods = ['GET','POST'])
@login_required
def update(user_id):
    update = Users.query.get_or_404(user_id)
    update_form = UserInfoForm()

    if request.method == 'POST' and update_form.validate():
        first_name = update_form.first_name.data
        last_name = update_form.last_name.data
        email = update_form.email.data
        phone_number = update_form.phone_number.data
        password = update_form.password.data
        user_id = current_user.id
        update.first_name = first_name
        update.last_name = last_name
        update.email = email
        update.phone_number = phone_number
        update.password = generate_password_hash(password)
        update.user_id = user_id
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('update.html',update_form = update_form)

