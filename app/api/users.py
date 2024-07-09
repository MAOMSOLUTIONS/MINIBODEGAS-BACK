from flask import request, jsonify, current_app, url_for  # Agrega url_for aquí
from . import api_blueprint
from ..database import db
from .models import User
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import traceback
from flask_mail import Mail, Message
from sqlalchemy import func
import bcrypt


#from app import app, mail


#class User(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String(80), nullable=False)
#    email = db.Column(db.String(120), unique=True, nullable=False)

#    def __repr__(self):
#        return f'<User {self.name}>'

@api_blueprint.route('/users', methods=['POST'])
def users():
    data = request.get_json()
    print(">>>>", data)
    
    # Validación básica de los campos requeridos
    if 'email' not in data:
        return jsonify({'error': 'Falta el nombre o el correo electrónico'}), 400    
    try:
        # Obtén la instancia de Mail de la aplicación
        mail = current_app.extensions['mail']
        # Validación adicional para birthDate
        birth_date = None
        if data.get('birth_date'):
            birth_date = datetime.strptime(data.get('birth_date'), '%d/%m/%Y').date()
        username = data.get("first_name")
        password = data.get("last_name")
        print('password',password)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        print('hashed_password',hashed_password)
        user = User(
            first_name=data.get('first_name'),
            username=username,
            password=hashed_password,
            last_name=data.get('last_name'),
            surname=data.get('surname'),
            birth_date=birth_date,  # Utiliza la fecha válida o None
            email=data.get('email'),
            phone=data.get('phone'),
            sex=data.get('sex'),
            street=data.get('street'),
            interior_number=data.get('interior_number'),
            exterior_number=data.get('exterior_number'),
            municipality=data.get('municipality'),
            city=data.get('city'),
            country=data.get('country'),
            postal_code=data.get('postal_code'),
            profile=data.get('profile'),
            status=data.get('status'),
            created_at = func.now()
        )
        db.session.add(user)
        db.session.commit()
        # Return a success response
        return jsonify({'message': 'Usuario creado correctamente', 'idUser': user.id_user}), 201
    except IntegrityError:
        # Handle integrity errors, e.g. a duplicate email
        db.session.rollback()
        return jsonify({'message': 'El email ya existe'}), 409
    except Exception as e:
        # Handle other exceptions
        db.session.rollback()
        traceback.print_exc()  # Imprime la traza del error
        return jsonify({'message': 'Un error ocurrió', 'detalles': str(e)}), 500


@api_blueprint.route('/users/<int:id_user>', methods=['PUT'])
def update_user(id_user):
    data = request.get_json()
    print(data)
    user = User.query.get(id_user)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    try:
        # Actualizar campos del usuario
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.surname = data.get('surname', user.surname)
        # Asegúrate de manejar adecuadamente la fecha de nacimiento
        birth_date = data.get('birth_date')
        if birth_date:
            user.birth_date = datetime.strptime(birth_date, '%d/%m/%Y').date()
        user.email = data.get('email', user.email)
        user.phone = data.get('phone', user.phone)
        user.sex = data.get('sex', user.sex)
        user.street = data.get('street', user.street)
        user.interior_number = data.get('interior_number', user.interior_number)
        user.exterior_number = data.get('exterior_number', user.exterior_number)
        user.municipality = data.get('municipality', user.municipality)
        user.city = data.get('city', user.city)
        user.country = data.get('country', user.country)
        user.postal_code = data.get('postal_code', user.postal_code)
        user.profile = data.get('profile', user.profile)
        user.status = data.get('status', user.status)
        user.updated_at =func.now()

        db.session.commit()
        print('Usuario actualizado correctamente')
        return jsonify({'message': 'Usuario actualizado correctamente','idUser': user.id_user}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()  # Esto ayudará en la depuración
        print('Error al actualizar el usuario')
        return jsonify({'message': 'Error al actualizar el usuario', 'detalles': str(e)}), 500

def generate_confirmation_token(email):
    # Genera un token de confirmación único (puedes usar una biblioteca como 'secrets' para esto)
    # También puedes incluir una marca de tiempo o algún otro dato para mayor seguridad
    return "TOKEN_AQUI"

def send_confirmation_email(email, token, mail):
    with current_app.app_context():
        # Envía el correo electrónico de confirmación
        msg = Message('Confirm your registration', sender='miguel.ochoa@cinlat.com', recipients=[email])
        msg.body = f'Click the following link to confirm your registration: {url_for("api.confirm", token=token, _external=True)}'
        mail.send(msg)

@api_blueprint.route('/confirm/<token>', methods=['GET'], endpoint='confirm')
def confirm(token):
    # Verifica el token y marca al usuario como confirmado en la base de datos
    user = User.query.filter_by(confirmation_token=token).first()
    if user:
        user.confirmed = True
        user.confirmation_token = None  # Opcional: Borra el token después de la confirmación
        db.session.commit()
        return jsonify({'message': 'User confirmed successfully'}), 200
    else:
        return jsonify({'message': 'Invalid or expired token'}), 400

@api_blueprint.route('/user', methods=['GET'])
def get_users():
   # Recuperar los parámetros de búsqueda desde la solicitud
    id_user = request.args.get('idUser', '')
    first_name = request.args.get('firstName', '')
    last_name = request.args.get('lastName', '')
    email = request.args.get('email', '')
    status = request.args.get('status', '')
    # Iniciar la consulta
    query = User.query
    # Aplicar filtros si los parámetros de búsqueda están presentes
    if id_user:
        query = query.filter(User.id_user.ilike(f'%{id_user}%'))
    if first_name:
        query = query.filter(User.first_name.ilike(f'%{first_name}%'))
    if last_name:
        query = query.filter(User.last_name.ilike(f'%{last_name}%'))
    if email:
        query = query.filter(User.email.ilike(f'%{email}%'))
    if status:
        query = query.filter(User.status.ilike(f'%{status}%'))

    
    # Ejecutar la consulta y devolver los resultados
    users = query.all()
    return jsonify([
            {
                'id_user': user.id_user, 
                'first_name': user.first_name, 
                'last_name': user.last_name, 
                'surname': user.surname,
                'birth_date': user.birth_date,
                'email': user.email,
                'phone': user.phone,
                'sex': user.sex,
                'street': user.street,
                'interior_number': user.interior_number,
                'exterior_number': user.exterior_number,
                'municipality': user.municipality,
                'city': user.city,
                'country': user.country,
                'postal_code': user.postal_code,
                'profile': user.profile,
                'status': user.status
            } for user in users
        ])