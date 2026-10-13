#!/usr/bin/env bash
# Rodada de VALIDAÇÃO (Nei, 13/10/2026: "manda para mim sem o avatar, usa uma foto no lugar, e depois com o avatar, só desta vez quero validar").
# Para uma edição que já tem falas.json + tempos.json + narracao.wav: manda ao bot v3 a versão com FOTO do avatar,
# depois faz o avatar no estúdio HeyGen (assinatura), monta e manda a versão COM avatar. Não publica no YouTube, não commita.
# uso: auto/validar.sh <pasta-da-edicao> "<rótulo>" [mundo]
#   mundo = antes roda o claude -p com auto/roteiro-mundo.md (modelo: Short 9:16 do mundo amazonia-reel)
set -uo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
E="$1"; ROT="$2"; MODO="${3:-}"
mkdir -p "$E/avatar" "$E/pesquisa"; E="$(cd "$E" && pwd)"
exec >>"$E/validar.log" 2>&1
# DISPLAY fixo em :99: rodando da sessão RDP o DISPLAY herdado (:10) abria o navegador do HeyGen na tela do Nei (13/10/2026)
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH" DISPLAY=:99
BOT="$HOME/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs"
DIA=$(basename "$E" | cut -c1-10); DATA_BR=$(date -d "$DIA" +%d/%m/%Y)
echo "=== $(date '+%F %T') validar $ROT"
bot(){ rm -f "$1.envio-v3.json"; node "$BOT" "$1" "$2" || echo "falhou envio ao bot: $1"; }

if [ -n "$MODO" ]; then
  case "$MODO" in
    mundo) PREV="$RAIZ/edicoes/2026-10-12-amazonia-reel" ;;
    dia)   PREV="$RAIZ/edicoes/2026-10-13-ultimas-24h"  # Clima do DIA: boletim do meio-dia em fonte/transcript.txt + coleta para o mapa
           mkdir -p "$E/pesquisa/bruto"
           timeout 1200 python3 "$RAIZ/coleta/ultimas24h.py" "$E/pesquisa/bruto" > "$E/pesquisa/coleta.log" 2>&1 || echo "coleta com erro"
           timeout 1800 python3 "$RAIZ/coleta/satelite_gibs.py" "$E" --base "$(date -u -d "$DIA -1 day" +%Y-%m-%dT17:30)" \
             --de "$(date -u -d "-24 hour" +%Y-%m-%dT%H:00)" --ate "$(date -u +%Y-%m-%dT%H:00)" --passo 30 --bbox=-76,-35,-33,7 > "$E/pesquisa/sat.log" 2>&1 || echo "satélite com erro" ;;
    *) echo "modo inválido: $MODO"; exit 2 ;;
  esac
  [ -f "$E/gerar_cena.py" ] || cp "$PREV/gerar_cena.py" "$E/"
  cp --update=none "$PREV/narrar.py" "$E/"; cp --update=none "$RAIZ/edicoes/2026-10-13-ultimas-24h/avatar/retempo.py" "$E/avatar/"
  PROMPT=$(sed -e "s|{ED}|$E|g" -e "s|{PREV}|$PREV|g" -e "s|{RAIZ}|$RAIZ|g" -e "s|{DATA_BR}|$DATA_BR|g" -e "s|{DIA}|$DIA|g" "$RAIZ/auto/roteiro-$MODO.md")
  ( cd "$E" && timeout 5400 env -u ANTHROPIC_API_KEY claude -p "$PROMPT" --permission-mode bypassPermissions --add-dir "$RAIZ" > "$E/claude.log" 2>&1 ) || echo "claude -p saiu com erro"
  [ -f "$E/ERRO.txt" ] && { bot "$E/ERRO.txt" "$ROT · $DATA_BR · não saiu: $(head -c 300 "$E/ERRO.txt")"; exit 1; }
fi
for f in falas.json tempos.json narracao.wav yt.txt; do [ -s "$E/$f" ] || { echo "faltou $f"; exit 1; }; done
TOM=$(grep -o -i -w -E "tu|teu|tua|teus|tuas|ti|contigo|segue o canal|se inscreve|inscreva-se|por sorte|felizmente|ainda bem|boa notícia|melhor" "$E/falas.json" | sort -u | head -5 | tr '\n' ' ')
[ -n "$TOM" ] && echo "AVISO tom: $TOM"

# 1. versão com FOTO no lugar do avatar (SO_AVATAR=1 pula: já foi enviada)
if [ "${SO_AVATAR:-}" = 1 ]; then echo "pulando a versão com foto"
elif bash "$RAIZ/auto/previa.sh" "$E" > "$E/previa.log" 2>&1; then
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$E/video-previa.mp4" | cut -d. -f1)
  bot "$E/video-previa.mp4" "$ROT · $DATA_BR · ${D}s · SEM avatar (foto no lugar) · validação, não publicado
$(head -1 "$E/yt.txt")${TOM:+
⚠ tom: $TOM}"
else echo "prévia falhou: $(tail -2 "$E/previa.log")"; fi

# 2. versão COM avatar (estúdio HeyGen)
V="$E/video-avatar.mp4"
if bash "$RAIZ/auto/avatar.sh" "$E" "EVX-VAL-$(basename "$E")" > "$E/avatar.log" 2>&1 \
   && ( cd "$E" && python3 gerar_cena.py --canto ) \
   && ( cd "$RAIZ" && GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh "$E" "$V" > "$E/build-avatar.log" 2>&1 ); then
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V" | cut -d. -f1)
  L=$(ffmpeg -nostats -i "$V" -af ebur128 -f null - 2>&1 | grep -A1 Integrated | grep -o -- '-\?[0-9.]* LUFS' | tail -1)
  bot "$V" "$ROT · $DATA_BR · ${D}s · COM avatar · validação, não publicado ($L)
$(head -1 "$E/yt.txt")"
else
  bot "$E/validar.log" "$ROT · $DATA_BR · o avatar falhou: $(grep -h ERRO "$E/avatar.log" 2>/dev/null | tail -1 | cut -c1-200)"
fi
echo "=== fim $(date '+%F %T')"
