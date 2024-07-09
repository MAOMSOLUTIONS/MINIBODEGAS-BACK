import pulp
import pandas as pd
import csv
from tabulate import tabulate

#Variables
porcentaje_aumento  = 0.9
archivo_productos_csv = 'productos.csv'
archivo_paqueteria_csv = 'paqueteria.csv'

def obtener_capacidad_camion_por_paqueteria(archivo_csv, paqueteria):
    # Define un diccionario para almacenar la capacidad de camiones
    capacidad_camion = {}

    # Abre el archivo CSV de camiones y lee sus contenidos
    with open(archivo_csv, newline='') as csvfile:
        reader = csv.reader(csvfile)

        # Salta la primera fila que contiene encabezados
        next(reader)

        for row in reader:
            tipo_paqueteria = row[0]
            tipo_camion = row[1]
            capacidad = float(row[6])
            if tipo_paqueteria == paqueteria:
                capacidad_camion[tipo_camion] = capacidad

    return capacidad_camion


def organizar_datos_producto_por_paqueteria(archivo_csv):
    datos_por_paqueteria = {}

    # Abre el archivo CSV y lee sus contenidos
    with open(archivo_csv, newline='') as csvfile:
        reader = csv.reader(csvfile)

        # Salta la primera fila que contiene encabezados
        next(reader)

        # Itera a través de las filas del archivo CSV
        for row in reader:
            codigo = row[0]
            descripcion = row[1]
            paqueteria = row[8]
            volumen = float(row[6])
            cantidad = int(row[7])

            nombre_producto = f"Producto_{codigo}"

            if paqueteria not in datos_por_paqueteria:
                datos_por_paqueteria[paqueteria] = {
                    "productos": [],
                    "volumen_producto": {},
                    "demanda_producto": {}
                }

            datos_por_paqueteria[paqueteria]["productos"].append(nombre_producto)
            datos_por_paqueteria[paqueteria]["volumen_producto"][nombre_producto] = volumen
            datos_por_paqueteria[paqueteria]["demanda_producto"][nombre_producto] = cantidad

    return datos_por_paqueteria



# Función para resolver el problema de optimización y devolver resultados en una tabla
def resolver_optimizacion(porcentaje_aumento, productos, volumen_producto, demanda_producto,capacidad_camion):
    # Calcula la suma de los productos de volumetría total
    suma_volumetria_total = sum(volumen_producto[producto] * demanda_producto[producto] for producto in volumen_producto)
    # Imprime la suma
#    print("La suma de los productos de volumetría total es:", suma_volumetria_total)
    # Calcula la suma de la capacidad de camiones
    suma_capacidad_camiones  = sum(capacidad_camion.values())
    # Imprime la suma
#    print("La suma de la capacidad de los camiones es:", suma_capacidad_camiones )

    # Compara si la suma de los productos multiplicada por el porcentaje es mayor o igual a la suma de la capacidad de camiones
    if suma_volumetria_total  >= suma_capacidad_camiones * porcentaje_aumento:
        # Duplica el diccionario de capacidad de camiones con un consecutivo
        consecutivo = 1
        nuevos_tipos_camion = {}
        for tipo, capacidad in capacidad_camion.items():
            nuevos_tipo = f"{tipo}_{consecutivo}"
            while nuevos_tipo in nuevos_tipos_camion:
                consecutivo += 1
                nuevos_tipo = f"{tipo}_{consecutivo}"
            nuevos_tipos_camion[nuevos_tipo] = capacidad
        capacidad_camion.update(nuevos_tipos_camion)
    # Imprime el diccionario de capacidad de camiones (puede contener duplicados)
    #print(capacidad_camion)
    # Datos
    #productos = ["Producto_A", "Producto_B", "Producto_C"]
    #volumen_producto = {"Producto_A": 3, "Producto_B": 2, "Producto_C": 5}
    #demanda_producto = {"Producto_A": 10, "Producto_B": 3, "Producto_C": 2}

    #Crea una lista de tipos de camiones (originales y duplicados)
    tipos_camion = list(capacidad_camion.keys())
    print("tipos_camion",tipos_camion)


    # Crear el problema
    problema = pulp.LpProblem("Asignacion_Camiones", pulp.LpMinimize)

    # Variables de decisión: asignación de productos a camiones por tipo
    # Variables de decisión: asignación de productos a camiones por tipo
    x = {(producto, camion): pulp.LpVariable(f"Asignado_{producto}_{camion}", lowBound=0, cat=pulp.LpInteger)
        for producto in productos
        for camion in capacidad_camion.keys()}


    # Variables para representar la cantidad de camiones utilizados por tipo
    y = {camion: pulp.LpVariable(f"Camiones_{camion}", cat=pulp.LpBinary) for camion in capacidad_camion.keys()}

    # Función objetivo: minimizar la cantidad total de camiones utilizados
    problema += pulp.lpSum(y[camion] for camion in capacidad_camion.keys())

    # Restricciones de capacidad de volumetría
    for camion in capacidad_camion.keys():
        problema += pulp.lpSum(x[(producto, camion)] * volumen_producto[producto] for producto in productos) <= capacidad_camion[camion] * y[camion]

    # Restricciones de demanda de productos
    for producto in productos:
        problema += pulp.lpSum(x[(producto, camion)] for camion in capacidad_camion.keys()) >= demanda_producto[producto]

    # Restricción para que los camiones sean enteros (0 o 1 si se utiliza o no)
    for camion in capacidad_camion.keys():
        problema += y[camion] >= 0
        problema += y[camion] <= 1

    # Resolver el problema
    problema.solve()


    # Resultados para las asignaciones de productos a camiones
    tabla_asignaciones = []

    for producto in productos:
        for camion in capacidad_camion.keys():
            asignado = x[(producto, camion)].varValue
            if asignado > 0:
                tabla_asignaciones.append([f"Asignar {asignado} unidades de {producto} al Camión {camion}",
                                            asignado * volumen_producto[producto]])

    # Resultados para la información de volumetría por camión
    tabla_volumetria = []

    for camion in capacidad_camion.keys():
        total_volumen_utilizado = sum(x[(producto, camion)].varValue * volumen_producto[producto] for producto in productos)
        total_volumen_disponible = capacidad_camion[camion]
        # Formatea el valor de la volumetría con dos decimales
        valor_formateado = "{:.2f}".format(total_volumen_disponible)
        tabla_volumetria.append([f"Volumetría por Camión ({camion})", valor_formateado])    
        total_volumen_utilizado = "{:.2f}".format(total_volumen_utilizado)
        tabla_volumetria.append([f"Volumetría Total Utilizada ({camion})", total_volumen_utilizado])
        volumetria_disponible = "{:.2f}".format(total_volumen_disponible - float(total_volumen_utilizado))
        tabla_volumetria.append([f"Volumetría Disponible ({camion})", volumetria_disponible])

    # Resultados para el número total de camiones utilizados
    tabla_camiones_utilizados = []

    total_camiones_por_tipo = {camion: y[camion].varValue for camion in capacidad_camion.keys()}
    for camion, cantidad in total_camiones_por_tipo.items():
        tabla_camiones_utilizados.append([f"Número total de camiones utilizados ({camion})", cantidad])

    # Imprimir las tablas
#    print("____________________________________________________________________________")

#    print("Asignaciones de Productos a Camiones:")
#    print(tabulate(tabla_asignaciones, headers=["Descripción", "Valor"], tablefmt="pretty"))

#    print("\nVolumetría por Camión:")
#    print(tabulate(tabla_volumetria, headers=["Descripción", "Valor"], tablefmt="pretty"))

#    print("\nNúmero Total de Camiones Utilizados:")
#    print(tabulate(tabla_camiones_utilizados, headers=["Descripción", "Valor"], tablefmt="pretty")) 

    return {
        "asignaciones": tabla_asignaciones,
        "volumetria": tabla_volumetria,
        "camiones_utilizados": tabla_camiones_utilizados
    }

def guardar_resultados_en_csv(resultados, nombre_archivo):
    with open(nombre_archivo, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        for paqueteria, tablas in resultados.items():
            writer.writerow([f'Paquetería: {paqueteria}'])

            # Escribe las tablas de asignaciones de productos a camiones
            writer.writerows(tablas["asignaciones"])

            # Escribe las tablas de información de volumetría por camión
            writer.writerows(tablas["volumetria"])

            # Escribe las tablas de número total de camiones utilizados
            writer.writerows(tablas["camiones_utilizados"])



if __name__ == "__main__":
    datos_organizados = organizar_datos_producto_por_paqueteria(archivo_productos_csv)
    resultados_por_paqueteria = {}
#    print(f"datos_organizados: {datos_organizados}")

    resultados_por_paqueteria = {}    
    # Accede a los datos organizados por paquetería
    for paqueteria, datos in datos_organizados.items():
#        print(">>>>>>>>>>>")
        print(f"Paquetería: {paqueteria}")
#        print("Productos:", datos["productos"])
#        print("Volumen Producto:", datos["volumen_producto"])
#        print("Demanda Producto:", datos["demanda_producto"])
        capacidad_camion = obtener_capacidad_camion_por_paqueteria(archivo_paqueteria_csv, paqueteria)
        resultados = resolver_optimizacion(porcentaje_aumento, datos["productos"], datos["volumen_producto"], datos["demanda_producto"],capacidad_camion)
#        print("****", resultados)
