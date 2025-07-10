from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = "users"

    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    role = db.Column(db.String)
    description = db.Column(db.String)

    def __repr__(self):
        return f"<User: {self.username}, Role: {self.role}>"

    def get_id(self):
        return self.uid
    
class Customer(db.Model):
    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=True)
    phone = db.Column(db.String, nullable=True)
    address = db.Column(db.String, nullable=True)

    quotes = db.relationship("Quote", back_populates="customer")

    def __repr__(self):
        return f"<Customer {self.name}>"


class Salesman(db.Model):
    __tablename__ = "salesman"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=True)
    phone = db.Column(db.String, nullable=True)

    quotes = db.relationship("Quote", back_populates="salesman")

    def __repr__(self):
        return f"<Salesman {self.first_name} {self.last_name}>"

class TruckMake(db.Model):
    __tablename__ = 'truck_make'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    code = db.Column(db.String, nullable=True)
    models = db.relationship("TruckModel", back_populates="make")

class TruckModel(db.Model):
    __tablename__ = 'truck_model'
    id = db.Column(db.Integer, primary_key=True)
    make_id = db.Column(db.Integer, ForeignKey('truck_make.id'), nullable=False)
    name = db.Column(db.String, nullable=False)

    make = db.relationship("TruckMake", back_populates="models")
    available_options = db.relationship("TruckModelOption", back_populates="truck_model")
    
class TruckModelOption(db.Model):
    __tablename__ = 'truck_model_option'
    id = db.Column(db.Integer, primary_key=True)
    truck_model_id = db.Column(db.Integer, ForeignKey('truck_model.id'), nullable=False)
    option_id = db.Column(db.Integer, ForeignKey('option.id'), nullable=False)

    truck_model = db.relationship("TruckModel", back_populates="available_options")
    option = db.relationship("Option", back_populates="available_for_models")


class Section(db.Model):
    __tablename__ = 'section'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    headings = db.relationship("Heading", back_populates="section")


class Heading(db.Model):
    __tablename__ = 'heading'
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, ForeignKey('section.id'), nullable=False)
    name = db.Column(db.String, nullable=False)

    section = db.relationship("Section", back_populates="headings")
    options = db.relationship("Option", back_populates="heading")


class Option(db.Model):
    __tablename__ = 'option'
    id = db.Column(db.Integer, primary_key=True)
    heading_id = db.Column(db.Integer, ForeignKey('heading.id'), nullable=False)
    name = db.Column(db.String, nullable=False)

    heading = db.relationship("Heading", back_populates="options")
    attributes = db.relationship("OptionAttribute", back_populates="option")
    available_for_models = db.relationship("TruckModelOption", back_populates="option")


class OptionAttribute(db.Model):
    __tablename__ = 'option_attribute'
    id = db.Column(db.Integer, primary_key=True)
    option_id = db.Column(db.Integer, ForeignKey('option.id'), nullable=False)
    name = db.Column(db.String, nullable=False)

    option = db.relationship("Option", back_populates="attributes")
    values = db.relationship("OptionAttributeValue", back_populates="attribute")


class OptionAttributeValue(db.Model):
    __tablename__ = 'option_attribute_value'
    id = db.Column(db.Integer, primary_key=True)
    attribute_id = db.Column(db.Integer, ForeignKey('option_attribute.id'), nullable=False)
    value = db.Column(db.String, nullable=False)

    attribute = db.relationship("OptionAttribute", back_populates="values")

class Quote(db.Model):
    __tablename__ = 'quote'
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    salesman_id = db.Column(db.Integer, db.ForeignKey('salesman.id'), nullable=True)

    customer = db.relationship("Customer", back_populates="quotes")
    salesman = db.relationship("Salesman", back_populates="quotes")

    selections = db.relationship("QuoteOptionSelection", back_populates="quote")

class QuoteOptionSelection(db.Model):
    __tablename__ = 'quote_option_selection'
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, ForeignKey('quote.id'), nullable=False)
    option_id = db.Column(db.Integer, ForeignKey('option.id'), nullable=False)
    notes = db.Column(db.Text)

    quote = db.relationship("Quote", back_populates="selections")
    option = db.relationship("Option")
    selected_attributes = db.relationship("QuoteOptionAttributeValue", back_populates="quote_option")


class QuoteOptionAttributeValue(db.Model):
    __tablename__ = 'quote_option_attribute_value'
    id = db.Column(db.Integer, primary_key=True)
    quote_option_id = db.Column(db.Integer, ForeignKey('quote_option_selection.id'), nullable=False)
    attribute_id = db.Column(db.Integer, ForeignKey('option_attribute.id'), nullable=False)
    value_id = db.Column(db.Integer, ForeignKey('option_attribute_value.id'), nullable=False)

    quote_option = db.relationship("QuoteOptionSelection", back_populates="selected_attributes")
    attribute = db.relationship("OptionAttribute")
    value = db.relationship("OptionAttributeValue")

