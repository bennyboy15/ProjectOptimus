from collections import defaultdict
from datetime import datetime
from functools import wraps
import io
import os
from flask import flash, jsonify, make_response, redirect, render_template, request, url_for
import requests
from sqlalchemy import desc
from forms import LoginForm, RegisterForm
from models import User
from flask_bcrypt import Bcrypt
from flask_login import login_manager, login_required, login_user, logout_user, current_user
from datetime import datetime, timedelta

bcrypt = Bcrypt()

def register_routes(app, db):

    @app.login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route("/")
    def index():
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
                    response = make_response(redirect(url_for("worksheets")))
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
        return render_template('auth/login.html', form=form)

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
            
        return render_template('auth/register.html', form=form)
    
    @app.route("/home")
    def home():
        API_KEY = os.environ.get('WEATHER_API_KEY')
        city = "Adelaide"
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            temperature = data["main"]["temp"]
            description = data["weather"][0]["description"]
            weather = f"{city} ({temperature}°C, {description})"
        else:
            print("Error fetching weather:", response.status_code)
        return render_template("home/home.html", weather=weather)
    
    @app.route("/worksheets")
    def worksheets():
        return render_template("worksheets/worksheets_view.html")
    
    @app.route("/update_user/<int:uid>")
    def update_user(uid):
        user = User.query.get_or_404(uid)
        user.role = "admin"
        user.first_name = "Benjamin"
        user.last_name = "Harvey"  
        db.session.commit()
        return redirect(url_for('login'))