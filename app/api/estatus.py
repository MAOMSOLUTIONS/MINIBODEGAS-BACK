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
    print("aqui")
    return jsonify({'message': 'Un error ocurrió'}), 500
