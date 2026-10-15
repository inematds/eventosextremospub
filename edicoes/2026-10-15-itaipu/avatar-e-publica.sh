#!/usr/bin/env bash
# E se Itaipu rompesse? (15/10/2026): espera o avatar do Nei (ESTÚDIO HeyGen, unidade itaipu-avatar), monta o 16:9,
# mede o volume, publica no lives10 (pedido do Nei, 15/10) e manda: links ao inemaytbot, arquivo 720p ao bot v3.
# Se o lives10 falhar, o arquivo vai ao v3 mesmo assim e o aviso diz "NÃO publicado".
# uso: systemd-run --user --unit=itaipu-publica bash <este arquivo>   · estado em AVATAR-STATUS.txt
set -uo pipefail
export PATH="$HOME/.npm-global/bin:$PATH"   # systemd usa /usr/bin/codex antigo (12/10/2026)
RAIZ="$HOME/projetos/eventosextremospub"
E="$RAIZ/edicoes/2026-10-15-itaipu"
ST="$E/AVATAR-STATUS.txt"; BOT="$HOME/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs"; YT="$HOME/projetos/yt-pubx/yt-pubx"
log(){ echo "$(date '+%F %T') $*" >> "$ST"; }
ytbot(){ python3 - "$1" <<'EOF'
import json, sys, urllib.request, urllib.parse
from pathlib import Path
tok = next(l.split("=", 1)[1].strip().strip('"') for l in (Path.home() / "projetos/yt-pub-livesx-master/config/.env").read_text().splitlines() if l.startswith("TELEGRAM_NOTIFY_BOT_TOKEN="))
chat = (Path.home() / ".config/aventurasinemavideo/telegram_chat").read_text().strip()
d = urllib.parse.urlencode({"chat_id": chat, "text": sys.argv[1], "disable_web_page_preview": "true"}).encode()
r = json.load(urllib.request.urlopen(f"https://api.telegram.org/bot{tok}/sendMessage", d, timeout=60))
assert r.get("ok"), r
EOF
}

log "início"
mkdir -p "$E/avatar"; cp -n "$RAIZ/edicoes/2026-10-12-ultimas-24h/avatar/retempo.py" "$E/avatar/"
# retomada: avatar.mp4 + tempos.json já prontos → não refaz (o retempo transcreve de novo e falha com a GPU cheia, 15/10)
[ -s "$E/avatar/avatar.mp4" ] && [ -s "$E/avatar/tempos.json" ] && [ "${PULA_RENDER:-}" = 1 ] || \
while systemctl --user is-active -q itaipu-avatar; do sleep 60; done
[ -s "$E/avatar/tempos.json" ] && [ -s "$E/avatar/avatar.mp4" ] || { log "FALHOU avatar ($(tail -2 "$E/avatar.log" | tr '\n' ' '))"; exit 1; }
log "avatar ok ($(cat "$E/avatar/video_id.txt"))"
( cd "$E" && python3 gerar_cena.py --avatar ) >> "$E/avatar.log" 2>&1 || { log "FALHOU gerar_cena"; exit 1; }
( cd "$RAIZ" && DISPLAY=:99 GEO=geo.js LAYOUT=largo motor/compor_avatar.sh "$E" "$E/video-avatar.mp4" ) > "$E/build-avatar.log" 2>&1 || { log "FALHOU compor"; exit 1; }
I=$(ffmpeg -nostats -i "$E/video-avatar.mp4" -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1 | awk '{print $2}')
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$E/video-avatar.mp4" | cut -d. -f1)
log "video-avatar.mp4 pronto (${D}s, ${I} LUFS)"

# lives10
TIT="$(head -1 "$E/yt.txt" | cut -c1-100)"
timeout 2400 "$YT" publicar "$E/video-avatar.mp4" --canal lives10 --title "$TIT" --sem-thumb \
  --contexto "Vídeo do INEMA com Nei Maldaner sobre o estudo hipotético de ruptura de Itaipu (UFPR, ABRHidro 2024), as cidades no cenário e a chuva de 2026 na bacia do Paraná e do Iguaçu comparada a 2024, com a previsão (15/10/2026). Deixe claro que é cenário hipotético e risco muito baixo. Use a descrição do arquivo como base, sem inventar números. Termine com: No inema.club você pode aprender sobre inteligência artificial: https://inema.club" \
  --contexto-arquivo "$E/yt.txt" > "$E/publicar.log" 2>&1
ID=$(grep -o 'watch?v=[A-Za-z0-9_-]*' "$E/publicar.log" | tail -1 | cut -d= -f2)
if [ -n "$ID" ]; then echo "$ID" > "$E/youtube-lives10.txt"; U="https://www.youtube.com/watch?v=$ID"; log "publicado no lives10 $U"
  ytbot "Publicado no lives10 (E se Itaipu rompesse?, 15/10/2026):
$U" && log "link enviado ao inemaytbot" || log "FALHOU aviso ao inemaytbot"
else MOT=$(grep -h -i 'erro\|error\|quota\|limit' "$E/publicar.log" | tail -1 | cut -c1-160); log "FALHOU publicar no lives10 ($MOT)"
  ytbot "⚠ NÃO publicado no lives10 (E se Itaipu rompesse?, 15/10/2026): $MOT" || true; fi

# bot v3: só o arquivo, 720p
V="$E/video-avatar-bot.mp4"
ffmpeg -v error -y -i "$E/video-avatar.mp4" -vf scale=1280:720 -c:v libx264 -crf 26 -preset medium -c:a copy -movflags +faststart "$V"
rm -f "$V.envio-v3.json"
node "$BOT" "$V" "E se Itaipu rompesse? · estudo UFPR + chuva 2026 · 16:9 (720p) · ${D}s · com avatar" >> "$E/avatar.log" 2>&1 \
  && log "bot v3 msg $(python3 -c "import json;print(json.load(open('$V.envio-v3.json'))['message_id'])")" || log "FALHOU bot v3"
log "fim"
