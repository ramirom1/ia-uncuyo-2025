"""Run N-Queens CSP experiments and collect metrics."""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from nqueens_csp import (
    SolverMetrics,
    solve_n_queens_backtracking_metrics,
    solve_n_queens_forward_checking_metrics,
)

DEFAULT_BOARD_SIZES: Sequence[int] = (4, 8, 10)
SEEDS: Iterable[int] = range(30)
RESULTS_DIR = Path(__file__).parent / "results"


def _ensure_results_dir() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run N-Queens CSP experiments and export metrics."
    )
    parser.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=None,
        help="Board sizes to evaluate (default: 4 8 10).",
    )
    return parser.parse_args(args=argv)


def _run_algorithm(
    name: str,
    solver,
    board_sizes: Sequence[int],
) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    for n in board_sizes:
        for seed in SEEDS:
            metrics: SolverMetrics = solver(n, max_solutions=1, seed=seed)
            records.append(
                {
                    "algorithm": name,
                    "n": n,
                    "seed": seed,
                    "found_solution": metrics.success,
                    "time_milliseconds": round(metrics.time_seconds * 1000, 6),
                    "nodes_explored": metrics.nodes_explored,
                }
            )
    return records


def _write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    fieldnames = [
        "algorithm",
        "n",
        "seed",
        "found_solution",
        "time_milliseconds",
        "nodes_explored",
    ]
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _stats_for_records(
    records: List[Dict[str, object]], board_sizes: Sequence[int]
) -> Dict[int, Dict[str, float]]:
    stats: Dict[int, Dict[str, float]] = {}
    for n in board_sizes:
        subset = [r for r in records if r["n"] == n]
        total = len(subset)
        successes = [r for r in subset if r["found_solution"]]
        success_pct = 100.0 * len(successes) / total if total else 0.0
        if successes:
            times = [float(r["time_milliseconds"]) for r in successes]
            nodes = [int(r["nodes_explored"]) for r in successes]
            avg_time = statistics.mean(times)
            std_time = statistics.stdev(times) if len(times) > 1 else 0.0
            avg_nodes = statistics.mean(nodes)
            std_nodes = statistics.stdev(nodes) if len(nodes) > 1 else 0.0
        else:
            avg_time = std_time = avg_nodes = std_nodes = 0.0
        stats[n] = {
            "success_pct": success_pct,
            "avg_time": avg_time,
            "std_time": std_time,
            "avg_nodes": avg_nodes,
            "std_nodes": std_nodes,
        }
    return stats


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    board_sizes = tuple(args.sizes) if args.sizes else tuple(DEFAULT_BOARD_SIZES)

    _ensure_results_dir()
    algorithms = {
        "backtracking": solve_n_queens_backtracking_metrics,
        "forward_checking": solve_n_queens_forward_checking_metrics,
    }

    for name, solver in algorithms.items():
        records = _run_algorithm(name, solver, board_sizes)
        csv_path = RESULTS_DIR / f"{name}_results.csv"
        _write_csv(csv_path, records)

        stats = _stats_for_records(records, board_sizes)
        print(f"Algorithm: {name}")
        for n, values in stats.items():
            print(
                f"  n={n}: success={values['success_pct']:.1f}% | "
                f"time={values['avg_time']:.6f}ms ± {values['std_time']:.6f}ms | "
                f"nodes={values['avg_nodes']:.1f} ± {values['std_nodes']:.1f}"
            )
        print(f"  Results saved to: {csv_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
