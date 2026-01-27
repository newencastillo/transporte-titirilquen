"""Implementación de bid-auction equilibrium para asignación de agentes/hogares
Como descrito en el Libro de Francisco Martínez Concha"""


import matplotlib.pyplot as plt
import numpy as np
from scipy.special import logsumexp



### crear Datos exógenos

np.random.seed(22)

I = 1001   # número de parcelas
CBD = I//2
H = 3    # estratos

H_h = np.array([33300, 33300, 33300]) # Cantidad de hogares por estrato
y = np.array([10.0, 7.0, 4.0]) # Ingresos por estrato
total_households = H_h.sum()

beta = 1.0 

def generar_oferta_normal(I, N, CBD, stdv=None) -> list[int]:
    """
    Genera uan oferta posible de capacidades por terreno para la ciudad de los parámetros 
    como una "normal" discreta que excluye el CBD.
    
    :param I: Cantidad de parcelas o terrenos de la ciudad
    :param N: Cantidad de habitantes totales
    :param CBD: Posición del centro donde no se construiran terrenos
    :para
    :return: S[i] vector de capacidades por terreno (cantidad de hogares)
    :rtype: np.array[int]
    """
    if stdv is None:
        stdv = min(CBD, I - 1 - CBD) / 2

    S = np.zeros(I, dtype=int)

    # muestreamos en el intervalo sin CBD
    samples = np.random.normal(loc=CBD, scale=stdv, size=N)

    for s in samples:
        i = int(np.round(s))

        if i >= CBD:
            i += 1
        # reflejar en los bordes
        if i < 0:
            i = -i
        if i >= I:
            i = 2*(I-1) - i

        # saltar CBD sin distorsionar
        

        S[i] += 1

    return S
S = generar_oferta_normal(I, total_households, CBD)

print("Distribucion de parcelas", S)
print("cantidad de casas", sum(S))


T = np.array([abs(i - CBD)/I for i in range(I)]) # factor distancia T:I (parcela) -> R (Valor)
# TODO cambiar por  por logsuma de seba logyt



def resolver_equilibrio_54(
    y,          # (H,) ingresos
    H_h,        # (H,) masas por estrato
    S,          # (I,) capacidades parcelas
    T,          # (I,) distancia / atributo espacial
    beta,       # escalar
    lambda_h,   # (H,) pendientes de puja
    alpha,      # (H,) peso transporte
    rho,        # (H,) peso densidad
    tol=1e-8,
    max_iter=10000
):
    """
    Resuelve utilidades normalizadas \bar u según ecuación (5.4)
    """

    H = len(y)
    I = len(S)

    y = np.asarray(y)
    H_h = np.asarray(H_h)
    S = np.asarray(S)
    lambda_h = np.asarray(lambda_h)
    alpha = np.asarray(alpha)
    rho = np.asarray(rho)
    #S_norm = S/S.mean() # normalizamos S para que no se rompa el cálculo cuando cambia el I
    # -------------------------
    # f_h(z_i) / lambda_h
    # -------------------------
    # f_h(z_i) / lambda_h
    f_div_lambda = (
        - alpha[:, None] * T[None, :]
        - rho[:, None] * S[None, :]
    ) / lambda_h[:, None]

    # log z_hi = log H_h + beta (y_h + f_h(z_i)/lambda_h)
    log_z = (
        np.log(H_h)[:, None]
        + beta * (y[:, None] + f_div_lambda)
    )


    # -------------------------
    # operador de punto fijo F(\bar u)
    # -------------------------
    def F(u_bar):
        """
        Operador de punto fijo según ecuación (5.4)
        usando logsumexp (numéricamente estable)
        """

        # log denom_i = log sum_g H_g exp(beta(y_g + f_gi/lambda_g - u_g))
        log_denom = logsumexp(
            log_z - beta * u_bar[:, None],
            axis=0
        )  # shape (I,)

        # log numerador_h = log sum_i S_i * exp(beta(y_h + f_hi/lambda_h) - log denom_i)
        log_num = (
            np.log(S)[None, :]
            + beta * (y[:, None] + f_div_lambda)
            - log_denom[None, :]
        )

        u_new = (1 / beta) * logsumexp(log_num, axis=1)

        # normalización (invarianza por traslación)
        u_new -= u_new[0]

        return u_new

    # -------------------------
    # iteración
    # -------------------------
    u_bar = np.zeros(H)

    for it in range(max_iter):
        u_new = F(u_bar)
        if np.linalg.norm(u_new - u_bar) < tol:
            print(f"Convergió en {it} iteraciones")
            break
        u_bar = u_new


    # -------------------------
    # precios de equilibrio
    # -------------------------
   

    log_p = logsumexp(
    np.log(H_h)[:, None]
    + beta * (y[:, None] + f_div_lambda - u_bar[:, None]),
    axis=0
    )

    p = log_p / beta


    # -------------------------
    # probabilidades Q_hi
    # -------------------------
    Q = np.zeros((H, I))

    for i in range(I):
        log_q = (
            np.log(S[i])
            + beta * (y + f_div_lambda[:, i] - u_bar - p[i])
        )

        Q[:, i] = np.exp(log_q - logsumexp(log_q))


    return u_bar, p, Q


u, p, Q = resolver_equilibrio_54(
    T=T,
    S=S,
    H_h=H_h,
    y=y,
    beta=beta,
    alpha=[1.0, 1.0, 1.0],
    rho=[0.5, 0.5, 0.5],
    lambda_h=[0.6,0.5,0.4] # marginal utility of income, que tanta utilidad me genera la plata
)
# normalizar precios
p -= p.min()+1 # normalizar precios,

R = p*S # Renta total del terreno
print("Asignación total por estrato:", Q.sum(axis=1))
print("Capacidad por parcela:", (H_h[:,None]*Q).sum(axis=0)[:])

print("Niveles de utilidad en equilibrio", u)
print("PRecios por hogar: ", p)
print("Precios totales", R)

def asignar_hogares_simple(Q, H, S): # TODO implementar
    """Asigna hogares de una mediante una pruta adaptación de las probabilidades desubasta Q
     - Q : Matriz de probabilidades de asignacion
     - H : Vector de cantidad de hogares por estrato
     - S : Vector de espacios disponibles por cada parcela
    Retorna
    -------
    Asignación de cada parcela
    parcelas : lista de parcelas, cada parcela es una lista de los hogares que la ocupan (estratos posibles)

    Nota
    ----
    Se hará la asignación en base a la probabilidad de subasta
    que razonablemente considerará la cantidad de 
    """
    print("Asignando hogares simple")

    num_estratos, num_parcelas = Q.shape
    # Q[h, i] = P(hogar de h -> parcela i)
    parcelas: list[list[int]] = [[] for _ in range(num_parcelas)]
    
    try:
        assert sum(S) == sum(H), "La cantidad de espacios disponibles debe ser igual a la cantidad de hogares" 
        assert len(S) == num_parcelas, "Deben calzar en la matriz de subasta la cantidad de parcelas de la ciudad"
        assert len(H) == num_estratos, "Deben calzar en la matriz de subasta la cantidad de estratos económicos"
    except AssertionError as e:
        print("Los parámetros no calzan entre sí")
        print(e)
        return
    
    # contador hogares sin asignar
    # Recorremos las parcelas en orden
    
    S = np.asarray(S, dtype=int).copy()
    H = np.asarray(H, dtype=int).copy()

    parcelas = [[] for _ in range(num_parcelas)]
    hogares_restantes = H.copy()

    for i in range(num_parcelas):
        pesos = Q[:, i].copy()
        capacidad = S[i]

        for _ in range(capacidad):
            pesos[hogares_restantes == 0] = 0.0

            if pesos.sum() == 0:
                print("Error en la asignación, un hogar individual no se pudo asignar!!")
                break

            probs = pesos / pesos.sum()
            h = np.random.choice(num_estratos, p=probs)

            parcelas[i].append(int(h))
            hogares_restantes[h] -= 1

    return parcelas






def asignar_hogares_con_reasignacion(Q, H, S, max_intentos=100_000):
    """
    - Q[h, i] : probabilidad de que estrato h elija parcela i
    - H[h]    : número de hogares del estrato h
    - S[i]    : capacidad de la parcela i
    """
    print("iniciando asignación de hogares")
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
                    assignments[i].append(h+1) # los estratos parten desde el 1
                    ocupacion[i] += 1
                    asignado = True

    return assignments


# =====================
# Funciones de graficar
# =====================



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

def plot_stratum_composition_by_parcel(Q, labels=None):
    """
    Q[h, i]: matriz de probabilidades
    Grafica barras apiladas:
        - una barra por parcela
        - colores = estratos
        - altura = proporción del estrato en la parcela
    """
    Q = np.asarray(Q)
    H, I = Q.shape

    # composición relativa por parcela
    col_sum = Q.sum(axis=0, keepdims=True)
    col_sum[col_sum == 0] = 1.0  # seguridad numérica
    P = Q / col_sum

    x = np.arange(I)
    bottom = np.zeros(I)

    plt.figure(figsize=(10, 4))
    print("iniciando graficación de ciudad")
    for h in range(H):
        plt.bar(
            x,
            P[h],
            bottom=bottom,
            label=labels[h] if labels else f"Estrato {h}"
        )
        bottom += P[h]

    plt.xlabel("Parcela i")
    plt.ylabel("Proporción")
    plt.title("Composición por estrato en cada parcela")
    plt.legend()
    plt.tight_layout()
    plt.show()


assignments = asignar_hogares_simple(Q, H_h, S)
graficar_asignacion(assignments, 3)




plot_stratum_composition_by_parcel(
    Q,
    labels=["Alto ingreso", "Ingreso medio", "Bajo ingreso" ]
)



