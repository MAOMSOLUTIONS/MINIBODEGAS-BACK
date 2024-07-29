from ..database import db
from datetime import datetime
from sqlalchemy.sql import func

class Enterprise(db.Model):
    id_enterprise = db.Column(db.Integer, primary_key=True)
    enterprise_name = db.Column(db.String(80), unique=True, nullable=False)
    enterprise_rfc = db.Column(db.String(50))
    enterprise_phone = db.Column(db.String(20), nullable=True)
    enterprise_email = db.Column(db.String(100), nullable=True)
    enterprise_contact_name = db.Column(db.String(100), nullable=True)
    enterprise_fiscal_name = db.Column(db.String(100), nullable=True)
    enterprise_fiscal_street = db.Column(db.String(100), nullable=True)
    enterprise_fiscal_internal_number = db.Column(db.String(20), nullable=True)
    enterprise_fiscal_external_number = db.Column(db.String(20), nullable=True)
    enterprise_fiscal_municipio = db.Column(db.String(100), nullable=True)
    enterprise_fiscal_state = db.Column(db.String(100), nullable=True)
    enterprise_fiscal_country = db.Column(db.String(100), nullable=True)
    enterprise_fiscal_postal_code = db.Column(db.String(20), nullable=True)
    enterprise_fiscal_email = db.Column(db.String(100), nullable=True)
    enterprise_fiscal_phone = db.Column(db.String(20), nullable=True)
    enterprise_id_status = db.Column(db.Integer, db.ForeignKey('Status.id_status'), nullable=False)
    status_name = db.relationship('Status', backref=db.backref('Enterprises', lazy=True))
    created_at = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True))

