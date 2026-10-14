#!/usr/bin/env bash
# Prévia com FOTO do avatar (Nei, 13/10/2026: "manda o vídeo feito com uma imagem do avatar enquanto ele está sendo feito").
# Monta o layout canto com um quadro parado de um avatar anterior + a narração local (voz do Nei, Chatterbox),
# numa subpasta previa/ (não toca em avatar/, senão o avatar.sh acharia o avatar.mp4 e pularia o download).
# uso: auto/previa.sh <pasta-da-edicao>   -> <ed>/video-previa.mp4
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
E="$(cd "$1" && pwd)"; P="$E/previa"
rm -rf "$P"; mkdir -p "$P/avatar"
for f in "$E"/*; do n=$(basename "$f"); case "$n" in previa|avatar|build|cena.js|gerar_cena.py|video*) ;; *) ln -s "$f" "$P/$n" ;; esac; done
cp "$E/gerar_cena.py" "$P/"; cp "$E/tempos.json" "$P/avatar/tempos.json"
# quadro parado: o avatar mais recente já baixado (TEMPLATE-AVATAR16, 1920x1080)
SRC=$(ls -t "$RAIZ"/edicoes/*/avatar/avatar.mp4 | grep -v "^$E/" | head -1)
ffmpeg -v error -y -ss 4 -i "$SRC" -frames:v 1 "$P/avatar/foto.png"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$E/narracao.wav")
ffmpeg -v error -y -loop 1 -framerate 30 -i "$P/avatar/foto.png" -i "$E/narracao.wav" -t "$D" \
  -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k "$P/avatar/avatar.mp4"
( cd "$P" && python3 gerar_cena.py --canto )
( cd "$RAIZ" && GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh "$P" "$E/video-previa.mp4" )
