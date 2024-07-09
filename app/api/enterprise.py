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
        print("ESTAMOS AQUI")
        id_status = data.get('id_status')
        status = data.get('status')

        if id_status is None:
            return jsonify({'error': 'El campo id_status es requerido'}), 400
        if status is None:
            return jsonify({'error': 'El campo status es requerido'}), 400



        enterprise = Enterprise(
            enterprise_name=data.get('enterprise_name'),
            rfc=data.get('rfc'),
            id_status=id_status,
            status=status,            
            created_at=func.now()
        )
        print(enterprise.id_enterprise,enterprise.enterprise_name,enterprise.status,enterprise.id_status)
        db.session.add(enterprise)
        db.session.commit()
        # Return a success response
        return jsonify({'message': 'Empresa creada correctamente', 'idUser': enterprise.id_enterprise}), 201
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
    if not enterprise:
        return jsonify({'message': 'Empresa no encontrada'}), 404

    try:
        # Actualizar campos del usuario
        enterprise.first_name = data.get('first_name', enterprise.first_name)
        enterprise.last_name = data.get('last_name', enterprise.last_name)
        enterprise.surname = data.get('surname', enterprise.surname)
        # Asegúrate de manejar adecuadamente la fecha de nacimiento
        birth_date = data.get('birth_date')
        if birth_date:
            enterprise.birth_date = datetime.strptime(birth_date, '%d/%m/%Y').date()
        enterprise.email = data.get('email', enterprise.email)
        enterprise.phone = data.get('phone', enterprise.phone)
        enterprise.sex = data.get('sex', enterprise.sex)
        enterprise.street = data.get('street', enterprise.street)
        enterprise.interior_number = data.get('interior_number', enterprise.interior_number)
        enterprise.exterior_number = data.get('exterior_number', enterprise.exterior_number)
        enterprise.municipality = data.get('municipality', enterprise.municipality)
        enterprise.city = data.get('city', enterprise.city)
        enterprise.country = data.get('country', enterprise.country)
        enterprise.postal_code = data.get('postal_code', enterprise.postal_code)
        enterprise.profile = data.get('profile', enterprise.profile)
        enterprise.status = data.get('status', enterprise.status)
        enterprise.updated_at =func.now()

        db.session.commit()
        print('Empresa actualizada correctamente')
        return jsonify({'message': 'Empresa actualizada correctamente','idEnterprise': enterprise.id_enterprise}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()  # Esto ayudará en la depuración
        print('Error al actualizar el usuario')
        return jsonify({'message': 'Error al actualizar el usuario', 'detalles': str(e)}), 500



@api_blueprint.route('/enterprise', methods=['GET'])
def get_enterprise():
   # Recuperar los parámetros de búsqueda desde la solicitud
    print("estamos en la consulta")

    id_enterprise = request.args.get('id_enterprise', '')
    enterprise_name = request.args.get('enterprise_name', '')
    rfc = request.args.get('rfc', '')
    status = request.args.get('status', '')
    

    # Iniciar la consulta
    query = Enterprise.query
    # Aplicar filtros si los parámetros de búsqueda están presentes
    if id_enterprise:
        query = query.filter(Enterprise.id_enterprise.ilike(f'%{id_enterprise}%'))
    if enterprise_name:
        query = query.filter(Enterprise.enterprise_name.ilike(f'%{enterprise_name}%'))
    if rfc:
        query = query.filter(Enterprise.rfc.ilike(f'%{rfc}%'))
    if status:
        query = query.filter(Enterprise.status.ilike(f'%{status}%'))

    
    # Ejecutar la consulta y devolver los resultados
    enterprises = query.all()

    return jsonify([
        {
            'id_enterprise': enterprise.id_enterprise, 
            'enterprise_name': enterprise.enterprise_name, 
            'rfc': enterprise.rfc, 
            'status': enterprise.status
        } for enterprise in enterprises
    ])