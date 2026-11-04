#!/usr/bin/env bash
# Agenda o Short do clima no Instagram eventos.extremos (Reel, até 180 s) e no TikTok eventos.extremos, marca "eventosextremos" (blogId 7800440) no Metricool da conta inematds
# (conector MCP "metricool-inematds", apelido "metritds"). Ligado em 04/11/2026 no inema.tds; no mesmo dia o Nei
# mandou trocar: "o conteúdo do eventosextremos não deve ser no inematds e sim em outro canal chamado eventosextremos".
# Nunca publica na marca inema.tds: se nenhuma conta do eventos.extremos estiver conectada na marca, não agenda e avisa.
# Instagram só se a conta ligada for eventos.extremos (Nei, 04/11/2026: "este é o canal do evento extremo no instagram"). Chamado pelo auto/rodar.sh depois do YouTube.
# uso: auto/metritds.sh <pasta-da-edição> [video.mp4]
#   publica em agora + 10 min. RASCUNHO=1 agenda como rascunho · SEM_BOT=1 não avisa no v3 · FORCAR=1 refaz.
# Vídeo público para o Metricool: anexo da release "social" do repo público inematds/eventosextremospub.
set -uo pipefail
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"
ED="$(cd "$1" && pwd)"; V="${2:-}"
[ -z "$V" ] && for c in video-avatar.mp4 video-14.mp4 video.mp4; do [ -s "$ED/$c" ] && { V="$ED/$c"; break; }; done
LOG="$ED/metritds.log"; exec > >(tee -a "$LOG") 2>&1
echo "== $(date '+%F %T') metritds $ED ($V)"
[ -s "$V" ] || { echo "sem vídeo"; exit 1; }
[ -s "$ED/yt.txt" ] || { echo "sem yt.txt"; exit 1; }
[ -s "$ED/metritds.txt" ] && [ -z "${RASCUNHO:-}${FORCAR:-}" ] && { echo "já agendado ($(head -1 "$ED/metritds.txt")): nada a fazer"; exit 0; }
BOT="$HOME/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs"

ALVO=$(( $(date +%s) + 600 ))
QUANDO_UTC=$(date -u -d "@$ALVO" +%Y-%m-%dT%H:%M:00)   # UTC: o Metricool deslocou 1 h o horário local perto da meia-noite
QUANDO_BR=$(TZ=America/Sao_Paulo date -d "@$ALVO" '+%d/%m %H:%M')

# 1. link público do vídeo
NOME="clima-$(basename "$ED").mp4"
gh release view social -R inematds/eventosextremospub >/dev/null 2>&1 || \
  gh release create social -R inematds/eventosextremospub --title "Vídeos para redes sociais" \
     --notes "Cópias dos Shorts do clima usadas pelo Metricool (TikTok eventosextremos)." >/dev/null
TMP="$(mktemp -d)"; cp "$V" "$TMP/$NOME"
gh release upload social "$TMP/$NOME" -R inematds/eventosextremospub --clobber || { echo "Falhou: upload na release"; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"
MEDIA="https://github.com/inematds/eventosextremospub/releases/download/social/$NOME"

# 2. legenda: yt.txt (título + pontos) + YouTube + hashtags
TIT=$(head -1 "$ED/yt.txt")
YTID=$(head -1 "$ED/youtube-lives10.txt" 2>/dev/null)
{
  head -c 1500 "$ED/yt.txt"; echo
  [ -n "$YTID" ] && echo "No YouTube: https://www.youtube.com/shorts/$YTID"
  echo "Aprenda inteligência artificial em inema.club"
  echo "#clima #previsaodotempo #tempo #chuva #alerta #inemaclub"
} > "$ED/metritds-texto.txt"

# 3. agenda pelo conector metricool-inematds (claude -p, assinatura)
DURV=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V" 2>/dev/null | cut -d. -f1)
IGOK=$([ "${DURV:-999}" -le 180 ] && echo sim || echo "não (vídeo de ${DURV}s; Reel aceita até 180 s)")
PEDIDO="Use só as ferramentas do servidor MCP metricool-inematds.
1) getBrandSettings: pegue o blogId da marca de label exatamente \"eventosextremos\" (NUNCA use a marca inema.tds nem outra).
   Redes válidas nessa marca (confira em networksData):
   - instagram: só se instagramData for exatamente \"eventos.extremos\" e o Instagram estiver liberado ($IGOK).
   - tiktok: só se tiktokData for exatamente \"eventos.extremos\".
   Se nenhuma rede for válida, NÃO agende nada e responda ok=false com erro \"nenhuma rede do eventos.extremos conectada na marca eventosextremos\".
2) createScheduledPost UMA vez, só com as redes válidas em providers (nenhuma outra):
   date = ${QUANDO_UTC}Z ; publicationDate = {dateTime: \"${QUANDO_UTC}\", timezone: \"UTC\"}
   media = [\"$MEDIA\"] ; text = conteúdo exato do arquivo $ED/metritds-texto.txt (leia com a ferramenta Read)
   draft = $([ -n "${RASCUNHO:-}" ] && echo true || echo false) ; autoPublish = true
   tiktokData (só se tiktok for válido) = {privacyOption: \"PUBLIC_TO_EVERYONE\", title: primeira linha do texto (até 90 caracteres), isAigc: true}
   instagramData (só se instagram for válido) = {type: \"REEL\", showReelOnFeed: true, isAiGenerated: true}
3) Responda APENAS uma linha JSON, sem crase: {\"ok\":true|false,\"redes\":[...],\"planner\":[plannerUrl...],\"erro\":\"texto do erro ou vazio\"}"
cd "$ED"
OUT=$(printf '%s' "$PEDIDO" | timeout 600 env -u ANTHROPIC_API_KEY claude -p \
      --allowedTools "mcp__metricool-inematds__getBrandSettings mcp__metricool-inematds__createScheduledPost Read" 2>&1)
echo "claude: $OUT"
J=$(printf '%s' "$OUT" | grep -o '{.*"ok".*}' | tail -1)
campo() { printf '%s' "$J" | python3 -c "import sys,json
try: d=json.loads(sys.stdin.read())
except Exception: d={}
v=d.get('$1','');print(', '.join(v) if isinstance(v,list) else v)" 2>/dev/null; }
OK=$(printf '%s' "$J" | python3 -c 'import sys,json;print("1" if json.loads(sys.stdin.read() or "{}").get("ok") else "")' 2>/dev/null)
REDES=$(campo redes); PLAN=$(campo planner); ERRO=$(campo erro)

FAIXA="🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦"
if [ -n "$OK" ]; then
  [ -z "${RASCUNHO:-}" ] && printf '%s\n%s\n' "$QUANDO_BR" "$REDES" > "$ED/metritds.txt"
  MSG="$FAIXA
🔵 PUBLICADO DIRETO · eventos.extremos (metritds) $([ -n "${RASCUNHO:-}" ] && echo '(RASCUNHO DE TESTE)')
$FAIXA
$TIT
Quando: $QUANDO_BR · Redes: ${REDES:-?}
Instagram: https://www.instagram.com/eventos.extremos/
TikTok: https://www.tiktok.com/@eventos.extremos
Metricool: ${PLAN:-https://app.metricool.com/planner}"
else
  MSG="$FAIXA
⚠ METRITDS: NÃO AGENDOU (eventos.extremos)
$FAIXA
$TIT
Erro: ${ERRO:-$(printf '%s' "$OUT" | tail -c 300)}
Log: $LOG"
fi
echo "$MSG"
if [ -z "${SEM_BOT:-}" ]; then
  CAPA="$ED/metritds-capa.jpg"
  ffmpeg -v error -y -ss 3 -i "$V" -frames:v 1 -vf scale=540:-2 "$CAPA"
  rm -f "$CAPA.envio-v3.json"
  node "$BOT" "$CAPA" "$MSG" || echo "falhou o envio ao bot"
fi
[ -n "$OK" ]
