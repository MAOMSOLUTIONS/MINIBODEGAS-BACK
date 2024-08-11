from flask import request, jsonify
from . import api_blueprint
from ..database import db
from .models import AssetType
from sqlalchemy.exc import IntegrityError

@api_blueprint.route('/asset_type', methods=['POST'])
def add_asset_type():
    data = request.get_json()

    if 'asset_type_name' not in data:
        return jsonify({'error': 'Falta el nombre del tipo de asset'}), 400

    try:
        asset_type = AssetType(
            asset_type_name=data.get('asset_type_name')
        )

        db.session.add(asset_type)
        db.session.commit()
        return jsonify({'message': 'Tipo de asset creado correctamente', 'id': asset_type.id_asset_type}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'El tipo de asset ya existe'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Un error ocurrió', 'detalles': str(e)}), 500

@api_blueprint.route('/asset_type', methods=['GET'])
def get_asset_types():
    try:
        asset_types = AssetType.query.all()
        asset_type_list = [{'id_asset_type': asset_type.id_asset_type, 'asset_type_name': asset_type.asset_type_name} for asset_type in asset_types]
        return jsonify(asset_type_list), 200
    except Exception as e:
        return jsonify({'message': 'Un error ocurrió al obtener los tipos de asset'}), 500

@api_blueprint.route('/asset_type/<int:id>', methods=['PUT'])
def update_asset_type(id):
    data = request.get_json()

    if 'asset_type_name' not in data:
        return jsonify({'error': 'Falta el nombre del tipo de asset'}), 400

    try:
        asset_type = AssetType.query.get(id)
        if asset_type is None:
            return jsonify({'message': 'Tipo de asset no encontrado'}), 404

        asset_type.asset_type_name = data.get('asset_type_name')

        db.session.commit()
        return jsonify({'message': 'Tipo de asset actualizado correctamente'}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'El tipo de asset ya existe'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Un error ocurrió', 'detalles': str(e)}), 500

@api_blueprint.route('/asset_type/<int:id>', methods=['DELETE'])
def delete_asset_type(id):
    try:
        asset_type = AssetType.query.get(id)
        if asset_type is None:
            return jsonify({'message': 'Tipo de asset no encontrado'}), 404

        db.session.delete(asset_type)
        db.session.commit()
        return jsonify({'message': 'Tipo de asset eliminado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Un error ocurrió al eliminar el tipo de asset', 'detalles': str(e)}), 500
