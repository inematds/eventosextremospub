#!/usr/bin/env bash
# Termina a versão COM avatar de uma edição cujo card do HeyGen ficou Draft e o Nei gerou à mão no estúdio
# (Nei, 19/10/2026: "eu vou lá e resolvo; quando terminar você termina o vídeo").
# uso: auto/terminar-avatar.sh <pasta-da-edicao> <video_id>   → video-avatar.mp4 + bot v3 (não publica no YouTube)
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
ED="$(cd "$1" && pwd)"; ID="$2"
A="$ED/avatar"; PERFIL="$HOME/.cache/inemaccbot/perfil-heygen"; ENG="$HOME/projetos/explicavideos/engine"
BOT="$HOME/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs"
export DISPLAY="${DISPLAY:-:99}"
echo "$ID" > "$A/video_id.txt"
cd "$HOME/projetos/explicavideos"
[ -s "$A/avatar.mp4" ] || node "$ENG/heygen-estudio-baixar.mjs" --id "$ID" --saida "$A/avatar.mp4" \
    --perfil "$PERFIL" --minutos 290 --intervalo 120 > "$A/baixar.log" 2>&1 \
  || { node "$BOT" "$A/baixar.log" "🔴 Clima 24h $(basename "$ED"): o avatar $ID não baixou: $(tail -1 "$A/baixar.log" | cut -c1-200)"; exit 4; }
for k in 1 2 3; do python3 "$A/retempo.py" && break; [ $k = 3 ] && exit 6; sleep 60; done
python3 "$RAIZ/motor/pausa_pergunta.py" "$ED" --avatar
( cd "$ED" && python3 gerar_cena.py --canto )
V="$ED/video-avatar.mp4"
( cd "$RAIZ" && GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh "$ED" "$V" > "$ED/build-avatar.log" 2>&1 )
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V" | cut -d. -f1)
LUFS=$(ffmpeg -nostats -i "$V" -af ebur128 -f null - 2>&1 | grep -A1 Integrated | grep -o -- '-\?[0-9.]* LUFS' | tail -1)
rm -f "$V.envio-v3.json"
node "$BOT" "$V" "Clima 24h · $(basename "$ED") · ${DUR}s · $LUFS · versão COM avatar (rascunho gerado à mão pelo Nei). A versão mapa já está no lives10 ($(cat "$ED/youtube-lives10.txt" 2>/dev/null)); esta não foi publicada no YouTube.
$(head -1 "$ED/yt.txt")"
echo "Terminei: $V · ${DUR}s · $LUFS"
