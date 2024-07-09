from flask import request, jsonify
from . import api_blueprint
from app.api.cubi1000 import resolver_optimizacion
import pandas as pd
import json





@api_blueprint.route('/cubicuadraje', methods=['POST'])
def cubicuadraje():
    #print(">>>>>>>>>>>ESTAMOS AQEUI")
    try:
        file = 'CATALOGO_PRODUCTOS.xlsx'
        df_productos = pd.read_excel(file)
        print("ARCHIV EXCEL", df_productos)

        porcentaje_aumento  = 0.9
        # Obtén los datos de productos y paquetería del cuerpo de la solicitud
        data = request.json
        data_productos = pd.DataFrame(data['productos'])
        print("DATA FRAME", data_productos)

#        df_productos['CODIGO'] = df_productos['CODIGO'].astype(str)
#        data_productos['CODIGO'] = data_productos['CODIGO'].astype(str)

        df_merged = pd.merge(data_productos,df_productos, on='CODIGO', how='left')
        print("DataFrame combinado:", df_merged)

        paqueteria_total = data['paqueteria']
        # Procesa los datos y conviértelos en el formato deseado
#        print("ESTOS SON LOS DATOS QUE LLEGAN",data)
        datos_procesados = {}
        datos_productos_sin_volumetria = []

        for index, producto in df_merged.iterrows():
            paqueteria = producto['PAQUETERIA']
            print("PAQUETERIA",paqueteria)
            if paqueteria not in datos_procesados:
                datos_procesados[paqueteria] = {
                    'productos': [],
                    'volumen_producto': {},
                    'demanda_producto': {}
                }
            producto_codigo = f'Producto_{producto["CODIGO"]}'
            print("producto_codigo",producto_codigo)

            print("FRENTE",float(producto['FRENTE']))
            print("ANCHO",float(producto['ANCHO']))
            print("ALTURA",float(producto['ALTURA']))
#            volumetria = ((float(producto['FRENTE']) /100) * (float(producto['ANCHO']) /100) * (float(producto['ALTURA']) /100)) * float(producto['CANTIDAD'])
            if pd.notnull(producto['FRENTE']) and pd.notnull(producto['ANCHO']) and pd.notnull(producto['ALTURA']):
                # Todos los valores están presentes, realiza el cálculo
                volumetria = ((float(producto['FRENTE']) / 100) * 
                            (float(producto['ANCHO']) / 100) * 
                            (float(producto['ALTURA']) / 100))
            else:
                volumetria = 0  
                datos_productos_sin_volumetria.append(producto["CODIGO"])


            print("volumetria",volumetria)

            datos_procesados[paqueteria]['productos'].append(producto_codigo)
            datos_procesados[paqueteria]['demanda_producto'][producto_codigo] = producto['CANTIDAD']
            datos_procesados[paqueteria]['volumen_producto'][producto_codigo] = volumetria

        resultados_por_paqueteria = {}
        for paqueteria, datos in datos_procesados.items():
            camiones_filtrados = [camion for camion in paqueteria_total if camion['PAQUETERIA'] == paqueteria]
            capacidad_camion = {
                camion['CAMION']: camion['VOLUMEN M3'] for camion in camiones_filtrados
            }
            print(">>>>>>>>>>>")
            print(f"Paquetería: {paqueteria}")
            print("Productos:", datos["productos"])
            print("Volumen Producto:", datos["volumen_producto"])
            print("Demanda Producto:", datos["demanda_producto"])
            print("Demanda Camiones:",capacidad_camion)
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

        for paqueteria, datos in resultados_por_paqueteria.items():
            print(f"Paquetería: {paqueteria}")
            for clave, valor in datos.items():
                print(f"{clave}:")
                for item in valor[0]:
                    print(item)
            print("------")        # Devuelve un mensaje de respuesta
        print(resultados_por_paqueteria)
        response = {
            'message': 'Datos procesados exitosamente.',
            'resultados': resultados_por_paqueteria,
            'productos_sin_volmetria':datos_productos_sin_volumetria
        }
        return jsonify(response), 200
    except Exception as e:
        print(">>>>>>>>>>> error",str(e))
        # Maneja errores en caso de que ocurran
        return jsonify({'error': str(e)})
