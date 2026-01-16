
import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt


def mostrar_estadisticas_jornada(poblacion):
    """
    Calcula y grafica la distribución de tipos de jornada y teletrabajo.
    Si la persona hace Teletrabajo, se clasifica como 'Teletrabajo' (prioridad).
    Si no, se clasifica por su 'tipo_jornada' (Rígido, Flexible, Part-Time).
    """
    print("--- Calculando Estadísticas de Jornadas ---")

    conteo = {
        "Teletrabajo": 0,
        "Rígido": 0,
        "Flexible": 0,
        "Part-Time": 0
    }

    total_poblacion = len(poblacion)

    for p in poblacion:
        # Prioridad 1: ¿Hace teletrabajo?
        if p['teletrabaja']:
            conteo["Teletrabajo"] += 1
        else:
            # Prioridad 2: Si viaja, ¿qué horario tiene?
            tipo = p['tipo_jornada'] # "Rígido", "Flexible" o "Part-Time"
            if tipo in conteo:
                conteo[tipo] += 1
            else:
                # Por si acaso hubiera algún tipo no registrado
                conteo[tipo] = 1

    # Crear DataFrame para visualizar mejor
    df_resumen = pd.DataFrame.from_dict(conteo, orient='index', columns=['Personas'])
    df_resumen['Porcentaje'] = (df_resumen['Personas'] / total_poblacion) * 100

    # Formato bonito para el porcentaje
    df_resumen['Porcentaje'] = df_resumen['Porcentaje'].apply(lambda x: f"{x:.1f}%")

    display(df_resumen)

    # --- GRÁFICO ---
    # Convertimos a numérico para graficar
    valores = df_resumen['Personas']
    etiquetas = df_resumen.index

    plt.figure(figsize=(8, 5))
    barras = plt.bar(etiquetas, valores, color=['#3498db', '#e74c3c', '#f1c40f', '#2ecc71'])

    plt.title('Distribución de Jornadas Laborales', fontsize=14)
    plt.xlabel('Tipo de Jornada / Modalidad', fontsize=12)
    plt.ylabel('Cantidad de Personas', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Añadir etiquetas de valor encima de las barras
    for bar in barras:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{int(height)}',
                 ha='center', va='bottom')

    plt.show()

# --- EJECUCIÓN ---
mostrar_estadisticas_jornada(poblacion) # Falta generar pobla

def mostrar_estadisticas_jornada_por_estrato(poblacion):
    """
    Genera estadísticas cruzadas de Estrato vs. Tipo de Jornada/Teletrabajo.
    Muestra tabla de porcentajes y gráfico de barras agrupadas.
    """
    # 1. Estructura de datos para contar: { Estrato: {Tipo: Cantidad} }
    datos_agregados = {1: {}, 2: {}, 3: {}}
    categorias = ["Teletrabajo", "Rígido", "Flexible", "Part-Time"]

    # Inicializar contadores en 0
    for estrato in datos_agregados:
        for cat in categorias:
            datos_agregados[estrato][cat] = 0

    # 2. Llenar datos iterando sobre la población
    for p in poblacion:
        e = p['estrato']
        # Prioridad: Teletrabajo mata jornada presencial
        if p['teletrabaja']:
            datos_agregados[e]["Teletrabajo"] += 1
        else:
            tipo = p['tipo_jornada']
            datos_agregados[e][tipo] += 1

    # 3. Crear DataFrame y Calcular Porcentajes
    df = pd.DataFrame(datos_agregados).T # Transponer para que Estratos sean filas (index)
    df.index.name = "Estrato"

    # Calcular % por fila (cada estrato suma 100%)
    df_pct = df.div(df.sum(axis=1), axis=0) * 100

    print("--- Distribución Porcentual por Estrato ---")
    # Formato visual con %
    display(df_pct.round(1).astype(str) + '%')

    # 4. Graficar
    ax = df_pct.plot(kind='bar', figsize=(10, 6), colormap='viridis', edgecolor='black', width=0.8)

    plt.title('Distribución de Modalidad Laboral por Estrato', fontsize=14)
    plt.ylabel('Porcentaje (%)', fontsize=12)
    plt.xlabel('Estrato Socioeconómico', fontsize=12)
    plt.legend(title='Modalidad', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.xticks(rotation=0)

    # Etiquetar barras con el %
    for container in ax.containers:
        ax.bar_label(container, fmt='%.0f%%', label_type='center', color='white', fontsize=9, padding=3)

    plt.tight_layout()
    plt.show()

# --- EJECUCIÓN ---
mostrar_estadisticas_jornada_por_estrato(poblacion)


import pandas as pd
import matplotlib.pyplot as plt

def mostrar_participacion_modal_por_estrato(poblacion):
    """
    Genera un gráfico de Partición Modal desglosado por Estrato.
    Muestra qué porcentaje de cada estrato eligió Auto, Metro, Bici, etc.
    """
    print("--- Calculando Partición Modal por Estrato ---")

    # 1. Agrupar datos
    datos = {1: {}, 2: {}, 3: {}}
    modos_posibles = ["Auto", "Metro", "Bici", "Caminata", "Teletrabajo"]

    # Inicializar en 0
    for e in datos:
        for m in modos_posibles:
            datos[e][m] = 0

    # Contar elecciones
    for p in poblacion:
        estrato = p['estrato']
        modo = p.get('modo_elegido') # Puede ser None si no se corrió la elección aún

        if modo:
            if modo not in datos[estrato]:
                datos[estrato][modo] = 0
            datos[estrato][modo] += 1

    # 2. Crear DataFrame
    df = pd.DataFrame(datos).T # Transponer: Filas=Estratos, Columnas=Modos
    df.index.name = "Estrato"

    # 3. Calcular Porcentajes (Market Share)
    # Dividimos cada fila por la suma de esa fila
    df_pct = df.div(df.sum(axis=1), axis=0) * 100

    # Mostramos tabla numérica
    display(df_pct.round(1).astype(str) + '%')

    # 4. Graficar (Barras Apiladas al 100%)
    # Definimos colores coherentes para cada modo
    colores = {
        "Auto": "#e74c3c",      # Rojo
        "Metro": "#f1c40f",     # Amarillo
        "Bici": "#2ecc71",      # Verde
        "Caminata": "#3498db",  # Azul
        "Teletrabajo": "#95a5a6" # Gris
    }
    color_list = [colores.get(col, "#333333") for col in df_pct.columns]

    ax = df_pct.plot(kind='bar', stacked=True, figsize=(10, 6), color=color_list, edgecolor='white')

    plt.title('Elección Modal por Estrato Socioeconómico', fontsize=14)
    plt.ylabel('Porcentaje de Viajes (%)', fontsize=12)
    plt.xlabel('Estrato', fontsize=12)

    # Mover la leyenda afuera para que no tape
    plt.legend(title='Modo de Transporte', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.xticks(rotation=0)

    # Etiquetas de datos (solo si el segmento es lo suficientemente grande)
    for c in ax.containers:
        # c es cada grupo de barras (ej. todas las barras de 'Auto')
        labels = [f'{v.get_height():.0f}%' if v.get_height() > 3 else '' for v in c]
        ax.bar_label(c, labels=labels, label_type='center', color='black', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.show()

mostrar_participacion_modal_por_estrato(poblacion_con_eleccion)

import pandas as pd
import matplotlib.pyplot as plt

def graficar_modo_vs_distancia(poblacion, ciudad):
    """
    Agrupa los viajes por distancia al CBD y grafica la partición modal.
    """
    print("--- Generando Gráfico de Modo vs. Distancia ---")

    data = []

    # 1. Extraer datos de distancia y modo
    for p in poblacion:
        modo = p.get('modo_elegido')
        if not modo or modo == "Teletrabajo":
            continue # Opcional: Saltamos teletrabajo para ver solo viajes físicos

        # Calcular distancia real en Km
        celda_origen = p['celda_origen']
        distancia_km = abs(celda_origen - ciudad.cbd_index) * ciudad.ancho_celda

        # Redondear para agrupar mejor si usas decimales (opcional)
        distancia_km = round(distancia_km, 1)

        data.append({
            "Distancia_CBD_Km": distancia_km,
            "Modo": modo
        })

    if not data:
        print("No hay datos de viajes para graficar.")
        return

    # 2. Crear DataFrame
    df = pd.DataFrame(data)

    # 3. Crear Tabla Cruzada (Crosstab) normalizada por filas (Index)
    # Esto nos da el % de elección para cada distancia
    df_crosstab = pd.crosstab(df['Distancia_CBD_Km'], df['Modo'], normalize='index') * 100

    # 4. Mostrar tabla numérica rápida
    print("Tabla de Porcentajes por Distancia:")
    display(df_crosstab.round(1).astype(str) + '%')

    # 5. Graficar
    # Definimos colores coherentes
    colores_map = {
        "Auto": "#f82a14",      # Rojo
        "Metro": "#f1c40f",     # Amarillo
        "Bici": "#2ecc71",      # Verde
        "Caminata": "#3498db"   # Azul
    }
    colores = [colores_map.get(c, "#333") for c in df_crosstab.columns]

    # Usamos 'area' para ver tendencias continuas o 'bar' para discreto
    ax = df_crosstab.plot(kind='bar', stacked=True, figsize=(10, 6), color=colores, width=0.9)

    plt.title('Elección Modal según Distancia al CBD', fontsize=14)
    plt.ylabel('Participación Modal (%)', fontsize=12)
    plt.xlabel('Distancia al Centro (km)', fontsize=12)
    plt.legend(title='Modo', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.3)

    # Ajustar eje Y de 0 a 100
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.show()

# --- EJECUCIÓN ---
graficar_modo_vs_distancia(poblacion_con_eleccion, mi_ciudad)


