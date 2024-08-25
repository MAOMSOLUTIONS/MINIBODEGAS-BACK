from sqlalchemy import Integer, String, Column, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import db

class Status(db.Model):
    id_status = db.Column(Integer, primary_key=True)
    status_name = db.Column(String(50), unique=True, nullable=False)
