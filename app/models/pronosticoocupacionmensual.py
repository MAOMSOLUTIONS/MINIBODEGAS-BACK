from ..database import db
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, Column, Float

class PronosticoOcupacionMensual(db.Model):
    id_pronostico_ocupacion_mensual = db.Column(db.Integer, primary_key=True)
    dia_pronostico_ocupacion_mensual  = db.Column(db.String(20))
    valor_pronostico_mensual  = db.Column(Float)
    