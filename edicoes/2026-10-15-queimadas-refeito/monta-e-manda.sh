#!/usr/bin/env bash
# Queimadas 16:9 REFEITO em 3D (15/10/2026) com o avatar já gravado: monta e manda ao bot v3 (720p), sem YouTube.

# uso: systemd-run --user --unit=queimadas-refeito bash <este arquivo>   · estado em AVATAR-STATUS.txt
set -uo pipefail
export PATH="$HOME/.npm-global/bin:$PATH"
RAIZ="$HOME/projetos/eventosextremospub"
E="$RAIZ/edicoes/2026-10-15-queimadas-refeito"
ST="$E/AVATAR-STATUS.txt"; BOT="$HOME/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs"
log(){ echo "$(date '+%F %T') $*" >> "$ST"; }
log "início"

[ -s "$E/avatar/tempos.json" ] && [ -s "$E/avatar/avatar.mp4" ] || { log "FALHOU avatar ($(tail -2 "$E/avatar.log" | tr '\n' ' '))"; exit 1; }
log "avatar ok ($(cat "$E/avatar/video_id.txt"))"
( cd "$E" && python3 gerar_cena.py --avatar ) >> "$E/avatar.log" 2>&1 || { log "FALHOU gerar_cena"; exit 1; }
( cd "$RAIZ" && flock "$RAIZ/.render.lock" env DISPLAY=:99 GEO=geo-br.js LAYOUT=largo motor/compor_avatar.sh "$E" "$E/video-avatar.mp4" ) > "$E/build-avatar.log" 2>&1 || { log "FALHOU compor"; exit 1; }
# guarda: render concorrente na GPU já deixou o mapa todo branco (15/10/2026) → confere o brilho de 3 quadros e refaz uma vez
branco(){ for t in 10 30 50; do ffmpeg -v error -y -ss $t -i "$E/video-avatar.mp4" -frames:v 1 -vf "crop=1200:800:0:150,scale=64:64,format=gray" -f rawvideo - | python3 -c "import sys;b=sys.stdin.buffer.read();sys.exit(0 if sum(b)/len(b)>200 else 1)" && return 0; done; return 1; }
if branco; then log "mapa branco no render, refazendo"; ( cd "$RAIZ" && flock "$RAIZ/.render.lock" env DISPLAY=:99 GEO=geo-br.js LAYOUT=largo motor/compor_avatar.sh "$E" "$E/video-avatar.mp4" ) > "$E/build-avatar.log" 2>&1 || { log "FALHOU compor 2"; exit 1; }
  branco && { log "FALHOU mapa branco de novo"; exit 1; }; fi
I=$(ffmpeg -nostats -i "$E/video-avatar.mp4" -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1 | awk '{print $2}')
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$E/video-avatar.mp4" | cut -d. -f1)
log "video-avatar.mp4 pronto (${D}s, ${I} LUFS)"
V="$E/video-avatar-bot.mp4"; ffmpeg -v error -y -i "$E/video-avatar.mp4" -vf scale=1280:720 -c:v libx264 -crf 26 -maxrate 2M -bufsize 4M -c:a copy -movflags +faststart "$V"   # 720p para o bot (limite 49 MB)
rm -f "$V.envio-v3.json"
node "$BOT" "$V" "Queimadas na Amazônia · 16:9 REFEITO em 3D com o avatar anterior · ${D}s · com avatar · NÃO publicado, para aprovação" >> "$E/avatar.log" 2>&1 \
  && log "bot v3 msg $(python3 -c "import json;print(json.load(open('$V.envio-v3.json'))['message_id'])")" || log "FALHOU bot v3"
log "fim"
