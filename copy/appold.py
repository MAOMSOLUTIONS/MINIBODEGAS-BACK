from flask import Flask, request, jsonify, url_for, session
from flask_cors import CORS
import os
import bcrypt
from cubi1000 import resolver_optimizacion
from flask_wtf.csrf import CSRFProtect

# Configuración
porcentaje_aumento = 0.9
app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)  # Genera una clave secreta aleatoria para mayor seguridad

# Simulación de una base de datos de usuarios
users = [
    {"username": "Miguel", "password": bcrypt.hashpw("Ochoa".encode('utf-8'), bcrypt.gensalt())},
    {"username": "usuario2", "password": bcrypt.hashpw("contraseña2".encode('utf-8'), bcrypt.gensalt())},
]

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = next((u for u in users if u["username"] == username), None)
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
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


@app.route("/reset-password", methods=["GET"])
def reset_password():
    try:
        email = request.json.get("email")
        # Implementar lógica para enviar correo y/o generar token
        response = {"success": True, "message": "Solicitud de restablecimiento de contraseña exitosa"}
        return jsonify(response), 200
    except Exception as e:
        response = {"success": False, "message": "Error en la solicitud de restablecimiento de contraseña"}
        return jsonify(response), 500


@app.route('/api/cubicuadraje', methods=['POST'])
def cubicuadraje():
    try:
        data = request.json
        paqueteria_total = data['paqueteria']
        # Procesamiento y cálculos...
        # ...
        response = {
            'message': 'Datos procesados exitosamente.',
            'resultados': resultados_por_paqueteria
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/')
def index():
    response = {"success": True, "message": "API de Acceso"}
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
