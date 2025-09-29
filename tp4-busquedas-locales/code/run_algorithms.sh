#!/usr/bin/env bash
set -euo pipefail

MAX_STATES=${MAX_STATES:-5000}
OUTPUT_DIR=${OUTPUT_DIR:-results}
SIZES=${SIZES:-"4 8 10"}
SEED_COUNT=${SEED_COUNT:-30}

mkdir -p "$OUTPUT_DIR"

declare -A FILES=(
  [random]="random_results.csv"
  [HC]="hill_climbing_results.csv"
  [SA]="simulated_annealing_results.csv"
  [GA]="genetic_algorithm_results.csv"
)

for key in "${!FILES[@]}"; do
  file="$OUTPUT_DIR/${FILES[$key]}"
  echo "algorithm_name,env_n,size,best_solution,H,states,time" > "$file"
done

python3 - "$OUTPUT_DIR" "$MAX_STATES" "$SIZES" "$SEED_COUNT" <<'PYTHON'
import sys
import os
import csv
import time
import random
import reinas

output_dir = sys.argv[1]
max_states = int(sys.argv[2])
sizes = [int(x) for x in sys.argv[3].split()]
seed_count = int(sys.argv[4])

files = {
    'random': os.path.join(output_dir, 'random_results.csv'),
    'HC': os.path.join(output_dir, 'hill_climbing_results.csv'),
    'SA': os.path.join(output_dir, 'simulated_annealing_results.csv'),
    'GA': os.path.join(output_dir, 'genetic_algorithm_results.csv'),
}

handles = {name: open(path, 'a', newline='') for name, path in files.items()}
writers = {name: csv.writer(f) for name, f in handles.items()}

columns = [
    'algorithm_name',
    'env_n',
    'size',
    'best_solution',
    'H',
    'states',
    'time',
]

try:
    for size in sizes:
        for seed in range(1, seed_count + 1):
            start = time.perf_counter()
            best, h_value, states = reinas.random_search(size, max_states, seed=seed)
            elapsed = time.perf_counter() - start
            writers['random'].writerow(['random', seed, size, repr(best), h_value, states, f"{elapsed:.6f}"])

            start = time.perf_counter()
            best, h_value, states = reinas.hill_climbing(size, max_states, seed=seed)
            elapsed = time.perf_counter() - start
            writers['HC'].writerow(['HC', seed, size, repr(best), h_value, states, f"{elapsed:.6f}"])

            start = time.perf_counter()
            best, h_value, states = reinas.simulated_annealing(size, max_states, seed=seed)
            elapsed = time.perf_counter() - start
            writers['SA'].writerow(['SA', seed, size, repr(best), h_value, states, f"{elapsed:.6f}"])

            random_seed = seed
            random.seed(random_seed)
            tam_poblacion = 100
            limite_generaciones = max(1, max_states // tam_poblacion)
            start = time.perf_counter()
            best, h_value, states = reinas.genetic_algorithm(
                size,
                tam_poblacion=tam_poblacion,
                limite_generaciones=limite_generaciones,
                tasa_mutacion=0.25,
                seed=seed,
            )
            elapsed = time.perf_counter() - start
            writers['GA'].writerow(['GA', seed, size, repr(best), h_value, states, f"{elapsed:.6f}"])
finally:
    for f in handles.values():
        f.close()
PYTHON
