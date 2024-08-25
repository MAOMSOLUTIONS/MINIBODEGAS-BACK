from sqlalchemy import Integer, String, Column, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import db


class Client(db.Model):
    id_client = db.Column(Integer, primary_key=True)
    client_name = db.Column(String(100), nullable=False)
    client_email = db.Column(String(100), nullable=False)
    client_phone = db.Column(String(15), nullable=False)
    client_address = db.Column(String(200))  # Reincluye este campo si sigue en la base de datos
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con las reservaciones
    reservations = db.relationship('Reservation', backref='client_reservations')  # Cambié el backref para evitar colisiones
