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
