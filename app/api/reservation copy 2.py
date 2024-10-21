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

    print("Datos recibidos para la creación:", data)  # Depuración: imprime los datos recibidos

    try:
        # Procesar las fechas recibidas
        expiration_date_str = data.get('reservation_expiration_date')
        expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d") if expiration_date_str else None
        print("Fecha de expiración:", expiration_date)

        payment_due_date_str = data.get('payment_due_date')  # Obtener la fecha límite para el pago
        payment_due_date = datetime.strptime(payment_due_date_str, "%Y-%m-%d") if payment_due_date_str else None
        print("Fecha límite para el pago:", payment_due_date)

        start_date_str = data.get('start_date')
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
        print("Fecha de inicio:", start_date)

        end_date_str = data.get('end_date')
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None
        print("Fecha de fin:", end_date)

        duration = data.get('duration', 0)
        print("Duración:", duration)

        # Inicializar valores de reserva
        total_amount = data['reservation_total_amount']
        rent_price = data.get('reservation_rent_price', 0)  # Nuevo: Precio de Renta
        paid_amount = data['reservation_amount_paid']
        deposit_amount = data['reservation_deposit_amount']
        minimum_deposit = data.get('reservation_minimum_deposit', 10)  # Nuevo: Depósito mínimo

        pending_amount = total_amount - paid_amount
        pending_deposit = deposit_amount - paid_amount if paid_amount < deposit_amount else 0

        print(f"Total Amount: {total_amount}, Rent Price: {rent_price}, Paid Amount: {paid_amount}")
        print(f"Deposit Amount: {deposit_amount}, Minimum Deposit: {minimum_deposit}, Pending Amount: {pending_amount}, Pending Deposit: {pending_deposit}")

        # Crear la instancia de reservación
        reservation = Reservation(
            id_client=data['id_client'],
            id_asset=data['id_asset'],
            reservation_deposit_amount=deposit_amount,
            reservation_minimum_deposit=minimum_deposit,  # Guardar depósito mínimo
            reservation_rent_price=rent_price,  # Guardar el precio de renta
            reservation_total_amount=total_amount,
            reservation_amount_paid=paid_amount,
            reservation_pending_amount=pending_amount,
            reservation_pending_deposit=pending_deposit,
            reservation_expiration_date=expiration_date,
            payment_due_date=payment_due_date,  # Guardar la fecha límite
            start_date=start_date,
            end_date=end_date,
            duration=duration,
        )
        print("LO QUE SE INSERTA",reservation.reservation_amount_paid)

        db.session.add(reservation)
        db.session.commit()

        return jsonify({'id_reservation': reservation.id_reservation}), 201

    except Exception as e:
        print(f"Error al crear la reservación: {e}")  # Imprimir el error en consola
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
            

@api_blueprint.route('/reservations/<int:id>', methods=['PUT'])
def add_payment(id):
    data = request.get_json()

    print("Datos recibidos para la aplicación del pago:", data)  # Depuración: imprime los datos recibidos


    reservation = Reservation.query.get(id)

    if not reservation:
        return jsonify({'message': 'Reservación no encontrada'}), 404

    try:
        # Validar que el monto no esté siendo duplicado
        payment_amount = data.get('payment_amount', 0)
        if payment_amount <= 0:
            return jsonify({'message': 'El monto del pago no es válido'}), 400

        # Verificar si el mismo monto ya fue registrado
        existing_payments = Payment.query.filter_by(reservation_id=id, payment_amount=payment_amount).all()
        if existing_payments:
            return jsonify({'message': 'Este pago ya ha sido registrado'}), 400

        # Crear el pago
        payment = Payment(
            reservation_id=id,
            payment_method=data['payment_method'],
            payment_amount=payment_amount,
            payment_date=datetime.strptime(data['payment_date'], "%Y-%m-%d")
        )
        print("LA CREACION DEL PAGO",payment)


        db.session.add(payment)
        db.session.commit()

        return jsonify({'message': 'Pago registrado con éxito'}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error al registrar el pago: {e}")
        return jsonify({'message': 'Error al registrar el pago', 'details': str(e)}), 500
            

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
    
@api_blueprint.route('/reservations/<int:id>', methods=['GET'])
def get_reservation(id):
    reservation = Reservation.query.get(id)

    if not reservation:
        return jsonify({'message': 'Reservación no encontrada'}), 404

    return jsonify({
        'id_reservation': reservation.id_reservation,
        'id_client': reservation.id_client,
        'id_asset': reservation.id_asset,
        'reservation_reservation_date': reservation.reservation_reservation_date,
        'reservation_deposit_amount': reservation.reservation_deposit_amount,
        'reservation_total_amount': reservation.reservation_total_amount,
        'reservation_amount_paid': reservation.reservation_amount_paid,
        'reservation_payment_status': reservation.reservation_payment_status,
        'reservation_status': reservation.reservation_status,
        'reservation_expiration_date': reservation.reservation_expiration_date,
        'created_at': reservation.created_at,
        'updated_at': reservation.updated_at
    }), 200

