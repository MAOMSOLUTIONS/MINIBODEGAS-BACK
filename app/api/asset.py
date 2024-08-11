from flask import request, jsonify, current_app, url_for  # Agrega url_for aquí
from . import api_blueprint
from ..database import db
from .models import Asset
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import traceback
from flask_mail import Mail, Message
from sqlalchemy import func
import bcrypt

@api_blueprint.route('/assets', methods=['POST'])
def add_asset():
    data = request.get_json()
    print("Datos recibidos:", data)  # Agrega esta línea para ver los datos recibidos
    try:
        asset = Asset(
            id_property=data['id_property'],
            asset_number=data['asset_number'],
            asset_name=data['asset_name'],
            asset_front=data['asset_front'],
            asset_depth=data['asset_depth'],
            asset_height=data['asset_height'],
            asset_m2=data['asset_m2'],
            asset_m3=data['asset_m3'],
            asset_comments=data.get('asset_comments'),
            asset_photo1=data.get('asset_photo1'),
            asset_photo2=data.get('asset_photo2'),
            asset_photo3=data.get('asset_photo3'),
            asset_photo4=data.get('asset_photo4'),
            asset_photo5=data.get('asset_photo5'),
            asset_type=data['asset_type'],
            asset_status=data['asset_status']
        )
        db.session.add(asset)
        db.session.commit()
        return jsonify({'message': 'Asset creado correctamente', 'id': asset.id_asset}), 201
    except Exception as e:
        db.session.rollback()
        print("Error:", e)  # Agrega esta línea para ver el error detallado
        return jsonify({'message': 'Error al crear el Asset', 'details': str(e)}), 500
        
@api_blueprint.route('/assets/<int:id_asset>', methods=['PUT'])
def update_asset(id_asset):
    data = request.get_json()
    try:
        asset = Asset.query.get(id_asset)
        if not asset:
            return jsonify({'message': 'Asset no encontrado'}), 404

        asset.id_property = data['id_property']
        asset.asset_number = data['asset_number']
        asset.asset_name = data['asset_name']
        asset.asset_front = data['asset_front']
        asset.asset_depth = data['asset_depth']
        asset.asset_height = data['asset_height']
        asset.asset_m2 = data['asset_m2']
        asset.asset_m3 = data['asset_m3']
        asset.asset_comments = data.get('asset_comments')
        asset.asset_photo1 = data.get('asset_photo1')
        asset.asset_photo2 = data.get('asset_photo2')
        asset.asset_photo3 = data.get('asset_photo3')
        asset.asset_photo4 = data.get('asset_photo4')
        asset.asset_photo5 = data.get('asset_photo5')
        asset.asset_type = data['asset_type']
        asset.asset_status = data['asset_status']

        db.session.commit()
        return jsonify({'message': 'Asset actualizado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al actualizar el Asset', 'details': str(e)}), 500

@api_blueprint.route('/assets', methods=['GET'])
def get_assets():
    try:
        assets = Asset.query.all()
        assets_list = [{
            'id_asset': asset.id_asset,
            'id_property': asset.id_property,
            'property_name': asset.property.property_name if asset.property else None,
            'asset_number': asset.asset_number,
            'asset_name': asset.asset_name,
            'asset_type': asset.asset_type,
            'asset_type_name': asset.asset_type_rel.asset_type_name if asset.asset_type_rel else None,
            'asset_status': asset.asset_status,
            'asset_status_name': asset.asset_status_rel.status_name if asset.asset_status_rel else None,
            'asset_front': asset.asset_front,
            'asset_depth': asset.asset_depth,
            'asset_height': asset.asset_height,
            'asset_m2': asset.asset_m2,
            'asset_m3': asset.asset_m3,
            'asset_comments': asset.asset_comments,
            'asset_photo1': asset.asset_photo1,
            'asset_photo2': asset.asset_photo2,
            'asset_photo3': asset.asset_photo3,
            'asset_photo4': asset.asset_photo4,
            'asset_photo5': asset.asset_photo5,
        } for asset in assets]

        return jsonify(assets_list), 200
    except Exception as e:
        return jsonify({'message': 'Error al obtener los assets', 'details': str(e)}), 500