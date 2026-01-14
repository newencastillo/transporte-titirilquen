import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def generar_datos(L, N, CBD, estratos=None):
    """
    Genera un uso de suelo urbano y retorna un DataFrame con información
    de cada hogar.

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
    pandas.DataFrame
        Columnas:
        - hogar_id
        - ingreso
        - estrato
        - parcela
    """

    if estratos is None:
        estratos = [
            {"clase": 1, "ingresos": np.linspace(100, 200, N), "z": 0.2, "multiplicador": 4},
            {"clase": 2, "ingresos": np.linspace(100, 200, N), "z": 0.4, "multiplicador": 2},
            {"clase": 3, "ingresos": np.linspace(100, 200, N), "z": 0.6, "multiplicador": 1},
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
    filas = []

    for idx_parcela, parcela in enumerate(ciudad.parcelas):
        for hogar in parcela:
            info = next(h for h in hogares_info if h["hogar_ref"] is hogar)

            filas.append({
                "hogar_id": info["hogar_id"],
                "ingreso": info["ingreso"],
                "estrato": info["estrato"],
                "parcela": idx_parcela
            })

    df = pd.DataFrame(filas)
    return df


class Ciudad():
    """
    Clase que almacena la info. de una ciudad entera para la simulación
    La ciudad tiene un tamaño L, que corresponden a las "parcelas" de terreno.
    Un distrito de negocios central (CBD)
    Una lista de parcelas, cada una puede contener una cantidad de casas
    """
    def __init__(self, L=100, CBD = 50):
        self.L = L; """Cantidad de Parcelas"""
        self.parcelas: list[list[Hogar]] = [[] for i in range(L)] # una lista de listas, cada lsita interior representa las casas en el terreno
        self.CBD = CBD
        self.hogares: list[Hogar] = []

    def run(self,p=0.8):
        """
        DESPRECIADO
        Rápida ejecución de la dinámica del proceso
        p: cantidad de hogares con respecto a la cantidad de parcelas"""
        self.iniciar_hogares(int(self.L*p))
        for i in range(3):
            self.asignar_hogares_glauber(1000000)
            self.dibujar_hogares()
        
    def añadir_hogar(self, hogar: Hogar):
        """Añade un hogar a la lsita de hogares de la ciudad sin asignar
        dado un hogar iniciado"""
        self.hogares.append(hogar)
    
    def añadir_hogar(self, ingreso: int, bid_fun):
        """Añade un hogar a la lsita de hogares de la ciudad sin asignar
        Crea un hogar con el ingreso y función de puje dada"""
        hogar = Hogar(ingreso, bid_fun)
        self.hogares.append(hogar)

    def iniciar_hogares(self, N: int):
        """
        Inicia una cantidad de hogares sin asignarles terrenos.
        Limpia los hogares y las parcelas de la ciudad
        """
        self.hogares = []
        self.parcelas = [[] for i in range(self.L)]
        for i in range(N):
            self.hogares.append(Hogar(1000+i*100))

    def hogares_asignados(self) -> bool:
        """True si todos los hogares de la ciudad se declaran asignados
        Falso de otro modo"""
        for hogar in self.hogares:
            if not hogar.asignado:
                return False
        return True
    
    def hogares_no_asignados(self) -> int:
        """Cantidad de hogares sin terreno asignado en la ciudad"""
        i = 0
        for hogar in self.hogares:
            if not hogar.asignado:
                i+=1
        return i
    
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
    
    """
    def __init__(self, ingreso, bid_fun = lambda I, d, z, n: I*(1 - z)/((n**(1.2))*d**(1/2)+ 0.01), T = lambda d:d):
            self.ingreso = ingreso
            self.bid = bid_fun
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
    
