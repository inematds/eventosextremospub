#!/usr/bin/env bash
# Micro clipe para o motor (Impacto Sul, Nei 07/11/2026: "imagens ou micro clipes ocupando a tela toda, e sobre ela os quadros de texto e o avatar").
# Corta um trecho de um vídeo, recorta só a área da filmagem (tira legenda, data e ícones queimados) e grava quadros 1080x1920 (cover).
# SOBE=<px> sobe o clipe em relação ao meio (padrão 120: a legenda e o avatar ficam embaixo)
# uso: motor/clip_quadros.sh <video.mp4> <início s> <duração s> <recorte w:h:x:y em px do vídeo, ou "-"> <pasta de saída> [fps=30]
# na cena: {"seq": sorted(glob("<pasta>/*.jpg")), "fps": 30, "ini": ..., "fim": ..., "zoom": .04}  (C.telas do gerar_cena.py)
set -euo pipefail
V="$1"; INI="$2"; DUR="$3"; CROP="$4"; OUT="$5"; FPS="${6:-30}"
mkdir -p "$OUT"; rm -f "$OUT"/*.jpg
# padrão: a área limpa costuma sair baixa (ex.: 576x350); ela ocupa a largura toda no meio e a mesma cena desfocada e ampliada
# preenche a tela atrás (nada de esticar e pixelar). CHEIO=1: cover direto (só quando o recorte já é alto, perto de 9:16).
C=""; [ "$CROP" != - ] && C="crop=$CROP,"
if [ "${CHEIO:-}" = 1 ]; then
  F="${C}scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=$FPS"
else
  F="${C}split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=28:2,eq=brightness=-0.12[f];[b]scale=1080:-2[c];[f][c]overlay=0:(H-h)/2-${SOBE:-120},fps=$FPS"
fi
ffmpeg -v error -y -ss "$INI" -t "$DUR" -i "$V" -filter_complex "$F" -q:v 3 "$OUT/%04d.jpg"
echo "$(ls "$OUT"/*.jpg | wc -l) quadros em $OUT"
