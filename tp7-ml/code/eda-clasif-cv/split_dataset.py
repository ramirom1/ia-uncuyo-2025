#!/usr/bin/env python3
"""Split a CSV into train and validation subsets keeping the header."""

from __future__ import annotations

import argparse
import random
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Randomly split a CSV into train/validation files with uniform sampling."
    )
    parser.add_argument(
        "input_csv",
        type=Path,
        help="Source CSV file (e.g., arbolado-mza-dataset.csv).",
    )
    parser.add_argument(
        "--val-output",
        type=Path,
        default=Path("arbolado-mendoza-dataset-validation.csv"),
        help="Validation CSV output path (default: arbolado-mendoza-dataset-validation.csv).",
    )
    parser.add_argument(
        "--train-output",
        type=Path,
        default=Path("arbolado-mendoza-dataset-train.csv"),
        help="Train CSV output path (default: arbolado-mendoza-dataset-train.csv).",
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.2,
        help="Fraction of rows to assign to validation (default: 0.2).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible shuffling (default: None).",
    )
    args = parser.parse_args()

    if not 0 < args.val_ratio < 1:
        raise ValueError("val_ratio must be between 0 and 1.")

    rng = random.Random(args.seed)

    with args.input_csv.open("r", encoding="utf-8") as f:
        header = f.readline()
        rows = f.readlines()

    rng.shuffle(rows)

    split_index = int(len(rows) * args.val_ratio)
    val_rows = rows[:split_index]
    train_rows = rows[split_index:]

    for path, data in (
        (args.val_output, val_rows),
        (args.train_output, train_rows),
    ):
        with path.open("w", encoding="utf-8") as f:
            f.write(header)
            f.writelines(data)

    print(f"Total registros: {len(rows)} (sin contar cabecera)")
    print(f"Validación: {len(val_rows)} -> {args.val_output}")
    print(f"Entrenamiento: {len(train_rows)} -> {args.train_output}")


if __name__ == "__main__":
    main()

