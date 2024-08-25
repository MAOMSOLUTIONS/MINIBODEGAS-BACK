from sqlalchemy import Integer, String, Column, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import db

class ReservationStatus(db.Model):
    id_reservation_status = db.Column(Integer, primary_key=True)
    reservation_status_name = db.Column(String(50), unique=True, nullable=False)
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(DateTime(timezone=True), onupdate=func.now())