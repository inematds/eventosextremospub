#!/usr/bin/env bash
# Rodada automática do "Clima 24 h" (Short 9:16 diário, publicado no lives10 e mandado ao bot v3).
# Autorizado pelo Nei em 10/10/2026: "pode fazer pronto... não precisa minha aprovação, mas sim mandar para o bot v3" (avatar incluso).
# coleta (APIs de clima gratuitas liberadas) → pesquisa + roteiro + cena + versão mapa (claude -p, assinatura)
#   → avatar do Nei (estúdio HeyGen, assinatura) → vídeo com avatar → lives10 + bot v3 → git push.
# uso: auto/rodar.sh [AAAA-MM-DD, padrão hoje] [24h|semana|ventos|mundo|dia|previsao]   (PREVIA=1 manda antes a versão com foto do avatar)
#   semana = domingo à tarde: previsão da semana (dias 1–7) + tendência de 15 dias (Nei, 11/10/2026), roteiro em auto/roteiro-semana.md
# Teste: SEM_AVATAR=1 pula o HeyGen (publica a versão mapa); SEM_YT=1 não publica; SEM_BOT=1 simula o bot; SEM_GIT=1 não commita.
# SEM_TRAVA=1 não espera a trava de outra rodada (piloto a pedido).
# Teste isolado: ED=<pasta> (não mexe na edição do dia).
# Pular um dia: linha "AAAA-MM-DD" em auto/pular.txt.
set -uo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
DIA="${1:-$(date +%F)}"; MODO="${2:-24h}"
case "$MODO" in
  24h)    SUF=ultimas-24h; ROT="clima 24h"; PROMPT_MD=roteiro.md ;;
  semana) SUF=semana; ROT="clima da semana"; PROMPT_MD=roteiro-semana.md ;;
  ventos) SUF=ventos-24h; ROT="ventos extremos 24h"; PROMPT_MD=roteiro-ventos.md ;;  # especial a pedido (13/10/2026)
  mundo)  SUF=mundo-7d; ROT="clima no mundo"; PROMPT_MD=roteiro-mundo.md ;;  # diário 18:00, aprovado pelo Nei em 13/10/2026
  dia)    SUF=clima-do-dia; ROT="clima do dia"; PROMPT_MD=roteiro-dia.md ;;  # diário após o boletim do meio-dia, aprovado pelo Nei em 13/10/2026
  previsao) SUF=previsao-do-dia; ROT="previsão do dia"; PROMPT_MD=roteiro-previsao.md ;;  # diário 10:00, último vídeo do canal de previsão (Nei, 15/10/2026)
  *) echo "modo inválido: $MODO"; exit 2 ;;
esac
ED="${ED:-$RAIZ/edicoes/$DIA-$SUF}"; mkdir -p "$ED/pesquisa/bruto" "$ED/avatar"
LOG="$ED/rodada.log"; exec >>"$LOG" 2>&1
exec 8>"$RAIZ/auto/.rodando"; if [ "${SEM_TRAVA:-}" = 1 ]; then echo "SEM_TRAVA=1: roda junto com outra rodada (piloto)"; elif [ "$MODO" = semana ] || [ "$MODO" = mundo ] || [ "$MODO" = dia ] || [ "$MODO" = previsao ]; then  # a de domingo espera (até 3 h) a outra rodada em vez de sumir calada
  flock -w "$([ "$MODO" = previsao ] && echo 21600 || echo 10800)" 8 || { echo "outra rodada segurou a trava por horas"; exit 1; }  # a previsão (10:00) pega o clima 24h ainda no avatar: espera até 6 h
else flock -n 8 || { echo "outra rodada em andamento"; exit 0; }; fi
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH" DISPLAY="${DISPLAY:-:99}"
echo "=== $(date '+%F %T') $ROT $DIA"
grep -qx "$DIA$(case "$MODO" in semana|mundo|dia|previsao) echo " $MODO";; esac)" "$RAIZ/auto/pular.txt" 2>/dev/null && { echo "pulado (auto/pular.txt)"; exit 0; }
BOT="$HOME/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs"
DRY=""; [ "${SEM_BOT:-}" = 1 ] && DRY=--dry-run
DATA_BR=$(date -d "$DIA" +%d/%m/%Y)

avisar() {  # manda texto ao bot e sai
  echo "$1" > "$ED/aviso.txt"; rm -f "$ED/aviso.txt.envio-v3.json"
  node "$BOT" $DRY "$ED/aviso.txt" "$ROT · $DATA_BR
$1" || echo "falhou o envio do aviso"
  echo "AVISO: $1"; exit "${2:-1}"
}

# 0. modelo = a edição mais recente do mesmo modo antes de hoje (a 1ª de domingo parte da última clima 24h)
PREV=$(ls -d "$RAIZ"/edicoes/*-$SUF 2>/dev/null | grep -vx "$ED" | sort | tail -1)
[ -z "$PREV" ] && [ "$MODO" = previsao ] && PREV=$(ls -d "$RAIZ"/edicoes/*-clima-do-dia 2>/dev/null | grep -vx "$ED" | sort | tail -1)
[ -z "$PREV" ] && PREV=$(ls -d "$RAIZ"/edicoes/*-ultimas-24h 2>/dev/null | grep -vx "$ED" | sort | tail -1)
[ -n "$PREV" ] && [ -f "$PREV/gerar_cena.py" ] || avisar "não achei a edição modelo (edicoes/*-ultimas-24h)"
[ -f "$ED/gerar_cena.py" ] || cp "$PREV/gerar_cena.py" "$ED/"
cp --update=none "$PREV/narrar.py" "$ED/"; cp --update=none "$PREV/avatar/retempo.py" "$ED/avatar/"
echo "modelo: $PREV"

# 0b. Clima do DIA: a fonte da verdade é o boletim do meio-dia (baixado e transcrito pelo inemavox; o canal nunca é citado)
if [ "$MODO" = dia ]; then
  bash "$RAIZ/auto/boletim.sh" "$ED" "$DIA" > "$ED/pesquisa/boletim.log" 2>&1; RC=$?
  [ "$RC" = 3 ] && avisar "sem boletim de meteorologia hoje até as 17h; não saiu Clima do DIA" 0
  [ "$RC" = 0 ] || avisar "falhou o boletim do dia: $(tail -1 "$ED/pesquisa/boletim.log")"
fi

# 0c. Previsão do Dia: a fonte da verdade é o último vídeo do canal de previsão (o canal nunca é citado)
if [ "$MODO" = previsao ]; then
  bash "$RAIZ/auto/fonte-previsao.sh" "$ED" "$DIA" > "$ED/pesquisa/fonte.log" 2>&1; RC=$?
  [ "$RC" = 3 ] && avisar "sem vídeo novo de previsão hoje até as 12h (nem de ontem); não saiu Previsão do Dia" 0
  [ "$RC" = 0 ] || avisar "falhou a fonte da previsão: $(tail -1 "$ED/pesquisa/fonte.log")"
fi

# 1. coleta (só APIs gratuitas de clima liberadas: INMET, INPE, NOAA, CEMADEN, Open-Meteo, NASA GIBS); o Clima no Mundo não usa a coleta do Brasil
# REUSAR_ROTEIRO=1 com a cena pronta: não recoleta (refazer a coleta mudaria os números que a cena já usa e gasta até 50 min)
if [ "${REUSAR_ROTEIRO:-}" = 1 ] && [ -s "$ED/video.mp4" ] && [ -s "$ED/sat/web/ir_tempos.json" ]; then echo "reusando coleta e satélite da edição"
elif [ "$MODO" != mundo ]; then
timeout 1200 python3 "$RAIZ/coleta/ultimas24h.py" "$ED/pesquisa/bruto" > "$ED/pesquisa/coleta.log" 2>&1 || echo "coleta com erro (ver pesquisa/coleta.log)"
AGORA=$(date -u +%Y-%m-%dT%H:00); ONTEM=$(date -u -d "-24 hour" +%Y-%m-%dT%H:00); BASE=$(date -u -d "$DIA -1 day" +%Y-%m-%dT17:30)
timeout 1800 python3 "$RAIZ/coleta/satelite_gibs.py" "$ED" --base "$BASE" --de "$ONTEM" --ate "$AGORA" --passo 30 --bbox=-76,-35,-33,7 > "$ED/pesquisa/sat.log" 2>&1 \
  || avisar "falhou o satélite (NASA GIBS): $(tail -1 "$ED/pesquisa/sat.log")"
fi
if [ "$MODO" = semana ]; then
  timeout 1800 python3 "$RAIZ/coleta/previsao15d.py" "$ED" --dia "$DIA" > "$ED/pesquisa/prev15.log" 2>&1 \
    || avisar "falhou a previsão de 15 dias (Open-Meteo): $(tail -1 "$ED/pesquisa/prev15.log")"
fi

# 2. pesquisa + roteiro + cena + versão mapa pelo Claude (assinatura, claude -p)
if [ "${REUSAR_ROTEIRO:-}" = 1 ] && [ -s "$ED/falas.json" ] && [ -s "$ED/video.mp4" ]; then
  echo "reusando falas.json e video.mp4 da edição"
else
  rm -f "$ED/ERRO.txt" "$ED/falas.json" "$ED/yt.txt" "$ED/video.mp4"
  PROMPT=$(sed -e "s|{ED}|$ED|g" -e "s|{PREV}|$PREV|g" -e "s|{RAIZ}|$RAIZ|g" -e "s|{DATA_BR}|$DATA_BR|g" -e "s|{DIA}|$DIA|g" "$RAIZ/auto/$PROMPT_MD")
  ( cd "$ED" && timeout 10800 env -u ANTHROPIC_API_KEY claude -p "$PROMPT" --permission-mode bypassPermissions \
      --add-dir "$RAIZ" > "$ED/claude.log" 2>&1 ) || echo "claude -p saiu com erro"
  [ -f "$ED/ERRO.txt" ] && avisar "o roteiro não saiu: $(head -c 400 "$ED/ERRO.txt")"
fi
for f in falas.json yt.txt video.mp4 tempos.json; do
  [ -s "$ED/$f" ] || avisar "faltou $f depois do claude -p ($(tail -c 300 "$ED/claude.log"))"
done
# portão de tom/CTA (Nei, 11/10/2026): "você", nunca "tu"; CTA só o inema.club, sem "segue o canal"
TOM=$(grep -o -i -w -E "tu|teu|tua|teus|tuas|ti|contigo|segue o canal|se inscreve|inscreva-se|por sorte|felizmente|ainda bem|boa notícia|melhor" "$ED/falas.json" "$ED/gerar_cena.py" | sort -u | head -5 | tr '\n' ' ')
[ -n "$TOM" ] && avisar "roteiro reprovado no tom/CTA (usar 'você'; CTA só inema.club): $TOM"
# portão da palavra morte (Nei, 15/10/2026: "não pode usar palavra morte", os vídeos que falaram tiveram pouca entrega): usar "vítimas"
MORTE=$(grep -o -i -w -E "mort[eoa]s?|morreu|morreram|morrem|morrer|óbitos?|falecid[oa]s?|faleceu|faleceram" "$ED/falas.json" "$ED/gerar_cena.py" "$ED/yt.txt" 2>/dev/null | sort -u | head -5 | tr '\n' ' ')
[ -n "$MORTE" ] && avisar "roteiro reprovado: palavra proibida (morte/morto/morreu; usar 'vítimas'): $MORTE"

# 2b. PREVIA=1: manda ao bot a versão com FOTO do avatar enquanto o estúdio gera o avatar de verdade (Nei, 13/10/2026)
if [ "${PREVIA:-}" = 1 ]; then
  if bash "$RAIZ/auto/previa.sh" "$ED" > "$ED/previa.log" 2>&1; then
    rm -f "$ED/video-previa.mp4.envio-v3.json"
    node "$BOT" $DRY "$ED/video-previa.mp4" "$ROT · $DATA_BR · PRÉVIA com foto do avatar (o avatar de verdade está sendo feito no estúdio; a versão final chega depois)
$(head -1 "$ED/yt.txt")" || echo "falhou o envio da prévia"
  else echo "prévia falhou: $(tail -2 "$ED/previa.log")"; fi
fi

# 3. avatar do Nei (estúdio HeyGen); se falhar, publica a versão mapa (voz do Nei pelo Chatterbox)
V="$ED/video-avatar.mp4"; NOTA=""
if [ "${SEM_AVATAR:-}" != 1 ] && bash "$RAIZ/auto/avatar.sh" "$ED" "EVX-$DIA-$SUF" > "$ED/avatar.log" 2>&1 \
   && python3 "$RAIZ/motor/pausa_pergunta.py" "$ED" --avatar >> "$ED/avatar.log" 2>&1 \
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
[ "$MODO" = semana ] && CTX="Short de domingo 'Previsão da semana + 15 dias' do INEMA com Nei Maldaner: o que vem no clima do Brasil de segunda a domingo e a tendência de 15 dias (tendência pode mudar), a partir de $DATA_BR. Dados com fonte na tela (Open-Meteo, INMET). Escreva 'mensagem de texto', nunca 'SMS'. Curso gratuito em https://inema.club."
[ "$MODO" = dia ] && CTX="Short diário 'Clima do DIA' do INEMA com Nei Maldaner: a situação do tempo hoje no Brasil e o que vem nos próximos dias, $DATA_BR. Não citar nenhum canal, apresentador ou vídeo de origem. Dados com fonte na tela. Escreva 'mensagem de texto', nunca 'SMS'. Curso gratuito em https://inema.club."
[ "$MODO" = previsao ] && CTX="Short diário 'Previsão do Dia' do INEMA com Nei Maldaner: a previsão do tempo para hoje e os próximos dias no Brasil, $DATA_BR. Não citar nenhum canal, meteorologista, apresentador ou vídeo de origem. Dados com fonte na tela. Escreva 'mensagem de texto', nunca 'SMS'. Curso gratuito em https://inema.club."
[ "$MODO" = mundo ] && CTX="Short diário 'Clima no Mundo' do INEMA com Nei Maldaner: os eventos de clima e desastres naturais mais graves do mundo nos últimos 7 dias, até $DATA_BR. Dados com fonte na tela. Curso gratuito em https://inema.club."
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
node "$BOT" $DRY "$V" "$ROT · $DATA_BR · ${DUR}s $NOTA
$ST
$(tail -n +2 "$ED/yt.txt" | head -c 600)" || echo "falhou o envio ao bot"
echo "$ST"

# 5. git (autor inematds); arquivos pesados e gerados ficam fora pelo .gitignore
if [ "${SEM_GIT:-}" != 1 ] && [ -z "$DRY" ]; then
  cd "$RAIZ"
  ARQ=()
  for f in falas.json gerar_cena.py narrar.py tempos.json yt.txt youtube-lives10.txt avatar/fala.txt avatar/retempo.py avatar/tempos.json \
           avatar/video_id.txt avatar/APROVADO_HEYGEN fonte/video_id.txt fonte/video_info.txt pesquisa/noticias.md pesquisa/boletim.md pesquisa/dados.md pesquisa/proposta.md pesquisa/bruto/resumo.json pesquisa/bruto/previsao7d.json om/prev15_resumo.json; do
    p="edicoes/$DIA-$SUF/$f"; [ -f "$p" ] && ! git check-ignore -q "$p" && ARQ+=("$p")
  done
  git add -- "${ARQ[@]}" && git -c user.name=inematds -c user.email=inematds@gmail.com commit -qm "$ROT $DATA_BR (rodada automática): $ST" \
    && { git pull -q --rebase && git push -q && echo "push ok"; } || echo "git falhou"
fi
echo "=== fim $(date '+%F %T')"
