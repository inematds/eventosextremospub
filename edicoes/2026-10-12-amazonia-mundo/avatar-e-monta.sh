#!/usr/bin/env bash
# Amazônia e o mundo (12/10/2026): avatar do Nei pelo ESTÚDIO HeyGen (liberado sempre, Nei 12/10) para o 16:9 e o reel,
# monta cada um com o avatar, mede o volume e manda ao bot v3 (só o arquivo). NÃO publica no YouTube.
# Roda sozinho (horas, por causa da fila do HeyGen): systemd-run --user --unit=amazonia-avatar bash <este arquivo>
# Estado em edicoes/2026-10-12-amazonia-mundo/AVATAR-STATUS.txt (uma linha por etapa).
set -uo pipefail
RAIZ="$HOME/projetos/eventosextremospub"
M="$RAIZ/edicoes/2026-10-12-amazonia-mundo"; R="$RAIZ/edicoes/2026-10-12-amazonia-reel"
ST="$M/AVATAR-STATUS.txt"; BOT="$HOME/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs"
log(){ echo "$(date '+%F %T') $*" >> "$ST"; }

um(){  # <edição> <título> <flag gerar_cena> <LAYOUT> <legenda do bot> <bot720>
  local E="$1" TIT="$2" FLAG="$3" LAY="$4" CAP="$5" B720="$6" nome; nome=$(basename "$E")
  mkdir -p "$E/avatar"; cp -n "$RAIZ/edicoes/2026-10-12-ultimas-24h/avatar/retempo.py" "$E/avatar/"
  log "$nome: avatar no estúdio (fila pode levar horas)"
  bash "$RAIZ/auto/avatar.sh" "$E" "$TIT" > "$E/avatar.log" 2>&1 || { log "$nome: FALHOU avatar ($(tail -1 "$E/avatar.log"))"; return 1; }
  log "$nome: avatar ok ($(cat "$E/avatar/video_id.txt"))"
  ( cd "$E" && python3 gerar_cena.py "$FLAG" ) >> "$E/avatar.log" 2>&1 || { log "$nome: FALHOU gerar_cena"; return 1; }
  ( cd "$RAIZ" && GEO=geo-br.js LAYOUT="$LAY" motor/compor_avatar.sh "$E" "$E/video-avatar.mp4" ) > "$E/build-avatar.log" 2>&1 || { log "$nome: FALHOU compor"; return 1; }
  local I; I=$(ffmpeg -nostats -i "$E/video-avatar.mp4" -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1 | awk '{print $2}')
  local D; D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$E/video-avatar.mp4" | cut -d. -f1)
  log "$nome: video-avatar.mp4 pronto (${D}s, ${I} LUFS)"
  local V="$E/video-avatar.mp4"
  if [ "$B720" = 1 ]; then V="$E/video-avatar-bot.mp4"
    ffmpeg -v error -y -i "$E/video-avatar.mp4" -vf scale=1280:720 -c:v libx264 -crf 26 -preset medium -c:a copy -movflags +faststart "$V"; fi
  rm -f "$V.envio-v3.json"
  node "$BOT" "$V" "$CAP · ${D}s · com avatar" >> "$E/avatar.log" 2>&1 && log "$nome: bot v3 msg $(python3 -c "import json;print(json.load(open('$V.envio-v3.json'))['message_id'])")" || log "$nome: FALHOU bot v3"
}

log "início"
um "$R" "EVX-amazonia-reel" --canto canto "Amazônia e o mundo · reel 9:16" 0 &
sleep 300   # o estúdio entra um por vez no perfil; o 2º espera o 1º submeter
um "$M" "EVX-amazonia-mundo" --avatar largo "Amazônia e o mundo · 16:9 (720p)" 1 &
wait
log "fim"
