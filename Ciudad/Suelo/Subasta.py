"""Implementación de bid-auction equilibrium para asignación de agentes/hogares
Como descrito en el Libro de Francisco Martínez Concha"""

import numpy as np


### crear Datos exógenos

#np.random.seed(0)

I = 20   # número de parcelas
CBD = 10
H = 3    # estratos
y = np.array([10.0, 7.0, 4.0]) # Ingresos por estrato
beta = 1.0 


H_h = np.array([10, 10, 10]) # Cantidad de loquitos por coso
total_households = H_h.sum()

# Creamos los edificios o algo asi
S = np.random.randint( max((H//I)-3,1), (H//I) +3, size=I)
S = S / S.sum()   
S = (S * total_households).astype(int)
S[-1] += total_households - S.sum() # ajustamos el ultimo depa pa q calce


T = [abs(i - CBD) for i in range(I)] # factor distancia o whatever
# TODO cambiar por  por logsuma de seba logyt

def f(h, i):
    # pesos por estrato?
    alpha = [1.0, 0.5, 0.2]      # penaliza distancia
    gamma = [0.1, 0.3, 0.6]      # penaliza densidad 
    
    return - alpha[h] * T[i] - gamma[h] * S[i]


# calcular coso importante
Z = np.zeros((H, I))

for h in range(H):
    for i in range(I):
        Z[h, i] = H_h[h] * np.exp(beta * (y[h] + f(h, i)))

# Operador de punto fijo

def F(u):
    """
    Operador de punto fijo en utilidades
    """
    denom = np.sum(Z * np.exp(-beta * u[:, None]), axis=0)
    
    u_new = (1 / beta) * np.log(
        np.sum(S * Z / denom, axis=1)
    )
    
    # normalización (invariante a traslación)
    u_new -= u_new[0]
    
    return u_new


## Iterar para encontrar punto fijo

u = np.zeros(H)
tol = 1e-6
max_iter = 500

for it in range(max_iter):
    u_new = F(u)
    
    if np.linalg.norm(u_new - u) < tol:
        print(f"Convergió en {it} iteraciones")
        break
    
    u = u_new

print("Utilidades de equilibrio:", u)

p = np.zeros(I)

for i in range(I):
    p[i] = (1 / beta) * np.log(
        sum(
            H_h[h] * np.exp(beta * (y[h] - u[h] + f(h, i)))
            for h in range(H)
        )
    )

print("Presios:" , p)


# Prob de asignaciones
Q = np.zeros((H, I))

for h in range(H):
    num = S * np.exp(beta * (y[h] - u[h] + np.array([f(h, i) for i in range(I)]) - p))
    Q[h, :] = num / num.sum()

print("Asignación total por estrato:", Q.sum(axis=1))
print("Capacidad por parcela:", (H_h[:,None]*Q).sum(axis=0)[:])


import numpy as np


def asignar_hogares_con_reasignacion(Q, H, S, max_intentos=10_000):
    """
    - Q[h, i] = probabilidad de que estrato h elija parcela i
    - H[h]    = número de hogares del estrato h
    - S[i]    = capacidad de la parcela i
    """

    num_estratos, num_parcelas = Q.shape

    
    assignments = [[] for _ in range(num_parcelas)]

    # que tan ocupado esta la parcela i (para saber que rellenar)
    ocupacion = np.zeros(num_parcelas, dtype=int)

    for h in range(num_estratos):
        for _ in range(H[h]):
            asignado = False
            intentos = 0

            while not asignado:
                intentos += 1
                if intentos > max_intentos:
                    raise RuntimeError(
                        "No se pudo asignar un hogar (capacidades muy restrictivas)"
                    )

                i = np.random.choice(num_parcelas, p=Q[h])

                if ocupacion[i] < S[i]:
                    assignments[i].append(h)
                    ocupacion[i] += 1
                    asignado = True

    return assignments

import matplotlib.pyplot as plt
import numpy as np


def graficar_asignacion(assignments, num_estratos):
    """
    assignments[i] = lista de estratos que ocupan la parcela i
    """

    num_parcelas = len(assignments)

    conteos = np.zeros((num_estratos, num_parcelas))

    for i, parcela in enumerate(assignments):
        for h in parcela:
            conteos[h, i] += 1

    bottom = np.zeros(num_parcelas)

    colores = ["tab:blue", "tab:orange", "tab:green"]
    etiquetas = [f"Estrato {h}" for h in range(num_estratos)]

    plt.figure(figsize=(12, 4))

    for h in range(num_estratos):
        plt.bar(
            range(num_parcelas),
            conteos[h],
            bottom=bottom,
            color=colores[h],
            label=etiquetas[h]
        )
        bottom += conteos[h]

    plt.xlabel("Parcela")
    plt.ylabel("Número de hogares")
    plt.title("Asignación espacial de hogares por estrato")
    plt.legend()
    plt.tight_layout()
    plt.show()

assignments = asignar_hogares_con_reasignacion(Q, H_h, S)
graficar_asignacion(assignments, 3)




