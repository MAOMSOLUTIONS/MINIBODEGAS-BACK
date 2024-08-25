from sqlalchemy import Integer, String, Column, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import db

class Property(db.Model):
    id_property = db.Column(Integer, primary_key=True)
    property_name = db.Column(String(100), nullable=False)
    enterprise_id = db.Column(Integer, ForeignKey('enterprise.id_enterprise'), nullable=False)
    property_id_status = db.Column(Integer, ForeignKey('status.id_status'), nullable=False)

    created_at = db.Column(DateTime(timezone=True), default=func.now())
    updated_at = db.Column(DateTime(timezone=True), onupdate=func.now())

    enterprise = db.relationship('Enterprise', backref=db.backref('properties', lazy=True))
    status = db.relationship('Status', backref=db.backref('properties', lazy=True))
