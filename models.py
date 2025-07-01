from datetime import datetime
from app import db
from flask_login import UserMixin

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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    orders = db.relationship('Order', backref='customer', lazy=True)
    code = db.Column(db.String(100))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    rego = db.Column(db.String)
    order_items = db.relationship('OrderItem', backref='order', lazy=True)
    created = db.Column(db.DateTime, default=datetime.now)
    returns = db.relationship('Return', backref='order', lazy=True)
    status = db.Column(db.Integer, default=0)
    # 0 = pending
    # 1 = resolved
    # 2 = backlog

class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.String(100))
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    order_items = db.relationship('OrderItem', backref='part', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    returned_quantity = db.Column(db.Integer, default=0)  # <--- optional helper

class Return(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    reason = db.Column(db.String(255))
    created = db.Column(db.DateTime, default=datetime.now)
    return_items = db.relationship('ReturnItem', backref='return_record', lazy=True)

class ReturnItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    return_id = db.Column(db.Integer, db.ForeignKey('return.id'), nullable=False)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order_item = db.relationship('OrderItem', backref='return_items')