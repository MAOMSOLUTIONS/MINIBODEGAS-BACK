from flask import request, jsonify
from . import api_blueprint
from app.api.cubi1000 import resolver_optimizacion



@api_blueprint.route('/cubicuadraje', methods=['POST'])
def cubicuadraje():
#    print(">>>>>>>>>>>")
    try:
        porcentaje_aumento  = 0.9
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
#        print(resultados_por_paqueteria)
        response = {
            'message': 'Datos procesados exitosamente.',
            'resultados': resultados_por_paqueteria
        }
        return jsonify(response), 200
    except Exception as e:
#        print(">>>>>>>>>>> error")
        # Maneja errores en caso de que ocurran
        return jsonify({'error': str(e)})


#def cubicuadraje():
#    response = {"success": True, "message": "API de Acceso"}
#    return jsonify(response)
#@api_blueprint.route('/', methods=['GET'])
#def inicio():
#    response = {"success": True, "message": "API de Acceso"}
#    return jsonify(response)
