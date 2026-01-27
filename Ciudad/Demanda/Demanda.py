import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt

#CLASE CIUDAD despreciar
class CiudadLineal:
    def __init__(self, n_celdas, ancho_celda):
        self.n_celdas = n_celdas
        self.cbd_index = n_celdas // 2 #CBD a la mitad
        self.ancho_celda = ancho_celda
        self.largo_total = n_celdas * ancho_celda

#CONFIGURACIÓN DE DEMANDA (INPUTS)
CONFIG_DEMANDA = {
    "globales": {
        "v_auto": 31, "v_metro": 35, "v_bici": 14, "v_caminata": 4.8,
        "costo_combustible_km" : 120, "costo_tarifa_metro": 800, "costo_parking": 6000 #CLP
    },
    "estratos": {
        1: { # ESTRATO ALTO
            "prob_teletrabajo": 0.40, "prob_jornada_flexible": 0.50, "prob_part_time": 0.05,
            "jornada": {"horas_rigido": 9.0, "horas_flexible": 8.0, "horas_part_time": 4.0},
            "betas": {
                "asc_auto": 1.5, "asc_metro": -0.2, "asc_bici": -0.9, "asc_caminata": -0.5,
                "b_tiempo_viaje": -0.055,
                "b_tiempo_espera": -0.05,
                "b_tiempo_caminata": -0.15,
                "b_costo": -0.00008,
                "penalizaciones_fisicas": {
                    "bici_10": -0.09, "bici_20": -0.15, "bici_30": -0.5,
                    "walk_5": -0.09,  "walk_15": -0.18, "walk_25": -0.4
                }
            }
        },
        2: { # ESTRATO MEDIO
            "prob_teletrabajo": 0.20, "prob_jornada_flexible": 0.30, "prob_part_time": 0.10,
            "jornada": {"horas_rigido": 9.0, "horas_flexible": 8.5, "horas_part_time": 4.5},
            "betas": {
                "asc_auto": 0.7889, "asc_metro": 0.1040, "asc_bici": -0.6818, "asc_caminata": 0.1,
                "b_tiempo_viaje": -0.0331,
                "b_tiempo_espera": -0.0243,
                "b_tiempo_caminata": -0.0440,
                "b_costo": -0.0002,
                "penalizaciones_fisicas": {
                    "bici_10": -0.0634, "bici_20": -0.1, "bici_30": -0.4,
                    "walk_5": -0.05,  "walk_15": -0.09, "walk_25": -0.2
                }
            }
        },
        3: { # ESTRATO BAJO
            "prob_teletrabajo": 0.05, "prob_jornada_flexible": 0.10, "prob_part_time": 0.15,
            "jornada": {"horas_rigido": 9.5, "horas_flexible": 9.0, "horas_part_time": 5.0},
            "betas": {
                "asc_auto": 0.2, "asc_metro": 0.25, "asc_bici": -0.4, "asc_caminata": 0.4,
                "b_tiempo_viaje": -0.0150,
                "b_tiempo_espera": -0.0150,
                "b_tiempo_caminata": -0.0250,
                "b_costo": -0.0006,
                "penalizaciones_fisicas": {
                    "bici_10": -0.0300, "bici_20": -0.0500, "bici_30": -0.7,
                    "walk_5": -0.0250,  "walk_15": -0.0400, "walk_25": -0.08
                }
            }
        }
    }
}
print("Configuración de Demandas y Jornadas actualizada.")

#Creación de ciudad
mi_ciudad = CiudadLineal(n_celdas=1000, ancho_celda=0.01) #Definición de número de celdas y ancho (km) de cada una
print(f"Ciudad creada con {mi_ciudad.n_celdas} celdas. CBD en {mi_ciudad.cbd_index}.")
print(f"Largo Total calculado: {mi_ciudad.largo_total} km, con CBD en {mi_ciudad.largo_total//2} km")

#FUNCIONES AUXILIARES (estandarización unidades)
def formato_hora(minutos):
    h = int(minutos // 60) % 24
    m = int(minutos % 60)
    return f"{h:02d}:{m:02d}"

def redondear_horario(minutos_reales, intervalo):
    if intervalo <= 0: return int(minutos_reales)
    bloques = round(minutos_reales / intervalo)
    return int(bloques * intervalo)

def calcular_duracion_jornada(estrato, es_flexible, config):
    params = config["estratos"][estrato]
    params_j = params["jornada"]

    es_part_time = random.random() < params["prob_part_time"]

    if es_part_time:
        return int(params_j["horas_part_time"] * 60), "Part-Time"
    elif es_flexible:
        return int(params_j["horas_flexible"] * 60), "Flexible"
    else:
        return int(params_j["horas_rigido"] * 60), "Rígido"



#FUNCIONES DE TIEMPO

def formato_hora(minutos): #minutos a horas
    h = int(minutos // 60) % 24
    m = int(minutos % 60)
    return f"{h:02d}:{m:02d}"

def redondear_horario(minutos_reales, intervalo): #redondeo a intervalo
    if intervalo <= 0: return int(minutos_reales)
    bloques = round(minutos_reales / intervalo)
    return int(bloques * intervalo)

def asignar_horario_entrada_discreto(estrato, config, intervalo=15):
    """Calcula la hora de entrada basada en probabilidad y estrato"""
    prob_flex = config["estratos"][estrato]["prob_jornada_flexible"]

    #Media y Desviación por estrato(Sigma)
    perfiles = {
        1: {'media': 540, 'sigma_rigido': 20, 'sigma_flex': 60}, # 9:00 AM
        2: {'media': 510, 'sigma_rigido': 15, 'sigma_flex': 40}, # 8:30 AM
        3: {'media': 480, 'sigma_rigido': 10, 'sigma_flex': 20}  # 8:00 AM
    }

    es_flexible = random.random() < prob_flex
    p = perfiles[estrato]
    sigma = p['sigma_flex'] if es_flexible else p['sigma_rigido']

    minuto_continuo = np.random.normal(loc=p['media'], scale=sigma)
    return redondear_horario(minuto_continuo, intervalo)

test_hora = asignar_horario_entrada_discreto(estrato=1, config=CONFIG_DEMANDA)
print(f" Prueba de hora generada: {test_hora} minutos ({formato_hora(test_hora)})")



# TODO modificar esta función para que tome de Suelo.Ciudad.generar_datos()
def generar_poblacion_completa(ciudad, config):
    datos = []
    id_counter = 1

    print(f"Generando población completa para {ciudad.n_celdas} celdas...")

    for i in range(ciudad.n_celdas):
        if i == ciudad.cbd_index: continue

        estrato = random.choice([1, 2, 3])

        #Teletrabajo
        prob_tele = config["estratos"][estrato]["prob_teletrabajo"]
        teletrabaja = random.random() < prob_tele

        #Flexible
        prob_flex = config["estratos"][estrato]["prob_jornada_flexible"]
        es_flexible = random.random() < prob_flex

        #Calcular Entrada (Usando la función auxiliar, sin redundancia)
        minuto_entrada = asignar_horario_entrada_discreto(estrato, config, intervalo=15)
        # -----------------------

        #Calcular Duración y Salida
        duracion_min, tipo_jornada = calcular_duracion_jornada(estrato, es_flexible, config)
        minuto_salida = minuto_entrada + duracion_min

        usuario = {
            "id_unico": id_counter,
            "celda_origen": i,
            "estrato": estrato,
            "teletrabaja": teletrabaja,
            "es_flexible": es_flexible,
            "tipo_jornada": tipo_jornada,
            "hora_entrada": formato_hora(minuto_entrada),
            "hora_salida": formato_hora(minuto_salida),
            "duracion_horas": duracion_min / 60,
            "min_entrada": minuto_entrada,
            "min_salida": minuto_salida
        }
        datos.append(usuario)
        id_counter += 1

    return datos

#Actualización población
poblacion = generar_poblacion_completa(mi_ciudad, CONFIG_DEMANDA)

def visualizacion1():
    df = pd.DataFrame(poblacion)
    cols = ['id_unico', 'estrato', 'tipo_jornada', 'hora_entrada', 'duracion_horas', 'hora_salida']
    # print(df[cols].head(40)) # Esto es para notebooks
    df[cols].head(40)



def calcular_utilidades(usuario, ciudad, config, vector_tiempos_oferta):
    estrato = usuario['estrato']
    celda_origen = usuario['celda_origen']
    celda_destino = ciudad.cbd_index

    betas = config['estratos'][estrato]['betas']
    penalizaciones = betas['penalizaciones_fisicas']
    globales = config['globales']

    #Distancia
    distancia_km = abs(celda_destino - celda_origen) * ciudad.ancho_celda

    #AUTO
    if vector_tiempos_oferta is None:
        t_auto = (distancia_km / globales['v_auto']) * 60
    else:
        t_auto = vector_tiempos_oferta[celda_origen]

    costo_auto = (distancia_km * globales['costo_combustible_km']) + globales['costo_parking']
    v_auto = (betas['asc_auto'] + (betas['b_tiempo_viaje'] * t_auto) + (betas['b_costo'] * costo_auto))

    #METRO
    t_viaje_metro = (distancia_km / globales['v_metro']) * 60
    t_espera = 5 #tiempo espera genérico
    t_caminata_acceso = 10 #tiempo caminata genérico
    costo_metro = globales['costo_tarifa_metro']

    v_metro = (betas['asc_metro'] +
               (betas['b_tiempo_viaje'] * t_viaje_metro) +
               (betas['b_tiempo_espera'] * t_espera) +
               (betas['b_tiempo_caminata'] * t_caminata_acceso) +
               (betas['b_costo'] * costo_metro))

    #BICICLETA (Ajuste fatiga)
    t_bici = (distancia_km / globales['v_bici']) * 60

    # Límite a los 60 minutos
    LIMITE_BICI_MIN = 60

    if t_bici > LIMITE_BICI_MIN:
        v_bici = -9999.0
    else:
        penalidad_bici = 0
        if t_bici > 10: penalidad_bici += penalizaciones['bici_10']
        if t_bici > 20: penalidad_bici += penalizaciones['bici_20']
        if t_bici > 30: penalidad_bici += penalizaciones['bici_30']

        # Penalización Cuadrática (Fatiga Progresiva)
        if t_bici > 40:
            factor_sudor = 0.15
            penalidad_bici -= factor_sudor * ((t_bici - 25)**2)

        v_bici = (betas['asc_bici'] +
                  (betas['b_tiempo_viaje'] * t_bici) +
                  penalidad_bici)

    #CAMINATA
    t_caminata = (distancia_km / globales['v_caminata']) * 60

    LIMITE_WALK_MIN = 45 # Nadie camina más de 45 min (aprox 3.5 km)

    if t_caminata > LIMITE_WALK_MIN:
        v_caminata = -9999.0
    else:
        penalidad_walk = 0
        if t_caminata > 5:  penalidad_walk += penalizaciones['walk_5']
        if t_caminata > 15: penalidad_walk += penalizaciones['walk_15']
        if t_caminata > 25: penalidad_walk += penalizaciones['walk_25']

        # Penalización fuerte si caminas más de 20 min
        if t_caminata > 30:
            factor_cansancio = 0.08 # Caminar cansa más rápido que la bici
            penalidad_walk -= factor_cansancio * ((t_caminata - 20)**2)

        v_caminata = (betas['asc_caminata'] +
                      (betas['b_tiempo_caminata'] * t_caminata) +
                      penalidad_walk)

    return {
        "Auto": v_auto,
        "Metro": v_metro,
        "Bici": v_bici,
        "Caminata": v_caminata
    }


## TODO ESTO ES UNA VISUALIZACION DE DATOS FALTA PONERLO EN UN FN
# Tomamos al primer usuario de la lista
def probar_utilidades():
    usuario_test = poblacion[0]

    # Simulamos que no hay congestión (None)
    utilidades = calcular_utilidades(usuario_test, mi_ciudad, CONFIG_DEMANDA, vector_tiempos_oferta=None)

    print(f"Usuario Estrato {usuario_test['estrato']} desde Celda {usuario_test['celda_origen']}:")
    for modo, u in utilidades.items():
        print(f"  V({modo}): {u:.2f}")


## LOGIT 

def elegir_modo_logit(utilidades):
    modos = list(utilidades.keys())
    v_values = np.array(list(utilidades.values()))

    max_v = np.max(v_values)
    exp_values = np.exp(v_values - max_v)

    sum_exp = np.sum(exp_values)

    probabilidades = exp_values / sum_exp
    # random.choices elige basado en los pesos (probabilidades)
    eleccion = random.choices(modos, weights=probabilidades, k=1)[0]

    dict_probs = {modo: round(p, 4) for modo, p in zip(modos, probabilidades)}

    return eleccion, dict_probs

def ejecutar_eleccion_modal(poblacion, ciudad, config, vector_tiempos=None):
    print(f"--- Ejecutando Elección Modal para {len(poblacion)} agentes ---")
    conteo_modos = {"Auto": 0, "Metro": 0, "Bici": 0, "Caminata": 0}

    for persona in poblacion:
        #teletrabajo, no viaja
        if persona['teletrabaja']:
            persona['modo_elegido'] = "Teletrabajo"
            persona['utilidades'] = {}
            persona['probs'] = {}
            continue

        #Calcular Utilidades
        utils = calcular_utilidades(persona, ciudad, config, vector_tiempos)

        #Calcular Probabilidades y Elegir
        eleccion, probs = elegir_modo_logit(utils)

        #Guardar resultados en el agente
        persona['modo_elegido'] = eleccion
        persona['utilidades'] = utils
        persona['probs'] = probs

        conteo_modos[eleccion] += 1

    return poblacion, conteo_modos


# Modelo de elección
poblacion_con_eleccion, resumen = ejecutar_eleccion_modal(poblacion, mi_ciudad, CONFIG_DEMANDA, vector_tiempos=None)

print("\n RESUMEN DE PARTICIÓN MODAL (Iteración 0)")
total_viajes = sum(resumen.values())
for modo, cantidad in resumen.items():
    pct = (cantidad / total_viajes * 100) if total_viajes > 0 else 0
    print(f"{modo}: {cantidad} viajes ({pct:.1f}%)")

#Detalle de un agente
print("\n--- Detalle del primer viajero ---")
#Primero que NO haga teletrabajo para ver datos reales
viajero = next(p for p in poblacion_con_eleccion if p['modo_elegido'] != "Teletrabajo")
print(f"Estrato: {viajero['estrato']} | Origen: {viajero['celda_origen']}")
print(f"Utilidades: {viajero['utilidades']}")
print(f"Probabilidades: {viajero['probs']}")
print(f"--> ELIGIÓ: {viajero['modo_elegido']}")


### CREAR TABLA TODO ENTENDER ESTO 

def generar_tabla_detallada_viajes(poblacion, ciudad, config):
    filas = []
    globales = config['globales']

    print("Generando tabla y calculando tiempos de salida")

    for p in poblacion:
        # Si hace teletrabajo
        if p['modo_elegido'] == "Teletrabajo":
            # Marcamos valores nulos para evitar errores
            p['min_salida_casa'] = None
            filas.append({
                "ID": p['id_unico'],
                "Celda Origen": p['celda_origen'],
                "Modo Elegido": "Teletrabajo",
                "Hora Salida Casa": "-",
                "Tiempo Viaje (min)": 0,
                "Hora Entrada Trabajo": "-"
            })
            continue

        modo = p['modo_elegido']
        celda = p['celda_origen']
        distancia_km = abs(ciudad.cbd_index - celda) * ciudad.ancho_celda

        #Recalcular Tiempo de Viaje (solo del modo elegido)
        t_viaje_min = 0

        if modo == "Auto":
            t_viaje_min = (distancia_km / globales['v_auto']) * 60
        elif modo == "Metro":
            t_v = (distancia_km / globales['v_metro']) * 60
            t_viaje_min = t_v + 5 + 10 # Espera + Acceso
        elif modo == "Bici":
            t_viaje_min = (distancia_km / globales['v_bici']) * 60
        elif modo == "Caminata":
            t_viaje_min = (distancia_km / globales['v_caminata']) * 60

        #Calcular Hora de Salida del Domicilio
        minuto_salida_casa = p['min_entrada'] - t_viaje_min

        p['min_salida_casa'] = minuto_salida_casa
        p['min_viaje_real'] = t_viaje_min
        # -----------------------------

        filas.append({
            "ID": p['id_unico'],
            "Celda Origen": celda,
            "Modo Elegido": modo,
            "Hora Salida Casa": formato_hora(minuto_salida_casa),
            "Tiempo Viaje (min)": round(t_viaje_min, 1),
            "Hora Entrada Trabajo": p['hora_entrada']
        })

    return pd.DataFrame(filas)

df_viajes = generar_tabla_detallada_viajes(poblacion_con_eleccion, mi_ciudad, CONFIG_DEMANDA)
df_viajes



def generar_vectores_demanda(poblacion, ciudad, delta_t=60):
    #Rangos de tiempo (Bins)
    tiempos = range(0, 1440 + delta_t, delta_t) # que es este 1440
    modos_posibles = ["Auto", "Metro", "Bici", "Caminata"]
    demanda = {}

    for t in tiempos:
        demanda[t] = {}
        for m in modos_posibles:
            demanda[t][m] = np.zeros(ciudad.n_celdas, dtype=int)

    print(f"--- Calculando vectores de demanda (Delta T = {delta_t} min) ---")

    for p in poblacion:
        modo = p['modo_elegido']

        # Filtro Teletrabajo
        if modo == "Teletrabajo" or p.get('min_salida_casa') is None:
            continue

        celda = p['celda_origen']

        minuto_carga = p['min_salida_casa']

        # "Binning": Redondeamos hacia abajo al bloque más cercano
        bloque_t = (int(minuto_carga) // delta_t) * delta_t

        # Acumular (+1)
        if 0 <= bloque_t <= 1440:
            demanda[bloque_t][modo][celda] += 1

    return demanda

vectores_demanda = generar_vectores_demanda(poblacion_con_eleccion, mi_ciudad, delta_t=60)


# función para verificar el vector de demandas (?)

def ver_vector(demanda_dict, hora, modo):

    minuto = hora * 60

    # Intentamos obtener el vector para esa hora
    datos_hora = demanda_dict.get(minuto)

    if datos_hora is None:
        print(f"No hay datos registrados para el minuto {minuto} ({hora}:00).")
        return None

    # Intentamos obtener el vector para ese modo
    vector = datos_hora.get(modo)

    if vector is None:
        print(f"El modo '{modo}' no existe en los datos.")
        return None

    # Si todo está bien, mostramos la info
    print(f"--- Vector de Demanda | Hora {hora}:00 | Modo {modo} ---")
    print(f"Total viajes en esta hora: {np.sum(vector)}")
    # Mostramos solo las primeras 15 celdas para no saturar la pantalla
    print(f"Distribución espacial (primeras 15 celdas): {vector[:15]}")

    return vector


## TODO lo siguiente es lo que crea la tabla creo o ke nose

# --- 1. CONFIGURACIÓN DEL INTERVALO ---
INTERVALO_MINUTOS = 60  # <--- CAMBIA ESTE VALOR (ej. 5, 10, 15, 30, 60)

# Generamos los vectores agrupando por el intervalo deseado
vectores_demanda = generar_vectores_demanda(poblacion_con_eleccion, mi_ciudad, delta_t=INTERVALO_MINUTOS)

data_detallada = []

print(f"Procesando datos con intervalos de {INTERVALO_MINUTOS} minutos...")

# --- 2. EXTRACCIÓN DE DATOS POR CELDA Y MODO ---
for t, modos_dict in vectores_demanda.items():
    # Filtro de horario (5:00 AM a 12:00 PM) para no hacer el archivo gigante innecesariamente
    if t < 300 or t > 720: continue

    hora_str = formato_hora(t)

    for modo, vector_celdas in modos_dict.items():
        # En lugar de sumar todo, buscamos los índices de las celdas que tienen viajes (> 0)
        celdas_con_demanda = np.nonzero(vector_celdas)[0]

        for celda in celdas_con_demanda:
            cantidad = vector_celdas[celda]

            # Guardamos la fila con el detalle espacial
            data_detallada.append({
                "Minuto_Inicio": t,
                "Hora_Inicio": hora_str,
                "Intervalo": f"{INTERVALO_MINUTOS} min",
                "Modo": modo,
                "Celda_Origen": celda,
                "Cantidad_Viajes": cantidad
            })

# --- 3. CREACIÓN Y EXPORTACIÓN DEL CSV ---
if len(data_detallada) > 0:
    df_detallado = pd.DataFrame(data_detallada)

    # Nombre del archivo dinámico según el intervalo
    nombre_archivo = f"demanda_detallada_{INTERVALO_MINUTOS}min.csv"
    df_detallado.to_csv(nombre_archivo, index=False)

    print(f"\n¡Éxito! Archivo guardado como: {nombre_archivo}")
    print(f"Total de registros generados: {len(df_detallado)}")

    # Mostramos una muestra de la tabla
    print("\n--- Muestra de los datos generados ---")
    print(df_detallado.head(10))
else:
    print("No se encontraron viajes en el rango de horario seleccionado.")


## TODO meter lo siguiente a una funcion( despues de entenderlo todo y si efectivamente es lo que hay que hacer)


data_detalle = []

print("Procesando vectores de demanda...")

# Iteramos sobre el diccionario de vectores 
for t, modos_dict in vectores_demanda.items():
    if t < 300 or t > 720: continue # Filtro de 5AM a 12PM

    str_hora = formato_hora(t)

    for modo, vector in modos_dict.items():
        # AQUÍ ESTÁ EL CAMBIO:
        # En lugar de sumar todo, buscamos qué celdas tienen valores > 0
        indices_celdas_activas = np.nonzero(vector)[0]

        for celda in indices_celdas_activas:
            cantidad = vector[celda]

            # Guardamos la fila detallada
            data_detalle.append({
                "Minuto": t,
                "Hora": str_hora,
                "Modo": modo,
                "Celda": celda,        # El número de la celda (ubicación)
                "Cantidad": cantidad   # Cuántos viajes hay ahí
            })

# Convertimos a DataFrame
df_detalle = pd.DataFrame(data_detalle)



# --- 1. Generación de la tabla de datos ---
data_detalle = []
print("Procesando vectores de demanda...")

# Iteramos sobre el diccionario de vectores
for t, modos_dict in vectores_demanda.items():
    if t < 300 or t > 720: continue # Filtro de 5AM a 12PM

    # Aseguramos que formato_hora exista, si no, usamos str(t)
    try:
        str_hora = formato_hora(t)
    except NameError:
        str_hora = f"{int(t//60):02d}:{int(t%60):02d}"

    for modo, vector in modos_dict.items():
        # Buscamos qué celdas tienen valores > 0
        indices_celdas_activas = np.nonzero(vector)[0]

        for celda in indices_celdas_activas:
            cantidad = vector[celda]

            # Guardamos la fila detallada
            data_detalle.append({
                "Minuto": t,
                "Hora": str_hora,
                "Modo": modo,
                "Celda": celda,
                "Cantidad": cantidad
            })

# Convertimos a DataFrame
df_detalle = pd.DataFrame(data_detalle)

# --- 2. Visualización y Exportación ---
if not df_detalle.empty:
    print(f"\n--- Detalle Desagregado: {len(df_detalle)} registros encontrados ---")
    print(df_detalle.head(10))

    # === AQUÍ ESTÁ LA LÍNEA PARA EXPORTAR ===
    nombre_archivo = "tabla_detalle_demanda.csv"
    df_detalle.to_csv(nombre_archivo, index=False)
    print(f"\n[ÉXITO] Tabla exportada correctamente como '{nombre_archivo}'.")
    print("Busca el archivo en la carpeta de archivos (panel izquierdo en Colab) para descargarlo.")

    # TRUCO ADICIONAL: Sugerir qué minuto usar para el OTRO notebook
    if 'Auto' in df_detalle['Modo'].unique():
        df_autos = df_detalle[df_detalle['Modo'] == 'Auto']
        if not df_autos.empty:
            mejor_minuto = df_autos.groupby('Minuto')['Cantidad'].sum().idxmax()
            print(f"\nNOTA IMPORTANTE: Para el modelo de Oferta, te conviene usar el minuto {mejor_minuto} ({formato_hora(mejor_minuto)}), ya que es el que tiene más autos.")
else:
    print("ADVERTENCIA: No hay datos para exportar en el rango seleccionado.")


import pandas as pd
import numpy as np

# Configuración de tu ciudad (Asegúrate que coincida con tus parámetros)
L_CIUDAD_KM = 10
NUM_CELDAS = 1000
KM_POR_CELDA = L_CIUDAD_KM / NUM_CELDAS

lista_viajes_individuales = []

print("Generando listado detallado de viajes...")

# Recorremos todos los minutos y modos
for t, modos_dict in vectores_demanda.items():
    # Filtro opcional: Solo horas relevantes (ej: 6:00 a 10:00)
    # if t < 360 or t > 600: continue

    str_hora = formato_hora(t)

    for modo, vector in modos_dict.items():
        # Indices de celdas con viajes
        indices_celdas = np.nonzero(vector)[0]

        for celda in indices_celdas:
            cantidad_viajes = int(vector[celda])

            # Ubicación en Km
            posicion_km = celda * KM_POR_CELDA

            # --- AQUÍ DESAGREGAMOS "CADA VIAJE" ---
            # Si cantidad es 3, creamos 3 filas individuales
            for i in range(cantidad_viajes):
                lista_viajes_individuales.append({
                    "ID_Viaje": len(lista_viajes_individuales) + 1, # Un ID único
                    "Minuto": t,
                    "Hora": str_hora,
                    "Modo": modo,
                    "Celda_Origen": celda,
                    "Posicion_Km": round(posicion_km, 3) # Redondeado a metros
                })

# Crear DataFrame
df_viajes = pd.DataFrame(lista_viajes_individuales)

# Visualizar
print(f"\n--- Total de Viajes Individuales Generados: {len(df_viajes)} ---")
print(df_viajes.head(10))

# Exportar
nombre_archivo_final = "listado_todos_los_viajes.csv"
df_viajes.to_csv(nombre_archivo_final, index=False)
print(f"\nArchivo guardado: {nombre_archivo_final}")


import numpy as np

# 1. Seleccionar la hora punta (ejemplo: 8:00 AM = 480 minutos)
hora_analisis = 8 # 8:00 AM
minuto_analisis = hora_analisis * 60

# 2. Extraer el vector espacial de autos para esa hora
# vectores_demanda es el diccionario que ya creaste con la función generar_vectores_demanda
vector_autos_hora_punta = vectores_demanda[minuto_analisis]['Auto']

print(f"Exportando demanda de Autos para las {hora_analisis}:00")
print(f"Total de autos: {np.sum(vector_autos_hora_punta)}")
print(f"Dimensiones del vector: {len(vector_autos_hora_punta)} celdas")

# 3. Guardar como archivo CSV (texto plano)
np.savetxt("input_demanda_autos.csv", vector_autos_hora_punta, delimiter=",")

print("Archivo 'input_demanda_autos.csv' generado exitosamente.")


# --- FUNCIÓN DE AGREGACIÓN (COPIAR ESTO) ---
def obtener_vectores_demanda(poblacion, ciudad):
    N = ciudad.n_celdas
    flujos_auto = np.zeros(N)
    flujos_metro = np.zeros(N)
    flujos_bici = np.zeros(N)

    for agente in poblacion:
        if agente.get('teletrabaja', False):
            continue

        origen = agente['celda_origen']
        modo = agente.get('modo_elegido')

        # Validación de rango para evitar errores de índice
        if origen >= N: continue

        if modo == "Auto":
            flujos_auto[origen] += 1
        elif modo == "Metro": # O Tren
            flujos_metro[origen] += 1
        elif modo == "Bici":
            flujos_bici[origen] += 1

    return flujos_auto, flujos_metro, flujos_bici


# --- BLOQUE DE EJECUCIÓN LINEAL Y DIAGNÓSTICO ---

# 1. Configuración Inicial
print("--- INICIANDO DIAGNÓSTICO DE DEMANDA (Versión Compatible) ---")
# Asegúrate de que mi_ciudad esté creada
# Si no está creada en celdas anteriores, descomenta la siguiente línea:
# mi_ciudad = CiudadLineal(n_celdas=1000, ancho_celda=0.01)
print(f"Ciudad: {mi_ciudad.n_celdas} celdas. Largo: {mi_ciudad.largo_total} km")

# 2. Generar Población
poblacion = generar_poblacion_completa(mi_ciudad, CONFIG_DEMANDA)
print(f"Población generada: {len(poblacion)} agentes.")

# 3. Elección Modal (Iteramos una vez)
print("Calculando elecciones iniciales...")

for agente in poblacion:
    # IMPORTANTE: Pasamos 'None' como vector de tiempos.
    # Tu función 'calcular_utilidades' ya sabe que si es None, debe usar tiempos default (flujo libre).
    vector_tiempos_dummy = None

    # --- CORRECCIÓN AQUÍ: Usamos el nombre exacto de TU función ---
    utils = calcular_utilidades(agente, mi_ciudad, CONFIG_DEMANDA, vector_tiempos_dummy)

    # Elegir Modo
    eleccion, _ = elegir_modo_logit(utils)

    # Guardamos la elección en el agente
    agente['modo_elegido'] = eleccion

# 4. AGREGACIÓN (Usamos la función nueva que insertaste antes)
vec_auto, vec_metro, vec_bici = obtener_vectores_demanda(poblacion, mi_ciudad)

# 5. OUTPUT PARA REVISIÓN
print("\n--- RESULTADOS DEL DIAGNÓSTICO ---")
print(f"Total Viajes Auto:   {np.sum(vec_auto)}")
print(f"Total Viajes Metro:  {np.sum(vec_metro)}")
print(f"Total Viajes Bici:   {np.sum(vec_bici)}")
print("-" * 30)
print("Muestra de flujo de Autos (Primeras 20 celdas):")
print(vec_auto[:20])



