from ..database import db
from datetime import datetime
from sqlalchemy.sql import func

class User(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    birth_date = db.Column(db.Date)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    sex = db.Column(db.String(20))
    street = db.Column(db.String(100))
    interior_number = db.Column(db.String(10))
    exterior_number = db.Column(db.String(10))
    municipality = db.Column(db.String(50))
    city = db.Column(db.String(50))
    country = db.Column(db.String(50))
    postal_code = db.Column(db.String(10))
    profile = db.Column(db.String(50))
    id_empresa = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
