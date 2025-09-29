import math
import random
from collections import Counter
from typing import List, Optional, Tuple

def generar_estado(n: int, seed: Optional[int] = None) -> List[int]:
    """Genera un tablero aleatorio para el problema de las n reinas."""

    if n < 0:
        raise ValueError("n debe ser no negativo")

    generador = random.Random(seed) if seed is not None else random
    return [generador.randrange(n) for _ in range(n)]


def pairs(n: int) -> int:
    return n * (n - 1) // 2 if n > 1 else 0


def h(tablero: List[int]) -> int:

    n = len(tablero)
    if n <= 1:
        return 0

    # Contar amenazas por filas
    por_fila = Counter(tablero)
    amenazas_fila = sum(pairs(cnt) for cnt in por_fila.values())

    # Contar amenazas por diagonales: fila - columna y fila + columna
    diag_principal = Counter()
    diag_secundaria = Counter()
    for col, fila in enumerate(tablero):
        diag_principal[fila - col] += 1
        diag_secundaria[fila + col] += 1

    amenazas_diag_principal = sum(pairs(cnt) for cnt in diag_principal.values())
    amenazas_diag_secundaria = sum(pairs(cnt) for cnt in diag_secundaria.values())

    return amenazas_fila + amenazas_diag_principal + amenazas_diag_secundaria


def hill_climbing(
    n: int,
    limite_estados: int,
    seed: Optional[int] = None,
    history: Optional[List[int]] = None,
) -> Tuple[List[int], int, int]:

    if n < 0:
        raise ValueError("n debe ser no negativo")
    if limite_estados < 0:
        raise ValueError("limite_estados debe ser no negativo")

    if n == 0:
        return [], 0, 0

    tablero_inicial = generar_estado(n, seed)
    mejorTablero = list(tablero_inicial)
    mejor_h = h(mejorTablero)
    evaluaciones = 0

    if history is not None:
        history.clear()
        history.append(mejor_h)

    if limite_estados == 0:
        return mejorTablero, mejor_h, evaluaciones

    for col in range(n):
        for fila in range(n):
            if fila == mejorTablero[col]:
                continue
            candidato = mejorTablero.copy()
            candidato[col] = fila
            valor = h(candidato)
            evaluaciones += 1

            if valor < mejor_h:
                mejorTablero = candidato
                mejor_h = valor

            if history is not None:
                history.append(mejor_h)

            if evaluaciones >= limite_estados:
                return mejorTablero, mejor_h, evaluaciones

    return mejorTablero, mejor_h, evaluaciones


def simulated_annealing(
    n: int,
    limite_estados: int,
    temperatura_inicial: float = 2.5,
    factor_enfriamiento: float = 0.95,
    temperatura_minima: float = 1e-3,
    seed: Optional[int] = None,
    history: Optional[List[int]] = None,
) -> Tuple[List[int], int, int]:

    if n < 0:
        raise ValueError("n debe ser no negativo")
    if limite_estados < 0:
        raise ValueError("limite_estados debe ser no negativo")
    if factor_enfriamiento <= 0:
        raise ValueError("factor_enfriamiento debe ser positivo")

    if n == 0:
        return [], 0, 0
    if n == 1:
        tablero = generar_estado(1, seed)
        if history is not None:
            history.clear()
            history.append(0)
        return tablero, 0, 0

    rng = random.Random(seed) if seed is not None else random

    actual = generar_estado(n, seed)
    mejor = list(actual)
    valor_actual = h(actual)
    mejor_valor = valor_actual
    temperatura = max(temperatura_inicial, temperatura_minima)
    evaluaciones = 0

    if history is not None:
        history.clear()
        history.append(valor_actual)

    if limite_estados == 0:
        return mejor, mejor_valor, evaluaciones

    while (
        evaluaciones < limite_estados
        and temperatura > temperatura_minima
        and mejor_valor > 0
    ):
        columna = rng.randrange(n)
        fila_actual = actual[columna]

        fila_candidata = rng.randrange(n)
        if fila_candidata == fila_actual:
            fila_candidata = (fila_candidata + 1) % n

        candidato = actual.copy()
        candidato[columna] = fila_candidata
        valor_candidato = h(candidato)
        evaluaciones += 1

        delta = valor_candidato - valor_actual

        aceptar = False
        if delta <= 0:
            aceptar = True
        else:
            probabilidad = 0.0 if temperatura == 0 else math.exp(-delta / temperatura)
            if rng.random() < probabilidad:
                aceptar = True

        if aceptar:
            actual = candidato
            valor_actual = valor_candidato
            if valor_actual < mejor_valor:
                mejor = actual
                mejor_valor = valor_actual

        if history is not None:
            history.append(valor_actual)

        temperatura *= factor_enfriamiento

    return mejor, mejor_valor, evaluaciones


def genetic_algorithm(
    n: int,
    tam_poblacion: int,
    limite_generaciones: int,
    tasa_mutacion: float = 0.25,
    seed: Optional[int] = None,
    history: Optional[List[int]] = None,
) -> Tuple[List[int], int, int]:

    if n < 0:
        raise ValueError("n debe ser no negativo")
    if tam_poblacion <= 0:
        raise ValueError("tam_poblacion debe ser positivo")
    if limite_generaciones < 0:
        raise ValueError("limite_generaciones debe ser no negativo")
    if not 0.0 <= tasa_mutacion <= 1.0:
        raise ValueError("tasa_mutacion debe estar en [0, 1]")

    if n == 0:
        return [], 0, 0

    rng = random.Random(seed) if seed is not None else random


    def cruzar(padre1: List[int], padre2: List[int]) -> List[int]:
        if n <= 1:
            return padre1[:]
        punto = rng.randrange(1, n)
        return padre1[:punto] + padre2[punto:]

    def mutar(individuo: List[int]) -> None:
        if rng.random() < tasa_mutacion:
            columna = rng.randrange(n)
            individuo[columna] = rng.randrange(n)

    poblacion = [[rng.randrange(n) for _ in range(n)] for _ in range(tam_poblacion)]
    aptitudes = []
    evaluaciones = 0

    for individuo in poblacion:
        valor = h(individuo)
        aptitudes.append(valor)
        evaluaciones += 1

    mejor_idx = min(range(len(poblacion)), key=lambda idx: aptitudes[idx])
    mejor_individuo = poblacion[mejor_idx][:]
    mejor_valor = aptitudes[mejor_idx]

    if history is not None:
        history.clear()
        history.append(mejor_valor)

    if mejor_valor == 0:
        return mejor_individuo, mejor_valor, evaluaciones

    def seleccionar_indice() -> int:
        k = 3 if len(poblacion) >= 3 else len(poblacion)
        mejor_local = None
        indice = 0
        for _ in range(k):
            candidato = rng.randrange(len(poblacion))
            valor = aptitudes[candidato]
            if mejor_local is None or valor < mejor_local:
                mejor_local = valor
                indice = candidato
        return indice

    for _ in range(limite_generaciones):
        nueva_poblacion: List[List[int]] = []
        nueva_aptitudes: List[int] = []
        while len(nueva_poblacion) < tam_poblacion:
            idx1 = seleccionar_indice()
            idx2 = seleccionar_indice()
            padre1 = poblacion[idx1]
            padre2 = poblacion[idx2]

            hijo = cruzar(padre1, padre2)
            mutar(hijo)
            valor_hijo = h(hijo)
            evaluaciones += 1
            nueva_poblacion.append(hijo)
            nueva_aptitudes.append(valor_hijo)

            if len(nueva_poblacion) < tam_poblacion:
                hijo2 = cruzar(padre2, padre1)
                mutar(hijo2)
                valor_hijo2 = h(hijo2)
                evaluaciones += 1
                nueva_poblacion.append(hijo2)
                nueva_aptitudes.append(valor_hijo2)

        poblacion = nueva_poblacion
        aptitudes = nueva_aptitudes

        mejor_idx = min(range(len(poblacion)), key=lambda idx: aptitudes[idx])
        mejor_valor_actual = aptitudes[mejor_idx]
        if mejor_valor_actual < mejor_valor:
            mejor_valor = mejor_valor_actual
            mejor_individuo = poblacion[mejor_idx][:]

        if history is not None:
            history.append(mejor_valor)

        if mejor_valor == 0:
            break

    return mejor_individuo, mejor_valor, evaluaciones


def random_search(
    n: int,
    limite_estados: int,
    seed: Optional[int] = None,
    history: Optional[List[int]] = None,
) -> Tuple[List[int], int, int]:

    if n < 0:
        raise ValueError("n debe ser no negativo")
    if limite_estados < 0:
        raise ValueError("limite_estados debe ser no negativo")

    if n == 0:
        return [], 0, 0

    rng = random.Random(seed) if seed is not None else random

    mejor_tablero: Optional[List[int]] = None
    mejor_valor = math.inf
    evaluaciones = 0

    if history is not None:
        history.clear()

    while evaluaciones < limite_estados and mejor_valor > 0:
        evaluaciones += 1
        tablero = [rng.randrange(n) for _ in range(n)]
        valor = h(tablero)

        if mejor_tablero is None or valor < mejor_valor:
            mejor_tablero = tablero
            mejor_valor = valor

        if history is not None:
            history.append(mejor_valor if mejor_tablero is not None else valor)

    if mejor_tablero is None:
        mejor_tablero = [0 for _ in range(n)]
        mejor_valor = h(mejor_tablero)

    if history is not None and not history:
        history.append(mejor_valor)

    return mejor_tablero, mejor_valor, evaluaciones





"""
#Argumento elitismo: int = 1,
#Abajo de rng:     elitismo = max(0, min(elitismo, tam_poblacion))
#Arriba del while del for 

        if elitismo > 0:
            elites = sorted(range(len(poblacion)), key=lambda idx: aptitudes[idx])[:elitismo]
            for idx in elites:
                individuo = poblacion[idx][:]
                nueva_poblacion.append(individuo)
                nueva_aptitudes.append(aptitudes[idx])
"""

