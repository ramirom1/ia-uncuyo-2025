#!/usr/bin/env python3
"""Generate plots that explore inclinacion_peligrosa on the Mendoza tree dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create plots to inspect inclinacion_peligrosa distribution."
    )
    parser.add_argument(
        "csv_path",
        type=Path,
        help="Path to arbolado-mendoza-dataset-train.csv",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("figures"),
        help="Directory where plots and summaries will be stored.",
    )
    parser.add_argument(
        "--min-especie-count",
        type=int,
        default=50,
        help="Minimum number of registros for an especie to appear in plots.",
    )
    parser.add_argument(
        "--top-secciones",
        type=int,
        default=15,
        help="Number of secciones with most registros to display.",
    )
    args = parser.parse_args()

    sns.set_theme(style="whitegrid")

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.csv_path)
    df["inclinacion_peligrosa"] = df["inclinacion_peligrosa"].fillna(0).astype(int)

    overall_counts = (
        df["inclinacion_peligrosa"].value_counts().sort_index().rename_axis("clase")
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    palette = sns.color_palette("viridis", len(overall_counts))
    ax.bar(range(len(overall_counts)), overall_counts.values, color=palette)
    ax.set_xticks(range(len(overall_counts)))
    ax.set_xticklabels(overall_counts.index)
    ax.set_xlabel("inclinacion_peligrosa")
    ax.set_ylabel("Cantidad de registros")
    for x, val in enumerate(overall_counts.values):
        ax.text(x, val, f"{val:,}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    overall_path = out_dir / "inclinacion_distribution.png"
    fig.savefig(overall_path, dpi=150)
    plt.close(fig)

    section_summary = (
        df.groupby("nombre_seccion")["inclinacion_peligrosa"]
        .agg(["count", "sum", "mean"])
        .rename(columns={"count": "total", "sum": "peligrosos", "mean": "tasa"})
        .sort_values("tasa", ascending=False)
    )
    section_summary.to_csv(out_dir / "seccion_inclinacion_summary.csv")

    top_sections = (
        df["nombre_seccion"]
        .value_counts()
        .nlargest(args.top_secciones)
        .index.tolist()
    )
    section_plot = section_summary.loc[top_sections].sort_values("tasa", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = sns.color_palette("rocket", len(section_plot))
    ax.bar(range(len(section_plot)), section_plot["tasa"], color=colors)
    ax.set_xticks(range(len(section_plot)))
    ax.set_xticklabels(section_plot.index, rotation=45, ha="right")
    ax.set_xlabel("nombre_seccion")
    ax.set_ylabel("Tasa de inclinacion_peligrosa")
    ax.set_title(
        f"Tasa de inclinacion_peligrosa por sección (top {args.top_secciones} por tamaño)"
    )
    for idx, (name, row) in enumerate(section_plot.iterrows()):
        ax.text(
            idx,
            row["tasa"],
            f"{row['tasa']:.2%}\n(n={row['total']})",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    fig.tight_layout()
    section_plot_path = out_dir / "inclinacion_por_seccion.png"
    fig.savefig(section_plot_path, dpi=150)
    plt.close(fig)

    especie_summary = (
        df.groupby("especie")["inclinacion_peligrosa"]
        .agg(["count", "sum", "mean"])
        .rename(columns={"count": "total", "sum": "peligrosos", "mean": "tasa"})
    )
    especie_summary = especie_summary[especie_summary["total"] >= args.min_especie_count]
    especie_summary = especie_summary.sort_values("tasa", ascending=False)
    especie_summary.to_csv(out_dir / "especie_inclinacion_summary.csv")

    top_especies = especie_summary.nlargest(15, columns="tasa")
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = sns.color_palette("mako", len(top_especies))
    ax.bar(range(len(top_especies)), top_especies["tasa"], color=colors)
    ax.set_xticks(range(len(top_especies)))
    ax.set_xticklabels(top_especies.index, rotation=45, ha="right")
    ax.set_xlabel("especie")
    ax.set_ylabel("Tasa de inclinacion_peligrosa")
    ax.set_title("Especies con mayor tasa de inclinacion_peligrosa")
    for idx, (name, row) in enumerate(top_especies.iterrows()):
        ax.text(
            idx,
            row["tasa"],
            f"{row['tasa']:.2%}\n(n={row['total']})",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    fig.tight_layout()
    especie_plot_path = out_dir / "inclinacion_por_especie.png"
    fig.savefig(especie_plot_path, dpi=150)
    plt.close(fig)

    print("Distribución general:")
    print(overall_counts)
    print("\nSecciones más riesgosas (tasa, total, peligrosos):")
    print(section_summary.head(10))
    print("\nEspecies más riesgosas (filtrado por mínimo de registros):")
    print(especie_summary.head(10))

    print(f"\nGráficos guardados en: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
