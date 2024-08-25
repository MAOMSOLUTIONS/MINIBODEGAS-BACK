from ..database import db
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, Column, Float

class Price(db.Model):    
    id_price = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id_asset'), nullable=False)
    rental_price = db.Column(db.Float, nullable=False)
    deposit_type = db.Column(db.String(50), nullable=False)
    deposit_value = db.Column(db.Float, nullable=False)
    deposit_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    asset = db.relationship('Asset', backref=db.backref('prices', lazy=True))