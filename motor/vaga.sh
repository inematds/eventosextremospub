#!/usr/bin/env bash
# Passo pesado na vaga da MÁQUINA (memória única CPU+GPU do spark-922b; fila-vaga em ~/projetos/wifi/scripts, 09/11/2026).
# uso: motor/vaga.sh <gpu|render> <motor>-<passo> comando...
#   Só o passo pesado (Whisper, voz local, render chromium/ffmpeg): nunca a rodada inteira, a espera do HeyGen, download ou claude -p.
#   Espera: <CLASSE>_ESPERA_MIN → FILA_ESPERA_MIN → 30 min (padrão daqui); estourou → sai 75 = máquina ocupada (não é erro de conteúdo).
#   Ordem entre classes: render → gpu (nunca segurar gpu e pedir render).
#   Sem a fila instalada (ex.: VPS6) roda o comando direto; com VAGA_SEM_FILA_LOCK=<arquivo>, faz flock nele nesse caso.
FILA="${VAGA_CMD:-$HOME/projetos/wifi/scripts/fila-vaga}"
[ $# -ge 3 ] || { echo "uso: vaga.sh <classe> <quem> comando..." >&2; exit 2; }
C="$1"; Q="$2"; shift 2
tem_fila() { [ -x "$FILA" ]; }
if tem_fila; then export FILA_ESPERA_MIN="${FILA_ESPERA_MIN:-30}"; exec "$FILA" "$C" "$Q" -- "$@"; fi
[ -n "${VAGA_SEM_FILA_LOCK:-}" ] && exec flock "$VAGA_SEM_FILA_LOCK" "$@"
exec "$@"
