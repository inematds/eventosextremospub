#!/usr/bin/env bash
# Amazônia e o mundo: espera o serviço amazonia-avatar terminar e publica no lives10 (ok do Nei em 12/10/2026)
# o 16:9 normal e o reel como Short, só as versões COM avatar. Links + canal vão ao inemaytbot (o bot v3 recebe só arquivo).
# uso: systemd-run --user --unit=amazonia-publica bash <este arquivo>
set -uo pipefail
RAIZ="$HOME/projetos/eventosextremospub"
M="$RAIZ/edicoes/2026-10-12-amazonia-mundo"; R="$RAIZ/edicoes/2026-10-12-amazonia-reel"
ST="$M/AVATAR-STATUS.txt"; YT="$HOME/projetos/yt-pubx/yt-pubx"
log(){ echo "$(date '+%F %T') $*" >> "$ST"; }

while systemctl --user is-active -q amazonia-avatar; do sleep 120; done
log "publicação: avatar terminou, começando"

pub(){  # <edição> <sufixo do título> <prefixo da URL>
  local E="$1" SUF="$2" PRE="$3" nome; nome=$(basename "$E")
  [ -s "$E/video-avatar.mp4" ] || { log "$nome: sem video-avatar.mp4, NÃO publicado"; return 1; }
  local TIT; TIT="$(head -1 "$E/yt.txt" | cut -c1-90)$SUF"
  timeout 2400 "$YT" publicar "$E/video-avatar.mp4" --canal lives10 --title "$TIT" --sem-thumb \
    --contexto "Vídeo do INEMA com Nei Maldaner sobre a Amazônia e o mundo em 12/10/2026, com dados e fontes na tela. Use a descrição do arquivo como base, sem inventar números. Escreva 'mensagem de texto', nunca 'SMS'. Curso gratuito em https://inema.club." \
    --contexto-arquivo "$E/yt.txt" > "$E/publicar.log" 2>&1
  local ID; ID=$(grep -o 'watch?v=[A-Za-z0-9_-]*' "$E/publicar.log" | tail -1 | cut -d= -f2)
  [ -n "$ID" ] || { log "$nome: FALHOU publicar ($(grep -h -i 'erro\|error\|quota\|limit' "$E/publicar.log" | tail -1 | cut -c1-160))"; return 1; }
  echo "$ID" > "$E/youtube-lives10.txt"; log "$nome: publicado no lives10 $PRE$ID"
  echo "$PRE$ID"
}
U1=$(pub "$M" "" "https://www.youtube.com/watch?v=")
U2=$(pub "$R" " #Shorts" "https://www.youtube.com/shorts/")

# links ao inemaytbot, dizendo o canal
MSG="Publicado no lives10 (Amazônia e o mundo, 12/10/2026):
16:9: ${U1:-não publicado}
Short: ${U2:-não publicado}"
python3 - "$MSG" <<'EOF' && log "links enviados ao inemaytbot" || log "FALHOU aviso ao inemaytbot"
import json, sys, urllib.request, urllib.parse
from pathlib import Path
tok = next(l.split("=", 1)[1].strip().strip('"') for l in (Path.home() / "projetos/yt-pub-livesx-master/config/.env").read_text().splitlines() if l.startswith("TELEGRAM_NOTIFY_BOT_TOKEN="))
chat = (Path.home() / ".config/aventurasinemavideo/telegram_chat").read_text().strip()
d = urllib.parse.urlencode({"chat_id": chat, "text": sys.argv[1], "disable_web_page_preview": "true"}).encode()
r = json.load(urllib.request.urlopen(f"https://api.telegram.org/bot{tok}/sendMessage", d, timeout=60))
assert r.get("ok"), r
EOF
log "publicação: fim"
