from flask import Flask, request, jsonify, url_for, session
from flask_cors import CORS
import os
import bcrypt
from cubi1000 import resolver_optimizacion  # Importa la función resolver_optimizacion desde cubi113.py

porcentaje_aumento  = 0.9
app = Flask(__name__)
CORS(app)
app.secret_key = 'tu_clave_secreta' # Clave secreta para firmar los JWT

# Simulación de una base de datos de usuarios
users = [
    {"username": "Miguel", "password": "Ochoa"},
    {"username": "usuario2", "password": "contraseña2"},
]

@app.route("/api/login", methods=["POST"])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        print("data",data)

        user = next((u for u in users if u["username"] == username), None)
        if user and user["password"] == password:
            print("Inicio de sesión exitoso")

            # Genera una sal válida para bcrypt
            salt = bcrypt.gensalt()
            # Contraseña de ejemplo (cámbiala a la contraseña real)
            # Codifica la contraseña en formato UTF-8 antes de hashearla
            password_bytes = password.encode('utf-8')
            # Hashea la contraseña con la sal generada
            hashed_password = bcrypt.hashpw(password_bytes, salt)
            # El resultado 'hashed_password' es el hash de la contraseña que puedes almacenar en tu base de datos        
            print(hashed_password)
            # Contraseña ingresada por el usuario (cámbiala según lo que ingrese el usuario)
            user_input_password_bytes = password.encode('utf-8')
            # Verifica si la contraseña ingresada coincide con el hash almacenado
            if bcrypt.checkpw(user_input_password_bytes, hashed_password):

                
                print("La contraseña es válida.")
            else:
                print("La contraseña no es válida.")
            response = {
                "success": True,
                'message': 'Inicio de sesión exitoso',
            }
            return jsonify(response)
        else:
            print("Credenciales incorrectas")
            response = {
                "success": False,
                'message': 'Credenciales incorrectas'
            }
            return jsonify(response)


@app.route("/reset-password", methods=["GET"])
def reset_password():
    try:
        print("aqui")
        # Recibe la dirección de correo electrónico del cliente
        email = request.json.get("email")

        # Aquí puedes implementar la lógica para enviar un correo de restablecimiento de contraseña
        # y/o generar un token de restablecimiento de contraseña.

        # Enviar el correo o realizar otras acciones necesarias.

        # Responder con una confirmación de éxito.
        response = {"success": True, "message": "Solicitud de restablecimiento de contraseña exitosa"}
        return jsonify(response), 200
    except Exception as e:
        # Manejo de errores
        print(str(e))
        response = {"success": False, "message": "Error en la solicitud de restablecimiento de contraseña"}
        return jsonify(response), 500
    
@app.route('/api/cubicuadraje', methods=['POST'])
def cubicuadraje():
    try:
        # Obtén los datos de productos y paquetería del cuerpo de la solicitud
        data = request.json
        paqueteria_total = data['paqueteria']
        # Procesa los datos y conviértelos en el formato deseado
        datos_procesados = {}
        for producto in data['productos']:
            paqueteria = producto['PAQUETERIA']
            if paqueteria not in datos_procesados:
                datos_procesados[paqueteria] = {
                    'productos': [],
                    'volumen_producto': {},
                    'demanda_producto': {}
                }
            producto_codigo = f'Producto_{producto["CÓDIGO"]}'
            datos_procesados[paqueteria]['productos'].append(producto_codigo)
            datos_procesados[paqueteria]['volumen_producto'][producto_codigo] = float(producto['VOLUMEN M3'])
            datos_procesados[paqueteria]['demanda_producto'][producto_codigo] = producto['CANTIDAD']

        resultados_por_paqueteria = {}
        for paqueteria, datos in datos_procesados.items():
            camiones_filtrados = [camion for camion in paqueteria_total if camion['PAQUETERIA'] == paqueteria]
            capacidad_camion = {
                camion['CAMION']: camion['VOLUMEN M3'] for camion in camiones_filtrados
            }
#            print(">>>>>>>>>>>")
#            print(f"Paquetería: {paqueteria}")
#            print("Productos:", datos["productos"])
#            print("Volumen Producto:", datos["volumen_producto"])
#            print("Demanda Producto:", datos["demanda_producto"])
#            print("Demanda Camiones:",capacidad_camion)
            resultados = resolver_optimizacion(porcentaje_aumento, datos["productos"], datos["volumen_producto"], datos["demanda_producto"],capacidad_camion)
        # Agregar los resultados obtenidos al diccionario resultados_por_paqueteria bajo la clave de paquetería
            if paqueteria not in resultados_por_paqueteria:
                resultados_por_paqueteria[paqueteria] = {
                    'asignaciones': [],
                    'volumetria': [],
                    'camiones_utilizados': []
                }
                
            resultados_por_paqueteria[paqueteria]['asignaciones'].append(resultados['asignaciones'])
            resultados_por_paqueteria[paqueteria]['volumetria'].append(resultados['volumetria'])
            resultados_por_paqueteria[paqueteria]['camiones_utilizados'].append(resultados['camiones_utilizados'])

#        for paqueteria, datos in resultados_por_paqueteria.items():
#            print(f"Paquetería: {paqueteria}")
#            for clave, valor in datos.items():
#                print(f"{clave}:")
#                for item in valor[0]:
#                    print(item)
#            print("------")        # Devuelve un mensaje de respuesta
        print(resultados_por_paqueteria)
        response = {
            'message': 'Datos procesados exitosamente.',
            'resultados': resultados_por_paqueteria
        }
        return jsonify(response), 200
    except Exception as e:
        # Maneja errores en caso de que ocurran
        return jsonify({'error': str(e)})

    
# Rutas para la aplicación
@app.route('/')
def index():
    response = {"success": True, "message": "API de Acceso"}
    return jsonify(response), 500


if __name__ == "__main__":
    app.run(debug=True)
