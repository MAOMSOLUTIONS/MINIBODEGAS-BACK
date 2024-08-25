from sqlalchemy import Integer, String, Column, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import db

class User(db.Model):
    id_user = db.Column(Integer, primary_key=True)
    username = db.Column(String(80), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    first_name = db.Column(String(50))
    last_name = db.Column(String(50))
    surname = db.Column(String(50))
    birth_date = db.Column(db.Date)
    email = db.Column(String(100), unique=True)
    phone = db.Column(String(20))
    sex = db.Column(String(20))
    street = db.Column(String(100))
    interior_number = db.Column(String(10))
    exterior_number = db.Column(String(10))
    municipality = db.Column(String(50))
    city = db.Column(String(50))
    country = db.Column(String(50))
    postal_code = db.Column(String(10))
    profile = db.Column(String(50))
    status = db.Column(String(50))
    id_empresa = db.Column(Integer)
    created_at = db.Column(DateTime(timezone=True), default=func.now())
    updated_at = db.Column(DateTime(timezone=True), onupdate=func.now())

class Enterprise(db.Model):
    id_enterprise = db.Column(Integer, primary_key=True)
    enterprise_name = db.Column(String(80), unique=True, nullable=False)
    enterprise_rfc = db.Column(String(50))
    enterprise_phone = db.Column(String(20), nullable=True)
    enterprise_email = db.Column(String(100), nullable=True)
    enterprise_contact_name = db.Column(String(100), nullable=True)
    enterprise_fiscal_name = db.Column(String(100), nullable=True)
    enterprise_fiscal_street = db.Column(String(100), nullable=True)
    enterprise_fiscal_internal_number = db.Column(String(20), nullable=True)
    enterprise_fiscal_external_number = db.Column(String(20), nullable=True)
    enterprise_fiscal_municipio = db.Column(String(100), nullable=True)
    enterprise_fiscal_state = db.Column(String(100), nullable=True)
    enterprise_fiscal_country = db.Column(String(100), nullable=True)
    enterprise_fiscal_postal_code = db.Column(String(20), nullable=True)
    enterprise_fiscal_email = db.Column(String(100), nullable=True)
    enterprise_fiscal_phone = db.Column(String(20), nullable=True)
    enterprise_id_status = db.Column(Integer, ForeignKey('status.id_status'), nullable=False)
    status = db.relationship('Status', backref=db.backref('enterprises', lazy=True))

    created_at = db.Column(DateTime(timezone=True), default=func.now())
    updated_at = db.Column(DateTime(timezone=True), onupdate=func.now())

class Status(db.Model):
    id_status = db.Column(Integer, primary_key=True)
    status_name = db.Column(String(50), unique=True, nullable=False)

class Property(db.Model):
    id_property = db.Column(Integer, primary_key=True)
    property_name = db.Column(String(100), nullable=False)
    enterprise_id = db.Column(Integer, ForeignKey('enterprise.id_enterprise'), nullable=False)
    property_id_status = db.Column(Integer, ForeignKey('status.id_status'), nullable=False)

    created_at = db.Column(DateTime(timezone=True), default=func.now())
    updated_at = db.Column(DateTime(timezone=True), onupdate=func.now())

    enterprise = db.relationship('Enterprise', backref=db.backref('properties', lazy=True))
    status = db.relationship('Status', backref=db.backref('properties', lazy=True))

class AssetType(db.Model):
    id_asset_type = db.Column(Integer, primary_key=True)
    asset_type_name = db.Column(String(50), unique=True, nullable=False)

class AssetStatus(db.Model):
    id_status = db.Column(Integer, primary_key=True)
    status_name = db.Column(String(50), unique=True, nullable=False)

class Asset(db.Model):
    id_asset = db.Column(Integer, primary_key=True)
    id_property = db.Column(Integer, ForeignKey('property.id_property'), nullable=False)
    property = db.relationship('Property', backref='assets')
    asset_number = db.Column(String(50), nullable=False)
    asset_name = db.Column(String(100), nullable=False)
    asset_front = db.Column(Float, nullable=False)
    asset_depth = db.Column(Float, nullable=False)
    asset_height = db.Column(Float, nullable=False)
    asset_m2 = db.Column(Float, nullable=False)
    asset_m3 = db.Column(Float, nullable=False)
    asset_comments = db.Column(db.Text, nullable=True)
    asset_photo1 = db.Column(String(255), nullable=True)
    asset_photo2 = db.Column(String(255), nullable=True)
    asset_photo3 = db.Column(String(255), nullable=True)
    asset_photo4 = db.Column(String(255), nullable=True)
    asset_photo5 = db.Column(String(255), nullable=True)
    asset_type = db.Column(Integer, ForeignKey('asset_type.id_asset_type'), nullable=False)
    asset_type_rel = db.relationship('AssetType', backref='assets')
    asset_status = db.Column(Integer, ForeignKey('asset_status.id_status'), nullable=False)
    asset_status_rel = db.relationship('AssetStatus', backref='assets')
    created_at = db.Column(DateTime(timezone=True), default=func.now())
    updated_at = db.Column(DateTime(timezone=True), onupdate=func.now())
    def to_dict(self):
        return {
            'id_asset': self.id_asset,
            'asset_number': self.asset_number,
            'asset_name': self.asset_name,
            'asset_front': self.asset_front,
            'asset_depth': self.asset_depth,
            'asset_height': self.asset_height,
            'asset_m2': self.asset_m2,
            'asset_m3': self.asset_m3,
            'asset_status': self.asset_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            # Agrega otros campos que quieras incluir en el dict
        }

class Reservation(db.Model):
    id_reservation = db.Column(Integer, primary_key=True)
    id_client = db.Column(Integer, ForeignKey('client.id_client'), nullable=False)
    id_asset = db.Column(Integer, ForeignKey('asset.id_asset'), nullable=False)
    reservation_reservation_date = db.Column(DateTime, default=datetime.utcnow)
    reservation_deposit_amount = db.Column(Float, nullable=False)
    reservation_total_amount = db.Column(Float, nullable=False)
    reservation_amount_paid = db.Column(Float, default=0)  # Monto pagado hasta ahora
    reservation_payment_status = db.Column(String(50), nullable=False, default="Pendiente")  # Pendiente, Parcial, Completo
    reservation_status = db.Column(String(50), nullable=False, default="Apartada")  # Apartada, Reservada, Cancelada
    reservation_expiration_date = db.Column(DateTime, nullable=True)  # Fecha límite para completar el pago

    asset = db.relationship('Asset', backref='reservations')


class Client(db.Model):
    id_client = db.Column(Integer, primary_key=True)
    client_name = db.Column(String(100), nullable=False)
    client_email = db.Column(String(100), nullable=False)
    client_phone = db.Column(String(15), nullable=False)
    client_address = db.Column(String(200))  # Reincluye este campo si sigue en la base de datos
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con las reservaciones
    reservations = db.relationship('Reservation', backref='client_reservations')  # Cambié el backref para evitar colisiones

class ReservationStatus(db.Model):
    id_reservation_status = db.Column(Integer, primary_key=True)
    reservation_status_name = db.Column(String(50), unique=True, nullable=False)
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(DateTime(timezone=True), onupdate=func.now())

class Price(db.Model):
    id_price = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id_asset'), nullable=False)
    rental_price = db.Column(db.Float, nullable=False)
    deposit_type = db.Column(db.String(50), nullable=False)
    deposit_value = db.Column(db.Float, nullable=False)
    deposit_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    asset = db.relationship('Asset', backref=db.backref('prices', lazy=True))

