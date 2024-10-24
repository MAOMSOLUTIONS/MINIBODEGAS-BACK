from ..database import db
from sqlalchemy import Integer, String, Column, Float
from sqlalchemy.orm import relationship
from datetime import datetime


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
    enterprise_rfc = db.Column(db.String(50))
    enterprise_phone = db.Column(db.String(20), nullable=True)
    enterprise_email = db.Column(db.String(100), nullable=True)
    enterprise_contact_name = db.Column(db.String(100), nullable=True)
    enterprise_fiscal_name = db.Column(db.String(100), nullable=True)
    enterprise_fiscal_street = db.Column(db.String(100), nullable=True)
    enterprise_fiscal_internal_number = db.Column(db.String(20), nullable=True)
    enterprise_fiscal_external_number = db.Column(db.String(20), nullable=True)
    enterprise_fiscal_municipio = db.Column(db.String(100), nullable=True)
    enterprise_fiscal_state = db.Column(db.String(100), nullable=True)
    enterprise_fiscal_country = db.Column(db.String(100), nullable=True)
    enterprise_fiscal_postal_code = db.Column(db.String(20), nullable=True)
    enterprise_fiscal_email = db.Column(db.String(100), nullable=True)
    enterprise_fiscal_phone = db.Column(db.String(20), nullable=True)
    enterprise_id_status = db.Column(db.Integer, db.ForeignKey('status.id_status'), nullable=False)
    status = db.relationship('Status', backref=db.backref('enterprises', lazy=True))  # Nombre de relación corregido



#    status_name = db.relationship('Status', backref=db.backref('Enterprise', lazy=True))
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

class Status(db.Model):
    id_status = db.Column(db.Integer, primary_key=True)
    status_name  = db.Column(db.String(50), unique=True, nullable=False)


class Property(db.Model):
    id_property = db.Column(db.Integer, primary_key=True)
    property_name = db.Column(db.String(100), nullable=False)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprise.id_enterprise'), nullable=False)
    property_id_status = db.Column(db.Integer, db.ForeignKey('status.id_status'), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True))

    enterprise = db.relationship('Enterprise', backref=db.backref('properties', lazy=True))
    status = db.relationship('Status', backref=db.backref('properties', lazy=True))


class AssetType(db.Model):
    id_asset_type = db.Column(db.Integer, primary_key=True)
    asset_type_name = db.Column(db.String(50), unique=True, nullable=False)

class AssetStatus(db.Model):
    id_status = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(50), unique=True, nullable=False)


class Asset(db.Model):
    id_asset = db.Column(db.Integer, primary_key=True)
    id_property = db.Column(db.Integer, db.ForeignKey('property.id_property'), nullable=False)  
    property = db.relationship('Property', backref='assets')  # Relación con Property
    asset_number = db.Column(db.String(50), nullable=False)
    asset_name = db.Column(db.String(100), nullable=False)
    asset_front = db.Column(db.Float, nullable=False)
    asset_depth = db.Column(db.Float, nullable=False)
    asset_height = db.Column(db.Float, nullable=False)
    asset_m2 = db.Column(db.Float, nullable=False)
    asset_m3 = db.Column(db.Float, nullable=False)
    asset_comments = db.Column(db.Text, nullable=True)
    asset_photo1 = db.Column(db.String(255), nullable=True)
    asset_photo2 = db.Column(db.String(255), nullable=True)
    asset_photo3 = db.Column(db.String(255), nullable=True)
    asset_photo4 = db.Column(db.String(255), nullable=True)
    asset_photo5 = db.Column(db.String(255), nullable=True)
    asset_type = db.Column(db.Integer, db.ForeignKey('asset_type.id_asset_type'), nullable=False)
    asset_type_rel = db.relationship('AssetType', backref='assets')  # Relación con AssetType
    asset_status = db.Column(db.Integer, db.ForeignKey('asset_status.id_status'), nullable=False)
    asset_status_rel = db.relationship('AssetStatus', backref='assets')  # Relación con AssetStatus
    created_at = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True))

class Reservation(db.Model):
    id_reservation = db.Column(Integer, primary_key=True)
    id_client = db.Column(Integer, ForeignKey('client.id_client'), nullable=False)
    id_asset = db.Column(Integer, ForeignKey('asset.id_asset'), nullable=False)
    reservation_date = db.Column(DateTime, default=datetime.utcnow)
    deposit_amount = db.Column(Float, nullable=False)
    expiration_date = db.Column(DateTime, nullable=False)
    status = db.Column(String(50), nullable=False)  # Puede ser 'pendiente', 'confirmada', 'cancelada'
    total_amount = db.Column(Float, nullable=False)

    # Relación con la tabla Asset
    asset = relationship('Asset', backref='reservations')

    # Relación con la tabla Client se maneja desde Client con backref
    # client = relationship('Client', backref='reservations')
    created_at = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True))


class ReservationStatus(db.Model):
    id_reservation_status = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(50), unique=True, nullable=False)

class Client(db.Model):
    id_client = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    email = db.Column(String(100), nullable=False, unique=True)
    phone = db.Column(String(20), nullable=False)
    address = db.Column(String(200), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True))

    # Relación con la tabla Reservation
    reservation_list = relationship('Reservation', backref='client')

    # Relación con otras tablas (si es necesario)
    # Ejemplo:
    # payments = relationship('Payment', backref='client')