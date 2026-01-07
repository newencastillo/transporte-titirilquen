

class Ciudad():
    """
    Clase que almacena la info. de una ciudad entera para la simulación
    La ciudad tiene un tamaño L, que corresponden a las "parcelas" de terreno.
    Un distrito de negocios central (CBD)
    Una cantidad de hogares(?)
    """
    def __init__(self, L=100, CBD = 50):
        self.L = L
        self.CBD = CBD
        self.hogares_asignados = []
        self.hogares_no_asignados = []
        

    def iniciar_hogares(self, N):
        """
        Inicia una cantidad de hogares sin asignarles terrenos
        """
        for i in range(N):
            self.hogares_no_asignados.append(Hogar(1000, self.CBD))

    def asignar_hogares(self):
         """complejo.....
         Esta es la parte densa del modeluwu, tengo que decidir como voy a hacer esto en base a las bid rent,
         necesito implementar las parcelas como una lista de listas(? o un q"""
        


class Hogar():
    """
    Representa un "Household" de la teoría 
    Posee un ingreso, un punto de interés,
    una función de Bid-rent
    """
    def __init__(self, ingreso, CBD, bid_fun = lambda I, z, n: (I - z)/n):
            self.ingreso = ingreso
            self.CBD = CBD
            self.bid = bid_fun

    def bid_rent(self, I, z, n):
         return self.bid(I, z, n)
    
