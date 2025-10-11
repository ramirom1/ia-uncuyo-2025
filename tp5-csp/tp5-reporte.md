# TP5 - Constraint Satisfaction Problems (CSP)

## 1. Formulación CSP para Sudoku

### Variables

S[i,j] para 1 <= i,j => 9, donde cada variable es el valor dentro de la fila i con columna j

### Dominio

El dominio de las variables es el siguiente: {1,2,3,4,5,6,7,8,9}

### Restricciones

- **Restricciones por fila**: ∀i, ∀k ≠ j : S[i,j] ≠ S[i,k]

- **Restricciones por columna**: ∀j, ∀k ≠ i : S[i,j] ≠ S[k,j]

- **Restricciones por cuadrante**: ∀(i,j), (k,t), (i,j) ≠ (k,t) ; si ((i-1) // 3, (j-1) // 3) = ((k-1) // 3, (t-1) // 3) entonces S[i,j] ≠ S[k,t] 

## 2. Consistencia de arcos (AC-3) en el mapa de Australia

### Variables, dominios y vecinos

- Variables y vecindades relevantes

- WA vecina de NT y SA.
 
- SA vecina de WA, NT, Q, NSW y V.

- V vecina de SA y NSW.

- NT vecina de WA, SA y Q.

- Q vecina de NT, SA y NSW.

- NSW vecina de SA, Q y V.

- (Tasmania T no afecta: no tiene vecinos.)

- Dominios iniciales (tras la asignación parcial)

- WA = {red}

- V = {blue}

- NT, SA, Q, NSW, T = {red, green, blue}

### Demostración del resultado de ejecución

1) REVISE(SA→WA) con WA={red}
Elimina red de SA ⇒ SA ∈ {green, blue}

2) REVISE(SA→V) con V={blue}
Elimina blue de SA ⇒ SA = {green} (se fija SA)

Al reducir SA, se re-encolan arcos (NT→SA), (Q→SA), (NSW→SA), (WA→SA), (V→SA).

3) REVISE(NT→SA) con SA={green}
Elimina green de NT ⇒ NT ∈ {red, blue}

4) REVISE(NT→WA) con WA={red}
Elimina red de NT ⇒ NT = {blue} (se fija NT)

Re-encolar (Q→NT), (SA→NT), …

5) REVISE(Q→NT) con NT={blue}
Elimina blue de Q ⇒ Q ∈ {red, green}

6) REVISE(Q→SA) con SA={green}
Elimina green de Q ⇒ Q = {red} (se fija Q)

7) Re-encolar (NSW→Q), (NT→Q), (SA→Q), …

8) REVISE(NSW→Q) con Q={red}
Elimina red de NSW ⇒ NSW ∈ {green, blue}

9) REVISE(NSW→SA) con SA={green}
Elimina green de NSW ⇒ NSW = {blue} (se fija NSW)

10) REVISE(NSW→V) con V={blue} y restricción NSW≠V
Para el único valor de NSW, blue, no existe valor en V (solo blue) que satisfaga NSW≠V.
Se elimina blue de NSW ⇒ NSW = ∅ (dominio vacío)

## 3. Complejidad de AC-3 en CSP estructurado como árbol

O(n*d^3) en el peor caso.

Si hay n variables y cada dominio tiene tamaño máximo d, AC-3 cuesta O(e*d^3) (cada arco puede re-examinarse O(d) veces y cada REVISE cuesta O(d^2)).
En un árbol e=n−1, así que el costo se vuelve O((n−1)*d^3)=O(n *d^3).

## Implementación de Algoritmos

### Metricas promedio con desviación estándar

- **Backtracking**:
  n=4: success=100.0% | time=0.029971ms ± 0.020269ms | nodes=7.2 ± 2.9
  n=8: success=100.0% | time=0.151072ms ± 0.114736ms | nodes=21.3 ± 15.2
  n=10: success=100.0% | time=0.686876ms ± 0.911322ms | nodes=72.2 ± 93.4
- **Forward Checking**:
  n=4: success=100.0% | time=0.052579ms ± 0.026089ms | nodes=7.2 ± 2.9
  n=8: success=100.0% | time=0.209755ms ± 0.135001ms | nodes=16.6 ± 12.8
  n=10: success=100.0% | time=0.587702ms ± 0.593825ms | nodes=57.0 ± 84.1

## Comparación con tp4-busquedas-locales

Los exactos (Backtracking y, sobre todo, Forward Checking) logran 100% de éxito en n=4,8,10. Su costo crece con n, pero Forward Checking explora menos nodos que Backtracking y ambos mantienen tiempos medianos similares, ofreciendo fiabilidad garantizada y esfuerzo controlado frente al aumento de tamaño.

Las metaheurísticas y métodos estocásticos son ultra-rápidos cuando aciertan en n chico, pero su tasa de éxito cae fuerte al escalar: GA pasa de 100% (n=4) a ~60% (n=8) y ~37% (n=10); SA cae a ~20% y ~3%; HC y Random prácticamente no resuelven en n=10.

## Gráficos

![Grafico de cajas y extensiones de cantidad de nodos](nodes_boxplots.png)
![Grafico de cajas y extensiones de tiempo empleado](time_boxplots.png)

Para poder apreciar mejor el comportamiento de cada caso, se agregan los graficos por separado.
