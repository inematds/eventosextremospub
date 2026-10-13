#!/usr/bin/env bash
# O clima no mundo (16:9): o estúdio recusou o envio 4× (21:03–21:18, fila cheia com os 4 reels r7e).
# Espera os avatares dos reels chegarem, tenta de novo até 3× (20 min entre elas), monta com avatar e manda ao bot v3.
# NÃO publica no YouTube. uso: systemd-run --user --unit=mundo-avatar-depois --setenv=PATH="$PATH" --setenv=DISPLAY=:99 bash <este>
set -uo pipefail
export PATH="$HOME/.npm-global/bin:$PATH"
RAIZ="$HOME/projetos/eventosextremospub"; E="$RAIZ/edicoes/2026-10-12-mundo-clima"; R7="$HOME/projetos/reel7etapas/edicoes"
ST="$E/AVATAR-STATUS.txt"; log(){ echo "$(date '+%F %T') $*" >> "$ST"; }
log "esperando os avatares dos 4 reels"
for k in $(seq 1 180); do   # até 6 h
  n=0; for s in tailandia japao furacoes planeta; do [ -s "$R7/2026-10-12-clima-$s/avatar/avatar.mp4" ] && n=$((n+1)); done
  [ $n -ge 4 ] && break; sleep 120
done
log "reels com avatar: $n/4; tentando o 16:9"
for t in 1 2 3; do
  rm -f "$E/avatar/studio.log"
  bash "$RAIZ/auto/avatar.sh" "$E" "EVX-mundo-clima-t$t" > "$E/avatar.log" 2>&1 && { log "avatar ok (tentativa $t, $(cat "$E/avatar/video_id.txt"))"; break; }
  log "tentativa $t falhou: $(grep -h ERRO "$E/avatar.log" | tail -1 | cut -c1-120)"; [ $t -lt 3 ] && sleep 1200
done
[ -s "$E/avatar/avatar.mp4" ] || { log "SEM avatar: fica a versão sem avatar (video.mp4)"; exit 1; }
( cd "$E" && python3 gerar_cena.py --avatar ) >> "$E/avatar.log" 2>&1 || { log "FALHOU gerar_cena --avatar"; exit 1; }
( cd "$RAIZ" && GEO=geo-br.js LAYOUT=largo motor/compor_avatar.sh "$E" "$E/video-avatar.mp4" ) > "$E/build-avatar.log" 2>&1 || { log "FALHOU compor"; exit 1; }
I=$(ffmpeg -nostats -i "$E/video-avatar.mp4" -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1 | awk '{print $2}')
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$E/video-avatar.mp4" | cut -d. -f1)
log "video-avatar.mp4 pronto (${D}s, ${I} LUFS)"
ffmpeg -v error -y -i "$E/video-avatar.mp4" -vf scale=1280:720 -c:v libx264 -crf 26 -preset medium -c:a copy -movflags +faststart "$E/video-avatar-bot.mp4"
rm -f "$E/video-avatar-bot.mp4.envio-v3.json"
node "$HOME/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs" "$E/video-avatar-bot.mp4" "O clima no mundo · 16:9 (720p) · ${D}s · com avatar" >> "$E/avatar.log" 2>&1 \
  && log "bot v3 msg $(python3 -c "import json;print(json.load(open('$E/video-avatar-bot.mp4.envio-v3.json'))['message_id'])")" || log "FALHOU bot v3"
