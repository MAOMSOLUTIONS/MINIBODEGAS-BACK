from flask import request, jsonify
from . import api_blueprint
from ..database import db
from .models import Reservation,Asset,Price

from sqlalchemy.exc import IntegrityError
import traceback
from datetime import datetime
from sqlalchemy import func


@api_blueprint.route('/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()

    # Validación básica de los campos requeridos
    if not all(key in data for key in ('id_client', 'id_asset', 'reservation_deposit_amount', 'reservation_total_amount', 'reservation_amount_paid')):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    try:
        # Crear la reservación
        reservation = Reservation(
            id_client=data.get('id_client'),
            id_asset=data.get('id_asset'),
            reservation_reservation_date=datetime.utcnow(),
            reservation_deposit_amount=data.get('reservation_deposit_amount'),
            reservation_total_amount=data.get('reservation_total_amount'),
            reservation_amount_paid=data.get('reservation_amount_paid'),
            reservation_expiration_date=data.get('reservation_expiration_date')
        )

        # Determinar el estado del pago y la reservación
        if reservation.reservation_amount_paid >= reservation.reservation_total_amount:
            reservation.reservation_payment_status = "Completo"
            reservation.reservation_status = "Reservada"
        elif reservation.reservation_amount_paid > 0:
            reservation.reservation_payment_status = "Parcial"
            reservation.reservation_status = "Apartada"
        else:
            reservation.reservation_payment_status = "Pendiente"
            reservation.reservation_status = "Apartada"

        db.session.add(reservation)
        db.session.commit()

        return jsonify({'message': 'Reservación creada correctamente', 'id_reservation': reservation.id_reservation}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Error de integridad, probablemente ya exista una reservación similar'}), 409
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'message': 'Ocurrió un error', 'detalles': str(e)}), 500
    
@api_blueprint.route('/reservations/<int:id>', methods=['PUT'])
def update_reservation(id):
    data = request.get_json()
    reservation = Reservation.query.get(id)

    if not reservation:
        return jsonify({'message': 'Reservación no encontrada'}), 404

    try:
        # Actualizar el monto pagado y el estado de la reservación
        reservation.reservation_amount_paid += data.get('additional_payment', 0)

        # Revisar el estado del pago
        if reservation.reservation_amount_paid >= reservation.reservation_total_amount:
            reservation.reservation_payment_status = "Completo"
            reservation.reservation_status = "Reservada"
        elif reservation.reservation_amount_paid > 0:
            reservation.reservation_payment_status = "Parcial"
            reservation.reservation_status = "Apartada"
        
        reservation.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'Reservación actualizada correctamente', 'id_reservation': id}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'message': 'Error al actualizar la reservación', 'detalles': str(e)}), 500

@api_blueprint.route('/reservations', methods=['GET'])
def get_reservations():
    id_client = request.args.get('id_client', '')
    id_asset = request.args.get('id_asset', '')
    reservation_status = request.args.get('reservation_status', '')

    query = Reservation.query

    if id_client:
        query = query.filter(Reservation.id_client == id_client)
    if id_asset:
        query = query.filter(Reservation.id_asset == id_asset)
    if reservation_status:
        query = query.filter(Reservation.reservation_status.ilike(f'%{reservation_status}%'))

    reservations = query.all()

    return jsonify([
        {
            'id_reservation': reservation.id_reservation,
            'id_client': reservation.id_client,
            'id_asset': reservation.id_asset,
            'reservation_reservation_date': reservation.reservation_reservation_date,
            'reservation_deposit_amount': reservation.reservation_deposit_amount,
            'reservation_expiration_date': reservation.reservation_expiration_date,
            'reservation_status': reservation.reservation_status,
            'reservation_total_amount': reservation.reservation_total_amount,
            'created_at': reservation.created_at,
            'updated_at': reservation.updated_at
        } for reservation in reservations
    ])


@api_blueprint.route('/available', methods=['GET'])
def get_available_assets():
    try:
        # Parámetros de búsqueda
        asset_number = request.args.get('asset_number')
        asset_name = request.args.get('asset_name')
        asset_status = request.args.get('asset_status', type=int)
        available_from = request.args.get('available_from', type=str)
        available_to = request.args.get('available_to', type=str)
        asset_front_min = request.args.get('asset_front_min', type=float)
        asset_front_max = request.args.get('asset_front_max', type=float)
        asset_depth_min = request.args.get('asset_depth_min', type=float)
        asset_depth_max = request.args.get('asset_depth_max', type=float)
        asset_height_min = request.args.get('asset_height_min', type=float)
        asset_height_max = request.args.get('asset_height_max', type=float)
        asset_m2_min = request.args.get('asset_m2_min', type=float)
        asset_m2_max = request.args.get('asset_m2_max', type=float)
        rental_price_min = request.args.get('rental_price_min', type=float)
        rental_price_max = request.args.get('rental_price_max', type=float)
        deposit_value_min = request.args.get('deposit_value_min', type=float)
        deposit_value_max = request.args.get('deposit_value_max', type=float)

        # Subquery para obtener el último precio de renta y depósito por asset
        subquery = db.session.query(
            Price.asset_id,
            func.max(Price.created_at).label('max_created_at')
        ).group_by(Price.asset_id).subquery()

        # Consulta principal que une assets y precios con el último precio para cada asset
        query = db.session.query(
            Asset.id_asset,
            Asset.asset_name,
            Asset.asset_m2,
            Asset.asset_m3,
            Asset.asset_status,
            Price.rental_price.label('latest_price'),
            Price.deposit_value.label('deposit_value')
        ).join(subquery, (Price.asset_id == subquery.c.asset_id) & (Price.created_at == subquery.c.max_created_at)).join(
            Asset, Asset.id_asset == Price.asset_id)

        # Aplicar los filtros
        if asset_number:
            query = query.filter(Asset.asset_number.ilike(f'%{asset_number}%'))
        
        if asset_name:
            query = query.filter(Asset.asset_name.ilike(f'%{asset_name}%'))

        if asset_status:
            query = query.filter(Asset.asset_status == asset_status)
        
        if available_from:
            available_from_date = datetime.strptime(available_from, '%Y-%m-%d')
            query = query.filter(Asset.available_from >= available_from_date)
        
        if available_to:
            available_to_date = datetime.strptime(available_to, '%Y-%m-%d')
            query = query.filter(Asset.available_to <= available_to_date)

        if asset_front_min:
            query = query.filter(Asset.asset_front >= asset_front_min)
        
        if asset_front_max:
            query = query.filter(Asset.asset_front <= asset_front_max)

        if asset_depth_min:
            query = query.filter(Asset.asset_depth >= asset_depth_min)
        
        if asset_depth_max:
            query = query.filter(Asset.asset_depth <= asset_depth_max)

        if asset_height_min:
            query = query.filter(Asset.asset_height >= asset_height_min)
        
        if asset_height_max:
            query = query.filter(Asset.asset_height <= asset_height_max)

        if asset_m2_min:
            query = query.filter(Asset.asset_m2 >= asset_m2_min)
        
        if asset_m2_max:
            query = query.filter(Asset.asset_m2 <= asset_m2_max)

        if rental_price_min is not None:
            query = query.filter(Price.rental_price >= rental_price_min)
        
        if rental_price_max is not None:
            query = query.filter(Price.rental_price <= rental_price_max)

        if deposit_value_min is not None:
            query = query.filter(Price.deposit_value >= deposit_value_min)
        
        if deposit_value_max is not None:
            query = query.filter(Price.deposit_value <= deposit_value_max)

        # Ejecutar la consulta y obtener los resultados
        assets = query.all()

        # Serializar los resultados
        assets_list = [{
            "id_asset": asset.id_asset,
            "asset_name": asset.asset_name,
            "asset_m2": asset.asset_m2,
            "asset_m3": asset.asset_m3,
            "asset_status": asset.asset_status,
            "latest_price": asset.latest_price,
            "deposit_value": asset.deposit_value
        } for asset in assets]

        return jsonify(assets_list), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500