"""Generate boxplots for N-Queens CSP experiment metrics."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import matplotlib.pyplot as plt

RESULTS_DIR = Path(__file__).parent / "results"
RESULT_FILES = {
    "backtracking": RESULTS_DIR / "backtracking_results.csv",
    "forward_checking": RESULTS_DIR / "forward_checking_results.csv",
}


def _load_metric_data() -> Tuple[
    Dict[str, Dict[int, List[float]]], Dict[str, Dict[int, List[float]]]
]:
    """Load execution time (ms) and nodes explored grouped by algorithm and board size."""
    time_data: Dict[str, Dict[int, List[float]]] = defaultdict(lambda: defaultdict(list))
    node_data: Dict[str, Dict[int, List[float]]] = defaultdict(lambda: defaultdict(list))

    for algorithm, path in RESULT_FILES.items():
        if not path.exists():
            raise FileNotFoundError(
                f"Expected results file not found for {algorithm}: {path}"
            )
        with path.open("r", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                n = int(row["n"])
                time_ms = float(row["time_milliseconds"])
                nodes = int(row["nodes_explored"])
                time_data[algorithm][n].append(time_ms)
                node_data[algorithm][n].append(float(nodes))
    return time_data, node_data


def _create_boxplots(
    metric_data: Dict[str, Dict[int, List[float]]],
    ylabel: str,
    output_name: str,
    selected_ns: Optional[Iterable[int]] = None,
    title_suffix: str = "",
) -> Optional[Path]:
    filtered: Dict[str, Dict[int, List[float]]] = {}
    selected_set = set(selected_ns) if selected_ns is not None else None

    for algorithm, per_n in metric_data.items():
        ns = sorted(per_n.keys())
        if selected_set is not None:
            ns = [n for n in ns if n in selected_set]
        if not ns:
            continue
        filtered[algorithm] = {n: per_n[n] for n in ns}

    if not filtered:
        return None

    algorithms = sorted(filtered.keys())

    fig, axes = plt.subplots(
        1, len(algorithms), figsize=(5 * len(algorithms), 5), sharey=True
    )
    if len(algorithms) == 1:
        axes = [axes]  # ensure iterable

    for ax, algorithm in zip(axes, algorithms):
        per_n = filtered[algorithm]
        ns = sorted(per_n.keys())
        data = [per_n[n] for n in ns]
        ax.boxplot(data, labels=[str(n) for n in ns], showmeans=True)
        ax.set_title(algorithm.replace("_", " ").title())
        ax.set_xlabel("n")
        ax.set_ylabel(ylabel)

    fig.suptitle(f"Distribución de {ylabel.lower()} por algoritmo{title_suffix}")
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    output_path = RESULTS_DIR / output_name
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def main() -> None:
    time_data, node_data = _load_metric_data()

    generated: List[Path] = []
    for data, ylabel, base_name in [
        (time_data, "Tiempo de ejecución (ms)", "time"),
        (node_data, "Nodos explorados", "nodes"),
    ]:
        path_all = _create_boxplots(data, ylabel, f"{base_name}_boxplots.png")
        if path_all:
            generated.append(path_all)
        path_small = _create_boxplots(
            data,
            ylabel,
            f"{base_name}_boxplots_small.png",
            selected_ns=[2, 4],
            title_suffix=" (n = 2, 4)",
        )
        if path_small:
            generated.append(path_small)
        path_medium = _create_boxplots(
            data,
            ylabel,
            f"{base_name}_boxplots_medium.png",
            selected_ns=[8],
            title_suffix=" (n = 8)",
        )
        if path_medium:
            generated.append(path_medium)
        path_large = _create_boxplots(
            data,
            ylabel,
            f"{base_name}_boxplots_large.png",
            selected_ns=[10],
            title_suffix=" (n = 10)",
        )
        if path_large:
            generated.append(path_large)

    if generated:
        print("Gráficos guardados en:")
        for path in generated:
            print(f"  - {path}")


if __name__ == "__main__":
    main()
