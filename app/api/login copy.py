from flask import request, jsonify
from . import api_blueprint
import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf.csrf import CSRFProtect

# Crear una instancia de la aplicación Flask
csrf = CSRFProtect()

users = [
    {"username": "Miguel", "password": bcrypt.hashpw("Ochoa".encode('utf-8'), bcrypt.gensalt())},
    {"username": "usuario2", "password": bcrypt.hashpw("contraseña2".encode('utf-8'), bcrypt.gensalt())},
]

@api_blueprint.route("/login", methods=["POST"])
@csrf.exempt  # Eximir la vista de CSRF para permitir la autenticación
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = next((u for u in users if u["username"] == username), None)

    stored_password = user["password"]
    if isinstance(stored_password, str):
        stored_password = stored_password.encode('utf-8')

    if user and bcrypt.checkpw(password.encode('utf-8'), stored_password):
        response = {
            "success": True,
            'message': 'Inicio de sesión exitoso',
        }
        return jsonify(response)
    else:
        response = {
            "success": False,
            'message': 'Credenciales incorrectas'
        }
        return jsonify(response)
