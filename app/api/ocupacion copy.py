from flask import request, jsonify
from . import api_blueprint
from ..database import db
from sqlalchemy import Integer, String, Column, Float,func
from .models import Ocupacion,Factores,DatosOcupacion,DatosHistoricos,Forecast
import pandas as pd
import requests
import numpy as np


from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from sklearn.linear_model import LinearRegression

from datetime import datetime, timedelta

from sklearn.metrics import mean_squared_error, r2_score

from prophet import Prophet


@api_blueprint.route("/ocupacion", methods=["GET"])
def get_ocupacion():
    print("lalamada")
    # Simula obtener datos de tu base de datos
    data = {
        "devoluciones": [{"name": "Devoluciones", "real": 40, "proyectado": 100}],
        "stagging": [{"name": "Stagging", "real": 50, "proyectado": 80}],
        "rumba": [{"name": "Rumba", "real": 50, "proyectado": 100}],
        "rack": [{"name": "Rack", "real": 30, "proyectado": 80}]
    }
    return jsonify(data)   

@api_blueprint.route("/ocupacion", methods=["POST"])
def ocupacion():
    print("Directo a la DB")
    try:

        # Ejecuta la consulta para obtener todos los indicadores de ocupación
        indicadores = Ocupacion.query.all()

        # Inicializa un diccionario para almacenar los datos agrupados
        datos_agrupados = {}

        # Itera sobre cada indicador obtenido de la base de datos
        for indicador in indicadores:
            # Si la categoría del indicador no está en el diccionario, añádela
            if indicador.nombre not in datos_agrupados:
                datos_agrupados[indicador.nombre] = []
            
            # Añade el indicador a la categoría correspondiente
            datos_agrupados[indicador.nombre].append({
                'name': indicador.nombre,
                'real': indicador.valor_real,
                'proyectado': indicador.valor_proyectado
            })
        print(datos_agrupados)
        # Retorna los datos agrupados como JSON
        return jsonify(datos_agrupados), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'message': 'Un error ocurrió al obtener los datos de ocupación', 'detalles': str(e)}), 500
     

@api_blueprint.route("/insertar_indicadores", methods=["GET"])
def insertar_indicadores():
    db.session.query(Ocupacion).delete()
    # Simula obtener datos de tu base de datos
    data = {
        "devoluciones": [{"name": "Devoluciones", "real": 40, "proyectado": 386}],
        "stagging": [{"name": "Stagging", "real": 50, "proyectado": 80}],
        "rumba": [{"name": "Rumba", "real": 50, "proyectado": 100}],
        "rack": [{"name": "Rack", "real": 30, "proyectado": 80}]
    }

   # Prepara una lista para almacenar instancias del modelo a insertar
    nuevos_indicadores = []
    # Itera sobre cada categoría de indicadores en el objeto de datos
    for categoria, indicadores in data.items():
        # Itera sobre cada indicador en la categoría actual
        for indicador in indicadores:
            nuevo_indicador = Ocupacion(
                nombre=indicador['name'],
                valor_real=indicador['real'],
                valor_proyectado=indicador['proyectado']
            )
            nuevos_indicadores.append(nuevo_indicador)
    # Inserta todos los nuevos indicadores en la base de datos
    try:
        db.session.add_all(nuevos_indicadores)
        db.session.commit()
        return jsonify({'mensaje': 'Indicadores insertados con éxito'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al insertar indicadores', 'detalles': str(e)}), 500
    
@api_blueprint.route("/insertar_factores", methods=["GET"])
def insertar_factores():
    db.session.query(Factores).delete()
    print("Inserta Factores")
    # Datos corregidos con una lista de diccionarios
    data = [
        {"nombre_factores": "FIJO_TOTAL_RUMBA", "sku_tipo": "RUMBA", "valor_factores": 1722},
        {"nombre_factores": "FIJO_TOTAL_RACK", "sku_tipo": "RACK", "valor_factores": 400},
        {"nombre_factores": "FIJO_FACTOR_DEVOLUCIONES", "sku_tipo": "", "valor_factores": 0.04},
        {"nombre_factores": "FIJO_TOTAL_DEVOLUCIONES", "sku_tipo": "", "valor_factores": 240},
        {"nombre_factores": "FIJO_TOTAL_STAGGING", "sku_tipo": "", "valor_factores": 1500},
        {"nombre_factores": "FACTOR_AREA_STAGGING", "sku_tipo": "", "valor_factores": 1.32},
        {"nombre_factores": "DIAS_PRONOSTICO", "sku_tipo": "", "valor_factores": 15},
        {"nombre_factores": "DIAS_INVENTARIO_SEGURIDAD", "sku_tipo": "", "valor_factores": 3},
        {"nombre_factores": "DIAS_TIEMPO_ENTREGA", "sku_tipo": "", "valor_factores": 3}

    ]

    nuevos_factores = []
    for factor in data:
        nuevo_factor = Factores(
            nombre_factores=factor['nombre_factores'],
            sku_tipo=factor['sku_tipo'],
            valor_factores=factor['valor_factores']
        )
        nuevos_factores.append(nuevo_factor)

    try:
        db.session.add_all(nuevos_factores)
        db.session.commit()
        return jsonify({'mensaje': 'Factores insertados con éxito'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al insertar factores', 'detalles': str(e)}), 500
    
@api_blueprint.route('/cargar_datos_ocupacion_fija', methods=['GET'])
def cargar_datos_ocupacion():
    db.session.query(DatosOcupacion).delete()

    # Obtener el archivo del formulario subido
    file = 'CARGA_FIJA.xlsx'
    
    # Leer el archivo de Excel en un DataFrame de pandas
    df = pd.read_excel(file)

    # Renombrar columnas para que coincidan con el modelo de la base de datos
    df.rename(columns={
        'SKU': 'sku',
        'TIPO': 'sku_tipo',
        'FACTOR_INVENTARIO_ACTUAL': 'actual_factor_inventario',
        'FACTOR_INVENTARIO_DEVOLUCIONES': 'devoluciones_factor_inventario'
    }, inplace=True)


    # Insertar los datos en la base de datos
    try:
        for _, row in df.iterrows():
            datos_ocupacion = DatosOcupacion(
                sku=row['sku'],
                sku_tipo=row['sku_tipo'],
                actual_factor_inventario=row['actual_factor_inventario'],
                devoluciones_factor_inventario=row['devoluciones_factor_inventario'],
                # Asegúrate de asignar los valores predeterminados o nulos para los otros campos si son necesarios
            )
            db.session.add(datos_ocupacion)
        db.session.commit()
        return jsonify({'mensaje': 'Datos cargados con éxito'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al cargar los datos', 'detalles': str(e)}), 500
    

@api_blueprint.route('/obtener_datos_ocupacion', methods=['GET'])
def obtener_datos_ocupacion():
    try:
        # Obtener todos los registros de la tabla DatosOcupacion
        datos_ocupacion = DatosOcupacion.query.all()

        # Serializar los datos para JSON
        lista_datos_ocupacion = [
            {
                'id_datosocupacion': dato.id_datosocupacion,
                'sku': dato.sku,
                'sku_tipo': dato.sku_tipo,
                'actual_factor_inventario': dato.actual_factor_inventario,
                'actual_inventario': dato.actual_inventario,
                'actual_venta': dato.actual_venta,
                'actual_area': dato.actual_area,
                'devoluciones_factor_inventario': dato.devoluciones_factor_inventario,
                'devoluciones_inventario': dato.devoluciones_inventario,
                'devoluciones_area': dato.devoluciones_area,
                'mensual_venta': dato.mensual_venta,
                'mensual_venta_devoluciones': dato.mensual_venta_devoluciones,
                'stagging_factor_inventario': dato.stagging_factor_inventario,
                'stagging_inventario': dato.stagging_inventario,
                'stagging_area': dato.stagging_area,
                'pronostico_diario': dato.pronostico_diario,
                'pronostico_optimo': dato.pronostico_optimo,
                'area_pronostico_optimo': dato.area_pronostico_optimo,
                'inventario_seguridad': dato.inventario_seguridad,
                'punto_reorden': dato.punto_reorden,
                'cantidad_solicitar': dato.cantidad_solicitar
            }
            for dato in datos_ocupacion
        ]

        return jsonify(lista_datos_ocupacion), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al obtener los datos de ocupación', 'detalles': str(e)}), 500
    

@api_blueprint.route('/obtener_datos_historicos', methods=['POST'])
def obtener_datos_historicos():
    try:
        # Obtener todos los registros de la tabla DatosHistoricos
        datos_historicos = DatosHistoricos.query.all()

        # Serializar los datos para JSON
        lista_datos_historicos = [
            {
                'id_datos_historicos': dato.id_datos_historicos,
                'ano_datos_historicos': dato.ano_datos_historicos,
                'sku_datos_historicos': dato.sku_datos_historicos,
                'modelo_datos_historicos': dato.modelo_datos_historicos,
                'tipo_enser_datos_historicos': dato.tipo_enser_datos_historicos,
                'clasificacion_enser_datos_historicos': dato.clasificacion_enser_datos_historicos,
                'ventas_datos_historicos': dato.ventas_datos_historicos,
                'fecha_datos_historicos': dato.fecha_datos_historicos.isoformat(),
                'semana_datos_historicos': dato.semana_datos_historicos,
                'tipo': dato.tipo
            }
            for dato in datos_historicos
        ]

        return jsonify(lista_datos_historicos), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al obtener los datos históricos', 'detalles': str(e)}), 500



@api_blueprint.route('/actualizar_datos_ocupacion', methods=['GET'])
def actualizar_datos_ocupacion():
    # Obtener el archivo del formulario subido
    file = 'CARGA_ACTUALIZACION_DIARIA.xlsx'
    
    # Leer el archivo de Excel en un DataFrame de pandas
    df = pd.read_excel(file)

    # Renombrar columnas para que coincidan con el modelo de la base de datos
    df.rename(columns={
        'SKU': 'sku',
        'SKU_TIPO': 'sku_tipo',
        'INVENTARIO_ACTUAL': 'actual_inventario',
        'FACTOR_INVENTARIO_ACTUAL': 'actual_factor_inventario',
        'INVENTARIO_DEVOLUCIONES': 'devoluciones_inventario',
        'INVENTARIO_STAGGING': 'stagging_inventario'
    }, inplace=True)

    skus_no_encontrados = []
    total_area_actualizada_rack = 0  # Acumulador para el área total de tipo RACK
    total_area_actualizada_rumba = 0
    total_area_actualizada_devoluciones = 0
    total_area_actualizada_stagging = 0
    total_pronostico_optimo_rack = 0
    total_pronostico_optimo_rumba = 0
    total_pronostico_stagging = 0


    # Obtener factores fijos para RUMBA y RACK y OTROS
    factor_fijo_total_rumba = Factores.query.filter_by(nombre_factores='FIJO_TOTAL_RUMBA').first().valor_factores
    factor_fijo_total_rack = Factores.query.filter_by(nombre_factores='FIJO_TOTAL_RACK').first().valor_factores
    factor_fijo_total_devoluciones = Factores.query.filter_by(nombre_factores='FIJO_TOTAL_DEVOLUCIONES').first().valor_factores
    factor_fijo_total_stagging = Factores.query.filter_by(nombre_factores='FIJO_TOTAL_STAGGING').first().valor_factores
    factor_area_stagging = Factores.query.filter_by(nombre_factores='FACTOR_AREA_STAGGING').first().valor_factores
    dias_inventario_seguridad = Factores.query.filter_by(nombre_factores='DIAS_INVENTARIO_SEGURIDAD').first().valor_factores
    dias_pronostico = Factores.query.filter_by(nombre_factores='DIAS_PRONOSTICO').first().valor_factores
    dias_tiempo_entrega = Factores.query.filter_by(nombre_factores='DIAS_TIEMPO_ENTREGA').first().valor_factores


    
    




    try:
        for index, row in df.iterrows():
            datos_ocupacion = DatosOcupacion.query.filter_by(sku=row['sku']).first()
            if datos_ocupacion:
                datos_ocupacion.actual_inventario = row['actual_inventario']
                datos_ocupacion.devoluciones_inventario = row['devoluciones_inventario']
                datos_ocupacion.stagging_inventario = row['stagging_inventario']



                # Calcula actual_area si se dispone de actual_factor_inventario y actual_inventario
                if datos_ocupacion.actual_factor_inventario and datos_ocupacion.actual_inventario:
                    datos_ocupacion.actual_area = datos_ocupacion.actual_inventario * datos_ocupacion.actual_factor_inventario
                
                    if datos_ocupacion.pronostico_optimo:
                        datos_ocupacion.area_pronostico_optimo = datos_ocupacion.pronostico_optimo * datos_ocupacion.actual_factor_inventario
                    
                    
                    # Sumariza el área actualizada basada en el sku_tipo
                    if datos_ocupacion.sku_tipo == 'RACK':
                        total_area_actualizada_rack += datos_ocupacion.actual_area
                        if not datos_ocupacion.area_pronostico_optimo:
                            datos_ocupacion.area_pronostico_optimo = 0

                        total_pronostico_optimo_rack+= datos_ocupacion.area_pronostico_optimo + (datos_ocupacion.actual_inventario * datos_ocupacion.actual_factor_inventario)

                    elif datos_ocupacion.sku_tipo == 'RUMBA':
                        total_area_actualizada_rumba += datos_ocupacion.actual_area
#                        if datos_ocupacion.area_pronostico_optimo:
                        if not datos_ocupacion.area_pronostico_optimo:
                            datos_ocupacion.area_pronostico_optimo = 0
                        total_pronostico_optimo_rumba+= datos_ocupacion.area_pronostico_optimo + (datos_ocupacion.actual_inventario * datos_ocupacion.actual_factor_inventario)



                    #CALCULO INVENTARIO DE SEGURIDAD                    
                    if datos_ocupacion.pronostico_diario:
                        datos_ocupacion.inventario_seguridad = datos_ocupacion.pronostico_diario * dias_inventario_seguridad

                    #CALCULO PUNTO DE REORDEN
                    if datos_ocupacion.pronostico_diario and datos_ocupacion.inventario_seguridad:
                        datos_ocupacion.punto_reorden = (datos_ocupacion.inventario_seguridad + datos_ocupacion.pronostico_diario) * dias_tiempo_entrega

                    #CALCULO_CANTIDAD A SOLICITAR
                    if datos_ocupacion.actual_inventario and datos_ocupacion.punto_reorden and datos_ocupacion.pronostico_optimo:
                        if datos_ocupacion.actual_inventario <= datos_ocupacion.punto_reorden:
                            # Calcula la cantidad a solicitar
                            cantidad_calculada = datos_ocupacion.pronostico_optimo - datos_ocupacion.actual_inventario
                            # Establecer cantidad_solicitar a 0 si la cantidad calculada es negativa
                            datos_ocupacion.cantidad_solicitar = max(cantidad_calculada, 0)
                        else:
                            datos_ocupacion.cantidad_solicitar = 0



                if datos_ocupacion.devoluciones_inventario:
                    datos_ocupacion.devoluciones_area = datos_ocupacion.devoluciones_inventario * datos_ocupacion.devoluciones_factor_inventario                    
                    total_area_actualizada_devoluciones += datos_ocupacion.devoluciones_area

                if datos_ocupacion.stagging_inventario:
                    datos_ocupacion.stagging_factor_inventario = datos_ocupacion.stagging_inventario/4
                    datos_ocupacion.stagging_area = factor_area_stagging * datos_ocupacion.stagging_factor_inventario                    
                    total_area_actualizada_stagging += datos_ocupacion.stagging_area

                if not datos_ocupacion.pronostico_diario:
                    datos_ocupacion.pronostico_diario = 0
                total_pronostico_stagging += datos_ocupacion.pronostico_diario/4
                
            else:
                skus_no_encontrados.append(row['sku'])

        # Actualizar Ocupacion con los totales calculados ajustados por factores fijos
        ocupacion_rack = Ocupacion.query.filter_by(nombre='Rack').first()
        if ocupacion_rack and factor_fijo_total_rack:
            ocupacion_rack.valor_real = round((total_area_actualizada_rack / factor_fijo_total_rack)*100,1)
            ocupacion_rack.valor_proyectado = round((total_pronostico_optimo_rack / factor_fijo_total_rack)*100,1)
            



        ocupacion_rumba = Ocupacion.query.filter_by(nombre='Rumba').first()
        if ocupacion_rumba and factor_fijo_total_rumba:
            ocupacion_rumba.valor_real = round((total_area_actualizada_rumba / factor_fijo_total_rumba)*100,1)
            ocupacion_rumba.valor_proyectado = round((total_pronostico_optimo_rumba / factor_fijo_total_rumba)*100,1)


        ocupacion_devoluciones = Ocupacion.query.filter_by(nombre='Devoluciones').first()
        if ocupacion_devoluciones and factor_fijo_total_devoluciones:
            ocupacion_devoluciones.valor_real = round((total_area_actualizada_devoluciones / factor_fijo_total_devoluciones) * 100, 1)

        ocupacion_stagging = Ocupacion.query.filter_by(nombre='Stagging').first()
        if ocupacion_stagging and factor_fijo_total_stagging:
            ocupacion_stagging.valor_real = round((total_area_actualizada_stagging / factor_fijo_total_stagging) * 100, 1)

        if total_pronostico_stagging and factor_fijo_total_stagging and factor_area_stagging:
            ocupacion_stagging.valor_proyectado = round(((total_pronostico_stagging * factor_area_stagging)/factor_fijo_total_stagging)*100, 1)



        db.session.commit()

        return jsonify({
            'mensaje': 'Datos actualizados con éxito',

            'factor_fijo_total_rumba': factor_fijo_total_rumba,
            'factor_fijo_total_rack': factor_fijo_total_rack,            
            'factor_fijo_total_devoluciones': factor_fijo_total_devoluciones,
            'factor_fijo_total_stagging': factor_fijo_total_stagging,
            'dias_inventario_seguridad': dias_inventario_seguridad,
            'dias_pronostico': dias_pronostico,



            'area_total_actualizada_rack': total_area_actualizada_rack,
            'area_total_actualizada_rack_pronosticada': total_area_actualizada_rack,

            'total_pronostico_optimo_rack': total_pronostico_optimo_rack,
            'total_pronostico_optimo_rumba': total_pronostico_optimo_rumba,


            'area_total_actualizada_devoluciones': total_area_actualizada_devoluciones,
            'area_total_actualizada_stagging': total_area_actualizada_stagging,

            'ocupacion_rack.valor_real': ocupacion_rack.valor_real,
            'ocupacion_rumba.valor_real': ocupacion_rumba.valor_real,
            'ocupacion_devoluciones.valor_real': ocupacion_devoluciones.valor_real,
            'ocupacion_stagging.valor_real': ocupacion_stagging.valor_real,

            'ocupacion_rack.valor_proyectado': ocupacion_rack.valor_proyectado,
            'ocupacion_rumba.valor_proyectado': ocupacion_rumba.valor_proyectado,
            'ocupacion_stagging.valor_proyectado': ocupacion_stagging.valor_proyectado,
            
            



            'skus_no_encontrados': skus_no_encontrados
        }), 200
    except Exception as e:
        # Si algo sale mal, hacer rollback y devolver el error
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar los datos', 'detalles': str(e)}), 500
    

def actualizar_venta_sku(sku, opcion):
    # Reemplaza la URL base con la URL real de tu API externa.
    url = 'http://192.168.14.4:10012/web/services/SP_VTASXPRD/'
    body = {
        "PRD": sku,
        "TPRO": opcion
    }
    response = requests.post(url, json=body)
    if response.status_code == 200:
        # Asumiendo que la API externa devuelve un JSON con la estructura que necesitas.
        datos = response.json()
        return datos['QTY']  # Asegúrate de usar la clave correcta aquí.
    else:
        # Manejar error o respuesta inesperada
        return None


@api_blueprint.route('/actualizar_ventas', methods=['POST'])
def actualizar_ventas():
    # Leer todos los SKUs de la base de datos
    skus = DatosOcupacion.query.all()
    for sku in skus:
        nueva_venta = actualizar_venta_sku(sku.sku, 1)
        if nueva_venta is not None:
            sku.actual_venta = nueva_venta
        else:
            sku.actual_venta = 0            
        db.session.commit()
    return jsonify({'mensaje': 'Ventas actualizadas correctamente'}), 200


@api_blueprint.route('/cargar_datos_historicos', methods=['POST'])
def cargar_datos_historicos():
    file = 'CARGA_HISTORICO_PRONOSTICO.xlsx'
    db.session.query(DatosHistoricos).delete()


    # Iteramos sobre los años solicitados
#    for year in ['2022', '2023', '2024']:
    for year in ['2024']:
        df = pd.read_excel(file, sheet_name=str(year))
        for index, row in df.iterrows():
            # Convierte la fecha del formato del archivo Excel a datetime
            fecha = fecha = pd.to_datetime(row['FECHA']).to_pydatetime()
            # Crear instancia de DatosHistoricos
            dato_historico = DatosHistoricos(
                ano_datos_historicos=int(year),
                sku_datos_historicos=row['SKU'],
#                modelo_datos_historicos=row['MODELO'],
                tipo_enser_datos_historicos=row['TIPO DE ENSER'],
                clasificacion_enser_datos_historicos=row['CLASIFICACIÓN'],
                ventas_datos_historicos=row['VENTAS'],
                fecha_datos_historicos=fecha,
                semana_datos_historicos=row['semana'],
                tipo="H"
            )
            db.session.add(dato_historico)

    # Guardar todos los cambios en la base de datos
    db.session.commit()

    return jsonify({'mensaje': 'Datos históricos cargados correctamente'}), 200


@api_blueprint.route('/cargar_forecast', methods=['GET'])
def cargar_forecast():
    file = 'CARGA_HISTORICO_PRONOSTICO.xlsx'
    sheet = 'forecast'
    df = pd.read_excel(file, sheet_name=sheet)
    # Reemplazar valores NaN o None por 0 en las columnas que inician con 'Suma de'
    columns_to_replace = [col for col in df if col.startswith('Suma de')]
    df[columns_to_replace] = df[columns_to_replace].fillna(0)
    df[columns_to_replace] = df[columns_to_replace].replace({np.nan: 0, '': 0})

    db.session.query(Forecast).delete()

    for index, row in df.iterrows():
        year = 2024  # Asumiendo que todos los datos son para el año 2024
        for month in range(1, 9):  # Iterar a través de los meses (de Enero a Agosto)
            month_col = f'Suma de 2024-{month:02d}'  # Formato de la columna 'Suma de 2024-01', 'Suma de 2024-02', etc.
            if month_col in row:
                forecast_data = Forecast(
                    ano_forecast=year,
                    sku_forecats=row['SKU'],
                    mes_forecast=month,
                    ventas_forecast=row[month_col]
                )
                db.session.add(forecast_data)

    db.session.commit()
    return jsonify({'mensaje': 'Forecast cargado correctamente'}), 200


def create_sequences(data, n_steps):
    X, y = [], []
    for i in range(len(data)):
        end_ix = i + n_steps
        if end_ix > len(data)-1:
            break
        seq_x, seq_y = data[i:end_ix], data[end_ix]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)


@api_blueprint.route('/lstm', methods=['GET'])
def lstm():
    return jsonify({'mensaje': 'Datos_Historicos_Cargados'}), 200


@api_blueprint.route('/arima', methods=['GET'])
def arima():
    datos_historicos = DatosHistoricos.query.all()
    historico_df = pd.DataFrame([(d.sku_datos_historicos, d.ventas_datos_historicos, d.fecha_datos_historicos, d.semana_datos_historicos) for d in datos_historicos], columns=['sku_datos_historicos', 'ventas_datos_historicos', 'fecha_datos_historicos','semana_datos_historicos'])
    
    forecast =Forecast.query.all()
    forecast_df = pd.DataFrame([(d.sku_forecats, d.ventas_forecast, d.mes_forecast) for d in forecast], columns=['sku_forecats', 'ventas_forecast', 'mes_forecast'])

    historico_df['fecha_datos_historicos'] = pd.to_datetime(historico_df['fecha_datos_historicos'])
    historico_df.sort_values('fecha_datos_historicos', inplace=True)

    # Diccionario para almacenar las predicciones de cada SKU
    predicciones_por_sku = {}

    #  Seleccionar los dos primeros SKUs únicos
    skus_unicos = historico_df['sku_datos_historicos'].unique()[:2]  # Aquí limitamos a los dos primeros SKUs 
    for sku in skus_unicos:
        # Filtrar los datos para el SKU actual
        df_sku = historico_df[historico_df['sku_datos_historicos'] == sku]        
        df_sku.set_index('fecha_datos_historicos', inplace=True)
        df_sku.sort_index(inplace=True)
        # Comprobar si hay suficientes datos para el SKU
        if len(df_sku) < 20:  # Por ejemplo, asegurarse de tener un mínimo de datos para el análisis
            continue
        # Aplicar el modelo ARIMA
        try:
            model = ARIMA(df_sku['ventas_datos_historicos'], order=(5, 1, 2))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=15)  # Predecir los siguientes 15 días
            # Almacenar las predicciones
            predicciones_por_sku[sku] = forecast.tolist()
        except Exception as e:
            print(f"Error al predecir ventas para SKU {sku}: {e}")
            predicciones_por_sku[sku] = "Error al predecir"
    return jsonify(predicciones_por_sku), 200


@api_blueprint.route('/sarimax', methods=['GET'])
def sarimax():
    datos_historicos = DatosHistoricos.query.all()
    historico_df = pd.DataFrame([(d.sku_datos_historicos, d.ventas_datos_historicos, d.fecha_datos_historicos, d.semana_datos_historicos) for d in datos_historicos], columns=['sku_datos_historicos', 'ventas_datos_historicos', 'fecha_datos_historicos','semana_datos_historicos'])
    forecast =Forecast.query.all()
    forecast_df = pd.DataFrame([(d.sku_forecats, d.ventas_forecast, d.mes_forecast) for d in forecast], columns=['sku_forecats', 'ventas_forecast', 'mes_forecast'])

    # Preparación de datos históricos
    historico_df['fecha_datos_historicos'] = pd.to_datetime(historico_df['fecha_datos_historicos'])
    historico_df.sort_values('fecha_datos_historicos', inplace=True)
    historico_df.set_index('fecha_datos_historicos', inplace=True)
    
    predicciones_por_sku = {}
    skus_unicos = historico_df['sku_datos_historicos'].unique()[:2]  # Limitado a los dos primeros SKUs
    for sku in skus_unicos:
        df_sku = historico_df[historico_df['sku_datos_historicos'] == sku].copy()
        if len(df_sku) < 20:
            continue
        
        # Preparar variables exógenas para el entrenamiento
        df_sku['mes'] = df_sku.index.month
        exog = pd.get_dummies(df_sku['mes'], drop_first=True)
        
        # Preparar variables exógenas para el pronóstico
        df_forecast_sku = forecast_df[forecast_df['sku_forecats'] == sku]
        # Asumiendo que forecast_df['mes_forecast'] ya está en el formato correcto
        exog_forecast = pd.get_dummies(df_forecast_sku['mes_forecast'], drop_first=True)
        # Asegurarse de que exog_forecast tiene las mismas columnas que exog, rellenando con ceros donde sea necesario
        exog_forecast = exog_forecast.reindex(columns=exog.columns, fill_value=0)

        try:
            model = SARIMAX(df_sku['ventas_datos_historicos'], exog=exog, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
            model_fit = model.fit(disp=False)
            forecast = model_fit.forecast(steps=len(exog_forecast), exog=exog_forecast)  # Usar exog para el pronóstico
            predicciones_por_sku[sku] = forecast.tolist()
        except Exception as e:
            print(f"Error al predecir ventas para SKU {sku}: {e}")
            predicciones_por_sku[sku] = "Error al predecir"
            
    return jsonify(predicciones_por_sku), 200


@api_blueprint.route('/ventas_prediccion', methods=['GET'])
def ventas_prediccion():
    # Obtener los datos históricos y de pronóstico
    datos_historicos = DatosHistoricos.query.all()
    historico_df = pd.DataFrame([(d.sku_datos_historicos, d.ventas_datos_historicos, d.fecha_datos_historicos, d.semana_datos_historicos) for d in datos_historicos], columns=['sku_datos_historicos', 'ventas_datos_historicos', 'fecha_datos_historicos','semana_datos_historicos'])
    forecast = Forecast.query.all()
    forecast_df = pd.DataFrame([(d.sku_forecats, d.ventas_forecast, d.mes_forecast) for d in forecast], columns=['sku_forecats', 'ventas_forecast', 'mes_forecast'])

    return jsonify("predicciones_por_sku"), 200


@api_blueprint.route('/ventas_prediccion_lineal', methods=['GET'])
def ventas_prediccion_lineal():
    # Obtener los datos históricos y de pronóstico
    datos_historicos = db.session.query(
        DatosHistoricos.sku_datos_historicos,
        func.sum(DatosHistoricos.ventas_datos_historicos).label('ventas_datos_historicos'),
        DatosHistoricos.fecha_datos_historicos,
        DatosHistoricos.semana_datos_historicos
    ).group_by(
        DatosHistoricos.sku_datos_historicos,
        DatosHistoricos.fecha_datos_historicos
    ).all()

    historico_df = pd.DataFrame([(d.sku_datos_historicos, d.ventas_datos_historicos, d.fecha_datos_historicos, d.semana_datos_historicos) for d in datos_historicos], columns=['sku_datos_historicos', 'ventas_datos_historicos', 'fecha_datos_historicos','semana_datos_historicos'])
    #Filtra únicamente 2024
    historico_df = historico_df[historico_df['fecha_datos_historicos'].dt.year == 2024]                        
    # Convertir 'fecha_datos_historicos' a datetime y crear una columna numérica para representar las fechas
    historico_df['fecha_datos_historicos'] = pd.to_datetime(historico_df['fecha_datos_historicos'])

    forecast = Forecast.query.all()
    forecast_df = pd.DataFrame([(d.sku_forecats, d.ventas_forecast, d.mes_forecast) for d in forecast], columns=['sku_forecats', 'ventas_forecast', 'mes_forecast'])
    skus_con_forecast = set(forecast_df['sku_forecats'].unique()[:2])

    # Inicializar un diccionario para almacenar las proyecciones de los 15 días por SKU
    proyecciones_ventas = {}

    # Iterar sobre los SKU con pronóstico
    for sku in skus_con_forecast:
        # Filtrar los datos históricos para el SKU actual
        df_sku = historico_df[historico_df['sku_datos_historicos'] == sku]
        fecha_minima = historico_df['fecha_datos_historicos'].min()
        df_sku['fecha_num'] = (df_sku['fecha_datos_historicos'] - fecha_minima).dt.days

        # Verificar si hay datos históricos disponibles para el SKU actual
        if not df_sku.empty:
            # Obtener las ventas del 2024 para el SKU actual
            historicos = df_sku[['fecha_datos_historicos', 'ventas_datos_historicos']].values.tolist()
            historicos_formateados = [[fecha.strftime("%a, %d %b %Y"), ventas] for fecha, ventas in historicos]
            # Verifica que tiene historicos
            if not df_sku.empty:

                fecha_hoy = datetime.now().date()
                predicciones_con_fecha = []                
                for i in range(0, 30):
                    X = df_sku[['fecha_num']]
                    y = df_sku['ventas_datos_historicos']
                    modelo = LinearRegression().fit(X, y)

                    fecha_prediccion = fecha_hoy + timedelta(days=i)
                    dias_desde_inicio = (fecha_prediccion - df_sku['fecha_datos_historicos'].min().date()).days
                    prediccion = modelo.predict([[dias_desde_inicio]])[0]

                    fecha_prediccion_str = fecha_prediccion.strftime("%Y-%m-%d")
                    # Convertir la fecha de predicción a Timestamp para poder usar .isocalendar().week
                    fecha_prediccion_timestamp = pd.to_datetime(fecha_prediccion_str)
                    numero_semana = fecha_prediccion_timestamp.isocalendar().week
                    nuevo_dato = pd.DataFrame({
                        'sku_datos_historicos':sku,
                        'fecha_datos_historicos': [fecha_prediccion_timestamp],
                        'semana_datos_historicos':[numero_semana],
                        'fecha_num': dias_desde_inicio,
                        'ventas_datos_historicos': [prediccion]
                    })
                    df_sku = pd.concat([df_sku, nuevo_dato], ignore_index=True)

                    predicciones_con_fecha.append([fecha_prediccion.strftime("%a, %d %b %Y"), prediccion])
                print("df_sku--->",df_sku)

                    
                proyecciones_ventas[sku] = {"historico": historicos_formateados, "predicciones": predicciones_con_fecha}
    return jsonify(proyecciones_ventas=proyecciones_ventas), 200


@api_blueprint.route('/ventas_prediccion_lineal_ewma', methods=['GET'])
def ventas_prediccion_lineal_ewma():
    # Obtener los datos históricos y de pronóstico
    datos_historicos = db.session.query(
        DatosHistoricos.sku_datos_historicos,
        func.sum(DatosHistoricos.ventas_datos_historicos).label('ventas_datos_historicos'),
        DatosHistoricos.fecha_datos_historicos,
        DatosHistoricos.semana_datos_historicos
    ).group_by(
        DatosHistoricos.sku_datos_historicos,
        DatosHistoricos.fecha_datos_historicos
    ).all()

    historico_df = pd.DataFrame([(d.sku_datos_historicos, d.ventas_datos_historicos, d.fecha_datos_historicos, d.semana_datos_historicos) for d in datos_historicos], columns=['sku_datos_historicos', 'ventas_datos_historicos', 'fecha_datos_historicos','semana_datos_historicos'])
    #Filtra únicamente 2024
    historico_df = historico_df[historico_df['fecha_datos_historicos'].dt.year == 2024]                        
    # Convertir 'fecha_datos_historicos' a datetime y crear una columna numérica para representar las fechas
    historico_df['fecha_datos_historicos'] = pd.to_datetime(historico_df['fecha_datos_historicos'])

    forecast = Forecast.query.all()
    forecast_df = pd.DataFrame([(d.sku_forecats, d.ventas_forecast, d.mes_forecast) for d in forecast], columns=['sku_forecats', 'ventas_forecast', 'mes_forecast'])
    skus_con_forecast = set(forecast_df['sku_forecats'].unique()[:2])

    # Inicializar un diccionario para almacenar las proyecciones de los 15 días por SKU
    proyecciones_ventas = {}

    # Iterar sobre los SKU con pronóstico
    for sku in skus_con_forecast:
        # Filtrar los datos históricos para el SKU actual
        df_sku = historico_df[historico_df['sku_datos_historicos'] == sku]
        fecha_minima = historico_df['fecha_datos_historicos'].min()
        df_sku['fecha_num'] = (df_sku['fecha_datos_historicos'] - fecha_minima).dt.days

        # Verificar si hay datos históricos disponibles para el SKU actual
        if not df_sku.empty:
            # Obtener las ventas del 2024 para el SKU actual
            historicos = df_sku[['fecha_datos_historicos', 'ventas_datos_historicos']].values.tolist()
            historicos_formateados = [[fecha.strftime("%a, %d %b %Y"), ventas] for fecha, ventas in historicos]
            # Verifica que tiene historicos
            if not df_sku.empty:
                fecha_hoy = datetime.now().date()
                predicciones_con_fecha = []   
                             

                for i in range(0, 30):
                    df_sku.sort_values(by='fecha_datos_historicos', inplace=True)
                    # Aplicar EWMA para suavizar las ventas históricas
                    df_sku['ventas_suavizadas'] = df_sku['ventas_datos_historicos'].ewm(span=10).mean()

                    X = df_sku[['fecha_num']]
                    y = df_sku['ventas_suavizadas']
                    modelo = LinearRegression().fit(X, y)

                    fecha_prediccion = fecha_hoy + timedelta(days=i)
                    dias_desde_inicio = (fecha_prediccion - df_sku['fecha_datos_historicos'].min().date()).days
                    prediccion = modelo.predict([[dias_desde_inicio]])[0]

                    fecha_prediccion_str = fecha_prediccion.strftime("%Y-%m-%d")
                    # Convertir la fecha de predicción a Timestamp para poder usar .isocalendar().week
                    fecha_prediccion_timestamp = pd.to_datetime(fecha_prediccion_str)
                    numero_semana = fecha_prediccion_timestamp.isocalendar().week

                    prediccion_no_negativa = max(prediccion, 0)
                    prediccion_entero = int(round(prediccion_no_negativa))

                    nuevo_dato = pd.DataFrame({
                        'sku_datos_historicos':sku,
                        'fecha_datos_historicos': [fecha_prediccion_timestamp],
                        'semana_datos_historicos':[numero_semana],
                        'fecha_num': dias_desde_inicio,
                        'ventas_datos_historicos': [prediccion_entero]
                    })
                    df_sku = pd.concat([df_sku, nuevo_dato], ignore_index=True)

                    predicciones_con_fecha.append([fecha_prediccion.strftime("%a, %d %b %Y"), prediccion_entero])
                print("df_sku--->",df_sku)

                    
                proyecciones_ventas[sku] = {"historico": historicos_formateados, "predicciones": predicciones_con_fecha}
    return jsonify(proyecciones_ventas=proyecciones_ventas), 200

@api_blueprint.route('/ventas_prediccion_sarima_ewma', methods=['GET'])
def ventas_prediccion_sarima_ewma():
    #Elimina los registros previamente pronosticados
    db.session.query(DatosHistoricos).filter(DatosHistoricos.tipo == 'F').delete()
    db.session.commit()

    dias_pronostico = int(Factores.query.filter_by(nombre_factores='DIAS_PRONOSTICO').first().valor_factores)


    # Obtener los datos históricos y de pronóstico
    datos_historicos = db.session.query(
        DatosHistoricos.sku_datos_historicos,
        func.sum(DatosHistoricos.ventas_datos_historicos).label('ventas_datos_historicos'),
        DatosHistoricos.fecha_datos_historicos,
        DatosHistoricos.semana_datos_historicos
    ).filter(
        DatosHistoricos.tipo == 'H'
    ).group_by(
        DatosHistoricos.sku_datos_historicos,
        DatosHistoricos.fecha_datos_historicos
    ).all()

    historico_df = pd.DataFrame([(d.sku_datos_historicos, d.ventas_datos_historicos, d.fecha_datos_historicos, d.semana_datos_historicos) for d in datos_historicos], columns=['sku_datos_historicos', 'ventas_datos_historicos', 'fecha_datos_historicos','semana_datos_historicos'])

    #Filtra únicamente 2024
    historico_df = historico_df[historico_df['fecha_datos_historicos'].dt.year == 2024]                        
    # Convertir 'fecha_datos_historicos' a datetime y crear una columna numérica para representar las fechas
    historico_df['fecha_datos_historicos'] = pd.to_datetime(historico_df['fecha_datos_historicos'])

    forecast = Forecast.query.all()
    forecast_df = pd.DataFrame([(d.sku_forecats, d.ventas_forecast, d.mes_forecast) for d in forecast], columns=['sku_forecats', 'ventas_forecast', 'mes_forecast'])
    skus_con_forecast = set(forecast_df['sku_forecats'].unique()[:95])
#    skus_con_forecast = set(forecast_df['sku_forecats'].unique())

    # Inicializar un diccionario para almacenar las proyecciones de los 15 días por SKU
    proyecciones_ventas = {}

    # Iterar sobre los SKU con pronóstico
    for sku in skus_con_forecast:
        # Filtrar los datos históricos para el SKU actual
        df_sku = historico_df[historico_df['sku_datos_historicos'] == sku].copy()

        fecha_minima = historico_df['fecha_datos_historicos'].min()
        df_sku.loc[:, 'fecha_num'] = (df_sku['fecha_datos_historicos'] - fecha_minima).dt.days               
        nuevas_entradas = []
        sku_sin_historico = []

        # Verificar si hay datos históricos disponibles para el SKU actual
        if not df_sku.empty:
            # Obtener las ventas del 2024 para el SKU actual
            historicos = df_sku[['fecha_datos_historicos', 'ventas_datos_historicos']].values.tolist()
            historicos_formateados = [[fecha.strftime("%a, %d %b %Y"), ventas] for fecha, ventas in historicos]
            # Verifica que tiene historicos
            if not df_sku.empty:
                print("----SKU",df_sku)
                
                fecha_hoy = datetime.now().date()

                predicciones_con_fecha = []
                df_sku.sort_values(by='fecha_datos_historicos', inplace=True)
                df_sku.set_index('fecha_datos_historicos', inplace=True)
                df_sku = df_sku.asfreq('D')
                ventas_suavizadas = df_sku['ventas_datos_historicos'].ewm(span=10).mean()
                ventas_suavizadas = ventas_suavizadas.asfreq('D', method='ffill')
                ventas_suavizadas.fillna(method='ffill', inplace=True)
#                if not isinstance(ventas_suavizadas, pd.Series):
#                    ventas_suavizadas = ventas_suavizadas.squeeze() 
                if isinstance(ventas_suavizadas, pd.DataFrame):
                    ventas_suavizadas = ventas_suavizadas.squeeze()

                modelo_sarima = SARIMAX(ventas_suavizadas, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
                resultado_sarima = modelo_sarima.fit()
                predicciones_sarima = resultado_sarima.forecast(steps=dias_pronostico)
                fechas_prediccion = pd.date_range(fecha_hoy, periods=dias_pronostico)
                predicciones_con_fecha = []
                pronostico_diario = 0
                pronostico_optimo = 0

                for i, prediccion in enumerate(predicciones_sarima):
                    fecha_prediccion = fechas_prediccion[i]
                    fecha_prediccion_str = fecha_prediccion.strftime("%Y-%m-%d")
                    # Convertir la fecha de predicción a Timestamp para poder usar .isocalendar().week
                    fecha_prediccion_timestamp = pd.to_datetime(fecha_prediccion_str)
                    numero_semana = fecha_prediccion_timestamp.isocalendar().week
                    fecha_num = (fecha_prediccion - pd.Timestamp(df_sku.index.min())).days
                    prediccion_no_negativa = max(prediccion, 0)
                    prediccion_entero = int(round(prediccion_no_negativa))
                    if (i==1):
                        pronostico_diario = prediccion_entero
                    pronostico_optimo+= prediccion_entero

                    # Agregar cada predicción al DataFrame df_sku
                    nuevo_dato = {
                        'sku_datos_historicos': sku,
                        'fecha_datos_historicos': fecha_prediccion_timestamp,
                        'semana_datos_historicos': numero_semana,
                        'fecha_num': fecha_num,
                        'ventas_datos_historicos': prediccion_entero,
                        'tipo':"F"
                    }
                    nuevo_dato_df = pd.DataFrame([nuevo_dato])

                    nueva_entrada = DatosHistoricos(
                        ano_datos_historicos= "2024",
                        sku_datos_historicos=nuevo_dato['sku_datos_historicos'],
                        ventas_datos_historicos=nuevo_dato['ventas_datos_historicos'],
                        fecha_datos_historicos=nuevo_dato['fecha_datos_historicos'],
                        semana_datos_historicos=nuevo_dato['semana_datos_historicos'],
                        tipo=nuevo_dato['tipo']
                    )
                    nuevas_entradas.append(nueva_entrada)
                    # Asegurarse de que 'fecha_datos_historicos' es el índice si df_sku lo usa como índice
                    nuevo_dato_df.set_index('fecha_datos_historicos', inplace=True)
                    # Concatenar nuevo_dato_df con df_sku
                    df_sku = pd.concat([df_sku, nuevo_dato_df])                    
                    # Agregar a la lista de predicciones con fecha para la salida
                    predicciones_con_fecha.append([fecha_prediccion.strftime("%a, %d %b %Y"), prediccion_entero])                
                    print(predicciones_con_fecha)
                try:
                    db.session.bulk_save_objects(nuevas_entradas)
                    registro = db.session.query(DatosOcupacion).filter_by(sku=sku).first()
                    if registro:
                        # Actualiza los valores
                        registro.pronostico_optimo = pronostico_optimo
                        registro.pronostico_diario = pronostico_diario
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"Error al insertar los datos: {e}")
        else:
            sku_sin_historico.append(sku)

        print(">>>> AQUI ESTAMOS",historicos_formateados)
        proyecciones_ventas[sku] = {"historico": historicos_formateados, "predicciones": predicciones_con_fecha, "sku_sin_hsitorico": predicciones_con_fecha}
    return jsonify(proyecciones_ventas=proyecciones_ventas), 200



@api_blueprint.route('/ventas_prediccion_polifyt', methods=['GET'])
def ventas_prediccion_polyfit():
    # Leer parámetros de la solicitud
    sku_seleccionado = request.args.get('sku', '2610MD971664')  # Valor predeterminado

    grado_maximo = int(request.args.get('grado_maximo', 9))  # Límite superior para el grado
    
    dias_pronostico = int(Factores.query.filter_by(nombre_factores='DIAS_PRONOSTICO').first().valor_factores)

    # Obtener los datos históricos
    datos_historicos = db.session.query(
        DatosHistoricos.fecha_datos_historicos,
        func.sum(DatosHistoricos.ventas_datos_historicos).label('ventas_totales')
    ).filter(
        DatosHistoricos.tipo == 'H',        
        DatosHistoricos.sku_datos_historicos == sku_seleccionado
    ).group_by(
        DatosHistoricos.fecha_datos_historicos
    ).order_by(
        DatosHistoricos.fecha_datos_historicos
    ).all()

    # Preparar datos para polyfit
    fechas = [d.fecha_datos_historicos for d in datos_historicos]
    ventas = [d.ventas_totales for d in datos_historicos]

    fecha_inicial = min(fechas)
    x = np.array([(fecha - fecha_inicial).days for fecha in fechas])
    y = np.array(ventas)

    predicciones_por_grado = {}
    evaluaciones = {}  # Para almacenar MSE y R^2

    for grado in range(1, grado_maximo + 1):
        # Ajustar un modelo polinomial del grado actual
        coeficientes = np.polyfit(x, y, grado)
        modelo_polinomial = np.poly1d(coeficientes)

        # Predecir ventas para los datos históricos (para calcular MSE y R^2)
        predicciones_historicas = modelo_polinomial(x)
        mse = mean_squared_error(y, predicciones_historicas)
        r2 = r2_score(y, predicciones_historicas)
        evaluaciones[f'grado_{grado}'] = {'MSE': mse, 'R2': r2}

        # Predecir ventas para los próximos días
        x_futuro = np.array(range(max(x) + 1, max(x) + dias_pronostico + 1))
        predicciones_ventas = modelo_polinomial(x_futuro).tolist()
        predicciones_por_grado[f'grado_{grado}'] = predicciones_ventas

    # Datos para la respuesta
    datos_historicos_lista = [{'fecha': fecha.strftime('%Y-%m-%d'), 'ventas': venta} for fecha, venta in zip(fechas, ventas)]

    respuesta = {
        "sku": sku_seleccionado,
        "historico_ventas": datos_historicos_lista,
        "predicciones_por_grado": predicciones_por_grado,
        "evaluaciones": evaluaciones
    }

    return jsonify(respuesta), 200

@api_blueprint.route('/ventas_prediccion_prophet', methods=['GET'])
def ventas_prediccion_prophet():
    # Leer parámetros de la solicitud
    sku_seleccionado = request.args.get('sku', '2610MD971664')  # Valor predeterminado
    dias_pronostico = int(Factores.query.filter_by(nombre_factores='DIAS_PRONOSTICO').first().valor_factores)

    # Obtener los datos históricos
    datos_historicos = db.session.query(
        DatosHistoricos.fecha_datos_historicos.label('ds'),
        func.sum(DatosHistoricos.ventas_datos_historicos).label('y')
    ).filter(
        DatosHistoricos.tipo == 'H',        
        DatosHistoricos.sku_datos_historicos == sku_seleccionado
    ).group_by(
        DatosHistoricos.fecha_datos_historicos
    ).order_by(
        DatosHistoricos.fecha_datos_historicos
    ).all()

    # Convertir datos a DataFrame de Pandas
    df = pd.DataFrame(datos_historicos)

    # Ajustar modelo Prophet
    m = Prophet(daily_seasonality=True)  # Configura la estacionalidad como creas conveniente
    m.fit(df)

    # Crear DataFrame futuro para predicciones
    futuro = m.make_future_dataframe(periods=dias_pronostico)

    # Realizar predicciones
    forecast = m.predict(futuro)

    # Preparar respuesta
    predicciones = forecast[['ds', 'yhat']].tail(dias_pronostico)
    predicciones = predicciones.rename(columns={'ds': 'fecha', 'yhat': 'ventas_predichas'})
    predicciones['fecha'] = predicciones['fecha'].dt.strftime('%Y-%m-%d')
    predicciones_lista = predicciones.to_dict('records')

    respuesta = {
        "sku": sku_seleccionado,
        "historico_ventas": df.to_dict('records'),
        "predicciones_prophet": predicciones_lista
    }

    return jsonify(respuesta), 200







if __name__ == '__main__':
    app.run(debug=True)



