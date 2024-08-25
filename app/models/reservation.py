from sqlalchemy import Integer, String, Column, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import db


class Reservation(db.Model):
    id_reservation = db.Column(Integer, primary_key=True)
    id_client = db.Column(Integer, ForeignKey('client.id_client'), nullable=False)
    id_asset = db.Column(Integer, ForeignKey('asset.id_asset'), nullable=False)
    reservation_reservation_date = db.Column(DateTime, default=datetime.utcnow)
    reservation_deposit_amount = db.Column(Float, nullable=False)
    reservation_total_amount = db.Column(Float, nullable=False)
    reservation_amount_paid = db.Column(Float, default=0)  # Monto pagado hasta ahora
    reservation_payment_status = db.Column(String(50), nullable=False, default="Pendiente")  # Pendiente, Parcial, Completo
    reservation_status = db.Column(String(50), nullable=False, default="Apartada")  # Apartada, Reservada, Cancelada
    reservation_expiration_date = db.Column(DateTime, nullable=True)  # Fecha límite para completar el pago

    asset = db.relationship('Asset', backref='reservations')

