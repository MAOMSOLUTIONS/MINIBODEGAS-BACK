from flask import request, jsonify
from . import api_blueprint
from ..database import db
from .models import AssetStatus
from sqlalchemy.exc import IntegrityError 

@api_blueprint.route('/asset_status', methods=['POST'])
def add_asset_status():
    data = request.get_json()

    if 'status_name' not in data:
        return jsonify({'error': 'Falta el nombre del estado'}), 400

    try:
        asset_status = AssetStatus(
            status_name=data['status_name']
        )
        db.session.add(asset_status)
        db.session.commit()
        return jsonify({'message': 'Estado de asset creado correctamente', 'id': asset_status.id_status}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'El estado ya existe'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Un error ocurrió', 'detalles': str(e)}), 500

@api_blueprint.route('/asset_status', methods=['GET'])
def get_asset_statuses():
    try:
        statuses = AssetStatus.query.all()
        status_list = [{'id_status': status.id_status, 'status_name': status.status_name} for status in statuses]
        return jsonify(status_list), 200
    except Exception as e:
        return jsonify({'message': 'Un error ocurrió al obtener los estados'}), 500

@api_blueprint.route('/asset_status/<int:id>', methods=['PUT'])
def update_asset_status(id):
    data = request.get_json()

    try:
        status = AssetStatus.query.get(id)
        if not status:
            return jsonify({'message': 'Estado no encontrado'}), 404
        
        status.status_name = data.get('status_name', status.status_name)
        db.session.commit()
        return jsonify({'message': 'Estado de asset actualizado correctamente'}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'El estado ya existe'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Un error ocurrió', 'detalles': str(e)}), 500
