#!/usr/bin/env bash
# Renderiza o mapa da edição e mistura narração + trilha.  uso: motor/montar.sh <pasta-da-edicao> [saida.mp4]
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
E="$(cd "$1" && pwd)"; SAIDA="${2:-$E/video.mp4}"
MUSICA="${MUSICA:-$HOME/projetos/cardshorts/musicas/tensa.mp3}"
# Render na vaga render da MÁQUINA (motor/vaga.sh → ~/projetos/wifi/scripts/fila-vaga, 09/11/2026): o script inteiro (chromium + ffmpeg)
# entra na vaga; já dentro dela (RENDER_FILA_DONO) roda direto. Espera RENDER_ESPERA_MIN (20 min: o claude -p roda o montar com
# timeout de 50 min); estourou → sai 75 = máquina ocupada. Sem a fila instalada (VPS6) vale o .render.lock de antes.
VAGA="$AQUI/../motor/vaga.sh"
if [ -z "${RENDER_FILA_DONO:-}" ] && [ -x "${VAGA_CMD:-$HOME/projetos/wifi/scripts/fila-vaga}" ]; then
  RENDER_ESPERA_MIN="${RENDER_ESPERA_MIN:-20}" exec bash "$VAGA" render "eventosextremospub-$(basename "$AQUI")-mapa" bash "$0" "$@"
fi
rlock() { if [ -n "${RENDER_FILA_DONO:-}" ]; then "$@"; else flock "$AQUI/../.render.lock" "$@"; fi; }
mkdir -p "$E/build"
rlock node "$AQUI/render.mjs" "$E" "$E/build/mapa.mp4"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$E/narracao.wav")
FADE=$(python3 -c "print(max(0, $D - 1.4))")
ffmpeg -v error -y -i "$E/build/mapa.mp4" -i "$E/narracao.wav" -stream_loop -1 -i "$MUSICA" -filter_complex \
  "[1:a]aresample=48000,asplit=2[v][sc];[2:a]volume=0.22,aresample=48000[m];[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[md];[v][md]amix=inputs=2:duration=first:normalize=0,afade=t=out:st=$FADE:d=1.4[a]" \
  -map 0:v -map "[a]" -c:v libx264 -crf 23 -preset slow -maxrate 4M -bufsize 8M -c:a aac -b:a 192k -movflags +faststart -shortest "$SAIDA"
echo "ok $SAIDA ($(du -h "$SAIDA" | cut -f1))"
