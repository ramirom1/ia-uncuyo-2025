import gymnasium as gym
from gymnasium import wrappers
import argparse
import time
import numpy as np
from randomCustom import generate_random_map_custom
from algoritmos import bfs, dfs, dls, ucs, astar


def _run_actions(env, actions, scenario, states_explored=None):
    """Ejecuta una secuencia de acciones en el entorno y muestra métricas uniformes."""
    obs, _info = env.reset()
    states = [obs]
    done = False
    truncated = False
    actions_count = 0
    actions_cost = 0
    last_reward = 0.0

    for action in actions:
        if done or truncated:
            break
        obs, reward, done, truncated, _ = env.step(action)
        last_reward = reward
        actions_count += 1
        if scenario == 1:
            actions_cost += 1
        else:
            # FrozenLake: 0 LEFT, 1 DOWN, 2 RIGHT, 3 UP
            actions_cost += 1 if action in (0, 2) else 10
        states.append(obs) 

    solution_found = bool(done and last_reward == 1.0)
    states_n = states_explored if states_explored is not None else len(states)
    print(f"{states_n}, {actions_count}, {actions_cost}, {solution_found}")


def _run_random_episode(env, scenario):
    obs, _info = env.reset()
    done = False
    truncated = False
    actions_count = 0
    actions_cost = 0
    last_reward = 0.0
    states_n = 1  # incluye estado inicial

    while not (done or truncated):
        action = np.random.choice([0, 1, 2, 3])
        obs, reward, done, truncated, _ = env.step(action)
        last_reward = reward
        actions_count += 1
        if scenario == 1:
            actions_cost += 1
        else:
            actions_cost += 1 if action in (0, 2) else 10
        states_n += 1

    solution_found = bool(done and last_reward == 1.0)
    return states_n, actions_count, actions_cost, solution_found


def main():
    parser = argparse.ArgumentParser(description="Resolver FrozenLake mediante búsqueda")
    parser.add_argument("--algoritmo", default="random", help="random, bfs, dfs, dls, ucs, astar")
    parser.add_argument("--size", type=int, default=16, help="tamaño de la grilla")
    parser.add_argument("--p", type=float, default=0.92, help="probabilidad de camino congelado")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--limite", type=int, default=1000, help="Máximo de pasos para DLS")
    parser.add_argument("--scenario", type=int, choices=[1, 2], default=1, help="Escenario de costo: 1=uniforme, 2=U/D caro")
    parser.add_argument("--render", choices=["none", "human", "ansi"], default="none")
    args = parser.parse_args()

    description = generate_random_map_custom(args.size, args.p, args.seed)

    render_kwargs = {}
    if args.render != "none":
        render_kwargs["render_mode"] = args.render

    env = gym.make(
        'FrozenLake-v1',
        desc=description,
        is_slippery=False,
        **render_kwargs
    ).env
    env = wrappers.TimeLimit(env, 1000)

    print("Numero de estados:", env.observation_space.n)
    print("Numero de acciones:", env.action_space.n)

    algoritmo = (args.algoritmo or "random").lower()

    if algoritmo == "random":
        inicio = time.perf_counter()
        states_n, actions_count, actions_cost, solution_found = _run_random_episode(env, scenario=args.scenario)
        fin = time.perf_counter()
        print(f"{states_n}, {actions_count}, {actions_cost}, {solution_found}")
        print(f"Tiempo de búsqueda: {fin - inicio:.6f} s")
        return
    elif algoritmo == "bfs":
        inicio = time.perf_counter()
        actions, expanded = bfs(env, start=None, goal=None)
        fin = time.perf_counter()
    elif algoritmo == "dfs":
        inicio = time.perf_counter()
        actions, expanded = dfs(env, start=None, goal=None)
        fin = time.perf_counter()
    elif algoritmo == "dls":
        inicio = time.perf_counter()
        actions, expanded = dls(env, start=None, goal=None, limit=args.limite)
        fin = time.perf_counter()
    elif algoritmo == "ucs":
        inicio = time.perf_counter()
        actions, expanded = ucs(env, start=None, goal=None, scenario=args.scenario)
        fin = time.perf_counter()
    elif algoritmo == "astar":
        inicio = time.perf_counter()
        actions, expanded = astar(env, start=None, goal=None, scenario=args.scenario)
        fin = time.perf_counter()
    else:
        raise ValueError("Algoritmo no reconocido. Use: random, bfs, dfs, dls, ucs, astar")

    print("Acciones: ")
    print(actions)
    _run_actions(env, actions, scenario=args.scenario, states_explored=expanded)
    print(f"Tiempo de búsqueda: {fin - inicio:.6f} s")


if __name__ == "__main__":
    main()
    
