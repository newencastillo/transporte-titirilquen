import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.patches import Patch


from Ciudad.Suelo.Ciudad import *   # 


# ======================================================
# Parámetros globales del modelo
# ======================================================

N = 30       # hogares por estrato
L = 50          # cantidad de terrenos
CBD = L / 2     # posición del CBD

init_z_alta = 0.4
init_z_media = 0.4
init_z_baja = 0.4

init_alpha_alta = 100
init_alpha_media = 50
init_alpha_baja = 8

# ======================================================
# Factory de funciones bid (closure)
# ======================================================

def make_bid(z, alpha):
    """
    Devuelve una función de puja con parámetro z fijo.
    """
    def bid(hogar: Hogar, d, n=1):
        return (hogar.ingreso * z - hogar.T(d)) - ((n-1)*alpha)
    return bid


# ======================================================
# Correr simulación completa
# ======================================================

def correr_simulacion(z_alta, z_media, z_baja, alpha_alta, alpha_media, alpha_baja):

    """
    Construye la ciudad, asigna hogares y devuelve el objeto Ciudad.
    """
    ciudad = Ciudad(L, CBD)

    bid_alta = make_bid(z_alta, alpha_alta)
    bid_media = make_bid(z_media, alpha_media)
    bid_baja = make_bid(z_baja, alpha_baja) # alpha = 0 -> me es completamente indifernete tener vecinos (considerando edificio)

    ### Modificar aqui generacion de hogares
    for ingreso in np.linspace(100, 150, N):
        ciudad.añadir_hogar(ingreso * 6, bid_alta, 1)
        ciudad.añadir_hogar(ingreso * 2, bid_media, 2)
        ciudad.añadir_hogar(ingreso, bid_baja, 3)

    ciudad.asignar_hogares_estrato(5)

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

    # Barras y colores
    colores = []
    for parcela in ciudad.parcelas:
        if len(parcela) == 0:
            colores.append("lightgray")
        else:
            colores.append(
                {1: "red", 2: "blue", 3: "green"}[parcela[0].estrato]
            )
    barras = ax.bar(range(ciudad.L), alturas, color=colores)

    # Linea cbd
    ax.axvline(ciudad.cbd_index, linestyle="--", color="black", label="CBD")

    # Ajustar altura para que no queden barras pegadas al tope
    ymax = max(alturas) if max(alturas) > 0 else 1
    ax.set_ylim(0, ymax * 1.3)

    """# Texto de ingreso promedio por cada parcela
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
"""
    ax.set_xlabel("Terreno")
    ax.set_ylabel("Número de hogares")
    ax.set_title("Distribución de hogares en la ciudad")
    leyenda = [
        Patch(facecolor="red", label="Estrato alto"),
        Patch(facecolor="blue", label="Estrato medio"),
        Patch(facecolor="green", label="Estrato bajo"),
        Patch(label= f"Hogares sin asignar{len(ciudad.hogares_no_asignados())}")
    ]

    ax.legend(handles=leyenda)  



# ======================================================
# Interfaz gráfica
# ======================================================

# Valores iniciales


fig, ax = plt.subplots()
fig.subplots_adjust(left=0.25, bottom=0.35)

# Sliders
ax_z_alta = fig.add_axes([0.25, 0.25, 0.65, 0.03])
ax_z_media = fig.add_axes([0.25, 0.20, 0.65, 0.03])
ax_z_baja = fig.add_axes([0.25, 0.15, 0.65, 0.03])

slider_z_alta = Slider(ax_z_alta, "z alta", 0.0, 1.0, valinit=init_z_alta)
slider_z_media = Slider(ax_z_media, "z media", 0.0, 1.0, valinit=init_z_media)
slider_z_baja = Slider(ax_z_baja, "z baja", 0.0, 1.0, valinit=init_z_baja)

ax_alpha_alta = fig.add_axes([0.25, 0.10, 0.65, 0.03])
ax_alpha_media = fig.add_axes([0.25, 0.05, 0.65, 0.03])
ax_alpha_baja = fig.add_axes([0.25, 0.00, 0.65, 0.03])

slider_alpha_alta = Slider(ax_alpha_alta, "alpha alta", 0, 300, valinit=init_alpha_alta)
slider_alpha_media = Slider(ax_alpha_media, "alpha media", 0, 300, valinit=init_alpha_media)
slider_alpha_baja = Slider(ax_alpha_baja, "alpha baja", 0, 300, valinit=init_alpha_baja)

# ======================================================
# Update function
# ======================================================

def update(val):
    ciudad = correr_simulacion(
        slider_z_alta.val,
        slider_z_media.val,
        slider_z_baja.val,
        slider_alpha_alta.val,
        slider_alpha_media.val,
        slider_alpha_baja.val
    )
    dibujar_ciudad(ciudad, ax)
    fig.canvas.draw_idle()


slider_z_alta.on_changed(update)
slider_z_media.on_changed(update)
slider_z_baja.on_changed(update)
slider_alpha_alta.on_changed(update)
slider_alpha_media.on_changed(update)
slider_alpha_baja.on_changed(update)



# ======================================================
# Botón reset
# ======================================================

resetax = fig.add_axes([0.8, 0.05, 0.1, 0.04])
button = Button(resetax, 'Reset', hovercolor='0.975')

def reset(event):
    slider_z_alta.reset()
    slider_z_media.reset()
    slider_z_baja.reset()
    slider_alpha_alta.reset()
    slider_alpha_media.reset()
    slider_alpha_baja.reset()


button.on_clicked(reset)


# ======================================================
# Inicialización
# ======================================================

ciudad = correr_simulacion(init_z_alta, init_z_media, init_z_baja,init_alpha_alta, init_alpha_media, init_alpha_baja)
dibujar_ciudad(ciudad, ax)

plt.show()
