#!/usr/bin/env bash
# A semana no mundo: espera o serviço semana-avatar terminar, monta o 16:9 com avatar e manda ao bot v3. NÃO publica no YouTube.
set -uo pipefail
export PATH="$HOME/.npm-global/bin:$PATH"
RAIZ="$HOME/projetos/eventosextremospub"; E="$RAIZ/edicoes/2026-10-13-semana-mundo"; ST="$E/AVATAR-STATUS.txt"
log(){ echo "$(date '+%F %T') $*" >> "$ST"; }
while systemctl --user is-active -q semana-avatar; do sleep 60; done
[ -s "$E/avatar/avatar.mp4" ] && [ -s "$E/avatar/tempos.json" ] || { log "SEM avatar: fica o video.mp4 sem avatar"; exit 1; }
( cd "$E" && python3 gerar_cena.py --avatar ) >> "$E/build-avatar.log" 2>&1 || { log "FALHOU gerar_cena --avatar"; exit 1; }
( cd "$RAIZ" && GEO=geo-br.js LAYOUT=largo motor/compor_avatar.sh "$E" "$E/video-avatar.mp4" ) >> "$E/build-avatar.log" 2>&1 || { log "FALHOU compor"; exit 1; }
I=$(ffmpeg -nostats -i "$E/video-avatar.mp4" -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1 | awk '{print $2}')
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$E/video-avatar.mp4" | cut -d. -f1)
log "video-avatar.mp4 pronto (${D}s, ${I} LUFS)"
ffmpeg -v error -y -i "$E/video-avatar.mp4" -vf scale=1280:720 -c:v libx264 -crf 26 -preset medium -c:a copy -movflags +faststart "$E/video-avatar-bot.mp4"
node "$HOME/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs" "$E/video-avatar-bot.mp4" "A semana no mundo (06 a 13/10) · 16:9 (720p) · ${D}s · com avatar" >> "$E/build-avatar.log" 2>&1 \
  && log "bot v3 msg $(python3 -c "import json;print(json.load(open('$E/video-avatar-bot.mp4.envio-v3.json'))['message_id'])")" || log "FALHOU bot v3"
