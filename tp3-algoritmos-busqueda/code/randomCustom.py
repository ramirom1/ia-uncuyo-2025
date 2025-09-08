import random 

def generate_random_map_custom(size: int = 8, p_frozen: float = 0.92, seed: int | None = None):

    if seed is not None:
        random.seed(seed)

    # Generar grid con F/H
    grid = [['F' if random.random() < p_frozen else 'H' for _ in range(size)] for _ in range(size)]

    # Elegir posiciones aleatorias distintas para inicio y meta
    all_positions = [(i, j) for i in range(size) for j in range(size)]
    start = random.choice(all_positions)
    all_positions.remove(start)
    goal = random.choice(all_positions)

    # Asignar S y G en la grilla
    grid[start[0]][start[1]] = 'S'
    grid[goal[0]][goal[1]] = 'G'

    # Convertir a lista de strings
    desc = ["".join(row) for row in grid]
    return desc
