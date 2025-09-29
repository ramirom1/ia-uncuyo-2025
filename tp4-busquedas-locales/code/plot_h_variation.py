#!/usr/bin/env python3
import argparse
import os
import time
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt

import reinas


def run_algorithms(
    size: int,
    max_states: int,
    seed: int,
    population: int,
    generations: int,
    mutation: float,
) -> Dict[str, Tuple[List[int], List[int], float, int]]:
    results: Dict[str, Tuple[List[int], List[int], float, int]] = {}

    history: List[int] = []
    start = time.perf_counter()
    best, h_value, states = reinas.random_search(size, max_states, seed=seed, history=history)
    elapsed = time.perf_counter() - start
    results["random"] = (history.copy(), best, elapsed, states)

    history = []
    start = time.perf_counter()
    best, h_value, states = reinas.hill_climbing(size, max_states, seed=seed, history=history)
    elapsed = time.perf_counter() - start
    results["HC"] = (history.copy(), best, elapsed, states)

    history = []
    start = time.perf_counter()
    best, h_value, states = reinas.simulated_annealing(
        size,
        max_states,
        seed=seed,
        history=history,
    )
    elapsed = time.perf_counter() - start
    results["SA"] = (history.copy(), best, elapsed, states)

    history = []
    start = time.perf_counter()
    best, h_value, states = reinas.genetic_algorithm(
        size,
        tam_poblacion=population,
        limite_generaciones=generations,
        tasa_mutacion=mutation,
        seed=seed,
        history=history,
    )
    elapsed = time.perf_counter() - start
    results["GA"] = (history.copy(), best, elapsed, states)

    return results


def plot_series(
    name: str,
    history: List[int],
    size: int,
    seed: int,
    best: List[int],
    elapsed: float,
    states: int,
    output_dir: str,
) -> str:
    plt.figure(figsize=(6, 4))
    plt.plot(range(len(history)), history, marker="o", linewidth=1)
    plt.title(
        f"{name} - n={size}, seed={seed}\n"
        f"len={len(history)} | states={states} | time={elapsed:.3f}s"
    )
    plt.xlabel("Iteración")
    plt.ylabel("H(tablero)")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    filename = os.path.join(output_dir, f"{name}_n{size}_seed{seed}.png")
    plt.savefig(filename)
    plt.close()
    return filename


def main() -> None:
    parser = argparse.ArgumentParser(description="Graficar H() para una corrida de cada algoritmo")
    parser.add_argument("--size", type=int, default=8, help="Tamaño del tablero")
    parser.add_argument("--max-states", type=int, default=2000, help="Límite de estados para los algoritmos")
    parser.add_argument("--seed", type=int, default=1, help="Semilla para reproducibilidad")
    parser.add_argument("--population", type=int, default=100, help="Tamaño de población para GA")
    parser.add_argument("--generations", type=int, default=200, help="Límite de generaciones para GA")
    parser.add_argument("--mutation", type=float, default=0.25, help="Tasa de mutación para GA")
    parser.add_argument("--output", default="plots", help="Directorio de salida para las gráficas")
    parser.add_argument(
        "--combined",
        action="store_true",
        help="Generar una figura adicional con todas las curvas superpuestas",
    )
    args = parser.parse_args()

    if args.size < 0:
        raise ValueError("size debe ser no negativo")
    if args.max_states < 0:
        raise ValueError("max_states debe ser no negativo")
    if args.population <= 0:
        raise ValueError("population debe ser positivo")
    if args.generations < 0:
        raise ValueError("generations debe ser no negativo")

    os.makedirs(args.output, exist_ok=True)

    results = run_algorithms(
        size=args.size,
        max_states=args.max_states,
        seed=args.seed,
        population=args.population,
        generations=args.generations,
        mutation=args.mutation,
    )

    combined_fig = None
    combined_ax = None
    if args.combined:
        combined_fig, combined_ax = plt.subplots(figsize=(7, 5))
        combined_ax.set_title(f"Comparacion H() - n={args.size}, seed={args.seed}")
        combined_ax.set_xlabel("Iteración")
        combined_ax.set_ylabel("H(tablero)")
        combined_ax.grid(alpha=0.3)

    for name, (history, best, elapsed, states) in results.items():
        if not history:
            history = [0]
        filepath = plot_series(name, history, args.size, args.seed, best, elapsed, states, args.output)
        print(f"{name}: {filepath}")
        if args.combined and combined_ax is not None:
            combined_ax.plot(range(len(history)), history, marker="o", linewidth=1, label=name)

    if args.combined and combined_ax is not None:
        combined_ax.legend()
        combined_fig.tight_layout()
        combined_path = os.path.join(args.output, f"combined_n{args.size}_seed{args.seed}.png")
        combined_fig.savefig(combined_path)
        plt.close(combined_fig)
        print(f"combined: {combined_path}")


if __name__ == "__main__":
    main()
