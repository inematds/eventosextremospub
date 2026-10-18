#!/usr/bin/env bash
# Do chat ao agente 9:16 (18/10/2026): espera o avatar do Nei (estúdio HeyGen, unidade dochat-avatar) e as imagens do Codex,
# monta com layout canto, mede o volume e manda ao bot v3. NÃO publica no YouTube (Nei: "me mande no v3").
# uso: systemd-run --user --unit=dochat-manda bash <este arquivo>   · estado em AVATAR-STATUS.txt
set -uo pipefail
export PATH="$HOME/.npm-global/bin:$PATH"
RAIZ="$HOME/projetos/eventosextremospub"
E="$RAIZ/edicoes/2026-10-18-do-chat-ao-agente"
ST="$E/AVATAR-STATUS.txt"; BOT="$HOME/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs"
log(){ echo "$(date '+%F %T') $*" >> "$ST"; }
log "início"
while systemctl --user is-active -q dochat-avatar || systemctl --user is-active -q dochat-imagens; do sleep 60; done
[ -s "$E/avatar/tempos.json" ] && [ -s "$E/avatar/avatar.mp4" ] || { log "FALHOU avatar ($(tail -2 "$E/avatar.log" | tr '\n' ' '))"; exit 1; }
for f in abertura chat-copia janela-fecha terminal jarvis fila redes degraus; do
  [ -s "$E/capa/$f.png" ] || { log "FALHOU imagem capa/$f.png ausente"; exit 1; }; done
log "avatar ok ($(cat "$E/avatar/video_id.txt"))"
( cd "$E" && python3 gerar_cena.py --canto ) >> "$E/avatar.log" 2>&1 || { log "FALHOU gerar_cena"; exit 1; }
( cd "$RAIZ" && env DISPLAY=:99 GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh "$E" "$E/video-avatar.mp4" ) > "$E/build-avatar.log" 2>&1 || { log "FALHOU compor"; exit 1; }
I=$(ffmpeg -nostats -i "$E/video-avatar.mp4" -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1 | awk '{print $2}')
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$E/video-avatar.mp4" | cut -d. -f1)
log "video-avatar.mp4 pronto (${D}s, ${I} LUFS)"
V="$E/video-avatar.mp4"; [ "$(stat -c%s "$V")" -lt 48000000 ] || { V="$E/video-avatar-bot.mp4"; ffmpeg -v error -y -i "$E/video-avatar.mp4" -c:v libx264 -crf 27 -maxrate 3M -bufsize 6M -c:a copy -movflags +faststart "$V"; }
[ "${SEM_BOT:-}" = 1 ] && { log "SEM_BOT: não enviado"; exit 0; }
rm -f "$V.envio-v3.json"
node "$BOT" "$V" "Do chat ao agente · reel 9:16 no motor do eventosextremospub · eventos.inema.pro/do-chat-ao-agente · ${D}s · com avatar · NÃO publicado" >> "$E/avatar.log" 2>&1 \
  && log "bot v3 msg $(python3 -c "import json;print(json.load(open('$V.envio-v3.json'))['message_id'])")" || log "FALHOU bot v3"
log "fim"
