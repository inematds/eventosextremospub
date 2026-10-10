#!/usr/bin/env bash
# Avatar do Nei pelo ESTÚDIO do HeyGen (assinatura, nunca API): envia a fala de falas.json, espera, baixa e retemporiza.
# uso: auto/avatar.sh <pasta-da-edicao> <titulo>   -> <ed>/avatar/avatar.mp4 + avatar/tempos.json
# Sem flock próprio: heygen-studio.mjs e heygen-estudio-baixar.mjs já entram na fila do perfil (engine/heygen-perfil.mjs).
# O saudeviral segura o heygen-estudio.lock durante o download inteiro (horas): esperar por ele atrasaria o clima 24h.
# Com a fila do HeyGen cheia o vídeo pode ficar horas em 0% (10/10/2026): o download espera até 290 min.
# O script do estúdio recusa oferta de troca de plano (o Nei NUNCA troca de plano).
set -euo pipefail
E="$(cd "$1" && pwd)"; TITULO="$2"
A="$E/avatar"; mkdir -p "$A"
PERFIL="$HOME/.cache/inemaccbot/perfil-heygen"
ENG="$HOME/projetos/explicavideos/engine"
export DISPLAY="${DISPLAY:-:99}"
python3 -c "import json,sys; open(sys.argv[2],'w').write(' '.join(f['fala'] for f in json.load(open(sys.argv[1]))))" "$E/falas.json" "$A/fala.txt"
[ "$(wc -c < "$A/fala.txt")" -lt 4400 ] || { echo "ERRO: fala com mais de 4400 caracteres"; exit 2; }
echo 'Nei, 10/10/2026: "pode fazer pronto como lhe falei não precisa minha aprovação mas sim mandar para o bot v3" (clima 24h diário, avatar incluso, estúdio HeyGen pela assinatura)' > "$A/APROVADO_HEYGEN"
tenta(){ local log="$1" k; shift
  for k in $(seq 1 30); do
    "$@" > "$log" 2>&1 && return 0
    grep -q ProcessSingleton "$log" || return 1
    echo "perfil do HeyGen aberto por outro processo; nova tentativa em 2 min ($k/30)"; sleep 120
  done; return 1; }
(
  cd "$HOME/projetos/explicavideos"
  if [ -s "$A/video_id.txt" ] && [ "${REFAZER_HEYGEN:-}" != 1 ]; then echo "já enviado: $(cat "$A/video_id.txt")"
  else
    tenta "$A/studio.log" timeout 12000 node "$ENG/heygen-studio.mjs" --titulo "$TITULO" --fala-arquivo "$A/fala.txt" --perfil "$PERFIL" --template TEMPLATE-AVATAR16 \
      || { echo "ERRO no estúdio: $(grep -h ERRO "$A/studio.log" | tail -1)"; exit 3; }
    ID=$(grep -o 'create-v4/[0-9a-f]\{32\}' "$A/studio.log" | tail -1 | cut -d/ -f2)
    [ -n "$ID" ] || { echo "ERRO: id do vídeo não achado no studio.log"; exit 3; }
    echo "$ID" > "$A/video_id.txt"; sleep 60
  fi
  [ -s "$A/avatar.mp4" ] || tenta "$A/baixar.log" timeout 18000 node "$ENG/heygen-estudio-baixar.mjs" --id "$(cat "$A/video_id.txt")" --saida "$A/avatar.mp4" \
      --perfil "$PERFIL" --minutos 290 --intervalo 120 || { echo "ERRO ao baixar: $(tail -1 "$A/baixar.log")"; exit 4; }
)
# a transcrição (Whisper) às vezes falha com a GPU disputada (10/10/2026): tenta 3 vezes
for k in 1 2 3; do python3 "$A/retempo.py" && exit 0; echo "retempo falhou ($k/3)"; sleep 60; done
echo "ERRO: retempo falhou 3 vezes"; exit 6
