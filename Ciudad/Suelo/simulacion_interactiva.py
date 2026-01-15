import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

from Ciudad import *   # 


# ======================================================
# Parámetros globales del modelo
# ======================================================

N = 10          # hogares por estrato
L = 15          # cantidad de terrenos
CBD = L / 2     # posición del CBD


# ======================================================
# Factory de funciones bid (closure)
# ======================================================

def make_bid(z, alpha):
    """
    Devuelve una función de puja con parámetro z fijo.
    """
    def bid(hogar: Hogar, d, n=1):
        return (hogar.ingreso * z - hogar.T(d)) / (n**alpha)
    return bid


# ======================================================
# Correr simulación completa
# ======================================================

def correr_simulacion(z_alta, z_media, z_baja):
    """
    Construye la ciudad, asigna hogares y devuelve el objeto Ciudad.
    """
    ciudad = Ciudad(L, CBD)

    bid_alta = make_bid(z_alta, 1.5) # alpha = 1.5 -> prefiero no tener vecinos
    bid_media = make_bid(z_media, 1) # alpha = 1 -> me es indiferente tener vecinos
    bid_baja = make_bid(z_baja, 0.9) # alpha = 0.9 -> me gusta tener vecinos

    for ingreso in np.linspace(100, 150, N):
        ciudad.añadir_hogar(ingreso * 6, bid_alta)
        ciudad.añadir_hogar(ingreso * 2, bid_media)
        ciudad.añadir_hogar(ingreso, bid_baja)

    ciudad.asignar_hogares_compleja(4)

    return ciudad


# ======================================================
# Dibujar ciudad (versión compatible con matplotlib interactivo)
# ======================================================

def dibujar_ciudad(ciudad: Ciudad, ax):
    """
    Dibuja la distribución de hogares e ingreso promedio por terreno.
    """
    alturas = [len(p) for p in ciudad.parcelas]

    ingresos_promedio = []
    for parcela in ciudad.parcelas:
        if len(parcela) > 0:
            ingresos_promedio.append(
                sum(h.ingreso for h in parcela) / len(parcela)
            )
        else:
            ingresos_promedio.append(0)

    ax.clear()

    barras = ax.bar(range(ciudad.L), alturas)
    ax.axvline(ciudad.CBD, linestyle="--", color="black", label="CBD")

    ymax = max(alturas) if max(alturas) > 0 else 1
    ax.set_ylim(0, ymax * 1.3)

    # 🔹 AQUÍ VA TU BLOQUE
    for i, barra in enumerate(barras):
        altura = barra.get_height()
        ingreso = ingresos_promedio[i]

        if altura > 0:   # opcional: evita texto en parcelas vacías
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                altura,
                f"{ingreso:.1f}",
                ha="center",
                va="bottom",
                fontsize=8,
                rotation=90
            )

    ax.set_xlabel("Terreno")
    ax.set_ylabel("Número de hogares")
    ax.set_title("Distribución de hogares en la ciudad")
    ax.legend()



# ======================================================
# Interfaz gráfica
# ======================================================

# Valores iniciales
init_z_alta = 0.2
init_z_media = 0.4
init_z_baja = 0.6

fig, ax = plt.subplots()
fig.subplots_adjust(left=0.25, bottom=0.35)

# Sliders
ax_z_alta = fig.add_axes([0.25, 0.25, 0.65, 0.03])
ax_z_media = fig.add_axes([0.25, 0.20, 0.65, 0.03])
ax_z_baja = fig.add_axes([0.25, 0.15, 0.65, 0.03])

slider_z_alta = Slider(ax_z_alta, "z alta", 0.0, 1.0, valinit=init_z_alta)
slider_z_media = Slider(ax_z_media, "z media", 0.0, 1.0, valinit=init_z_media)
slider_z_baja = Slider(ax_z_baja, "z baja", 0.0, 1.0, valinit=init_z_baja)


# ======================================================
# Update function
# ======================================================

def update(val):
    ciudad = correr_simulacion(
        slider_z_alta.val,
        slider_z_media.val,
        slider_z_baja.val
    )
    dibujar_ciudad(ciudad, ax)
    fig.canvas.draw_idle()


slider_z_alta.on_changed(update)
slider_z_media.on_changed(update)
slider_z_baja.on_changed(update)


# ======================================================
# Botón reset
# ======================================================

resetax = fig.add_axes([0.8, 0.05, 0.1, 0.04])
button = Button(resetax, 'Reset', hovercolor='0.975')

def reset(event):
    slider_z_alta.reset()
    slider_z_media.reset()
    slider_z_baja.reset()

button.on_clicked(reset)


# ======================================================
# Inicialización
# ======================================================

ciudad = correr_simulacion(init_z_alta, init_z_media, init_z_baja)
dibujar_ciudad(ciudad, ax)

plt.show()
