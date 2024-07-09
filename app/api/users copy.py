from flask import request, jsonify, current_app, url_for  # Agrega url_for aquí
from . import api_blueprint
from ..database import db
from .models import User
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import traceback
from flask_mail import Mail, Message
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
    print(">>>>",data)
    # Validación básica de los campos requeridos
    if 'email' not in data:
        return jsonify({'error': 'Falta el nombre o el correo electrónico'}), 400
    try:
        print("aqui")
        # Obtén la instancia de Mail de la aplicación
        mail = current_app.extensions['mail']
#        mail = Mail(app)

        user = User(
            first_name=data.get('firstName'),
            last_name=data.get('lastName'),
            surname=data.get('surname'),
            birth_date=datetime.strptime(data.get('birthDate'), '%Y-%m-%d').date(),
            email=data.get('email'),
            phone=data.get('phone'),
            sex=data.get('sex'),
            street=data.get('street'),
            interior_number=data.get('interiorNumber'),
            exterior_number=data.get('exteriorNumber'),
            municipality=data.get('municipality'),
            city=data.get('city'),
            country=data.get('country'),
            postal_code=data.get('postalCode'),
            profile=data.get('profile'),
            status=data.get('status')


        )
        # Genera un token de confirmación único
        confirmation_token = generate_confirmation_token(user.email)
        # Envía el correo electrónico de confirmación
##        send_confirmation_email(user.email, confirmation_token,mail)
        # Guarda el token en la base de datos
        user.confirmation_token = confirmation_token
        
        # Add user to the session and commit to the database
        db.session.add(user)
        db.session.commit()
        # Return a success response
        return jsonify({'message': 'User created successfully', 'idUser': user.id}), 201
    except IntegrityError:
        # Handle integrity errors, e.g. a duplicate email
        db.session.rollback()
        return jsonify({'message': 'Email already exists'}), 409
    except Exception as e:
        # Handle other exceptions
        db.session.rollback()
        traceback.print_exc()  # Imprime la traza del error
        return jsonify({'message': 'An error occurred', 'details': str(e)}), 500

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
        query = query.filter(User.id.ilike(f'%{id_user}%'))
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
                'id': user.id, 
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