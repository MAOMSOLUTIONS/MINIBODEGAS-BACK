from sqlalchemy import Integer, String, Column, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import db

class Payment(db.Model):
    id_payment = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id_reservation'), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    card_type = db.Column(db.String(50), nullable=True)
    card_number = db.Column(db.String(50), nullable=True)
    account_number = db.Column(db.String(50), nullable=True)

    # Definimos el backref solo aquí, de manera que el pago pueda acceder a la reservación
    reservation = db.relationship('Reservation', backref=db.backref('payments', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha de creación
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Fecha de actualización
