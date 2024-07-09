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




def elimina_registros_previos():
    #Elimina los registros previamente pronosticados
    db.session.query(DatosHistoricos).filter(DatosHistoricos.tipo == 'F').delete()
    db.session.commit()
    pass

def obtiene_dias_pronostico(dato):
    return int(Factores.query.filter_by(nombre_factores=dato).first().valor_factores)

def obtiene_datos_historicos(skus_seleccionados=None):
    query = db.session.query(
        DatosHistoricos.sku_datos_historicos,
        func.sum(DatosHistoricos.ventas_datos_historicos).label('ventas_datos_historicos'),
        DatosHistoricos.fecha_datos_historicos,
        DatosHistoricos.semana_datos_historicos
    ).filter(DatosHistoricos.tipo == "H")
    
    # Filtrar por SKUs si se proporciona la lista
    if skus_seleccionados:
        query = query.filter(DatosHistoricos.sku_datos_historicos.in_(skus_seleccionados))
    
    return query.group_by(
        DatosHistoricos.sku_datos_historicos,
        DatosHistoricos.fecha_datos_historicos
    ).all()

def pronostico_sarima(ventas_suavizadas, dias_pronostico):
    modelo_sarima = SARIMAX(ventas_suavizadas, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    resultado_sarima = modelo_sarima.fit()
    predicciones_sarima = resultado_sarima.forecast(steps=dias_pronostico)
    return predicciones_sarima

def pronostico_prophet(ventas_suavizadas, dias_pronostico):
    m = Prophet(daily_seasonality=True)
    m.fit(ventas_suavizadas)
    predicciones_prophet = m.make_future_dataframe(periods=dias_pronostico)
    return predicciones_prophet



def modelo_ewma(datos_historicos, dias_pronostico):
    # Similar a 'modelo_sarima', esta función implementaría el modelo EWMA
    pass

def modelo_random_forest(datos_historicos, dias_pronostico):
    # Implementación del modelo Random Forest
    pass


@api_blueprint.route('/ventas_prediccion_proyeccion', methods=['POST'])
def ventas_prediccion_proyeccion():
    elimina_registros_previos()
    dias_pronostico = obtiene_dias_pronostico('DIAS_PRONOSTICO')
    #{"skus": ["2610MD971664", "2610MD164444"]}
        # Obtener datos enviados en la solicitud POST
    data = request.get_json()
    skus_seleccionados = data.get('skus', None)
    tipo_modelo = data.get('modelo', 'SARIMA')  # SARIMA es el valor predeterminado si no se especifica
    datos_historicos = obtiene_datos_historicos(skus_seleccionados)    


    # Obtener datos enviados en la solicitud POST
    
    historico_df = pd.DataFrame([(d.sku_datos_historicos, d.ventas_datos_historicos, d.fecha_datos_historicos, d.semana_datos_historicos) for d in datos_historicos], columns=['sku_datos_historicos', 'ventas_datos_historicos', 'fecha_datos_historicos','semana_datos_historicos'])

    #Filtra únicamente 2024
    historico_df = historico_df[historico_df['fecha_datos_historicos'].dt.year == 2024]                        
    # Convertir 'fecha_datos_historicos' a datetime y crear una columna numérica para representar las fechas
    historico_df['fecha_datos_historicos'] = pd.to_datetime(historico_df['fecha_datos_historicos'])

    forecast = Forecast.query.all()
    forecast_df = pd.DataFrame([(d.sku_forecats, d.ventas_forecast, d.mes_forecast) for d in forecast], columns=['sku_forecats', 'ventas_forecast', 'mes_forecast'])
    skus_con_forecast = set(forecast_df['sku_forecats'].unique())
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

        # Verificar si hay datos históricos disponibles para el SKU actual
        if not df_sku.empty:
            # Obtener las ventas del 2024 para el SKU actual
            historicos = df_sku[['fecha_datos_historicos', 'ventas_datos_historicos']].values.tolist()
            historicos_formateados = [[fecha.strftime("%a, %d %b %Y"), ventas] for fecha, ventas in historicos]
            # Verifica que tiene historicos
            if not df_sku.empty:
                print("----SKU",df_sku)
                
                fecha_hoy = datetime.now().date()
#                fecha_hoy = datetime.now().date() - timedelta(days=7)

                predicciones_con_fecha = []
                df_sku.sort_values(by='fecha_datos_historicos', inplace=True)
                df_sku.set_index('fecha_datos_historicos', inplace=True)
                df_sku = df_sku.asfreq('D')
                ventas_suavizadas = df_sku['ventas_datos_historicos'].ewm(span=10).mean()
                ventas_suavizadas = ventas_suavizadas.asfreq('D', method='ffill')
                ventas_suavizadas.fillna(method='ffill', inplace=True)
                if isinstance(ventas_suavizadas, pd.DataFrame):
                    ventas_suavizadas = ventas_suavizadas.squeeze()




                print("ventas_suavizadas",ventas_suavizadas)

                if tipo_modelo=="SARIMA":
                    predicciones_final = pronostico_sarima(ventas_suavizadas, dias_pronostico)
                elif tipo_modelo == "PROPHET":
                    predicciones_final = pronostico_prophet(ventas_suavizadas, dias_pronostico)
                    


                fechas_prediccion = pd.date_range(fecha_hoy, periods=dias_pronostico)
                predicciones_con_fecha = []
                pronostico_diario = 0
                pronostico_optimo = 0

                for i, prediccion in enumerate(predicciones_final):
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


                proyecciones_ventas[sku] = {"historico": historicos_formateados, "predicciones": predicciones_con_fecha}
    return jsonify(proyecciones_ventas=proyecciones_ventas), 200



@api_blueprint.route('/obtiene_datos_historicos_api', methods=['POST'])
def obtiene_datos_historicos_api():
    elimina_registros_previos()
    dias_pronostico = obtiene_dias_pronostico('DIAS_PRONOSTICO')
    data = request.get_json()
    skus_seleccionados = data.get('skus', None)
    datos_historicos = obtiene_datos_historicos(skus_seleccionados)
    datos_historicos_lista = [
        {
            'sku_datos_historicos': dato.sku_datos_historicos,
            'ventas_datos_historicos': dato.ventas_datos_historicos,
            'fecha_datos_historicos': dato.fecha_datos_historicos.strftime('%Y-%m-%d'), # Asumiendo que es un objeto datetime
            'semana_datos_historicos': dato.semana_datos_historicos
        }
        for dato in datos_historicos
    ]    
    
    return jsonify(datos_historicos_lista)



if __name__ == '__main__':
    app.run(debug=True)