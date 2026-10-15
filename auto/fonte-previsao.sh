#!/usr/bin/env bash
# Previsão do Dia (Nei, 15/10/2026): pega o último vídeo do canal de previsão (YouTube UCGEnQh_FXX9Qny0BqmUbZ2g), baixa e transcreve (inemavox) em <ED>/fonte/.
# O canal é só a fonte da verdade: nunca é citado no vídeo (mesma regra do Clima do DIA).
# Prefere o vídeo de HOJE (o canal posta entre 08:30 e 09:45, às vezes ao meio-dia): procura de 10 em 10 min até ESPERA (padrão 12:00);
# sem vídeo de hoje, usa o último ainda não usado de ONTEM; nada disso → sai 3. Vídeo já usado fica em auto/previsao-usados.txt.
# uso: auto/fonte-previsao.sh <pasta da edição> <AAAA-MM-DD>   → 0 = fonte/transcript.txt pronto; 3 = sem vídeo novo
# FONTE_ID=<id> força um vídeo; SO_ESCOLHER=1 só mostra o escolhido (teste, não baixa nem marca).
set -uo pipefail
ED="$1"; DIA="$2"; F="$ED/fonte"; mkdir -p "$F"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"; USADOS="$RAIZ/auto/previsao-usados.txt"; touch "$USADOS"
CANAL="https://www.youtube.com/channel/UCGEnQh_FXX9Qny0BqmUbZ2g/videos"
FIM=$(date -d "$DIA ${ESPERA:-12:00}" +%s)
HOJE=$(date -d "$DIA" +%Y%m%d); ONTEM=$(date -d "$DIA -1 day" +%Y%m%d)
[ -s "$F/transcript.txt" ] && { echo "fonte já transcrita"; exit 0; }

# últimos vídeos abertos (sem membros), com a data de envio: "id|aaaammdd|título"
lista(){ timeout 120 yt-dlp --flat-playlist --playlist-end 4 --print "%(id)s" "$CANAL" 2>/dev/null | while read -r i; do
    timeout 90 yt-dlp --skip-download --print "%(id)s|%(upload_date)s|%(availability)s|%(title)s" -- "$i" 2>/dev/null
  done | grep -v -E "\|(subscriber_only|premium_only|needs_auth)\|" | awk -F'|' '{print $1"|"$2"|"$4}'; }
novo(){ grep -vxFf <(cut -d' ' -f1 "$USADOS") <(cut -d'|' -f1); }   # ids que ainda não foram usados

ID="${FONTE_ID:-}"
while [ -z "$ID" ]; do
  L=$(lista)
  ID=$(echo "$L" | grep -F "|$HOJE|" | novo | head -1)
  [ -n "$ID" ] && break
  if [ "$(date +%s)" -ge "$FIM" ]; then
    ID=$(echo "$L" | grep -F "|$ONTEM|" | novo | head -1)
    [ -n "$ID" ] && { echo "sem vídeo de hoje até ${ESPERA:-12:00}: uso o de ontem"; break; }
    echo "nenhum vídeo novo de hoje nem de ontem"; exit 3
  fi
  echo "$(date +%T) vídeo de hoje ainda não saiu"; sleep 600
done
echo "fonte: $ID · $(echo "${L:-}" | grep -F -- "$ID|" | cut -d'|' -f2-)"
[ "${SO_ESCOLHER:-}" = 1 ] && exit 0
echo "$ID" > "$F/video_id.txt"
timeout 90 yt-dlp --skip-download --print "%(upload_date)s|%(title)s" -- "$ID" > "$F/video_info.txt" 2>/dev/null
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
echo "$ID $DIA" >> "$USADOS"
echo "transcrito: $(wc -w < "$F/transcript.txt") palavras"
