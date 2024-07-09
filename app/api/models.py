from ..database import db
from sqlalchemy import Integer, String, Column, Float

class User(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    password= db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    birth_date = db.Column(db.Date)    
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    sex = db.Column(db.String(20))
    street = db.Column(db.String(100))
    interior_number = db.Column(db.String(10))
    exterior_number = db.Column(db.String(10))
    municipality = db.Column(db.String(50))
    city = db.Column(db.String(50))
    country = db.Column(db.String(50))
    postal_code = db.Column(db.String(10))
    profile = db.Column(db.String(50))
    status = db.Column(db.String(50))
    id_empresa = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True))


class Enterprise(db.Model):
    id_enterprise = db.Column(db.Integer, primary_key=True)
    enterprise_name = db.Column(db.String(80), unique=True, nullable=False)
    rfc = db.Column(db.String(50))
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True))

class Ocupacion(db.Model):
    id_ocupacion = db.Column(db.Integer, primary_key=True)
    nombre  = db.Column(db.String(50))
    valor_real   = db.Column(Float)
    valor_proyectado    = db.Column(Float)

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



class PronosticoOcupacionDiario(db.Model):
    id_pronostico_ocupacion_diario = db.Column(db.Integer, primary_key=True)
    dia_pronostico_ocupacion_diario  = db.Column(db.String(20))
    valor_pronostico_diario  = db.Column(Float)

class PronosticoOcupacionMensual(db.Model):
    id_pronostico_ocupacion_mensual = db.Column(db.Integer, primary_key=True)
    dia_pronostico_ocupacion_mensual  = db.Column(db.String(20))
    valor_pronostico_mensual  = db.Column(Float)

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


class Forecast(db.Model):
    id_forecast = db.Column(db.Integer, primary_key=True)
    ano_forecast  = db.Column(db.Integer)
    sku_forecats  = db.Column(db.String(20))
    mes_forecast  = db.Column(db.Integer)
    ventas_forecast  = db.Column(Float)
