#!/usr/bin/env bash
set -u  # no -e ni pipefail para no abortar todo el lote

PYTHON="python3"
SCRIPT="entorno.py"
OUT_CSV="resultados.csv"
FALLOS_LOG="fallos.log"

ITER=30       # 30 seeds
SIZE=16
P=0.92
TIMEOUT_CMD="timeout 15s"   # ajustá el límite si querés (p. ej. 5s/10s/30s)

# CSV requerido:
# algorithm_name,env_n,states_n,actions_count,actions_cost,time,solution_found
echo "algorithm_name,env_n,states_n,actions_count,actions_cost,time,solution_found" > "$OUT_CSV"
: > "$FALLOS_LOG"

write_error_row() {
  local alg_label="$1" seed="$2" motivo="$3"
  echo "\"$alg_label\",$seed,-1,-1,-1,-1.0,False" >> "$OUT_CSV"
  echo "[seed=$seed] $alg_label  -> $motivo" >> "$FALLOS_LOG"
}

run_and_capture() {
  local alg_label="$1" algoritmo="$2" seed="$3" scenario="$4" limite="${5:-}"

  local cmd=( "$PYTHON" "$SCRIPT"
              --algoritmo "$algoritmo"
              --size "$SIZE" --p "$P"
              --seed "$seed"
              --scenario "$scenario"
              --render "none" )
  [[ -n "$limite" ]] && cmd+=( --limite "$limite" )

  # Ejecutar con timeout y capturar stdout+stderr
  local out rc
  out="$($TIMEOUT_CMD "${cmd[@]}" 2>&1)"; rc=$?

  # rc 124/137 suelen indicar timeout o kill
  if [[ $rc -ne 0 ]]; then
    write_error_row "$alg_label" "$seed" "rc=$rc; cmd=${cmd[*]}; out=${out//$'\n'/\\n}"
    return
  fi

  # Buscar línea de métricas (tolerante a espacios y True/False)
  local metrics
  metrics="$(printf "%s\n" "$out" | grep -E '^[[:space:]]*[0-9]+[[:space:]]*,[[:space:]]*[0-9]+[[:space:]]*,[[:space:]]*[0-9]+[[:space:]]*,[[:space:]]*(True|False|true|false)[[:space:]]*$' | tail -n1)"

  if [[ -z "$metrics" ]]; then
    write_error_row "$alg_label" "$seed" "no se pudo parsear métricas; cmd=${cmd[*]}; out=${out//$'\n'/\\n}"
    return
  fi

  metrics="$(echo "$metrics" | tr -d '[:space:]')"
  IFS=',' read -r states_n actions_count actions_cost solution_found <<< "$metrics"

  # Tiempo (si no aparece, 0.0)
  local time_s
  time_s="$(printf "%s\n" "$out" | grep -E 'Tiempo de búsqueda:' | tail -n1 | sed -E 's/.*:\s*([0-9.]+)\s*s/\1/')" || true
  [[ -z "$time_s" ]] && time_s="0.0"

  echo "\"$alg_label\",$seed,$states_n,$actions_count,$actions_cost,$time_s,$solution_found" >> "$OUT_CSV"
}

for seed in $(seq 1 "$ITER"); do
  # Escenario 1
  run_and_capture "RANDOM"   "random" "$seed" 1
  run_and_capture "BFS"      "bfs"    "$seed" 1
  run_and_capture "DFS"      "dfs"    "$seed" 1
  run_and_capture "DLS(50)"  "dls"    "$seed" 1 50
  run_and_capture "DLS(75)"  "dls"    "$seed" 1 75
  run_and_capture "DLS(100)" "dls"    "$seed" 1 100
  run_and_capture "UCS[E1]"  "ucs"    "$seed" 1
  run_and_capture "A*[E1]"   "astar"  "$seed" 1

  # Escenario 2 (solo para UCS y A*)
  run_and_capture "UCS[E2]"  "ucs"    "$seed" 2
  run_and_capture "A*[E2]"   "astar"  "$seed" 2
done

echo "Listo. CSV: $OUT_CSV"
echo "Detalle de fallos (si los hubo): $FALLOS_LOG"
