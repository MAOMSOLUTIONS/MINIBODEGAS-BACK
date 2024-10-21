from sqlalchemy import Integer, String, Column, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import db


class Reservation(db.Model):
    id_reservation = db.Column(db.Integer, primary_key=True)
    id_client = db.Column(db.Integer, db.ForeignKey('client.id_client'), nullable=False)
    id_asset = db.Column(db.Integer, db.ForeignKey('asset.id_asset'), nullable=False)

    # Campos de pago
    reservation_total_amount = db.Column(db.Float, default=0)  # Precio de Renta Total
    reservation_rent_price = db.Column(db.Float, default=0)  # Precio de Renta
    reservation_amount_paid = db.Column(db.Float, default=0)  # Monto Pagado
    reservation_pending_amount = db.Column(db.Float, default=0)  # Monto Pendiente
    reservation_deposit_amount = db.Column(db.Float, default=0)  # Depósito total
    reservation_minimum_deposit = db.Column(db.Float, default=0)  # Depósito Mínimo
    reservation_pending_deposit = db.Column(db.Float, default=0)  # Depósito Pendiente

    # Estado del pago y reserva
    reservation_payment_status = db.Column(db.String(50), nullable=False, default="Pendiente")
    reservation_status = db.Column(db.String(50), nullable=False, default="Apartada")

    # Fechas
    reservation_reservation_date = db.Column(db.DateTime, default=datetime.utcnow)
    reservation_expiration_date = db.Column(db.DateTime, nullable=True)  # Fecha de expiración de la reserva
    payment_due_date = db.Column(db.DateTime, nullable=True)  # Fecha límite para completar el pago
    start_date = db.Column(db.DateTime, nullable=False)  # Fecha de inicio de la reserva
    end_date = db.Column(db.DateTime, nullable=False)  # Fecha de fin de la reserva
    duration = db.Column(db.Integer, default=0)  # Duración de la reserva en días
    
    # Campos automáticos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha de creación
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Fecha de actualización
    
    # Relación con Asset
    asset = db.relationship('Asset', backref='reservations')