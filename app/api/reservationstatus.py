from flask import request, jsonify
from . import api_blueprint
from ..database import db
from .models import ReservationStatus
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func  # Asegúrate de importar func aquí
import traceback

@api_blueprint.route('/reservationstatus', methods=['POST'])
def create_reservation_status():
    data = request.get_json()

    if 'reservation_status_name' not in data:
        return jsonify({'error': 'Falta el nombre del estado de la reservación'}), 400

    try:
        reservation_status = ReservationStatus(
            reservation_status_name=data.get('reservation_status_name')
        )

        db.session.add(reservation_status)
        db.session.commit()

        return jsonify({'message': 'Estado de la reservación creado correctamente', 'id_reservation_status': reservation_status.id_reservation_status}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'El nombre del estado de la reservación ya existe'}), 409
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'message': 'Ocurrió un error', 'detalles': str(e)}), 500


@api_blueprint.route('/reservationstatus/<int:id>', methods=['PUT'])
def update_reservation_status(id):
    data = request.get_json()
    reservation_status = ReservationStatus.query.get(id)

    if not reservation_status:
        return jsonify({'message': 'Estado de la reservación no encontrado'}), 404

    try:
        new_name = data.get('reservation_status_name', reservation_status.reservation_status_name)
        existing_status = ReservationStatus.query.filter(ReservationStatus.reservation_status_name == new_name, ReservationStatus.id_reservation_status != id).first()

        if existing_status:
            return jsonify({'message': 'El nombre del estado de la reservación ya está en uso'}), 409

        reservation_status.reservation_status_name = new_name
        reservation_status.updated_at = func.now()

        db.session.commit()
        return jsonify({'message': 'Estado de la reservación actualizado correctamente', 'id_reservation_status': id}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'El nombre del estado de la reservación ya está en uso'}), 409
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'message': 'Error al actualizar el estado de la reservación', 'detalles': str(e)}), 500


@api_blueprint.route('/reservation_status', methods=['GET'])
def get_reservation_statuses():
    # Recuperar los parámetros de búsqueda desde la solicitud
    id_reservation_status = request.args.get('id_reservation_status', '')
    reservation_status_name = request.args.get('reservation_status_name', '')

    # Iniciar la consulta
    query = ReservationStatus.query

    # Aplicar filtros si los parámetros de búsqueda están presentes
    if id_reservation_status:
        query = query.filter(ReservationStatus.id_reservation_status.ilike(f'%{id_reservation_status}%'))
    if reservation_status_name:
        query = query.filter(ReservationStatus.reservation_status_name.ilike(f'%{reservation_status_name}%'))

    # Ejecutar la consulta y devolver los resultados
    reservation_statuses = query.all()

    return jsonify([
        {
            'id_reservation_status': status.id_reservation_status,
            'reservation_status_name': status.reservation_status_name,
        } for status in reservation_statuses
    ])
