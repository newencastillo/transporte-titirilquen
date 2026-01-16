import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import optimize


#Curva flujo-demora autos
def demora_auto_tramo(ubicacion_centro_km,demanda,v_m,a,l_veh,gap,L_ciudad_km,N_pistas,alpha,beta):
  def capacidad(a,l,v_m,gap):
  #Factor de ancho
    if a>=3.5:
      f_a=1
    elif 3<a<3.5:
      f_a=0.9
    else:
      f_a=0.75
    #Velocidad de Flujo libre
    v_l=v_m*f_a
    #Largo efectivo
    l_eff=l+gap
    #Densidad de embotellamiento
    k_e=1000/l_eff
    #Capacidad
    C=(k_e*v_l)/4
    return C,v_l
  C,v_l=capacidad(a,l_veh,v_m,gap)
  #Numero de "parcelas"
  N=len(demanda)
  #"Parcela central"
  idx_centro = int((ubicacion_centro_km /L_ciudad_km) *N)
  if idx_centro >= N:
        idx_centro = N - 1
  if idx_centro < 0:
        idx_centro = 0
  #Largo de las parcelas
  dx=L_ciudad_km/N
  #Tiempo de flujo libre
  t0=(dx/v_l)*60
  #Capacidad total por sentido
  Capacidad_dirección=C*N_pistas
  #Vector de demoras
  t_usuarios=np.zeros(N)
  #Vector de flujos
  flujos_en_via = np.zeros(N)
  demanda_aj=demanda.copy()
  demanda_aj[idx_centro]=0
  #Lado "izquierdo"
  if idx_centro > 0:
        d_izq = demanda_aj[:idx_centro]
        flujo_izq = np.cumsum(d_izq)
        flujos_en_via[:idx_centro] = flujo_izq
        t_local_izq = t0*(1 + alpha * ((flujo_izq / Capacidad_dirección)**beta))
        t_ac_izq = np.cumsum(t_local_izq[::-1])[::-1]
        t_usuarios[:idx_centro] = t_ac_izq - (t_local_izq / 2)
  #Lado "derecho"
  if idx_centro < N - 1:
        d_der = demanda_aj[idx_centro+1:]
        flujo_der = np.cumsum(d_der[::-1])[::-1]
        flujos_en_via[idx_centro+1:] = flujo_der
        t_local_der = t0*(1 + alpha * ((flujo_der / Capacidad_dirección)**beta))
        t_ac_der= np.cumsum(t_local_der)
        t_usuarios[idx_centro+1:] = t_ac_der - (t_local_der / 2)
  t_usuarios[idx_centro] = 0
  flujos_en_via[idx_centro] = 0
  return t_usuarios,flujos_en_via

# @title
def graficar_demoras_por_parcela(tiempos, ubicacion_centro_km, L_ciudad):
    """
    Grafica la demora en función del NÚMERO DE PARCELA (índice), no km.
    """
    N = len(tiempos)
    dx = L_ciudad / N

    # 1. El eje X son los índices de las parcelas (0, 1, 2...)
    eje_x_parcelas = np.arange(N)

    plt.figure(figsize=(10, 6))

    # 2. Graficar la curva
    plt.plot(eje_x_parcelas, tiempos, color='#e74c3c', linewidth=3, label='Tiempo de Viaje')
    plt.fill_between(eje_x_parcelas, tiempos, color='#e74c3c', alpha=0.1)

    # 3. Calcular dónde cae el centro en "coordenadas de parcela"
    # Fórmula inversa: Si x_km = idx * dx + dx/2  -->  idx = (x_km - dx/2) / dx
    centro_idx = (ubicacion_centro_km - dx/2) / dx

    plt.axvline(x=centro_idx, color='#2c3e50', linestyle='--', linewidth=2, label='Centro (CBD)')

    # 4. Detalles estéticos
    plt.title('Perfil de Demoras por Parcela', fontsize=14, fontweight='bold')
    plt.xlabel('Número de Parcela de Origen', fontsize=12)
    plt.ylabel('Tiempo total de viaje (minutos)', fontsize=12)

    # Ajustar límites para que se vean solo las parcelas existentes
    plt.xlim(-0.5, N - 0.5)
    plt.grid(True, which='both', linestyle=':', alpha=0.6)
    plt.legend()

    # Forzar que el eje X muestre enteros (0, 1, 2...)
    from matplotlib.ticker import MaxNLocator
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.show()

# @title
def graficar_demoras_espaciales(distancias, tiempos, ubicacion_centro_km, L_ciudad):
    plt.figure(figsize=(12, 6))

    # 1. Graficar la curva de demoras
    plt.plot(distancias, tiempos, color='#e74c3c', linewidth=3, label='Tiempo de Viaje (Auto)')

    # 2. Rellenar el área bajo la curva para mejor visualización
    plt.fill_between(distancias, tiempos, color='#e74c3c', alpha=0.1)

    # 3. Marcar la ubicación del Centro (CBD)
    plt.axvline(x=ubicacion_centro_km, color='#2c3e50', linestyle='--', linewidth=2, label='Centro (CBD)')

    # 4. Detalles estéticos y etiquetas
    plt.title('Perfil Espacial de Demoras: Tiempo de Viaje al Centro', fontsize=14, fontweight='bold')
    plt.xlabel('Ubicación del Tramo de Origen (km desde el extremo izquierdo)', fontsize=12)
    plt.ylabel('Tiempo total de viaje (minutos)', fontsize=12)

    # Ajustar límites y grilla
    plt.xlim(0, L_ciudad)
    plt.ylim(0, max(tiempos) * 1.1) # Dar un 10% de margen arriba
    plt.grid(True, which='both', linestyle=':', alpha=0.6)
    plt.legend()

    # Anotaciones informativas
    plt.annotate('Centro', xy=(ubicacion_centro_km, 0), xytext=(ubicacion_centro_km + 0.5, max(tiempos)*0.05),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5))

    plt.show()

#Ciclovías
#Curva flujo-demora ciclovías
def demora_bici_tramo(ubicacion_centro_km,capacidad,demanda,v_media,L_ciudad_km,alpha,beta,pendiente_porcentaje):
  #Número de "parcelas"
  N=len(demanda)
  #"Parcela central"
  idx_centro = int((ubicacion_centro_km /L_ciudad_km) *N)
  if idx_centro >= N:
        idx_centro = N - 1
  if idx_centro < 0:
        idx_centro = 0
  #Largo de las parcelas
  dx=L_ciudad_km/N
  #Factor de la pendiente
  def velocidad(v_media,pendiente_porcentaje):
    if pendiente_porcentaje>0:
      factor_pendiente=-0.0579*pendiente_porcentaje+0.9992
    else:
      factor_pendiente=-0.0455*pendiente_porcentaje+1
    v=v_media*factor_pendiente
    return max(min(v,45),5)
  #Velocidades ajustadas
  v_izq=velocidad(v_media,pendiente_porcentaje)
  v_der=velocidad(v_media,-pendiente_porcentaje)
  #Tiempos de flujo libre
  t0_izq=(dx/v_izq)*60
  t0_der=(dx/v_der)*60
  #Vector de demoras
  t_usuarios=np.zeros(N)
  #Vector de flujos
  flujos_en_pista = np.zeros(N)
  demanda_aj=demanda.copy()
  demanda_aj[idx_centro]=0
  if idx_centro > 0:
        d_izq = demanda_aj[:idx_centro]
        flujo_izq = np.cumsum(d_izq)
        flujos_en_pista[:idx_centro] = flujo_izq
        t_local_izq = t0_izq*(1 + alpha * ((flujo_izq / capacidad)**beta))
        t_ac_izq= np.cumsum(t_local_izq[::-1])[::-1]
        t_usuarios[:idx_centro] = t_ac_izq - (t_local_izq / 2)
  if idx_centro < N - 1:
        d_der = demanda_aj[idx_centro+1:]
        flujo_der = np.cumsum(d_der[::-1])[::-1]
        flujos_en_pista[idx_centro+1:] = flujo_der
        t_local_der = t0_der*(1 + alpha * ((flujo_der / capacidad)**beta))
        t_ac_der = np.cumsum(t_local_der)
        t_usuarios[idx_centro+1:] = t_ac_der - (t_local_der / 2)
  t_usuarios[idx_centro] = 0
  flujos_en_pista[idx_centro] = 0
  return t_usuarios,flujos_en_pista


#TRENES
def oferta_tren(Demanda, L_ciudad, x_centro,v_t,K,n_s,v_c,tasa_carga_descarga, frec_min, frec_max):
  #Número de "parcelas"
  N=len(Demanda)
  #"Parcela central"
  idx_centro = int((x_centro /L_ciudad) *N)
  if idx_centro >= N:
        idx_centro = N - 1
  if idx_centro < 0:
        idx_centro = 0
  #Largo de las parcelas
  dx=L_ciudad/N
  #Ubicación parcelas
  x_parcelas = np.arange(N) * dx + (dx / 2)
  #Distancia entre estaciones
  distancia_entre_estaciones = L_ciudad/ n_s
  #Ubicar estaciones
  estaciones_lista = [x_centro]
  cursor = x_centro + distancia_entre_estaciones
  while cursor <= L_ciudad:
      estaciones_lista.append(cursor)
      cursor += distancia_entre_estaciones
  cursor = x_centro - distancia_entre_estaciones
  while cursor >= 0:
      estaciones_lista.append(cursor)
      cursor -= distancia_entre_estaciones
  estaciones = np.array(sorted(estaciones_lista))
  num_s=len(estaciones)
  #Subidas
  pax_suben_hora = np.zeros(num_s)
  pax_bajan_hora = np.zeros(num_s)
  #Distancias de caminata
  dist_acceso = np.zeros(N)
  asignacion_estacion = np.zeros(N, dtype=int)
  for i in range(N):
        distancias = np.abs(estaciones - x_parcelas[i])
        idx_est_cercana = np.argmin(distancias)
        dist_acceso[i] = distancias[idx_est_cercana]
        asignacion_estacion[i] = idx_est_cercana
        if i != idx_centro:
            pax_suben_hora[idx_est_cercana] += Demanda[i]
  idx_estacion_centro = np.argmin(np.abs(estaciones - x_centro))
  suben_desde_izq = np.sum(pax_suben_hora[:idx_estacion_centro])
  suben_desde_der = np.sum(pax_suben_hora[idx_estacion_centro+1:])
  #Bajadas
  pax_bajan_hora[idx_estacion_centro] = np.sum(pax_suben_hora)
  #k
  carga_por_tramo = np.zeros(num_s - 1)
  acumulado = 0
  for i in range(0, idx_estacion_centro):
      acumulado += pax_suben_hora[i]
      carga_por_tramo[i] = acumulado
  acumulado = 0
  for i in range(num_s - 1, idx_estacion_centro, -1):
      acumulado += pax_suben_hora[i]
      carga_por_tramo[i-1] = acumulado
  #k_max
  carga_maxima = np.max(carga_por_tramo) if len(carga_por_tramo) > 0 else 0
  #Frecuencia
  f_ope = carga_maxima / K
  f_op=np.clip(f_ope, frec_min, frec_max)
  capacidad_ofrecida = f_op * K
  if capacidad_ofrecida < carga_maxima:
      print(f"¡ALERTA! Sistema Saturado. Demanda ({carga_maxima:.0f}) > Capacidad Máxima ({capacidad_ofrecida:.0f}) limitada por f_max.")
  suben_por_tren = pax_suben_hora / f_op
  bajan_por_tren = pax_bajan_hora / f_op
  #Tiempos de subida
  t_car=suben_por_tren/tasa_carga_descarga
  #Tiempos de bajada
  bajan_i=suben_desde_izq/f_op
  t_baj_i=bajan_i/tasa_carga_descarga
  bajan_d=suben_desde_der/f_op
  t_baj_d=bajan_d/tasa_carga_descarga
  t_detenido=np.sum(t_car+t_baj_d+t_baj_i)
  t_traslado=(2*L_ciudad)/v_t
  t_paradas=t_detenido/3600
  t_ciclo=t_traslado+t_paradas
  t_acceso=(dist_acceso / v_c) * 60
  t_espera=np.ones(N)*(1/(2*f_op))*60
  t_espera[idx_centro]=0
  t_viaje=(np.abs(x_parcelas - x_centro)/v_t)*60
  flota_minima=np.ceil(f_op*t_ciclo)
  t_usuarios=t_acceso+t_espera+t_viaje
  return t_acceso, t_espera,t_viaje, t_usuarios,f_op, flota_minima


# @title
#PRUEBAS TODO documentar estas funciones, que hacen y tal
def generar_demanda_concentrada(N, L_ciudad, x_centro, demanda_total_modo, dispersion):
    dx = L_ciudad / N
    x_parcelas = np.arange(N) * dx + (dx / 2) # Centroides

    distancia_al_centro = x_parcelas - x_centro
    forma = np.exp(- (distancia_al_centro**2) / (2 * dispersion**2))

    factor_escala = demanda_total_modo / np.sum(forma)
    demanda_vector = forma * factor_escala

    return demanda_vector, x_parcelas

# --- PARÁMETROS GENERALES ---
N_par = 1000000
L = 10
Centro = 5

# --- GENERACIÓN POR MODO ---

D_tren, x_axis = generar_demanda_concentrada(N_par, L, Centro, demanda_total_modo=50000, dispersion=5.0)

D_auto, _ = generar_demanda_concentrada(N_par, L, Centro, demanda_total_modo=15000, dispersion=5.0)

D_bici, _ = generar_demanda_concentrada(N_par, L, Centro, demanda_total_modo=5000, dispersion=2.5)


def graficar_curvas1():
    d_a,f_a=demora_auto_tramo(5,D_auto,60,4,4.5,2,10,1,0.15,4)
    graficar_demoras_por_parcela(d_a, 5, 10)
    d_b,f_b=demora_bici_tramo(5,1000,D_bici,25,10,0.5,2,3)
    graficar_demoras_por_parcela(d_b,10,20)
    d_ac,d_e,d_v,d_u,f_o,f_min=oferta_tren(D_tren,10,5,40,1250,7,3,2,6,20)
    graficar_demoras_por_parcela(d_u, 5, 10)
    print(d_a)
    print(d_b)
    print(d_ac)
    print(d_e)
    print(d_v)
    print(d_u)


### TODO ver que es este codigo y pasarlo a funcion
#CSV por horas
df_raw = pd.read_csv('demanda_detallada_60min (2).csv', sep=',')
df_raw['Hora'] = df_raw['Hora'].astype(str)
N_total = df_raw['Celda'].max() + 1
todas_las_parcelas = range(int(N_total))
horas = sorted(df_raw['Hora'].unique())
demandas_por_hora = {}
for hora in horas:
    df_hora = df_raw[df_raw['Hora'] == hora]
    df_pivot = df_hora.pivot_table(index='Celda',
                                   columns='Modo',
                                   values='Viajes',
                                   aggfunc='sum',
                                   fill_value=0)
    df_pivot = df_pivot.reindex(todas_las_parcelas, fill_value=0)
    demandas_por_hora[hora] = df_pivot


def demanda_horario(hora,demandas_por_hora):
  if hora in demandas_por_hora:
      df_hora = demandas_por_hora[hora]
  zeros_default = pd.Series(0, index=todas_las_parcelas)
  vec_metro = df_hora.get('Metro', zeros_default).values
  vec_auto  = df_hora.get('Auto',  zeros_default).values
  vec_bici  = df_hora.get('Bici',  zeros_default).values
  return vec_metro, vec_auto, vec_bici

#Probando TODO borrar esto.... pero sirve para saber cual es el flujo de cosas
v_m,v_a,v_b=demanda_horario('08:00',demandas_por_hora)
d_a2,f_a2=demora_auto_tramo(5,v_a,60,3.5,4.5,4,10,1,0.15,4)
print(d_a2)
graficar_demoras_por_parcela(d_a2, 5, 10)
d_b2,f_b2=demora_bici_tramo(5,1000,v_b,25,10,0.5,2,3)
graficar_demoras_por_parcela(d_b2,10,20)
d_ac2,d_e2,d_v2,d_u2,f_o2,f_min2=oferta_tren(v_m,10,5,40,1250,7,3,2,6,20)
graficar_demoras_por_parcela(d_u2, 5, 10)



## TODO meter esto a una función ordenada
#Genero CSV
N=len(d_u2)
demoras_modos = {
    'Parcela_ID': range(N),
    # Demoras
    'Tren_Acceso': d_ac2,
    'Tren_Espera': d_e2,
    'Tren_Viaje_En_Vehiculo': d_v2,
    'Tren_Total_General': d_u2,
    'Auto_Total': d_a2,
    'Bici_Total': d_b2
}

df_resultados = pd.DataFrame(demoras_modos)
df_resultados = df_resultados.round(2)

# Guardar a CSV
nombre_archivo = 'resultados_oferta_ciudad_lineal4.csv'
df_resultados.to_csv(nombre_archivo, index=False, sep=',')
# sep=',' usa comas. Si tu Excel usa punto y coma, cambia a sep=';'

print(f"Archivo '{nombre_archivo}' generado exitosamente con {len(df_resultados)} filas.")

# Previsualización en consola
print(df_resultados.head())




### ============================
###  ANALIZAR EL SIGUIENTE CODE
### ============================


def calcular_oferta_horaria(
    hora,
    demandas_por_hora,
    params_auto,
    params_bici,
    params_tren,
    L_ciudad,
    x_centro
):
    """
    Calcula las demoras por modo para una hora dada.
    Retorna un diccionario con todos los vectores.
    """

    # --- 1. Extraer demanda por modo ---
    vec_metro, vec_auto, vec_bici = demanda_horario(hora, demandas_por_hora)

    # --- 2. AUTO ---
    d_auto, f_auto = demora_auto_tramo(
        x_centro,
        vec_auto,
        **params_auto
    )

    # --- 3. BICI ---
    d_bici, f_bici = demora_bici_tramo(
        x_centro,
        vec_bici,
        **params_bici
    )

    # --- 4. TREN ---
    d_acceso, d_espera, d_viaje, d_total, f_op, flota_min = oferta_tren(
        vec_metro,
        L_ciudad,
        x_centro,
        **params_tren
    )

    return {
        "Auto_Total": d_auto,
        "Bici_Total": d_bici,
        "Tren_Acceso": d_acceso,
        "Tren_Espera": d_espera,
        "Tren_Viaje": d_viaje,
        "Tren_Total": d_total,
        "Frecuencia_Tren": f_op,
        "Flota_Minima": flota_min
    }

params_auto = dict(
    v_m=60,
    a=3.5,
    l_veh=4.5,
    gap=4,
    L_ciudad_km=10,
    N_pistas=1,
    alpha=0.15,
    beta=4
)

params_bici = dict(
    capacidad=1000,
    v_media=25,
    L_ciudad_km=10,
    alpha=0.5,
    beta=2,
    pendiente_porcentaje=3
)

params_tren = dict(
    v_t=40,
    K=1250,
    n_s=7,
    v_c=3,
    tasa_carga_descarga=2,
    frec_min=6,
    frec_max=20
)

resultados = calcular_oferta_horaria(
    hora="08:00",
    demandas_por_hora=demandas_por_hora,
    params_auto=params_auto,
    params_bici=params_bici,
    params_tren=params_tren,
    L_ciudad=10,
    x_centro=5
)

graficar_demoras_por_parcela(resultados["Auto_Total"], 5, 10)
graficar_demoras_por_parcela(resultados["Bici_Total"], 5, 10)
graficar_demoras_por_parcela(resultados["Tren_Total"], 5, 10)



