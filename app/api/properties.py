from flask import request, jsonify, current_app, url_for  # Agrega url_for aquí
from . import api_blueprint
from ..database import db
from .models import Property
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import traceback
from flask_mail import Mail, Message
from sqlalchemy import func
import bcrypt



@api_blueprint.route('/properties', methods=['POST'])
def create_property():
    data = request.get_json()

    # Validación básica de los campos requeridos
    if 'property_name' not in data or 'enterprise_id' not in data or 'property_id_status' not in data:
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    try:
        property = Property(
            property_name=data.get('property_name'),
            enterprise_id=data.get('enterprise_id'),
            property_id_status=data.get('property_id_status'),
            created_at=func.now()
        )

        db.session.add(property)
        db.session.commit()

        return jsonify({'message': 'Propiedad creada correctamente', 'property_id': property.id_property}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Error de integridad de datos'}), 409
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'message': 'Un error ocurrió', 'detalles': str(e)}), 500


@api_blueprint.route('/properties/<int:property_id>', methods=['PUT'])
def update_property(property_id):
    data = request.get_json()
    property = Property.query.get(property_id)

    if not property:
        return jsonify({'message': 'Propiedad no encontrada'}), 404

    try:
        property.property_name = data.get('property_name', property.property_name)
        property.enterprise_id = data.get('enterprise_id', property.enterprise_id)
        property.property_id_status = data.get('property_id_status', property.property_id_status)
        property.updated_at = func.now()

        db.session.commit()
        return jsonify({'message': 'Propiedad actualizada correctamente', 'property_id': property_id}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Error de integridad de datos'}), 409
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'message': 'Error al actualizar la propiedad', 'detalles': str(e)}), 500


@api_blueprint.route('/properties', methods=['GET'])
def get_properties():
    # Recuperar los parámetros de búsqueda desde la solicitud
    id_property = request.args.get('id_property', '')
    property_name = request.args.get('property_name', '')
    enterprise_id = request.args.get('enterprise_id', '')
    property_id_status = request.args.get('property_id_status', '')

    # Iniciar la consulta
    query = Property.query

    # Aplicar filtros si los parámetros de búsqueda están presentes
    if id_property:
        query = query.filter(Property.id_property.ilike(f'%{id_property}%'))
    if property_name:
        query = query.filter(Property.property_name.ilike(f'%{property_name}%'))
    if enterprise_id:
        query = query.filter(Property.enterprise_id.ilike(f'%{enterprise_id}%'))
    if property_id_status:
        query = query.filter(Property.property_id_status.ilike(f'%{property_id_status}%'))

    # Ejecutar la consulta y devolver los resultados
    properties = query.all()

    return jsonify([
        {
            'id_property': prop.id_property,
            'property_name': prop.property_name,
            'enterprise_id': prop.enterprise_id,
            'enterprise_name': prop.enterprise.enterprise_name if prop.enterprise else None,
            'property_id_status': prop.property_id_status,
            'status_name': prop.status.status_name if prop.status else None,
            'created_at': prop.created_at,
            'updated_at': prop.updated_at
        } for prop in properties
    ])