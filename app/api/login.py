from flask import request, jsonify
from . import api_blueprint
import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf.csrf import CSRFProtect
from .models import User
from flask import session



# Crear una instancia de la aplicación Flask
csrf = CSRFProtect()

@api_blueprint.route("/login", methods=["POST"])
@csrf.exempt  # Eximir la vista de CSRF para permitir la autenticación
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

#    response = {
#        "success": True,
#        'message': 'Inicio de sesión exitoso',
#        'usuario': username
#    }
#    return jsonify(response)
    if user:
        stored_password = user.password
        print(user.first_name)
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        try:
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                session['user_id'] = user.id_user
                response = {
                    "success": True,
                    'message': 'Inicio de sesión exitoso',
                    'usuario': user.first_name + " " +user.last_name
                }
                return jsonify(response)
            else:
                response = {
                    "success": False,
                    'message': 'Credenciales incorrectas'
                }
                return jsonify(response)
        except ValueError as e:
            print("Error en la verificación de la contraseña:", e)
            # Aquí puedes manejar el error adecuadamente y enviar una respuesta.
            response = {
                "success": False,
                'message': 'Error al verificar las credenciales'
            }
            return jsonify(response)
    else:
        response = {
            "success": False,
            'message': 'Usuario no encontrado'
        }
        return jsonify(response)