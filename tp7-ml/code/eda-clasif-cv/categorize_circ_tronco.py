#!/usr/bin/env python3
"""Add circ_tronco_cm_cat categorical column to the Mendoza tree dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create circ_tronco_cm_cat categories using predefined cut points."
    )
    parser.add_argument(
        "input_csv",
        type=Path,
        help="Path to arbolado-mendoza-dataset-train.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("arbolado-mendoza-dataset-circ_tronco_cm-train.csv"),
        help="Destination CSV path (default: arbolado-mendoza-dataset-circ_tronco_cm-train.csv).",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input_csv)
    circ = pd.to_numeric(df["circ_tronco_cm"], errors="coerce")
    conditions = [circ > 260, circ > 180, circ > 100]
    choices = ["muy alto", "alto", "medio"]
    df["circ_tronco_cm_cat"] = np.select(conditions, choices, default="bajo")

    df.to_csv(args.output, index=False)

    counts = df["circ_tronco_cm_cat"].value_counts().reindex(
        ["bajo", "medio", "alto", "muy alto"], fill_value=0
    )
    print("Distribución circ_tronco_cm_cat:")
    print(counts)
    print(f"\nArchivo guardado en: {args.output.resolve()}")


if __name__ == "__main__":
    main()

