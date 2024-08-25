from sqlalchemy import Integer, String, Column, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import db

class User(db.Model):
    id_user = db.Column(Integer, primary_key=True)
    username = db.Column(String(80), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    first_name = db.Column(String(50))
    last_name = db.Column(String(50))
    surname = db.Column(String(50))
    birth_date = db.Column(db.Date)
    email = db.Column(String(100), unique=True)
    phone = db.Column(String(20))
    sex = db.Column(String(20))
    street = db.Column(String(100))
    interior_number = db.Column(String(10))
    exterior_number = db.Column(String(10))
    municipality = db.Column(String(50))
    city = db.Column(String(50))
    country = db.Column(String(50))
    postal_code = db.Column(String(10))
    profile = db.Column(String(50))
    status = db.Column(String(50))
    id_empresa = db.Column(Integer)
    created_at = db.Column(DateTime(timezone=True), default=func.now())
    updated_at = db.Column(DateTime(timezone=True), onupdate=func.now())
