from collections import defaultdict
from datetime import datetime
from functools import wraps
import io
import os
from flask import flash, jsonify, make_response, redirect, render_template, request, url_for
import requests
from sqlalchemy import desc
from forms import LoginForm, RegisterForm
from models import Heading, Option, OptionAttribute, OptionAttributeValue, Quote, QuoteOptionAttributeValue, QuoteOptionSelection, Section, TruckMake, TruckModel, TruckModelOption, User
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
                response = make_response(redirect(url_for("home")))
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
    
    # -------- HOME ---------------
    @app.route("/home")
    def home():
        API_KEY = os.environ.get('WEATHER_API_KEY')
        city = "Adelaide"
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            temperature = round(data["main"]["temp"])
            description = data["weather"][0]["description"]
            weather = f"{city} ({temperature}°C, {description})"
        else:
            print("Error fetching weather:", response.status_code)
        return render_template("home/home.html", weather=weather)
    
    # -------- WORKSHEETS ---------------  
    @app.route('/quote/<int:quote_id>')
    def view_quote(quote_id):
        quote = Quote.query.get_or_404(quote_id)

        # Get truck model from any selected option
        truck_model = None
        if quote.selections:
            first_option = quote.selections[0].option
            for model_option in first_option.available_for_models:
                truck_model = model_option.truck_model
                break

        # Load all sections, headings, and options for that model
        all_data = {}
        for model_option in truck_model.available_options:
            option = model_option.option
            heading = option.heading
            section = heading.section

            if section.name not in all_data:
                all_data[section.name] = {}

            if heading.name not in all_data[section.name]:
                all_data[section.name][heading.name] = []

            all_data[section.name][heading.name].append(option)

        return render_template(
            "worksheets/quote.html",
            quote=quote,
            truck_model=truck_model,
            data=all_data
        )
    
    @app.route("/new_worksheet")
    def new_worksheet():
        return render_template('worksheets/new_worksheet.html')
    
    # -- OTHER --
    @app.route("/update_user/<int:uid>")
    def update_user(uid):
        user = User.query.get_or_404(uid)
        user.role = "admin"
        user.first_name = "Benjamin"
        user.last_name = "Harvey"  
        db.session.commit()
        return redirect(url_for('login'))
      
    @app.route('/make')
    def add_make():
        db.session.add_all([TruckMake(name="Kenworth", code="KW"),TruckMake(name="DAF", code="DAF")])
        db.session.commit()
        return "MAKE DONE"
    
    @app.route('/model')
    def add_model():
        db.session.add_all([TruckModel(make_id=1, name="T610SAR"),TruckModel(make_id=2, name="XG+")])
        db.session.commit()
        return "MODEL DONE"
    
    @app.route('/section')
    def add_section():
        db.session.add_all([Section(name="Predelivery"),Section(name="Stainless"),Section(name="Hydraulics")])
        db.session.commit()
        return "SECTION DONE"
    
    @app.route('/heading')
    def add_heading():
        db.session.add_all([
            Heading(section_id=2, name="FREIGHT"),
            Heading(section_id=2, name="PRE-DELIVERY"),
            Heading(section_id=2, name="ENGINE UP RATE"),
            Heading(section_id=2, name="FIRE EXT"),
            Heading(section_id=2, name="NUTCOVERS"),
            Heading(section_id=2, name="HUB CAPS"),
            Heading(section_id=2, name="SEAT COVERS"),
            Heading(section_id=2, name="DASH MAT"),
            Heading(section_id=2, name="FLOOR MATS"),
            Heading(section_id=2, name="SAFETY TRIANGLE/JACK"),
            Heading(section_id=2, name="MATTRESS PROTECTOR"),
            Heading(section_id=2, name="1ST AID KIT"),
            Heading(section_id=2, name="WEATHER SHIELD"),
            Heading(section_id=2, name="CHROME ADBLUE"),
            Heading(section_id=2, name="WHEEL ALIGNMENT"),
            Heading(section_id=2, name="WINDOW TINT"),
            Heading(section_id=2, name="DETAILING")
        ])
        db.session.commit()
        return "HEADING DONE"
    
    @app.route('/options')
    def add_options():
        db.session.add_all([
            Option(heading_id=2, name="Naismith"),
            Option(heading_id=2, name="Customer to pick-up"),
            
            Option(heading_id=3, name="CMV"),
            Option(heading_id=3, name="Bayswater / Hallam"),
            Option(heading_id=3, name="Tatiara"),
            
            Option(heading_id=4, name="Re-rate engine to 600HP / 2050"),
            
            Option(heading_id=5, name="1.5 KG Fire Ext & Blower"),
            Option(heading_id=5, name="Fit air blower only"),
            Option(heading_id=5, name="Relocate fire ext and fit air blower"),
            Option(heading_id=5, name="DAF Fire Ext & Blower"),
            
            Option(heading_id=6, name="FRONT ONLY NUT COVERS 33MM (20) SCREW ON"),
            Option(heading_id=6, name="NUT COVERS 33MM (60) SCREW ON"),
            Option(heading_id=6, name="60 YELLOW NUT INDICATORS WITH MATCHING NUT COVERS"),
            Option(heading_id=6, name="80 YELLOW NUT INDICATORS WITH MATCHING NUT COVERS"),
            Option(heading_id=6, name="100 YELLOW NUT INDICATORS WITH MATCHING NUT COVERS"),
            Option(heading_id=6, name="DAF CAP & NUT COVER KIT"),
        ])
        db.session.commit()
        return "OPTIONS DONE"
        
    @app.route('/option_attributes')
    def add_option_attributes():
        db.session.add_all([
            OptionAttribute(option_id=8, name="Location")
        ])
        db.session.commit()
        return "OPTION ATTRIBUTES DONE"

    @app.route('/option_attribute_values')
    def add_option_attribute_values():
        db.session.add_all([
            OptionAttributeValue(attribute_id=3, value="Under Passenger Seat"),
            OptionAttributeValue(attribute_id=3, value="In Front of Passenger Seat")
        ])
        db.session.commit()
        return "OPTION ATTRIBUTE VALUES DONE"

    @app.route('/add-test-data')
    def add_test_data():
        try:
            # 1. Truck Make and Model
            make = TruckMake(name="Kenworth")
            model = TruckModel(name="T409SAR", make=make)

            # 2. Section and Heading
            section = Section(name="Electrical")
            heading = Heading(name="Driving Lights", section=section)

            # 3. Option and Attributes
            option = Option(name="LED Bar", heading=heading)

            color_attr = OptionAttribute(name="Color", option=option)
            style_attr = OptionAttribute(name="Style", option=option)

            color_black = OptionAttributeValue(value="Black", attribute=color_attr)
            color_chrome = OptionAttributeValue(value="Chrome", attribute=color_attr)
            style_slim = OptionAttributeValue(value="Slimline", attribute=style_attr)
            style_heavy = OptionAttributeValue(value="Heavy Duty", attribute=style_attr)

            # 4. Link TruckModel to Option
            availability = TruckModelOption(truck_model=model, option=option)

            # 5. Salesman user (if not exists)
            salesman = User.query.filter_by(username="sales1").first()
            if not salesman:
                salesman = User(
                    username="sales1",
                    password="test",  # hash this in real app
                    first_name="Jane",
                    last_name="Doe",
                    role="sales"
                )
                db.session.add(salesman)
                db.session.flush()  # get salesman.uid

            # 6. Create Quote
            quote = Quote(
                customer_name="ACME Pty Ltd",
                salesman_id=salesman.uid
            )

            # 7. Add selected option
            selection = QuoteOptionSelection(
                quote=quote,
                option=option,
                notes="Customer wants a LED bar with chrome finish."
            )

            # 8. Add selected attributes
            selected_color = QuoteOptionAttributeValue(
                quote_option=selection,
                attribute=color_attr,
                value=color_chrome
            )
            selected_style = QuoteOptionAttributeValue(
                quote_option=selection,
                attribute=style_attr,
                value=style_heavy
            )

            # Commit all
            db.session.add_all([
                make, model,
                section, heading, option,
                color_attr, style_attr,
                color_black, color_chrome, style_slim, style_heavy,
                availability, quote, selection,
                selected_color, selected_style
            ])
            db.session.commit()

            return "✅ Test data added successfully!"

        except Exception as e:
            db.session.rollback()
            return f"❌ Error adding test data: {str(e)}", 500

    
    
    