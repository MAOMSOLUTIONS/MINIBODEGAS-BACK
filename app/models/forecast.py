from ..database import db
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, Column, Float




class Forecast(db.Model):
    id_forecast = db.Column(db.Integer, primary_key=True)
    ano_forecast  = db.Column(db.Integer)
    sku_forecats  = db.Column(db.String(20))
    mes_forecast  = db.Column(db.Integer)
    ventas_forecast  = db.Column(Float)
