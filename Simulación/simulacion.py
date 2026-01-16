from Ciudad.Demanda.Demanda import *
from Ciudad.Suelo.Ciudad import *
from Ciudad.Oferta.Oferta import *

###
### Datos iniciales:
delta_t = 60 # cambiar a string?
L = 100
N = 100
iteraciones = 5
###
### Generar ciudad
poblacion, ciudad = generar_datos(L, N,CBD=L/2 ).adaptar() # TODO


### LOOP OFERTA DEMANDA:

# Caso base generar una primera demanda
poblacion, _ = ejecutar_eleccion_modal(poblacion, ciudad, CONFIG_DEMANDA)
df_demanda = generar_vectores_demanda(poblacion, ciudad, delta_t)
# adaptar para oferta
demanda = data_detallada(df_demanda)

for i in range(iteraciones):
    # calcular oferta
    #recalcular demanda
    #graficar o una mondá asi
    pass