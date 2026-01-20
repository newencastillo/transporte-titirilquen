import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from itertools import combinations
import random
from ..Demanda.Demanda import *

def generar_datos(L, N, CBD, estratos=None) -> Ciudad:
    """
    Genera un uso de suelo urbano y retorna una ciudad con hogares asignados

    Parámetros
    ----------
    L : Número de parcelas (tamaño de la ciudad).
    N : Número de hogares por estrato.
    CBD : Posición del CBD.
    estratos : list de diccionarios, opcional
        Definición de los estratos económicos. Cada diccionario debe tener:
        - 'clase' : int
        - 'ingresos' :
        - 'z' : float
        - 'multiplicador' : 

    Retorna
    -------
    instacnia de Ciudad
    """

    if estratos is None:
        estratos = [
            {"clase": 1, "ingresos": np.linspace(100, 200, int(N/2)), "z": 0.2, "multiplicador": 4},
            {"clase": 2, "ingresos": np.linspace(100, 200, int(N/4)), "z": 0.4, "multiplicador": 2},
            {"clase": 3, "ingresos": np.linspace(100, 200, int(N/4)), "z": 0.6, "multiplicador": 1},
        ]

    ciudad = Ciudad(L, CBD)

    hogares_info = []  

    hogar_id = 0

    for estrato in estratos: # Construir hogares por cada 
        clase = estrato["clase"]
        z = estrato["z"]
        multiplicador = estrato["multiplicador"]

        def bid_factory(z):
            def bid(hogar, d, n=1):
                return (hogar.ingreso * z - hogar.T(d)) / n
            return bid

        bid_func = bid_factory(z)

        for ingreso_base in estrato["ingresos"]:
            ingreso = ingreso_base * multiplicador
            ciudad.añadir_hogar(ingreso, bid_func)

            hogares_info.append({
                "hogar_id": hogar_id,
                "ingreso": ingreso,
                "estrato": clase,
                "hogar_ref": ciudad.hogares[-1]
            })

            hogar_id += 1

    # Asignar hogares a parcelas
    ciudad.asignar_hogares_simple(1)

    # Construir DataFrame final
    return ciudad


class Ciudad():
    """
    Clase que almacena la info. de una ciudad entera para la simulación
    La ciudad tiene un tamaño L, que corresponden a las "parcelas" de terreno.
    Un distrito de negocios central (CBD)
    Una lista de parcelas, cada una puede contener una cantidad de casas
    """
    def __init__(self, L=100, CBD = 50, prohibidos = []):
        self.L = L; """Cantidad de Parcelas"""
        self.parcelas: list[list[Hogar]] = [[] for i in range(L)] # una lista de listas, cada lsita interior representa las casas en el terreno
        self.cbd_index = CBD
        self.hogares: list[Hogar] = []

        self.prohibidos = [CBD]
        self.prohibidos.append(prohibidos)

    def limpiar(self):
        """ Desaloja todos los terrenos y hogares"""
        self.parcelas = [[] for i in range(self.L)]
        for hogar in self.hogares:
            hogar.asignado = False
            hogar.parcela = None
        
    def añadir_hogar(self, hogar: Hogar):
        """Añade un hogar a la lsita de hogares de la ciudad sin asignar
        dado un hogar iniciado"""
        self.hogares.append(hogar)
    
    def añadir_hogar(self, ingreso: int, bid_fun, estrato: int):
        """Añade un hogar a la lsita de hogares de la ciudad sin asignar
        Crea un hogar con el ingreso y función de puje dada"""
        hogar = Hogar(ingreso,estrato, bid_fun)
        self.hogares.append(hogar)

    def iniciar_hogares(self, N: int):
        """
        DESPRECIADO ?
        Inicia una cantidad de hogares sin asignarles terrenos.
        Limpia los hogares y las parcelas de la ciudad
        """
        self.hogares = []
        self.parcelas = [[] for i in range(self.L)]
        for i in range(N):
            self.hogares.append(Hogar(1000+i*100))
    

    def generar_poblacion_completa(self, config):
        """ entrega el estado actual de la población y la ciudad como un diccionario para ser usado en el módulo demanda"""
        poblacion = []
        id_counter = 1

        print(f"Generando población completa para {self.L} celdas...")

        for hogar in self.hogares:
            if not hogar.asignado: continue

            estrato = hogar.estrato

            #Teletrabajo
            prob_tele = config["estratos"][estrato]["prob_teletrabajo"]
            teletrabaja = random.random() < prob_tele

            #Flexible
            prob_flex = config["estratos"][estrato]["prob_jornada_flexible"]
            es_flexible = random.random() < prob_flex

            #Calcular Entrada 
            minuto_entrada = asignar_horario_entrada_discreto(estrato, config, intervalo=15)
            # -----------------------

            #Calcular Duración y Salida
            duracion_min, tipo_jornada = calcular_duracion_jornada(estrato, es_flexible, config)
            minuto_salida = minuto_entrada + duracion_min

            usuario = {
                "id_unico": id_counter,
                "celda_origen": hogar.parcela,
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
            poblacion.append(usuario)
            id_counter += 1

        return poblacion

    def asignar_hogares_compleja(self, H_max):
        """
        Asigna hogares a terrenos mediante una subasta combinatoria greedy global.

        En cada iteración:
        - se consideran todas las combinaciones de hogares de tamaño 1..H_max
          para todos los terrenos disponibles,
        - se selecciona la combinación (terreno + conjunto de hogares)
          que maximiza la puja total,
        - se asignan esos hogares a ese terreno,
        - se eliminan esos hogares y ese terreno del sistema.

        Parámetros
        ----------
        H_max : int
            Altura máxima permitida por terreno.
        """

        hogares_activos = set(self.hogares)
        terrenos_activos = set(range(self.L))

        # limpiar parcelas por si acaso
        self.limpiar()

        while hogares_activos and terrenos_activos:

            print(f"Quedan {len(terrenos_activos)} terrenos por asignar")
            mejor_valor = -np.inf
            mejor_terreno = None
            mejor_combo = None

            for terreno in terrenos_activos: # en todo terreno
                print(f"Calculando postores para parcela {terreno}")
                d = abs(self.CBD - terreno)
                for n in range(1, min(H_max, len(hogares_activos)) + 1): # Por cada posible altura de edificio
                    for combo in combinations(hogares_activos, n): # Por cada combinaxion posible de altura fija

                        valor = sum(h.bid_rent(d, n) for h in combo)

                        if valor > mejor_valor:
                            mejor_valor = valor
                            mejor_terreno = terreno
                            mejor_combo = combo

            # si no hay ninguna combinación rentable (no es posible creo pero igual)
            if mejor_combo is None:
                break

            # asignar hogares al terreno ganador
            for h in mejor_combo:
                self.parcelas[mejor_terreno].append(h) # asignamos los hogares al terreno
                # Innecesario para lo que estamos haciendo pero igual para mentener consistencia 
                # y para la posibilidad de implementar nash o algo asi
                h.asignado = True
                h.parcela = mejor_terreno

            # eliminar hogares y terreno
            hogares_activos -= set(mejor_combo)
            terrenos_activos.remove(mejor_terreno)

    def hogares_asignados(self) -> bool:
        """True si todos los hogares de la ciudad se declaran asignados
        Falso de otro modo"""
        for hogar in self.hogares:
            if not hogar.asignado:
                return False
        return True
    
    def hogares_no_asignados(self) -> list[Hogar]:
        """Hogares sin terreno asignado en la ciudad"""
        noasign =[]
        for hogar in self.hogares:
            if not hogar.asignado:
                noasign.append(hogar)
        return noasign
    
    def asignar_hogares_simple(self, D):
        """Implementación simple de la asignación de terrenos
        EN CONSTRUCCION: ES NECESARIO IMPLEMENTAR LA FUNCIÓN DE BID ADECUADAMENTI PARA CADA ESTRATO SOCIAL
        Cada día se asigna el terreno a su mejor postor.
        D: Cantidad de días que se van a subastar lso terrenos (cantidad de iteraciones)"""
        #assert (len(self.hogares)<=self.L), "No pueden haber más casas que terrenos en este modelo"
        
        # calcular tamaño de la matriz inicial
        # Numero de hogares
        n = len(self.hogares)
        # Numero de parcelas
        m = self.L

        # Día de parcelas:
        for dia in range(D):
            
            subasta = np.zeros((n,m))
            # calcular matriz Bid terrenos/hogares 
            for h in range(n): #hogares
                for p in range(m): # Terrenos/parcelas
                    d = abs(self.CBD - p)
                    subasta[h,p] = self.hogares[h].bid_rent(d); """OJO AKI, e""" #ctmre

            
            # Aignar parcelas a terrenos hasta que se acaben las casas o terrenos
            casas_activas = list(range(n))
            terrenos_activos = list(range(m))

            while casas_activas and terrenos_activos:
                # la complejidad de la siguiente parte es para no perder los indices al eliminar filas y cols

                # submatriz de terrenos y casas que aun participan
                subM = subasta[np.ix_(casas_activas, terrenos_activos)]

                # Indices locales de el bid más alto
                i_loc, j_loc = np.unravel_index(np.argmax(subM), subM.shape) # gracias chatgpt

                # Traducir a los índices reales
                i = casas_activas[i_loc]
                j = terrenos_activos[j_loc]
                
                # Asignación
                # desasignar hogares de la parcela
                for hogar in self.parcelas[j]: 
                    hogar.asignado = False

                # asignar hogar al terreno que corresponde
                self.parcelas[j] = [self.hogares[i]]
                self.hogares[i].asignado = True
                
                # "quitar" filas y columnas
                casas_activas.remove(i)
                terrenos_activos.remove(j)
            pass

    def asignar_hogares_glauber(self, T):
         """Dinámica de glauber
         T: # de iteraciones"""
         listo = False
         for t in range(T): # TODO hacer iteraciones e ir disminuyendo el z aqui
            # Vamos a elegir un conjunto aleatorio de casas (asignadas o no) (o(L^2))
            n = min(np.random.geometric(0.6),len(self.hogares))
            casas = list(np.random.choice(self.hogares, n, replace=False))

            # vamos a escoger un terreno cualquiera
            i = np.random.choice(self.L)
            d = abs(i - self.CBD)

            # vamos a ver si el puje indica que hay que cambiar
            ataque = 0
            for casa in casas:
                ataque += casa.bid_rent(d, n)
            defensa = 0
            n2 = len(self.parcelas[i])
            for casa in self.parcelas[i]:
                defensa += casa.bid_rent(d, n2)

            # asignamos y desasignamos si corresponde
            if ataque > defensa:

                for casa in self.parcelas[i]:
                    casa.asignado = False
                    casa.parcela = None    
                self.parcelas[i] = []
                # Desasignamos la parcela y sus casas

                for casa in casas:
                    #quitar de la parcela en la que esten
                    j = casa.parcela
                    if j is not None and casa in self.parcelas[j]:
                        self.parcelas[j].remove(casa)
                    casa.asignado = True
                    casa.parcela = i
                    self.parcelas[i].append(casa)

            """if self.hogares_asignados():
                return"""

    def asignar_hogares_subasta(
        self,
        eps=1.0,
        max_iter=100_000
    ):
        """
        Subasta ascendente tipo Auction Algorithm (capacidad 1 por terreno)
        """

        hogares = self.hogares
        terrenos = list(range(self.L))

        precios = np.zeros(self.L)

        # Asignaciones
        asignacion_hogar = {h: None for h in hogares}
        asignacion_terreno = {t: None for t in terrenos}

        it = 0

        while it < max_iter:

            # hogares sin asignar
            libres = [h for h in hogares if asignacion_hogar[h] is None]

            if not libres:
                print(f"Convergió en {it} iteraciones")
                break

            for h in libres:

                # calcular utilidad en cada terreno
                valores = []
                for t in terrenos:
                    if t == self.prohibidos:
                        valores.append(-np.inf)
                        continue

                    d = abs(t - self.cbd_index)
                    valores.append(h.bid_rent(d) - precios[t])

                valores = np.array(valores)

                # mejor y segundo mejor terreno
                t_star = np.argmax(valores)
                mejor = valores[t_star]

                if mejor <= 0:
                    continue  # el hogar sale de la subasta

                # segundo mejor (para regla de precios)
                valores[t_star] = -np.inf
                segundo = np.max(valores)

                # incremento tipo Vickrey
                delta = mejor - segundo + eps
                precios[t_star] += delta

                # reasignación
                perdedor = asignacion_terreno[t_star]
                asignacion_terreno[t_star] = h
                asignacion_hogar[h] = t_star

                if perdedor is not None:
                    asignacion_hogar[perdedor] = None

            it += 1

        # Construir estructura final
        self.parcelas = [[] for _ in range(self.L)]

        for h, t in asignacion_hogar.items():
            if t is not None:
                h.asignado = True
                h.parcela = t
                self.parcelas[t].append(h)



    def asignar_hogares_estrato(self, h_max):
        """Se asignan los hogares a las parcelas maximizando el puje en conjunto de cada estrato
        """
        # Limpiar por si las moscas
        self.limpiar()
        
        #queremos recorrer los terrenos desde los más cercanos al cbd
        terrenos_ordenados = sorted(
            range(self.L),
            key=lambda t: abs(t - self.cbd_index)
        )

        # Hogares no asignados = [[I alto],[I medio], [I bajo]]
        no_asignados = {1: [], 2: [], 3: []}
        for h in self.hogares:
            no_asignados[h.estrato].append(h)



        #itermos terrenos en orden
        for t in terrenos_ordenados:
            d = t - self.cbd_index
            
            mejor_puje = -np.inf
            mejor_estrato = None
            mejor_altura = 0

            for estrato in [1,2,3]:
                disponibles = len(no_asignados[estrato])
                if disponibles == 0:
                    continue

                # chequeamos la mejor altura
                for altura in range(1, min(h_max, disponibles) +1): # range no incluye el ultimo
                    puje = no_asignados[estrato][0].bid_rent(d, altura) * altura
                    # deberia ser el mismo bid para cada estrato por lo que con tomar el primero bastaria
                    if puje > mejor_puje: # guardamos maximo local
                        mejor_puje = puje
                        mejor_altura = altura
                        mejor_estrato = estrato

            
            if mejor_estrato == None:
                continue # si nadie quiere esta parcela

            # de otro modo asignamos por estrato casas cualquiere   
            for _ in range(mejor_altura):
                h = no_asignados[mejor_estrato].pop(0)
                h.asignado = True
                h.parcela = t
                self.parcelas[t].append(h)

        
    

    def dibujar_hogares(self):
        """Plotea el estado actual de la ciudad y sus parcelas como un barplot
        adicionalmente se"""
        alturas = [len(p) for p in self.parcelas]

        # ingreso promedio por parcela
        ingresos_promedio = []
        for p in self.parcelas:
            if len(p) > 0:
                ingresos_promedio.append(
                    sum(h.ingreso for h in p) / len(p)
                )
            else:
                ingresos_promedio.append(0)

        plt.figure()
        plt.ylim(0, max(alturas) * 1.5)
        barras = plt.bar(
            range(self.L),
            alturas,
            color=("blue" if self.hogares_asignados() else "red")
        )

        plt.axvline(self.CBD, linestyle="--", label="CBD")

        # Anotar ingreso promedio por columna
        for i, barra in enumerate(barras):
            altura = barra.get_height()
            ingreso = ingresos_promedio[i]

            plt.text(
                barra.get_x() + barra.get_width() / 2,
                altura,
                f"{ingreso:.1f}",
                ha="center",
                va="bottom",
                fontsize=8,
                rotation=90
            )

        plt.xlabel("Terreno")
        plt.ylabel("Número de hogares")
        plt.title("Distribución de hogares en la ciudad")
        plt.legend()
        plt.tight_layout()
        plt.show()


                   
                   

        


class Hogar():
    """
    Representa un "Household" de la teoría 
    Posee un ingreso, un punto de interés,
    una función de Bid-rent

    Para llamar la función bid se usa bid_rent()

    Para asignar un nuevo bid se debe reasignar la variable self.bid: function
    
    """
    def __init__(self, ingreso, estrato: int, bid_fun = lambda I, d, z, n: I*(1 - z)/((n**(1.2))*d**(1/2)+ 0.01), T = lambda d:d):
            self.ingreso = ingreso
            self.bid = bid_fun
            self.estrato = estrato
            """Función de Puje del hogar, debe ser una función de 4 parámetros numéricos
            ingreso, distancia, z = porcentaje de ingreso que aspiro a conservar,
            n = número de hogares por parcela"""
            self.asignado = False
            self.parcela = None
            self.T = T
            """Función del costo del transporte, depende de la distancia al centro"""

    def utilidad(self, i, CBD, n=1):
        """Función que calcula la "utilidad" que le daría el habitar el terreno i.
        viene en unidades de dinero, por lo que no es utilidad más bien 'dinero sobrante'
        esto es porque faltaría considerar la "felicidad" del terreno en sí.
        """


    def bid_rent(self, *args):
         """Función de Puje de cada hogar """
         return self.bid(self, *args)
    
    def __repr__(self):
        return f"Hogar(${self.ingreso}, {self.parcela})"
    
