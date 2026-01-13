from Ciudad import *

### definir parámetros iniciales

# % del ingreso que se dispone para usar para arriendo
z_alta = 0.2
z_media = 0.4
z_baja = 0.6

# numero de hogares por estrato economico
N = 10
# Tamaño de la ciudad (cantidad de terrenos)
L = 14
# Posición del cbd
CBD = L/2

### Definir funciones Bid para cada estrato
def bid_alta(hogar: Hogar, d, n=1):
    return (hogar.ingreso*(z_alta) - hogar.T(d))/n
def bid_media(hogar: Hogar, d, n=1):
    return (hogar.ingreso*(z_media) - hogar.T(d))/n
def bid_baja(hogar: Hogar, d, n=1):
    return (hogar.ingreso*(z_baja) - hogar.T(d))/n


### Definir SImulación:

Titirilquen = Ciudad(L,CBD)
# Cargar hogares iniciales
for ingreso in np.linspace(100, 200, N):
    Titirilquen.añadir_hogar(ingreso*4, bid_alta)
    Titirilquen.añadir_hogar(ingreso*2, bid_media)
    Titirilquen.añadir_hogar(ingreso, bid_baja)
    

    # Asignar
Titirilquen.asignar_hogares_simple(1)
#Titirilquen.asignar_hogares_glauber(int(1e7)) 
    # Dibujar
Titirilquen.dibujar_hogares()
