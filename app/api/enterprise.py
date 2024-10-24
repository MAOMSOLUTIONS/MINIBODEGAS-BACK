from flask import request, jsonify, current_app, url_for  # Agrega url_for aquí
from . import api_blueprint
from ..database import db
from .models import Enterprise
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import traceback
from flask_mail import Mail, Message
from sqlalchemy import func
import bcrypt



@api_blueprint.route('/enterprises', methods=['POST'])
def enterprises():
    data = request.get_json()
    
    # Validación básica de los campos requeridos
    if 'enterprise_name' not in data:
        return jsonify({'error': 'Falta el nombre de la empresa'}), 400    
    try:
        enterprise = Enterprise(
            enterprise_name=data.get('enterprise_name'),
            enterprise_rfc=data.get('enterprise_rfc'),
            enterprise_phone=data.get('enterprise_phone'),
            enterprise_email=data.get('enterprise_email'),
            enterprise_contact_name=data.get('enterprise_contact_name'),
            enterprise_fiscal_name=data.get('enterprise_fiscal_name'),
            enterprise_fiscal_street=data.get('enterprise_fiscal_street'),
            enterprise_fiscal_internal_number=data.get('enterprise_fiscal_internal_number'),
            enterprise_fiscal_external_number=data.get('enterprise_fiscal_external_number'),
            enterprise_fiscal_municipio=data.get('enterprise_fiscal_municipio'),
            enterprise_fiscal_state=data.get('enterprise_fiscal_state'),
            enterprise_fiscal_country=data.get('enterprise_fiscal_country'),
            enterprise_fiscal_postal_code=data.get('enterprise_fiscal_postal_code'),
            enterprise_fiscal_email=data.get('enterprise_fiscal_email'),
            enterprise_fiscal_phone=data.get('enterprise_fiscal_phone'),
            enterprise_id_status=data.get('enterprise_id_status'),
            created_at=func.now()
        )

        print(enterprise.enterprise_name,enterprise.enterprise_id_status)
        # Agregar la empresa a la sesión de la base de datos
        db.session.add(enterprise)
        db.session.commit()
        print("Comit exitoso")


        # Confirmar que la empresa se ha añadido correctamente
        added_enterprise = Enterprise.query.filter_by(enterprise_name=data.get('enterprise_name')).first()


        if added_enterprise:
            print(f"Empresa agregada: {added_enterprise.enterprise_name}, ID: {added_enterprise.id_enterprise}")
        else:
            print("No se encontró la empresa después de agregarla.")

        # Return a success response
        return jsonify({'message': 'Empresa creada correctamente', 'enterprise_id': enterprise.id_enterprise}), 201
    except IntegrityError:
        # Handle integrity errors, e.g. a duplicate email
        db.session.rollback()
        return jsonify({'message': 'El email ya existe'}), 409
    except Exception as e:
        # Handle other exceptions
        db.session.rollback()
        traceback.print_exc()  # Imprime la traza del error
        return jsonify({'message': 'Un error ocurrió', 'detalles': str(e)}), 500


@api_blueprint.route('/enterprises/<int:enterprise_id>', methods=['PUT'])
def update_enterprises(enterprise_id):
    data = request.get_json()
    enterprise = Enterprise.query.get(enterprise_id)
    print("aqui estamos")
    if not enterprise:
        return jsonify({'message': 'Empresa no encontrada'}), 404
    try:
        # Verificar si el nuevo nombre de la empresa ya existe en otro registro
        new_name = data.get('enterprise_name', enterprise.enterprise_name)
        existing_enterprise = Enterprise.query.filter(Enterprise.enterprise_name == new_name, Enterprise.id_enterprise != enterprise_id).first()
        
        if existing_enterprise:
            return jsonify({'message': 'El nombre de la empresa ya está en uso'}), 409

        # Actualizar campos de la empresa existente
        enterprise.enterprise_name = new_name
        enterprise.enterprise_rfc = data.get('enterprise_rfc', enterprise.enterprise_rfc)
        enterprise.enterprise_phone = data.get('enterprise_phone', enterprise.enterprise_phone)
        enterprise.enterprise_email = data.get('enterprise_email', enterprise.enterprise_email)
        enterprise.enterprise_contact_name = data.get('enterprise_contact_name', enterprise.enterprise_contact_name)
        enterprise.enterprise_fiscal_name = data.get('enterprise_fiscal_name', enterprise.enterprise_fiscal_name)
        enterprise.enterprise_fiscal_street = data.get('enterprise_fiscal_street', enterprise.enterprise_fiscal_street)
        enterprise.enterprise_fiscal_internal_number = data.get('enterprise_fiscal_internal_number', enterprise.enterprise_fiscal_internal_number)
        enterprise.enterprise_fiscal_external_number = data.get('enterprise_fiscal_external_number', enterprise.enterprise_fiscal_external_number)
        enterprise.enterprise_fiscal_municipio = data.get('enterprise_fiscal_municipio', enterprise.enterprise_fiscal_municipio)
        enterprise.enterprise_fiscal_state = data.get('enterprise_fiscal_state', enterprise.enterprise_fiscal_state)
        enterprise.enterprise_fiscal_country = data.get('enterprise_fiscal_country', enterprise.enterprise_fiscal_country)
        enterprise.enterprise_fiscal_postal_code = data.get('enterprise_fiscal_postal_code', enterprise.enterprise_fiscal_postal_code)
        enterprise.enterprise_fiscal_email = data.get('enterprise_fiscal_email', enterprise.enterprise_fiscal_email)
        enterprise.enterprise_fiscal_phone = data.get('enterprise_fiscal_phone', enterprise.enterprise_fiscal_phone)
        enterprise.enterprise_id_status = data.get('enterprise_id_status', enterprise.enterprise_id_status)
        enterprise.updated_at = func.now()
        
        db.session.commit()
        return jsonify({'message': 'Empresa actualizada correctamente', 'enterprise_id': enterprise_id}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'El nombre de la empresa ya está en uso'}), 409
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()  # Esto ayudará en la depuración
        print('Error al actualizar la empresa')
        return jsonify({'message': 'Error al actualizar la empresa', 'detalles': str(e)}), 500
    


@api_blueprint.route('/enterprise', methods=['GET'])
def get_enterprise():
    # Recuperar los parámetros de búsqueda desde la solicitud
    id_enterprise = request.args.get('id_enterprise', '')
    enterprise_name = request.args.get('enterprise_name', '')
    enterprise_rfc = request.args.get('enterprise_rfc', '')  # Cambiado de 'rfc' a 'enterprise_rfc'
    enterprise_id_status = request.args.get('enterprise_id_status', '')  # Cambiado de 'status' a 'enterprise_id_status'

    # Iniciar la consulta
    query = Enterprise.query
    # Aplicar filtros si los parámetros de búsqueda están presentes
    if id_enterprise:
        query = query.filter(Enterprise.id_enterprise.ilike(f'%{id_enterprise}%'))
    if enterprise_name:
        query = query.filter(Enterprise.enterprise_name.ilike(f'%{enterprise_name}%'))
    if enterprise_rfc:
        query = query.filter(Enterprise.enterprise_rfc.ilike(f'%{enterprise_rfc}%'))  # Cambiado de 'rfc' a 'enterprise_rfc'
    if enterprise_id_status:
        query = query.filter(Enterprise.enterprise_id_status.ilike(f'%{enterprise_id_status}%'))  # Cambiado de 'status' a 'enterprise_id_status'

    # Ejecutar la consulta y devolver los resultados
    enterprises = query.all()

    for enterprise in enterprises:
        print(f"Enterprise ID: {enterprise.id_enterprise}, Name: {enterprise.enterprise_name}, RFC: {enterprise.enterprise_rfc}, ID_STATUS: {enterprise.enterprise_id_status}")

    return jsonify([
        {
          'id_enterprise': enterprise.id_enterprise,
            'enterprise_name': enterprise.enterprise_name,
            'enterprise_rfc': enterprise.enterprise_rfc,
            'enterprise_phone': enterprise.enterprise_phone,
            'enterprise_email': enterprise.enterprise_email,
            'enterprise_contact_name': enterprise.enterprise_contact_name,
            'enterprise_fiscal_name': enterprise.enterprise_fiscal_name,
            'enterprise_fiscal_street': enterprise.enterprise_fiscal_street,
            'enterprise_fiscal_external_number': enterprise.enterprise_fiscal_external_number,
            'enterprise_fiscal_municipio': enterprise.enterprise_fiscal_municipio,
            'enterprise_fiscal_state': enterprise.enterprise_fiscal_state,
            'enterprise_fiscal_country': enterprise.enterprise_fiscal_country,
            'enterprise_fiscal_postal_code': enterprise.enterprise_fiscal_postal_code,
            'enterprise_fiscal_email': enterprise.enterprise_fiscal_email,
            'enterprise_fiscal_phone': enterprise.enterprise_fiscal_phone,

            'enterprise_id_status': enterprise.enterprise_id_status,
            'status_name': enterprise.status.status_name if enterprise.status else None,  # Corregido

            'created_at': enterprise.created_at,
            'updated_at': enterprise.updated_at
        } for enterprise in enterprises
    ])


@api_blueprint.route('/enterprise_active', methods=['GET'])
def get_enterprise_active():

    # Iniciar la consulta filtrando por empresas activas (suponiendo que enterprise_id_status=1 indica "activo")
    query = Enterprise.query.filter(Enterprise.enterprise_id_status == 1)


    # Ejecutar la consulta y devolver los resultados
    enterprises = query.all()

    return jsonify([
        {
            'id_enterprise': enterprise.id_enterprise,
            'enterprise_name': enterprise.enterprise_name,
            'enterprise_rfc': enterprise.enterprise_rfc,
            'enterprise_phone': enterprise.enterprise_phone,
            'enterprise_email': enterprise.enterprise_email,
            'enterprise_contact_name': enterprise.enterprise_contact_name,
            'enterprise_fiscal_name': enterprise.enterprise_fiscal_name,
            'enterprise_fiscal_street': enterprise.enterprise_fiscal_street,
            'enterprise_fiscal_external_number': enterprise.enterprise_fiscal_external_number,
            'enterprise_fiscal_municipio': enterprise.enterprise_fiscal_municipio,
            'enterprise_fiscal_state': enterprise.enterprise_fiscal_state,
            'enterprise_fiscal_country': enterprise.enterprise_fiscal_country,
            'enterprise_fiscal_postal_code': enterprise.enterprise_fiscal_postal_code,
            'enterprise_fiscal_email': enterprise.enterprise_fiscal_email,
            'enterprise_fiscal_phone': enterprise.enterprise_fiscal_phone,
            'enterprise_id_status': enterprise.enterprise_id_status,
            'status_name': enterprise.status.status_name if enterprise.status else None,
            'created_at': enterprise.created_at,
            'updated_at': enterprise.updated_at
        } for enterprise in enterprises
    ])
