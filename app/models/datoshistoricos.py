from ..database import db
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, Column, Float

class DatosHistoricos(db.Model):
    id_datos_historicos = db.Column(db.Integer, primary_key=True)
    ano_datos_historicos  = db.Column(db.Integer)
    sku_datos_historicos  = db.Column(db.String(20))
    modelo_datos_historicos  = db.Column(db.String(20))
    tipo_enser_datos_historicos  = db.Column(db.String(50))
    clasificacion_enser_datos_historicos  = db.Column(db.String(5))
    ventas_datos_historicos  = db.Column(Float)
    fecha_datos_historicos = db.Column(db.DateTime(timezone=True))
    semana_datos_historicos =  db.Column(db.Integer)
    tipo =  db.Column(db.String(1))

