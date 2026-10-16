#!/usr/bin/env bash
# Telas do vídeo de origem (Nei, 16/10/2026): o roteirista olha como o meteorologista apresentou (mapas, setas, áreas)
# para buscar imagens impactantes ou refazer parecido em 3D no nosso motor. As telas são só referência: nunca entram no vídeo.
# uso: auto/telas_fonte.sh <pasta fonte/>  (lê fonte/video_id.txt; fb:<id> = reel do Facebook) → fonte/telas/tela-NN.jpg
set -uo pipefail
F="$1"; N="${TELAS:-12}"; T="$F/telas"
ID=$(cat "$F/video_id.txt" 2>/dev/null) || { echo "sem video_id.txt"; exit 1; }
ls "$T"/tela-*.jpg >/dev/null 2>&1 && { echo "telas já tiradas"; exit 0; }
case "$ID" in fb:*) URL="https://www.facebook.com/reel/${ID#fb:}";; *) URL="https://www.youtube.com/watch?v=$ID";; esac
V="$F/video.mp4"
if [ ! -s "$V" ]; then
  for Q in 720p 480p best; do  # o YouTube às vezes dá 403 numa qualidade e não em outra
    ( cd "$HOME/projetos/inemavox" && rm -rf "$F/dl-telas" && timeout 1200 python3 baixar_v1.py --url "$URL" --outdir "$F/dl-telas" --quality "$Q" ) > "$F/telas-baixar.log" 2>&1
    V=$(ls -S "$F"/dl-telas/*.mp4 2>/dev/null | head -1); [ -n "$V" ] && break
  done
  [ -n "$V" ] || { echo "download das telas falhou: $(tail -1 "$F/telas-baixar.log")"; exit 1; }
fi
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V" | cut -d. -f1)
[ "${DUR:-0}" -gt 0 ] || { echo "duração inválida"; exit 1; }
mkdir -p "$T"
for k in $(seq 1 "$N"); do  # N telas espaçadas, pulando a abertura e o fecho
  S=$(( DUR * (2 * k - 1) / (2 * N) ))
  ffmpeg -v error -y -ss "$S" -i "$V" -frames:v 1 -vf "scale=960:-2" -q:v 4 "$T/$(printf 'tela-%02d' "$k").jpg"
  echo "tela-$(printf %02d "$k").jpg ${S}s" >> "$T/tempos.txt"
done
rm -rf "$F/dl-telas"
echo "telas: $(ls "$T"/tela-*.jpg | wc -l) em $T"
