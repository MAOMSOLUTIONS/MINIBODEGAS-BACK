from ..database import db
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, Column, Float

class Factores(db.Model):
    id_factores = db.Column(db.Integer, primary_key=True)
    nombre_factores  = db.Column(db.String(50))
    sku_tipo  = db.Column(db.String(20))
    valor_factores   = db.Column(Float)
    def to_dict(self):
        return {
            'id_factores': self.id_factores,
            'nombre_factores': self.nombre_factores,
            'sku_tipo': self.sku_tipo,
            'valor_factores': self.valor_factores
        }
