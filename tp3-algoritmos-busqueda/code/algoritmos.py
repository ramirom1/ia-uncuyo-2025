import numpy as np
from collections import deque
import heapq

def _env_model(env):
    """Devuelve (transitions_model, n_rows, n_cols, description, num_actions) o None si no disponible."""
    unwrapped_env = getattr(env, 'unwrapped', env)
    transitions_model = getattr(unwrapped_env, 'P', None)
    if transitions_model is None:
        return None

    n_rows = getattr(unwrapped_env, 'nrow', None)
    n_cols = getattr(unwrapped_env, 'ncol', None)
    description = getattr(unwrapped_env, 'desc', None)
    if (n_rows is None or n_cols is None) and description is not None:
        try:
            n_rows, n_cols = description.shape
        except Exception:
            pass
    if n_rows is None or n_cols is None:
        try:
            side = int(np.sqrt(env.observation_space.n))
            n_rows = n_cols = side
        except Exception:
            return None

    num_actions = getattr(env.action_space, 'n', 4)
    return (transitions_model, n_rows, n_cols, description, num_actions)


def _state_from_tuple(row_col, ncol):
    row, col = row_col
    return int(row) * ncol + int(col)


def _find_in_desc(description, target_char):
    if description is None:
        return None
    # description suele ser array de bytes
    n_rows, n_cols = description.shape
    for row in range(n_rows):
        for col in range(n_cols):
            ch = description[row, col]
            if isinstance(ch, (bytes, bytearray)):
                ch = ch.decode()
            if ch == target_char:
                return (row, col)
    return None


def _normalize_start_goal(env, start, goal, description, ncol):
    start_state = None
    goal_state = None

    if start is None:
        rc = _find_in_desc(description, 'S')
        if rc is not None:
            start_state = _state_from_tuple(rc, ncol)
    elif isinstance(start, int):
        start_state = start
    elif isinstance(start, (tuple, list)) and len(start) == 2 and all(isinstance(x, (int, np.integer)) for x in start):
        start_state = _state_from_tuple(start, ncol)

    if goal is None:
        rc = _find_in_desc(description, 'G')
        if rc is not None:
            goal_state = _state_from_tuple(rc, ncol)
    elif isinstance(goal, int):
        goal_state = goal
    elif isinstance(goal, (tuple, list)) and len(goal) == 2 and all(isinstance(x, (int, np.integer)) for x in goal):
        goal_state = _state_from_tuple(goal, ncol)

    return start_state, goal_state


def _deterministic_next_state(transitions_model, state, action):
    transitions = transitions_model.get(state, {}).get(action, [])
    if not transitions:
        return None
    for prob, next_state, _reward, _done in transitions:
        if prob > 0:
            return next_state
    return None


def _successors(transitions_model, state, num_actions):
    """Genera pares (action, next_state) para un estado dado en entorno determinista."""
    for action in range(num_actions):
        next_state = _deterministic_next_state(transitions_model, state, action)
        if next_state is not None:
            yield action, next_state


def _reconstruct_actions(parent, parent_action, end_state):
    """Reconstruye la secuencia de acciones desde el inicio hasta end_state."""
    actions = []
    cur_state = end_state
    while parent.get(cur_state) is not None:
        actions.append(parent_action[cur_state])
        cur_state = parent[cur_state]
    actions.reverse()
    return actions


def _step_cost(action, scenario):
    """Costo por acción según escenario especificado."""
    if scenario == 1:
        return 1
    # FrozenLake mapping: 0:LEFT, 1:DOWN, 2:RIGHT, 3:UP
    return 1 if action in (0, 2) else 10

def random_search(env, start=None, goal=None, max_steps=10000):

    model = _env_model(env)
    if model is None:
        return [], 0
    transitions_model, _n_rows, n_cols, description, num_actions = model

    start_state, goal_state = _normalize_start_goal(env, start, goal, description, n_cols)
    if start_state is None or goal_state is None:
        return [], 0

    rng = np.random.default_rng()
    state = start_state
    actions = []
    expanded = 1  # cuenta el estado inicial

    for _ in range(max_steps):
        if state == goal_state:
            return actions, expanded
        # Elegir una acción al azar entre las posibles
        action = int(rng.integers(low=0, high=num_actions))
        next_state = _deterministic_next_state(transitions_model, state, action)
        if next_state is None:
            # si acción inválida, intenta otra sin penalizar expansión
            continue
        actions.append(action)
        state = next_state
        expanded += 1

    # No se alcanzó el objetivo dentro de max_steps
    if state == goal_state:
        return actions, expanded
    return [], expanded


def bfs(env, start, goal):
    """
    Búsqueda por Anchura (BFS) sobre el grafo de estados del entorno.

    - Optimiza el número de pasos (Escenario 1: costo uniforme).
    - Para Escenario 2, el camino hallado minimiza pasos, no costo; el costo se calcula al final.

    Parámetros
    - env: entorno FrozenLake (determinista, is_slippery=False recomendado)
    - start: entero (estado) o tupla (fila, col) o None para detectar desde el entorno
    - goal: entero (estado) o tupla (fila, col) o None para detectar desde el entorno
    """

    model = _env_model(env)
    if model is None:
        return [], 0
    transitions_model, _n_rows, n_cols, description, num_actions = model

    start_state, goal_state = _normalize_start_goal(env, start, goal, description, n_cols)

    if start_state is None or goal_state is None:
        return [], 0

    # BFS (minimiza número de acciones)
    queue = deque([start_state])
    visited_states = set([start_state])
    parent = {start_state: None}
    parent_action = {start_state: None}
    expanded = 0

    found_goal = False
    while queue:
        current_state = queue.popleft()
        expanded += 1
        if current_state == goal_state:
            found_goal = True
            break
        # Expandir sucesores deterministas (is_slippery=False => una transición por acción)
        for action in range(num_actions):
            next_state = _deterministic_next_state(transitions_model, current_state, action)
            if next_state is None:
                continue
            if next_state not in visited_states:
                visited_states.add(next_state)
                parent[next_state] = current_state
                parent_action[next_state] = action
                queue.append(next_state)

    if not found_goal:
        return [], expanded

    # Reconstruir camino
    return _reconstruct_actions(parent, parent_action, goal_state), expanded


def dfs(env, start, goal):
    """Búsqueda en Profundidad (DFS) iterativa con pila. Devuelve lista de acciones o []."""
    model = _env_model(env)
    if model is None:
        return [], 0
    transitions_model, _n_rows, n_cols, description, num_actions = model

    start_state, goal_state = _normalize_start_goal(env, start, goal, description, n_cols)
    if start_state is None or goal_state is None:
        return [], 0

    stack = [(start_state, 0, [])]  # (state, next_action_idx, path_actions)
    on_current_path = set([start_state])
    expanded = 0

    while stack:
        state, next_action_idx, path_actions = stack.pop()
        expanded += 1
        if state == goal_state:
            return path_actions, expanded
        if next_action_idx >= num_actions:
            on_current_path.discard(state)
            continue

        stack.append((state, next_action_idx + 1, path_actions))

        # Expandir un sucesor determinista correspondiente a next_action_idx
        action = next_action_idx
        next_state = _deterministic_next_state(transitions_model, state, action)
        if next_state is None or next_state in on_current_path:
            continue
        on_current_path.add(next_state)
        stack.append((next_state, 0, path_actions + [action]))

    return [], expanded


def dls(env, start, goal, limit=50):

    model = _env_model(env)
    if model is None:
        return [], 0
    transitions_model, _n_rows, n_cols, description, num_actions = model

    start_state, goal_state = _normalize_start_goal(env, start, goal, description, n_cols)
    if start_state is None or goal_state is None:
        return [], 0

    # Pila para simulación iterativa del backtracking: (state, next_action_idx, path_actions)
    stack = [(start_state, 0, [])]

    # Visitados globales (como en tu segundo algoritmo)
    visited = set([start_state])

    expanded = 0

    while stack:
        state, next_action_idx, path_actions = stack.pop()
        expanded += 1  # mantenemos la misma convención que tu versión original

        # Objetivo alcanzado
        if state == goal_state:
            return path_actions, expanded

        # Corte por límite o por acciones agotadas en este estado
        if next_action_idx >= num_actions or len(path_actions) >= limit:
            continue

        # Reinsertar el estado para probar la siguiente acción en una futura iteración
        stack.append((state, next_action_idx + 1, path_actions))

        # Generar el sucesor determinista para la acción actual
        action = next_action_idx
        next_state = _deterministic_next_state(transitions_model, state, action)
        if next_state is None:
            continue

        # Conjunto GLOBAL de visitados: si ya se descubrió ese estado, no lo volvemos a apilar
        if next_state in visited:
            continue

        visited.add(next_state)
        stack.append((next_state, 0, path_actions + [action]))

    # No se encontró solución dentro del límite
    return [], expanded


def ucs(env, start, goal, scenario=1):
    """
    Búsqueda de Costo Uniforme (UCS/Dijkstra).
    - scenario=1: costo de cada acción = 1 (equivale a BFS en óptimo de pasos).
    - scenario=2: LEFT/RIGHT=1, DOWN/UP=10.
    Devuelve la lista de acciones óptima o [].
    """
    model = _env_model(env)
    if model is None:
        return [], 0
    transitions_model, _n_rows, n_cols, description, num_actions = model

    start_state, goal_state = _normalize_start_goal(env, start, goal, description, n_cols)
    if start_state is None or goal_state is None:
        return [], 0

    def step_cost(action):
        return _step_cost(action, scenario)

    heap = [(0, start_state)]
    best_cost = {start_state: 0}
    parent = {start_state: None}
    parent_action = {start_state: None}
    expanded = 0

    while heap:
        g_cost, state = heapq.heappop(heap)
        if g_cost > best_cost.get(state, float('inf')):
            continue
        expanded += 1
        if state == goal_state:
            actions = []
            cur_state = state
            while parent[cur_state] is not None:
                actions.append(parent_action[cur_state])
                cur_state = parent[cur_state]
            actions.reverse()
            return actions, expanded

        for action, next_state in _successors(transitions_model, state, num_actions):
            new_cost = g_cost + step_cost(action)
            if new_cost < best_cost.get(next_state, float('inf')):
                best_cost[next_state] = new_cost
                parent[next_state] = state
                parent_action[next_state] = action
                heapq.heappush(heap, (new_cost, next_state))

    return [], expanded


def astar(env, start, goal, scenario=1):
    """
    Búsqueda A* con heurística admisible basada en distancia Manhattan.
    - scenario=1: h = |dx| + |dy|
    - scenario=2: h = |dx|*1 + |dy|*10 (L/R barato, U/D caro)
    Devuelve la lista de acciones óptima o [].
    """
    model = _env_model(env)
    if model is None:
        return [], 0
    transitions_model, _n_rows, n_cols, description, num_actions = model

    start_state, goal_state = _normalize_start_goal(env, start, goal, description, n_cols)
    if start_state is None or goal_state is None:
        return [], 0

    def step_cost(action):
        return _step_cost(action, scenario)

    goal_row, goal_col = divmod(goal_state, n_cols)

    def heuristic(state):
        row, col = divmod(state, n_cols)
        dx = abs(col - goal_col)
        dy = abs(row - goal_row)
        if scenario == 1:
            return dx + dy
        return dx * 1 + dy * 10

    heap = [(heuristic(start_state), 0, start_state)]  # (f, g, state)
    best_cost = {start_state: 0}
    parent = {start_state: None}
    parent_action = {start_state: None}
    expanded = 0

    while heap:
        f_cost, g_cost, state = heapq.heappop(heap)
        if g_cost > best_cost.get(state, float('inf')):
            continue
        expanded += 1
        if state == goal_state:
            actions = []
            cur_state = state
            while parent[cur_state] is not None:
                actions.append(parent_action[cur_state])
                cur_state = parent[cur_state]
            actions.reverse()
            return actions, expanded

        for action, next_state in _successors(transitions_model, state, num_actions):
            new_cost = g_cost + step_cost(action)
            if new_cost < best_cost.get(next_state, float('inf')):
                best_cost[next_state] = new_cost
                parent[next_state] = state
                parent_action[next_state] = action
                heapq.heappush(heap, (new_cost + heuristic(next_state), new_cost, next_state))

    return [], expanded
