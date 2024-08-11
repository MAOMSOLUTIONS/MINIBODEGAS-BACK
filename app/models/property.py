from ..database import db
from datetime import datetime
from sqlalchemy.sql import func

class Property(db.Model):
    id_property = db.Column(db.Integer, primary_key=True)
    property_name = db.Column(db.String(100), nullable=False)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprise.id_enterprise'), nullable=False)
    property_id_status = db.Column(db.Integer, db.ForeignKey('status.id_status'), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True))

    enterprise = db.relationship('Enterprise', backref=db.backref('properties', lazy=True))
    status = db.relationship('Status', backref=db.backref('properties', lazy=True))