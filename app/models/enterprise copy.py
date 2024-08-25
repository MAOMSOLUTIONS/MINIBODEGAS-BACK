from sqlalchemy import Integer, String, Column, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import db

class Enterprise(db.Model):
    id_enterprise = db.Column(Integer, primary_key=True)
    enterprise_name = db.Column(String(80), unique=True, nullable=False)
    enterprise_rfc = db.Column(String(50))
    enterprise_phone = db.Column(String(20), nullable=True)
    enterprise_email = db.Column(String(100), nullable=True)
    enterprise_contact_name = db.Column(String(100), nullable=True)
    enterprise_fiscal_name = db.Column(String(100), nullable=True)
    enterprise_fiscal_street = db.Column(String(100), nullable=True)
    enterprise_fiscal_internal_number = db.Column(String(20), nullable=True)
    enterprise_fiscal_external_number = db.Column(String(20), nullable=True)
    enterprise_fiscal_municipio = db.Column(String(100), nullable=True)
    enterprise_fiscal_state = db.Column(String(100), nullable=True)
    enterprise_fiscal_country = db.Column(String(100), nullable=True)
    enterprise_fiscal_postal_code = db.Column(String(20), nullable=True)
    enterprise_fiscal_email = db.Column(String(100), nullable=True)
    enterprise_fiscal_phone = db.Column(String(20), nullable=True)
    enterprise_id_status = db.Column(Integer, ForeignKey('status.id_status'), nullable=False)
    status = db.relationship('Status', backref=db.backref('enterprises', lazy=True))

    created_at = db.Column(DateTime(timezone=True), default=func.now())
    updated_at = db.Column(DateTime(timezone=True), onupdate=func.now())

