from ..database import db
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, Column, Float

class DatosOcupacion(db.Model):
    id_datosocupacion = db.Column(db.Integer, primary_key=True)
    sku  = db.Column(db.String(20))
    sku_tipo  = db.Column(db.String(20))
    actual_factor_inventario  = db.Column(Float)
    actual_inventario  = db.Column(Float)
    actual_venta  = db.Column(Float)
    actual_area  = db.Column(Float)    
    devoluciones_factor_inventario  = db.Column(Float)
    devoluciones_inventario  = db.Column(Float)
    devoluciones_area  = db.Column(Float)
    mensual_venta  = db.Column(Float)
    mensual_venta_devoluciones  = db.Column(Float)
    stagging_factor_inventario  = db.Column(Float)
    stagging_inventario  = db.Column(Float)
    stagging_area  = db.Column(Float)
    pronostico_diario = db.Column(Float)
    pronostico_optimo = db.Column(Float)
    area_pronostico_optimo = db.Column(Float)
    inventario_seguridad = db.Column(Float)
    punto_reorden = db.Column(Float)
    cantidad_solicitar = db.Column(Float)

