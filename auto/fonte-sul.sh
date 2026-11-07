#!/usr/bin/env bash
# Impacto Sul (Nei, 07/11/2026): "criar como referência este canal, todo dia às 21 h pegando os vídeos publicados no dia".
# Fonte da verdade = os vídeos do DIA do perfil do TikTok @temponosul (o perfil nunca é citado no vídeo, como no Clima do DIA).
# Lista pelo Chromium sem janela (auto/tiktok_lista.mjs; o yt-dlp não lista perfil do TikTok), baixa e transcreve cada vídeo pelo inemavox
# (Whisper local; Groq só se o Whisper falhar), tira 6 telas de cada um e junta tudo em <ED>/fonte/transcript.txt.
# uso: auto/fonte-sul.sh <pasta da edição> <AAAA-MM-DD>   → 0 = fonte pronta; 3 = nenhum vídeo no dia
# PERFIL=<handle> troca o perfil; SO_ESCOLHER=1 só lista os vídeos do dia (teste, não baixa).
set -uo pipefail
AUTO="$(cd "$(dirname "$0")" && pwd)"
ED="$(mkdir -p "$1" && cd "$1" && pwd)"; DIA="$2"; F="$ED/fonte"; mkdir -p "$F"  # absoluto: o inemavox roda com cd na pasta dele
PERFIL="${PERFIL:-temponosul}"
[ -s "$F/transcript.txt" ] && { echo "fonte já transcrita"; exit 0; }

L=""
for k in 1 2 3; do  # o TikTok às vezes devolve a grade vazia: tenta de novo
  L=$(timeout 240 node "$AUTO/tiktok_lista.mjs" "$PERFIL" 30 2>"$F/lista.err") && [ -n "$L" ] && break; sleep 60
done
[ -n "$L" ] || { echo "não consegui listar o perfil @$PERFIL: $(tail -1 "$F/lista.err")"; exit 1; }
echo "$L" > "$F/perfil.txt"
DOS=$(echo "$L" | grep -F "|$DIA " | sort -t'|' -k2)   # vídeos do dia, do mais antigo ao mais novo
[ -n "$DOS" ] || { echo "nenhum vídeo de @$PERFIL em $DIA"; exit 3; }
echo "vídeos de $DIA: $(echo "$DOS" | wc -l)"; echo "$DOS"
[ "${SO_ESCOLHER:-}" = 1 ] && exit 0

: > "$F/transcript.txt"; : > "$F/video_info.txt"; n=0
while IFS='|' read -r ID HORA URL <&3; do  # fd 3: ffmpeg/python lá dentro comiam o stdin e o laço parava no 1º vídeo
  n=$((n+1)); M=""; V="$F/v$n"; mkdir -p "$V"; echo "$ID" > "$V/video_id.txt"
  for k in 1 2 3; do
    ( cd "$HOME/projetos/inemavox" && rm -rf "$V/dl" && timeout 900 python3 baixar_v1.py --url "$URL" --outdir "$V/dl" --quality 720p ) > "$V/baixar.log" 2>&1
    M=$(ls -S "$V"/dl/*.mp4 2>/dev/null | head -1); [ -n "$M" ] && break; sleep 60
  done
  [ -n "${M:-}" ] || { echo "v$n ($ID): download falhou: $(tail -1 "$V/baixar.log")"; continue; }
  mv "$M" "$V/video.mp4"; rm -rf "$V/dl"
  DESC=$(timeout 90 yt-dlp --skip-download --print "%(description)s" -- "$URL" 2>/dev/null | tr '\n' ' ' | cut -c1-400)
  DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V/video.mp4" | cut -d. -f1)
  for k in 1 2; do
    ( cd "$HOME/projetos/inemavox" && timeout 2400 python3 transcrever_v1.py --in "$V/video.mp4" --outdir "$V" --whisper-model large-v3 --src pt ) > "$V/transcrever.log" 2>&1 \
      && [ -s "$V/transcript.txt" ] && break; sleep 60
  done
  [ -s "$V/transcript.txt" ] || python3 "$AUTO/groq_transcrever.py" "$V/video.mp4" "$V" > "$V/groq.log" 2>&1 || true
  [ -s "$V/transcript.txt" ] || { echo "v$n ($ID): transcrição falhou"; continue; }
  TELAS=6 bash "$AUTO/telas_fonte.sh" "$V" > "$V/telas.log" 2>&1 || true
  mkdir -p "$V/frames" && ffmpeg -v error -y -i "$V/video.mp4" -vf "fps=2/3,scale=720:-2" -q:v 3 "$V/frames/f-%03d.jpg"  # 1 quadro a cada 1,5 s: as cenas reais do vídeo (Nei, 07/11/2026: mais imagens reais, menos mapa)
  echo "$ID|$HORA|${DUR}s|$DESC" >> "$F/video_info.txt"
  { echo "### Vídeo $n · publicado $HORA · ${DUR}s · quadros em fonte/v$n/frames/ (1 a cada 1,5 s)"; [ -n "$DESC" ] && echo "Legenda do post: $DESC"; cat "$V/transcript.txt"; echo; } >> "$F/transcript.txt"
  echo "v$n ($ID, $HORA): $(wc -w < "$V/transcript.txt") palavras"
done 3<<< "$DOS"
echo "$DOS" | head -1 | cut -d'|' -f1 > "$F/video_id.txt"
[ "$(wc -w < "$F/transcript.txt")" -gt 30 ] || { rm -f "$F/transcript.txt"; echo "nenhum vídeo do dia foi transcrito"; exit 1; }
echo "fonte pronta: $(grep -c '^### Vídeo' "$F/transcript.txt") vídeos, $(wc -w < "$F/transcript.txt") palavras"
