from sqlalchemy import Integer, String, Column, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import db


class Reservation(db.Model):
    id_reservation = db.Column(db.Integer, primary_key=True)
    id_client = db.Column(db.Integer, db.ForeignKey('client.id_client'), nullable=False)
    id_asset = db.Column(db.Integer, db.ForeignKey('asset.id_asset'), nullable=False)
    reservation_reservation_date = db.Column(db.DateTime, default=datetime.utcnow)
    reservation_deposit_amount = db.Column(db.Float, nullable=False)
    reservation_total_amount = db.Column(db.Float, nullable=False)
    reservation_amount_paid = db.Column(db.Float, default=0)
    reservation_payment_status = db.Column(db.String(50), nullable=False, default="Pendiente")
    reservation_status = db.Column(db.String(50), nullable=False, default="Apartada")
    reservation_expiration_date = db.Column(db.DateTime, nullable=True)}
    payment_due_date = db.Column(db.DateTime, nullable=True)  # NUEVO CAMPO: Fecha límite para completar el pago

    # Agrega los campos faltantes
    start_date = db.Column(db.DateTime, nullable=True)  # Cambiar a nullable=True
    end_date = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Integer, nullable=True)


    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Campo de creación
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Campo de actualización

    # Relación con Payment, definimos solo el lado de Payment para manejar el backref
    asset = db.relationship('Asset', backref='reservations')
