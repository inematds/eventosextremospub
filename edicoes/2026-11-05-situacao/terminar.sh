#!/usr/bin/env bash
# Termina a "Situação dos Eventos Extremos" quando o avatar chegar (roda como serviço, não depende da sessão):
# espera o avatar.sh (unit evx-situacao-avatar) com aviso ⏳ no v3 a cada hora → pausa da pergunta → cena --canto
# → mapa com avatar → clipes reais na janela (canto) → bot v3 → lives10 (pedido do Nei, 05/11/2026) → git.
# Sem avatar: aviso 🔴 no v3 e NÃO publica (regra 05/11/2026).
set -uo pipefail
ED="$(cd "$(dirname "$0")" && pwd)"; RAIZ="$(cd "$ED/../.." && pwd)"
BOT="$HOME/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs"; ROT="Situação dos Eventos Extremos"; DATA_BR="05/11/2026"
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH" DISPLAY="${DISPLAY:-:99}"
LOG="$ED/terminar.log"; exec >>"$LOG" 2>&1
echo "=== $(date '+%F %T') terminar"
aviso() { echo "$1" > "$ED/aviso.txt"; rm -f "$ED/aviso.txt.envio-v3.json"; node "$BOT" "$ED/aviso.txt" "$1" || true; echo "AVISO: $1"; }

t0=$(date +%s); h=0
while systemctl --user is-active -q evx-situacao-avatar; do
  sleep 60
  if [ $(( ($(date +%s) - t0) / 3600 )) -gt "$h" ]; then h=$((h + 1))
    aviso "⏳ $ROT · $DATA_BR: esperando o avatar na fila do HeyGen há mais ${h} h; o vídeo só sai com avatar."; fi
done
if [ ! -s "$ED/avatar/avatar.mp4" ] || [ ! -s "$ED/avatar/tempos.json" ]; then
  aviso "🔴 $ROT · $DATA_BR · SEM AVATAR — não publiquei. Motivo: $(grep -h -E 'ERRO|Error' "$ED/avatar.log" | tail -1 | cut -c1-250)"; exit 5
fi
python3 "$RAIZ/motor/pausa_pergunta.py" "$ED" --avatar || { aviso "🔴 $ROT: falhou a pausa da pergunta (ver terminar.log); não publiquei"; exit 5; }
if ! ( cd "$ED" && python3 gerar_cena.py --canto ); then
  ERRO=$(cd "$ED" && python3 gerar_cena.py --canto 2>&1 | grep -E "Error" | tail -1 | cut -c1-300)
  ( cd "$ED" && timeout 2400 env -u ANTHROPIC_API_KEY claude -p "Na pasta $ED, 'python3 gerar_cena.py --canto' falhou com: $ERRO
A fala do avatar (avatar/tempos.json) é mais rápida que a narração (tempos.json). Ajuste SÓ tempos, durações e limites no gerar_cena.py (os clipes podem começar uma palavra antes; o mínimo de um clipe pode cair para 0,8 s), sem mudar falas, números nem textos. Rode 'python3 gerar_cena.py' e 'python3 gerar_cena.py --canto' até os dois passarem. Não renderize nem publique nada." \
      --permission-mode bypassPermissions --add-dir "$RAIZ" > "$ED/claude-canto.log" 2>&1 ) || true
  ( cd "$ED" && python3 gerar_cena.py --canto ) || { aviso "🔴 $ROT: a cena com os tempos do avatar reprovou: $ERRO; não publiquei"; exit 5; }
fi
( cd "$RAIZ" && GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh "$ED" "$ED/video-avatar-base.mp4" > "$ED/build-avatar.log" 2>&1 ) \
  || { aviso "🔴 $ROT: falhou a montagem com avatar ($(tail -1 "$ED/build-avatar.log" | cut -c1-200)); não publiquei"; exit 5; }
python3 "$ED/montar_clipes.py" "$ED/video-avatar-base.mp4" "$ED/video-avatar.mp4" canto \
  || { aviso "🔴 $ROT: falhou o encaixe dos clipes; não publiquei"; exit 5; }
V="$ED/video-avatar.mp4"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V" | cut -d. -f1)
LUFS=$(ffmpeg -nostats -i "$V" -af ebur128 -f null - 2>&1 | grep -A1 Integrated | grep -o -- '-\?[0-9.]* LUFS' | tail -1)
[ "${DUR:-0}" -ge 180 ] && { aviso "🔴 $ROT: ${DUR}s (Short não pode chegar a 3 min); não publiquei"; exit 5; }
# folha de 12 quadros para conferência
ffmpeg -v error -y -i "$V" -vf "fps=1/9,scale=270:-1,tile=6x2" -frames:v 1 "$ED/folha-final.jpg" || true

TIT="$(head -1 "$ED/yt.txt" | cut -c1-88) #Shorts"
CTX="Short 'Situação dos Eventos Extremos' do INEMA com Nei Maldaner: os impactos dos eventos extremos do dia anterior no Brasil (vídeos reais, números com fonte) e como o fenômeno acontece, $DATA_BR. Não citar canais, emissoras nem autores dos vídeos. Escreva 'vítimas', nunca 'mortes'. Curso gratuito em https://inema.club."
timeout 2400 "$HOME/projetos/yt-pubx/yt-pubx" publicar "$V" --canal lives10 --title "$TIT" --contexto "$CTX" --contexto-arquivo "$ED/yt.txt" > "$ED/publicar.log" 2>&1
ID=$(grep -o 'watch?v=[A-Za-z0-9_-]*' "$ED/publicar.log" | tail -1 | cut -d= -f2)
if [ -n "$ID" ]; then echo "$ID" > "$ED/youtube-lives10.txt"; ST="publicado no lives10: https://www.youtube.com/shorts/$ID"
else ST="⚠ NÃO publicou no lives10: $(grep -h -i 'erro\|error\|quota' "$ED/publicar.log" | tail -1 | cut -c1-200)"; fi
rm -f "$V.envio-v3.json"
node "$BOT" "$V" "$ROT · $DATA_BR · ${DUR}s · $LUFS · com avatar
$ST
$(tail -n +2 "$ED/yt.txt" | head -c 500)" || echo "falhou o envio ao bot"
cd "$RAIZ" && git add -- edicoes/2026-11-05-situacao/{falas.json,gerar_cena.py,narrar.py,tempos.json,yt.txt,clipes.json,cortar_clipes.py,montar_clipes.py,terminar.sh,pesquisa/FATOS.md,avatar/tempos.json,avatar/video_id.txt,avatar/retempo.py,youtube-lives10.txt} 2>/dev/null
git -c user.name=inematds -c user.email=inematds@gmail.com commit -qm "Situação dos Eventos Extremos 05/11 (piloto): $ST" && git pull -q --rebase --autostash && git push -q && echo "push ok"
echo "$ST"; echo "=== fim $(date '+%F %T')"
