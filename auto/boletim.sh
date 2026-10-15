#!/usr/bin/env bash
# Clima do DIA: espera o boletim de meteorologia do dia sair no canal-fonte, baixa e transcreve (inemavox) em <ED>/fonte/.
# O canal é só a fonte da verdade: nunca é citado no vídeo (Nei, 13/10/2026).
# uso: auto/boletim.sh <pasta da edição> <AAAA-MM-DD>   → 0 = fonte/transcript.txt pronto; 3 = não saiu boletim até o limite
# LIMITE=HH:MM (padrão 17:00) = até quando procurar, de 10 em 10 min.
set -uo pipefail
ED="$1"; DIA="$2"; F="$ED/fonte"; mkdir -p "$F"
CANAL="https://www.youtube.com/channel/UCGXu6BQZDlJhj99-wFroUEA/videos"
FIM=$(date -d "$DIA ${LIMITE:-17:00}" +%s)
[ -s "$F/transcript.txt" ] && { echo "boletim já transcrito"; exit 0; }
D1=$(date -d "$DIA" +%d/%m/%Y); D2=$(date -d "$DIA" +%m/%d/%Y)   # o yt-dlp às vezes traz o título traduzido (data em mm/dd)
ID=""
while :; do
  # boletim aberto do dia: título "Brasil | ... (dd/mm/aaaa)"; vídeo de membros fica de fora
  ID=$(timeout 120 yt-dlp --flat-playlist --playlist-end 10 --print "%(id)s|%(title)s" "$CANAL" 2>/dev/null \
       | grep -E "^[^|]+\|(Brasil|Brazil) \|" | grep -v -i -E "membros|members" | grep -F -e "($D1)" -e "($D2)" | head -1 | cut -d'|' -f1)
  [ -n "$ID" ] && break
  [ "$(date +%s)" -ge "$FIM" ] && { echo "nenhum boletim de $D1 até ${LIMITE:-17:00}"; exit 3; }
  echo "$(date +%T) boletim de $D1 ainda não saiu"; sleep 600
done
echo "boletim: $ID"; echo "$ID" > "$F/video_id.txt"
cd "$HOME/projetos/inemavox" || exit 1
for k in 1 2 3; do
  rm -rf "$F/dl"; timeout 1800 python3 baixar_v1.py --url "https://www.youtube.com/watch?v=$ID" --outdir "$F/dl" --quality 720p > "$F/baixar.log" 2>&1
  M=$(ls -S "$F"/dl/*.mp4 2>/dev/null | head -1); [ -n "$M" ] && break; sleep 120
done
[ -n "${M:-}" ] || { echo "download falhou: $(tail -1 "$F/baixar.log")"; exit 1; }
mv "$M" "$F/video.mp4"; rm -rf "$F/dl"
for k in 1 2 3; do  # GPU disputada por outras narrações: tenta de novo
  timeout 5400 python3 transcrever_v1.py --in "$F/video.mp4" --outdir "$F" --whisper-model large-v3 --src pt > "$F/transcrever.log" 2>&1 \
    && [ -s "$F/transcript.txt" ] && break; sleep 120
done
[ -s "$F/transcript.txt" ] || { echo "transcrição falhou: $(tail -1 "$F/transcrever.log")"; exit 1; }
echo "transcrito: $(wc -w < "$F/transcript.txt") palavras"
