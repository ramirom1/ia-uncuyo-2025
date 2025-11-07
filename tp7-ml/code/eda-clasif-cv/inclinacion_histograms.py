#!/usr/bin/env python3
"""Generate histograms for inclinacion_peligrosa with configurable bins."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def parse_bins(value: str) -> List[int]:
    """Parse comma-separated integers into a list of positive bin counts."""
    if not value:
        raise argparse.ArgumentTypeError("Bins list cannot be empty.")
    try:
        bins = [int(part.strip()) for part in value.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Bins must be integers.") from exc
    if any(b <= 0 for b in bins):
        raise argparse.ArgumentTypeError("Bin counts must be positive integers.")
    return bins


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create histograms for inclinacion_peligrosa using multiple bin counts."
    )
    parser.add_argument(
        "csv_path",
        type=Path,
        help="Path to arbolado-mendoza-dataset-train.csv",
    )
    parser.add_argument(
        "--bins",
        type=parse_bins,
        default=[2, 5, 10],
        help="Comma separated list of bin counts (default: 2,5,10).",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("figuras"),
        help="Base directory to save the generated histograms.",
    )
    args = parser.parse_args()

    base_dir = args.out_dir
    out_dir = base_dir / "inclinacion_hist"
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.csv_path)
    inclinacion = pd.to_numeric(df["inclinacion_peligrosa"], errors="coerce").dropna()

    sns.set_theme(style="whitegrid")

    for bins in args.bins:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(inclinacion, bins=bins, color="#d62728", edgecolor="black")
        ax.set_xlabel("inclinacion_peligrosa")
        ax.set_ylabel("Frecuencia")
        ax.set_title(f"Histograma de inclinacion_peligrosa (bins = {bins})")
        fig.tight_layout()
        out_path = out_dir / f"inclinacion_hist_bins_{bins}.png"
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        print(f"Histograma guardado: {out_path.resolve()}")


if __name__ == "__main__":
    main()

