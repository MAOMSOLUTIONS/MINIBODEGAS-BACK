from ..database import db
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, Column, Float

class Ocupacion(db.Model):
    id_ocupacion = db.Column(db.Integer, primary_key=True)
    nombre  = db.Column(db.String(50))
    valor_real   = db.Column(Float)
    valor_proyectado    = db.Column(Float)