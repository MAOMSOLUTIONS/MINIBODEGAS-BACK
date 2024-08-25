from flask import request, jsonify
from . import api_blueprint
from ..database import db
from .models import Client
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import traceback

@api_blueprint.route('/clients', methods=['POST'])
def create_client():
    data = request.get_json()

    # Validación básica de los campos requeridos
    if 'client_name' not in data or 'client_email' not in data or 'client_phone' not in data:
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    try:
        client = Client(
            client_name=data.get('client_name'),
            client_email=data.get('client_email'),
            client_phone=data.get('client_phone'),
            client_address=data.get('client_address'),
            created_at=func.now()
        )

        # Agregar el cliente a la sesión de la base de datos
        db.session.add(client)
        db.session.commit()

        # Confirmar que el cliente se ha añadido correctamente
        added_client = Client.query.filter_by(client_email=data.get('client_email')).first()

        if added_client:
            print(f"Cliente agregado: {added_client.client_name}, ID: {added_client.id_client}")
        else:
            print("No se encontró el cliente después de agregarlo.")

        # Retornar una respuesta exitosa
        return jsonify({'message': 'Cliente creado correctamente', 'client_id': client.id_client}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'El email ya existe'}), 409
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()  # Imprime la traza del error
        return jsonify({'message': 'Un error ocurrió', 'detalles': str(e)}), 500

@api_blueprint.route('/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    data = request.get_json()
    client = Client.query.get(client_id)
    
    if not client:
        return jsonify({'message': 'Cliente no encontrado'}), 404
    try:
        # Verificar si el nuevo email del cliente ya existe en otro registro
        new_email = data.get('client_email', client.client_email)
        existing_client = Client.query.filter(Client.client_email == new_email, Client.id_client != client_id).first()

        if existing_client:
            return jsonify({'message': 'El email ya está en uso'}), 409

        # Actualizar campos del cliente existente
        client.client_name = data.get('client_name', client.client_name)
        client.client_email = new_email
        client.client_phone = data.get('client_phone', client.client_phone)
        client.client_address = data.get('client_address', client.client_address)
        client.updated_at = func.now()

        db.session.commit()
        return jsonify({'message': 'Cliente actualizado correctamente', 'client_id': client_id}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'El email ya está en uso'}), 409
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()  # Esto ayudará en la depuración
        return jsonify({'message': 'Error al actualizar el cliente', 'detalles': str(e)}), 500

@api_blueprint.route('/client', methods=['GET'])
def get_clients():
    # Recuperar los parámetros de búsqueda desde la solicitud
    id_client = request.args.get('id_client', '')
    client_name = request.args.get('client_name', '')
    client_email = request.args.get('client_email', '')
    client_phone = request.args.get('client_phone', '')

    # Iniciar la consulta
    query = Client.query

    # Aplicar filtros si los parámetros de búsqueda están presentes
    if id_client:
        query = query.filter(Client.id_client.ilike(f'%{id_client}%'))
    if client_name:
        query = query.filter(Client.client_name.ilike(f'%{client_name}%'))
    if client_email:
        query = query.filter(Client.client_email.ilike(f'%{client_email}%'))
    if client_phone:
        query = query.filter(Client.client_phone.ilike(f'%{client_phone}%'))

    # Ejecutar la consulta y devolver los resultados
    clients = query.all()

    return jsonify([
        {
            'id_client': client.id_client,
            'client_name': client.client_name,
            'client_phone': client.client_phone,
            'client_email': client.client_email,
            'client_address': client.client_address,
            'created_at': client.created_at,
            'updated_at': client.updated_at
        } for client in clients
    ])

@api_blueprint.route('/client_active', methods=['GET'])
def get_active_clients():
    # Iniciar la consulta filtrando por clientes activos (asumiendo que tienen algún criterio específico)
    query = Client.query.filter(Client.client_phone != '')  # Ejemplo de criterio

    # Ejecutar la consulta y devolver los resultados
    clients = query.all()

    return jsonify([
        {
            'id_client': client.id_client,
            'client_name': client.client_name,
            'client_phone': client.client_phone,
            'client_email': client.client_email,
            'client_address': client.client_address,
            'created_at': client.created_at,
            'updated_at': client.updated_at
        } for client in clients
    ])
