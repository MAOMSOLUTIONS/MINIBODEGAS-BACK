from flask import request, jsonify
from . import api_blueprint
from ..database import db
from .models import Status
from sqlalchemy.exc import IntegrityError

@api_blueprint.route('/status', methods=['POST'])
def add_status():
    data = request.get_json()

    # Validación básica
    if 'status_name' not in data:
        return jsonify({'error': 'Falta el nombre del estado'}), 400

    try:
        status = Status(
            id_status=data.get('id_status'),
            status_name=data.get('status_name')
        )

        db.session.add(status)
        db.session.commit()
        print("Estado agregado correctamente")

        return jsonify({'message': 'Estado creado correctamente', 'id': status.id_status}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'El estado ya existe'}), 409
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'message': 'Un error ocurrió', 'detalles': str(e)}), 500

@api_blueprint.route('/status', methods=['GET'])
def get_status():
    try:
        # Consultar todos los registros de la tabla Status
        statuses = Status.query.all()
        
        # Convertir los objetos en una lista de diccionarios
        status_list = [{'id_status': status.id_status, 'status_name': status.status_name} for status in statuses]

        return jsonify(status_list), 200
    except Exception as e:
        # Manejo de errores
        print(f"Error al obtener el estado: {str(e)}")
        return jsonify({'message': 'Un error ocurrió al obtener los estados'}), 500

@api_blueprint.route('/status/<int:id>', methods=['PUT'])
def update_status(id):
    data = request.get_json()

    try:
        # Buscar el estado por su ID
        status = Status.query.get(id)
        if not status:
            return jsonify({'message': 'Estado no encontrado'}), 404

        # Actualizar los campos
        if 'status_name' in data:
            status.status_name = data['status_name']

        db.session.commit()
        return jsonify({'message': 'Estado actualizado correctamente'}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'El nombre del estado ya existe'}), 409
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'message': 'Un error ocurrió al actualizar el estado', 'detalles': str(e)}), 500
