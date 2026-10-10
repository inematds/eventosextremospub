#!/usr/bin/env bash
# Rodada automática do "Clima 24 h" (Short 9:16 diário, publicado no lives10 e mandado ao bot v3).
# Autorizado pelo Nei em 10/10/2026: "pode fazer pronto... não precisa minha aprovação, mas sim mandar para o bot v3" (avatar incluso).
# coleta (APIs de clima gratuitas liberadas) → pesquisa + roteiro + cena + versão mapa (claude -p, assinatura)
#   → avatar do Nei (estúdio HeyGen, assinatura) → vídeo com avatar → lives10 + bot v3 → git push.
# uso: auto/rodar.sh [AAAA-MM-DD, padrão hoje]
# Teste: SEM_AVATAR=1 pula o HeyGen (publica a versão mapa); SEM_YT=1 não publica; SEM_BOT=1 simula o bot; SEM_GIT=1 não commita.
# Teste isolado: ED=<pasta> (não mexe na edição do dia).
# Pular um dia: linha "AAAA-MM-DD" em auto/pular.txt.
set -uo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
DIA="${1:-$(date +%F)}"
ED="${ED:-$RAIZ/edicoes/$DIA-ultimas-24h}"; mkdir -p "$ED/pesquisa/bruto" "$ED/avatar"
LOG="$ED/rodada.log"; exec >>"$LOG" 2>&1
exec 8>"$RAIZ/auto/.rodando"; flock -n 8 || { echo "outra rodada em andamento"; exit 0; }
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH" DISPLAY="${DISPLAY:-:99}"
echo "=== $(date '+%F %T') clima 24h $DIA"
grep -qx "$DIA" "$RAIZ/auto/pular.txt" 2>/dev/null && { echo "pulado (auto/pular.txt)"; exit 0; }
BOT="$HOME/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs"
DRY=""; [ "${SEM_BOT:-}" = 1 ] && DRY=--dry-run
DATA_BR=$(date -d "$DIA" +%d/%m/%Y)

avisar() {  # manda texto ao bot e sai
  echo "$1" > "$ED/aviso.txt"; rm -f "$ED/aviso.txt.envio-v3.json"
  node "$BOT" $DRY "$ED/aviso.txt" "clima 24h · $DATA_BR
$1" || echo "falhou o envio do aviso"
  echo "AVISO: $1"; exit "${2:-1}"
}

# 0. modelo = a edição de clima 24h mais recente antes de hoje
PREV=$(ls -d "$RAIZ"/edicoes/*-ultimas-24h 2>/dev/null | grep -vx "$ED" | sort | tail -1)
[ -n "$PREV" ] && [ -f "$PREV/gerar_cena.py" ] || avisar "não achei a edição modelo (edicoes/*-ultimas-24h)"
[ -f "$ED/gerar_cena.py" ] || cp "$PREV/gerar_cena.py" "$ED/"
cp --update=none "$PREV/narrar.py" "$ED/"; cp --update=none "$PREV/avatar/retempo.py" "$ED/avatar/"
echo "modelo: $PREV"

# 1. coleta (só APIs gratuitas de clima liberadas: INMET, INPE, NOAA, CEMADEN, Open-Meteo, NASA GIBS)
timeout 1200 python3 "$RAIZ/coleta/ultimas24h.py" "$ED/pesquisa/bruto" > "$ED/pesquisa/coleta.log" 2>&1 || echo "coleta com erro (ver pesquisa/coleta.log)"
AGORA=$(date -u +%Y-%m-%dT%H:00); ONTEM=$(date -u -d "-24 hour" +%Y-%m-%dT%H:00); BASE=$(date -u -d "$DIA -1 day" +%Y-%m-%dT17:30)
timeout 1800 python3 "$RAIZ/coleta/satelite_gibs.py" "$ED" --base "$BASE" --de "$ONTEM" --ate "$AGORA" --passo 30 --bbox=-76,-35,-33,7 > "$ED/pesquisa/sat.log" 2>&1 \
  || avisar "falhou o satélite (NASA GIBS): $(tail -1 "$ED/pesquisa/sat.log")"

# 2. pesquisa + roteiro + cena + versão mapa pelo Claude (assinatura, claude -p)
if [ "${REUSAR_ROTEIRO:-}" = 1 ] && [ -s "$ED/falas.json" ] && [ -s "$ED/video.mp4" ]; then
  echo "reusando falas.json e video.mp4 da edição"
else
  rm -f "$ED/ERRO.txt" "$ED/falas.json" "$ED/yt.txt" "$ED/video.mp4"
  PROMPT=$(sed -e "s|{ED}|$ED|g" -e "s|{PREV}|$PREV|g" -e "s|{RAIZ}|$RAIZ|g" -e "s|{DATA_BR}|$DATA_BR|g" -e "s|{DIA}|$DIA|g" "$RAIZ/auto/roteiro.md")
  ( cd "$ED" && timeout 5400 env -u ANTHROPIC_API_KEY claude -p "$PROMPT" --permission-mode bypassPermissions \
      --add-dir "$RAIZ" > "$ED/claude.log" 2>&1 ) || echo "claude -p saiu com erro"
  [ -f "$ED/ERRO.txt" ] && avisar "o roteiro não saiu: $(head -c 400 "$ED/ERRO.txt")"
fi
for f in falas.json yt.txt video.mp4 tempos.json; do
  [ -s "$ED/$f" ] || avisar "faltou $f depois do claude -p ($(tail -c 300 "$ED/claude.log"))"
done

# 3. avatar do Nei (estúdio HeyGen); se falhar, publica a versão mapa (voz do Nei pelo Chatterbox)
V="$ED/video-avatar.mp4"; NOTA=""
if [ "${SEM_AVATAR:-}" != 1 ] && bash "$RAIZ/auto/avatar.sh" "$ED" "EVX-$DIA-ultimas-24h" > "$ED/avatar.log" 2>&1 \
   && ( cd "$ED" && python3 gerar_cena.py --canto ) \
   && ( cd "$RAIZ" && GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh "$ED" "$V" > "$ED/build-avatar.log" 2>&1 ); then
  echo "vídeo com avatar ok"
else
  V="$ED/video.mp4"
  if [ "${SEM_AVATAR:-}" = 1 ]; then NOTA="(teste sem avatar)"
  else NOTA="(sem avatar: $(grep -h ERRO "$ED/avatar.log" 2>/dev/null | tail -1 | cut -c1-150); saiu a versão mapa)"; fi
  echo "avatar falhou $NOTA"
  # o montar.sh deixa a versão mapa em ~-17 LUFS: sobe para -14 (padrão do YouTube) antes de publicar
  I0=$(ffmpeg -nostats -i "$ED/video.mp4" -af ebur128 -f null - 2>&1 | grep -A1 Integrated | grep -o -- '-[0-9.]*' | tail -1)
  [ -n "$I0" ] && ffmpeg -v error -y -i "$ED/video.mp4" -c:v copy -af "volume=$(python3 -c "print(round(-14-($I0),2))")dB,alimiter=limit=0.89" \
      -c:a aac -b:a 192k "$ED/video-14.mp4" && V="$ED/video-14.mp4"
fi
LUFS=$(ffmpeg -nostats -i "$V" -af ebur128 -f null - 2>&1 | grep -A1 "Integrated" | grep -o -- '-\?[0-9.]* LUFS' | tail -1)
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V" | cut -d. -f1)
echo "vídeo: $V · ${DUR}s · $LUFS"

# 4. lives10 (Short: título com #Shorts, sem thumb) + bot v3 sempre
TIT="$(head -1 "$ED/yt.txt" | cut -c1-88) #Shorts"
CTX="Short diário 'Clima 24 h' do INEMA com Nei Maldaner: o clima no Brasil nas últimas 24 horas e o que vem hoje, $DATA_BR. Dados com fonte na tela. Escreva 'mensagem de texto', nunca 'SMS'. Curso gratuito em https://inema.club."
URL=""
if [ "${SEM_YT:-}" != 1 ] && [ -z "$DRY" ]; then
  timeout 2400 "$HOME/projetos/yt-pubx/yt-pubx" publicar "$V" --canal lives10 --title "$TIT" --contexto "$CTX" \
      --contexto-arquivo "$ED/yt.txt" > "$ED/publicar.log" 2>&1
  ID=$(grep -o 'watch?v=[A-Za-z0-9_-]*' "$ED/publicar.log" | tail -1 | cut -d= -f2)
  [ -n "$ID" ] && { URL="https://www.youtube.com/shorts/$ID"; echo "$ID" > "$ED/youtube-lives10.txt"; }
fi
if [ -n "$URL" ]; then ST="publicado no lives10: $URL"
elif [ "${SEM_YT:-}" = 1 ] || [ -n "$DRY" ]; then ST="(sem YouTube nesta rodada)"
else ST="⚠ NÃO publicou no lives10: $(grep -h -i 'erro\|error\|quota\|limit' "$ED/publicar.log" | tail -1 | cut -c1-200)"; fi
rm -f "$V.envio-v3.json"
node "$BOT" $DRY "$V" "clima 24h · $DATA_BR · ${DUR}s $NOTA
$ST
$(tail -n +2 "$ED/yt.txt" | head -c 600)" || echo "falhou o envio ao bot"
echo "$ST"

# 5. git (autor inematds); arquivos pesados e gerados ficam fora pelo .gitignore
if [ "${SEM_GIT:-}" != 1 ] && [ -z "$DRY" ]; then
  cd "$RAIZ"
  ARQ=()
  for f in falas.json gerar_cena.py narrar.py tempos.json yt.txt youtube-lives10.txt avatar/fala.txt avatar/retempo.py avatar/tempos.json \
           avatar/video_id.txt avatar/APROVADO_HEYGEN pesquisa/noticias.md pesquisa/dados.md pesquisa/proposta.md pesquisa/bruto/resumo.json; do
    p="edicoes/$DIA-ultimas-24h/$f"; [ -f "$p" ] && ! git check-ignore -q "$p" && ARQ+=("$p")
  done
  git add -- "${ARQ[@]}" && git -c user.name=inematds -c user.email=inematds@gmail.com commit -qm "clima 24h $DATA_BR (rodada automática): $ST" \
    && { git pull -q --rebase && git push -q && echo "push ok"; } || echo "git falhou"
fi
echo "=== fim $(date '+%F %T')"
