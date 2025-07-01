from collections import defaultdict
from datetime import datetime
from functools import wraps
import io
import os
from flask import flash, jsonify, make_response, redirect, render_template, request, url_for
from sqlalchemy import desc
from forms import LoginForm, RegisterForm
from models import User, Customer, Part, Order, OrderItem, ReturnItem, Return
from flask_bcrypt import Bcrypt
from flask_login import login_manager, login_required, login_user, logout_user, current_user
from datetime import datetime, timedelta


bcrypt = Bcrypt()

def register_routes(app, db):

    @app.login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route("/")
    def home():
        return redirect(url_for("login"))
    
    def role_required(*roles):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                if not current_user.is_authenticated:
                    flash("Please log in", "warning")
                    return redirect(url_for("login"))
                if current_user.role not in roles:
                    flash("Access denied", "danger")
                    return redirect(url_for("page_not_found"))  # or a dedicated 403 page
                return f(*args, **kwargs)
            return wrapper
        return decorator

    # -------- AUTH ---------------
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            print(user.role)
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                # Redirect based on role
                if user.role == "admin":
                    response = make_response(redirect(url_for("dashboard")))
                elif user.role == "staff":
                    response = make_response(redirect(url_for("orders")))
                else:
                    response = make_response(redirect(url_for("new_order")))
                response.set_cookie("remembered_username", form.username.data, max_age=60*60*24*30)  # 30 days
                return response
            else:
                flash("Invalid username or password", "danger")
        else:
            print(form.errors)
        return render_template('login.html', form=form)

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route("/register", methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if request.method == "POST":
            if request.form['username'] and request.form['password']:
                if User.query.filter(User.username == request.form['username']).first():
                    flash("User already exists!", "danger")
                    return redirect(url_for("register"))

            new_user = User(
                username=request.form['username'], 
                password=bcrypt.generate_password_hash(request.form['password']).decode('utf-8'), 
                role="Software Developer", 
                description="Makes the software!"
                )
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Successfully created new user!", "success")
                return redirect(url_for("login"))
            except:
                flash("Error when registering", "danger")
                return redirect(url_for("register"))
            
        return render_template('register.html', form=form)
    