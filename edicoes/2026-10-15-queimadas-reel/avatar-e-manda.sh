#!/usr/bin/env bash
# Queimadas 9:16 3D (15/10/2026): espera o avatar do Nei (estúdio HeyGen, unidade queimadas-reel-avatar), monta o reel
# com layout canto, mede o volume e manda o arquivo ao bot v3. NÃO publica no YouTube (Nei: "faça primeiro ... e me manda").
# uso: systemd-run --user --unit=queimadas-reel-manda bash <este arquivo>   · estado em AVATAR-STATUS.txt
set -uo pipefail
export PATH="$HOME/.npm-global/bin:$PATH"
RAIZ="$HOME/projetos/eventosextremospub"
E="$RAIZ/edicoes/2026-10-15-queimadas-reel"
ST="$E/AVATAR-STATUS.txt"; BOT="$HOME/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs"
log(){ echo "$(date '+%F %T') $*" >> "$ST"; }
log "início"
while systemctl --user is-active -q queimadas-reel-avatar; do sleep 60; done
[ -s "$E/avatar/tempos.json" ] && [ -s "$E/avatar/avatar.mp4" ] || { log "FALHOU avatar ($(tail -2 "$E/avatar.log" | tr '\n' ' '))"; exit 1; }
log "avatar ok ($(cat "$E/avatar/video_id.txt"))"
( cd "$E" && python3 gerar_cena.py --canto ) >> "$E/avatar.log" 2>&1 || { log "FALHOU gerar_cena"; exit 1; }
( cd "$RAIZ" && DISPLAY=:99 GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh "$E" "$E/video-avatar.mp4" ) > "$E/build-avatar.log" 2>&1 || { log "FALHOU compor"; exit 1; }
# guarda: render concorrente na GPU já deixou o mapa todo branco (15/10/2026) → confere o brilho de 3 quadros e refaz uma vez
branco(){ for t in 10 30 50; do ffmpeg -v error -y -ss $t -i "$E/video-avatar.mp4" -frames:v 1 -vf "crop=1080:900:0:200,scale=64:64,format=gray" -f rawvideo - | python3 -c "import sys;b=sys.stdin.buffer.read();sys.exit(0 if sum(b)/len(b)>200 else 1)" && return 0; done; return 1; }
if branco; then log "mapa branco no render, refazendo"; ( cd "$RAIZ" && DISPLAY=:99 GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh "$E" "$E/video-avatar.mp4" ) > "$E/build-avatar.log" 2>&1 || { log "FALHOU compor 2"; exit 1; }
  branco && { log "FALHOU mapa branco de novo"; exit 1; }; fi
I=$(ffmpeg -nostats -i "$E/video-avatar.mp4" -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1 | awk '{print $2}')
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$E/video-avatar.mp4" | cut -d. -f1)
log "video-avatar.mp4 pronto (${D}s, ${I} LUFS)"
V="$E/video-avatar.mp4"; [ "$(stat -c%s "$V")" -lt 48000000 ] || { V="$E/video-avatar-bot.mp4"; ffmpeg -v error -y -i "$E/video-avatar.mp4" -c:v libx264 -crf 27 -maxrate 3M -bufsize 6M -c:a copy -movflags +faststart "$V"; }
rm -f "$V.envio-v3.json"
node "$BOT" "$V" "Queimadas na Amazônia · 9:16 com mapa 3D (colunas de fogo + satélite realista) · ${D}s · com avatar · NÃO publicado, para aprovação" >> "$E/avatar.log" 2>&1 \
  && log "bot v3 msg $(python3 -c "import json;print(json.load(open('$V.envio-v3.json'))['message_id'])")" || log "FALHOU bot v3"
log "fim"
