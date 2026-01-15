## Definir el problema:

Existe un conjunto de hogares que debe ser asignado a una cantidad de terrenos, esto representará la distribución de hogares en una ciudad.

La decisión de como se asignan estos hogares se basa en una especie de "subasta" por los terrenos, es decir, se basa enteramente en la demanda de terreno y en cuanto se está dispuesto a pagar por éste

Cada hogar decide cuánto esta dispuesto a pagar por cierto terreno en base a su *Bid-Rent*, una función propia de cada hogar, que depende de la distancia al centro urbano, y de la "utilidad" dispuesta a tener, de ahora en adelante me referiré a este término tan usado en la economía como "felicidad", que en esta simplificación dependerá exclusivamente de con cuanta plata me quiero quedar, y que tan "bueno" es el terreno, por ahora consideraremos que esto último depende de cuantos vecinos tengo en mi terreno.

Con esto, cuánto dinero cada hogar ofrece por un terreno, dependerá de la distancia al centro y de cuantos vecinos y dinero sobrante estoy dispuesto a tener.

¿La gente con menos ingresos está más dispuesta a vivir con más gente? Qué tan dispuesta esta la gente a vivir lejos del centro?, y otras suposiciones se pueden modelar dandole forma a esta función de bid rent.

la idea de la dinámica de puje, es que los hogares esten dispuestos a "sacrificar" felicidad si se quedan sin "opciones"

Se basa en el standard urban model, conocido tambien como Alonso-Muth-Mills, un modelo simplificado del crecimiento y uso de suelo de una ciudad con un único distrito de negocios central.

## Decisiones de diseño

### 6-1-26

La existencia de la division de clases en Ciudad.py, no esta teniendo mucha funcionalidad practica, me conviene manejar la informacion de la casa en la misma ciudad, para poder hacer cálculos de la utilidad y para poder acceder al bid rent de forma más facil, se podria definir una "forma de bid rent" definida para toda la ciudad, donde se tome como parametro además el ingreso, esto sería tambien para mejorar el control sobre los hogares desde la clase ciudad, creo que no es estrictamente necesario, pero lo que quiero hacer es  como representar el que un hogar este aceotado o no, cual es su valor ingreso para poder controlar el parámetro de "dinero sobrante" para el bid rent de cada casa, podria ser un porcentaje, mich
Se me ocurre lo siguiente:
- el si esta asignada o no sea una flag en la clase Hogar
- cada hogar entonces tiene un índice en la clase ciudad, (solo una lista de hogares en ciudad)
- los terrenos almacenan el índice de cada casa que lo ocupa
- COMO ASIGNO LOS HOGARES -> hacer funcion cañufla que asigne uniformemente o algo asi para tener algunos resultado 

### 7-1

Para una primera implementación de alguna forma de asignación, intentaré replicar una dinámica de Glauber, utilizando la utilidad como la "energía" a maximizar, de esta forma, se espera que el equilibrio estocastico se corresponda con algun tipo de equilibrio económico, el problema con esto es que es de cierta forma "cooperativo", todos los hogares trabajarían para maximizar la utilidad global.
La idea para arreglar esto, es que no se usa directamente la elección probabilista, la parte probabilista es escoger el terreno y el agente que va a pujar por él, cada agente consiste de uno o más hogares

#### Post reunión

Se intentará simplificar más los posibles resultados, se planteará otra asignación donde no se considere una posible densidad en los terrenos, es una casa por terreno, para intentar emular de forma más fácil los pujes de cada uno.

Cada día se subastan los terrenos
cada hogar tiene su terreno preferido, como estamos trabajando con el bid-rent, que toma en consideración las características importantes del terreno, lo usaremos para determinar cuál es este hogar preferido, que será el terreno con mayor bid rent.

Terreno a terreno, se asigna el mejor postor, **DD** que pasa con los hogares que no fueron asignados? hay problema con por ejemplo buscar el segundo terreno preferido ya que entonces importará el orden en que subasto los terrenos, y dejarlos para el siguiente día igual lo es, ya que el plan es cada día ir bajando la "utilidad" que considera el hogar para optar a un terreno.
en la vida real pasa esto mismo?
cuándo bajo la utilidad? cuando todos esten asignados? cuando falte por asignarse? esto no va a pasar aqui porque hay menos hogares que terrenos, por lo que con cualquier greedy se asignan todas los hogares
que hay de la defensa de la propiedad?
se puede entrar en un "loop" (no infinito) donde dos hogares subasta a subasta se roben el mismo terreno?

#### Descubrimientos importantes

Solicitando con otras inteligencias, he de notar que aparentemente es relevante afinar las funciones de bid de cada hogar, es importante aparentemente estratificar para tener comportamientos realmente distintos, onda los pobres que onda y eso, que sea la misma forma pero distintos parametros pe

Definir tres funciones de bid rent:
?? asignarla a cada hogar dependiendo de su ingreso
podria basarme en chile
así el ingreso puede variar fuertemente
sigue funcionando el modelo anterior estilo glauber
- añadir atributo de "clase" al hogar, que puede ser calculado en el constructor
- ordenar y mover "simulacion" a simulation.py
- IMPLEMENTAR BID PUSH
- + cada hogar elige su lugar preferido en base a donde esta dispuesto a pagar mas(?)
- + se subasta el terreno con más pujantes, el resto recalcula su siguiente opcion, hasta que se asignan las casas
- + esto es un dia de subasta, luego al siguiente día se disminuye la utilidad? 
- 
como funciona una subasta?
tengo algo que quiero pongo plata
se la queda el que pone mas plata
el resto ajusta su apuesta y vuelve a apostar.


### 9-1

Arreglar la subasta:
- hacer un primer prototipo de la subasta inicial como se tenia planteado:
- + El ajuste de la utilidad no mejor que no
- + Ponerle numero para ver la matriz de subasta.
- Pueden haber más casas que terreno, así los hogares que no quedan asignados son los que bajan su utilidad para intentar obtener un terreno, así es importante definir un nivel de utilidad mínimo para cada hogar
- que hay de intentar considerar el tamaño del terreno como una proporción de la parcela?
- + pueden haber distintas dinámicas de compra onda comprar terreno disponible o intentar quitar terreno?

