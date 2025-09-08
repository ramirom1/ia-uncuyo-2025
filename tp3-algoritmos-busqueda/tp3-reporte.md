Luego de realizar las distintas pruebas con los distintos algoritmos, he llegado a la conclusión de que el algoritmo A* (E1 y E2) fue el que mejor rindió en general, ya que explora pocos estados, tarda poco y las soluciones que encuentra son cortas y con bajo costo. Además, sus resultados son parejos (poca variación).

Luego respecto del UCS quedó muy cerca de A*. Suele tardar un poco más y recorrer más, pero también da soluciones buenas y estables. Es una opción segura cuando no tenemos pistas claras de por dónde conviene ir. Junto conn la anterior, BFS también funciona bien cuando todas las acciones cuestan lo mismo. Suele dar caminos cortos en cantidad de pasos. El lado flojo es que explora bastante y, si los costos cambian entre acciones, ya no es tan conveniente.

En cuanto a DFS y DLS (profundidad y profundidad limitada) muestran rendimiento irregular. A menudo recorren mucho, tardan más y terminan con soluciones más largas y caras. Solo los usaría en casos muy puntuales.

Por ultimo el algoritmo random no es competitivo. Sirve como comparación de base, pero no para resolver el problema en serio.