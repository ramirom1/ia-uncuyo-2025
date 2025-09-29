# -*- coding: utf-8 -*-
"""
analyze_results_grouped.py

Agrega métricas agrupadas por (algorithm_name, size), promediando sobre las ejecuciones de cada caso.

Entrada esperada (flexible en nombres):
  algorithm_name, env_n, size, H, states, time

Salida:
  - outputs/summary_metrics.csv (global)
  - outputs/percent_optimal_by_algorithm.csv (global por algoritmo)
  - outputs/grouped_metrics.csv (por algorithm_name, size)
  - outputs/box_time_optimos.png
  - outputs/box_estados_optimos.png
  - outputs/box_h.png
  - outputs/reporte.txt
"""
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from textwrap import dedent

def pick_col(df, candidates, required=False):
    lowered = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lowered:
            return lowered[cand.lower()]
    if required:
        raise KeyError(f"No se encontró ninguna de estas columnas: {candidates}")
    return None

def save_boxplot_series(series, title, ylabel, fname, rotation=45):
    if series.empty:
        return None
    plt.figure()
    data = list(series.values)
    labels = list(series.index.astype(str))
    plt.boxplot(data, labels=labels)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(rotation=rotation)
    out = Path(fname)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    return out

def grouped_metrics(df, col_alg, col_size, col_h, col_states, col_time, optimal_h_value):
    df = df.copy()
    df["is_optimal"] = df[col_h] == optimal_h_value

    # Funciones seguras para stats en subconjuntos (p.ej., solo óptimos)
    def mean_opt(sub):
        s = sub.loc[sub["is_optimal"], col_time]
        return s.mean() if len(s) else np.nan

    def std_opt(sub):
        s = sub.loc[sub["is_optimal"], col_time]
        return s.std(ddof=1) if len(s) > 1 else np.nan

    def mean_states_opt(sub):
        s = sub.loc[sub["is_optimal"], col_states]
        return s.mean() if len(s) else np.nan

    def std_states_opt(sub):
        s = sub.loc[sub["is_optimal"], col_states]
        return s.std(ddof=1) if len(s) > 1 else np.nan

    g = df.groupby([col_alg, col_size], dropna=False)
    out = g.apply(lambda sub: pd.Series({
        "n_runs": len(sub),
        "pct_optimal": 100.0 * sub["is_optimal"].mean(),
        "h_mean": sub[col_h].mean(),
        "h_std": sub[col_h].std(ddof=1) if len(sub) > 1 else np.nan,
        "time_opt_mean": mean_opt(sub),
        "time_opt_std": std_opt(sub),
        "states_opt_mean": mean_states_opt(sub),
        "states_opt_std": std_states_opt(sub),
    })).reset_index()

    # Orden de columnas amigable
    cols = [col_alg, col_size, "n_runs", "pct_optimal", "h_mean", "h_std",
            "time_opt_mean", "time_opt_std", "states_opt_mean", "states_opt_std"]
    return out[cols]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, default="results.csv", help="Ruta al CSV de entrada")
    parser.add_argument("--outdir", type=str, default="outputs", help="Directorio de salida")
    parser.add_argument("--optimal-h-value", type=float, default=0.0,
                        help="Valor de H considerado como óptimo (default: 0)")
    args = parser.parse_args()

    data_path = Path(args.csv)
    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path)

    # Column mapping
    col_algorithm = pick_col(df, ["algorithm_name", "algorithm", "alg", "name"], required=True)
    col_env       = pick_col(df, ["env_n", "env", "seed", "map"], required=False)
    col_size      = pick_col(df, ["size", "n", "problem_size", "board"], required=True)
    col_states    = pick_col(df, ["states", "states_n", "states_count", "visited_states"], required=True)
    col_time      = pick_col(df, ["time", "runtime", "seconds", "exec_time"], required=True)
    col_h         = pick_col(df, ["H", "h", "heuristic", "heuristic_value"], required=True)

    # Global quick stats (como en el script anterior)
    df["is_optimal"] = df[col_h] == args.optimal_h_value
    pct_opt_overall = 100.0 * df["is_optimal"].mean() if len(df) else np.nan
    pct_opt_by_alg = (
        df.groupby(col_algorithm)["is_optimal"].mean().mul(100.0).rename("pct_optimal").reset_index()
    )
    h_mean = df[col_h].mean() if len(df) else np.nan
    h_std  = df[col_h].std(ddof=1) if len(df) > 1 else np.nan
    time_opt = df[df["is_optimal"]][col_time]
    time_opt_mean = time_opt.mean() if len(time_opt) else np.nan
    time_opt_std  = time_opt.std(ddof=1) if len(time_opt) > 1 else np.nan
    states_opt = df[df["is_optimal"]][col_states]
    states_opt_mean = states_opt.mean() if len(states_opt) else np.nan
    states_opt_std  = states_opt.std(ddof=1) if len(states_opt) > 1 else np.nan

    summary_df = pd.DataFrame({
        "metric": [
            "Pct óptimo (global)",
            "H (mean)",
            "H (std)",
            "Tiempo óptimo (mean)",
            "Tiempo óptimo (std)",
            "Estados óptimo (mean)",
            "Estados óptimo (std)",
        ],
        "value": [
            pct_opt_overall,
            h_mean,
            h_std,
            time_opt_mean,
            time_opt_std,
            states_opt_mean,
            states_opt_std,
        ]
    })
    summary_df.to_csv(out_dir / "summary_metrics.csv", index=False)
    pct_opt_by_alg.to_csv(out_dir / "percent_optimal_by_algorithm.csv", index=False)

    # Grouped metrics (algorithm, size)
    grouped_df = grouped_metrics(df, col_algorithm, col_size, col_h, col_states, col_time, args.optimal_h_value)
    grouped_df.to_csv(out_dir / "grouped_metrics.csv", index=False)

    # Plots (usamos las mismas reglas)
    if df["is_optimal"].any():
        ser_time = df[df["is_optimal"]].groupby(col_algorithm)[col_time].apply(list)
        _ = save_boxplot_series(ser_time, "Tiempo (óptimos) por algoritmo", "segundos", out_dir / "box_time_optimos.png")
        ser_states = df[df["is_optimal"]].groupby(col_algorithm)[col_states].apply(list)
        _ = save_boxplot_series(ser_states, "Estados (óptimos) por algoritmo", "cantidad de estados", out_dir / "box_estados_optimos.png")
    ser_h = df.groupby(col_algorithm)[col_h].apply(list)
    _ = save_boxplot_series(ser_h, "Heurística H por algoritmo", "H", out_dir / "box_h.png")

    # Reporte corto
    with open(out_dir / "reporte.txt", "w", encoding="utf-8") as f:
        f.write(dedent(f"""
        Resultados basados en {data_path.name}
        Definición de óptimo: H == {args.optimal_h_value}

        (i) % óptimo global: {pct_opt_overall:.2f}%
        (ii) H mean/std: {h_mean} / {h_std}
        (iii) Tiempo óptimo mean/std: {time_opt_mean} / {time_opt_std}
        (iv) Estados óptimo mean/std: {states_opt_mean} / {states_opt_std}

        Métricas agrupadas por algoritmo y size en: grouped_metrics.csv
        """).strip())

    print("OK. Salida en:", out_dir.resolve())

if __name__ == "__main__":
    main()
