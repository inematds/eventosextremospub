#!/usr/bin/env bash
# Apaga os VIDEOS (.mp4) das edicoes com mais de N dias (padrao 10).
# Regra do Nei (09/11/2026): "videos de eventos extremos devem ser eliminados apos 10 dias".
# O video ja esta publicado; roteiro, dados e o que o git rastreia ficam.
#
# Uso: auto/limpa-videos.sh            -> so mostra o que apagaria
#      auto/limpa-videos.sh --aplicar  -> apaga
#      DIAS=15 auto/limpa-videos.sh    -> outro prazo
set -euo pipefail
cd "$(dirname "$0")/.."

DIAS=${DIAS:-10}
[[ "$DIAS" =~ ^[0-9]+$ && "$DIAS" -ge 3 ]] || { echo "DIAS invalido: $DIAS (minimo 3)"; exit 2; }
APLICAR=0; [[ "${1:-}" == "--aplicar" ]] && APLICAR=1
LOG=auto/limpa-videos.log

lista=$(mktemp); rastreados=$(mktemp); trap 'rm -f "$lista" "$rastreados"' EXIT
git ls-files -z -- edicoes | tr '\0' '\n' | grep -i '\.mp4$' | sort >"$rastreados" || true
find edicoes -type f -iname '*.mp4' -mtime +"$DIAS" | sort | comm -23 - "$rastreados" >"$lista"

n=$(wc -l <"$lista")
kb=$(tr '\n' '\0' <"$lista" | du -ck --files0-from=- 2>/dev/null | tail -1 | cut -f1)
gb=$(awk -v k="${kb:-0}" 'BEGIN{printf "%.1f", k/1048576}')

if [[ $APLICAR -eq 0 ]]; then
  echo "A SECO: $n videos com mais de $DIAS dias = $gb GB (use --aplicar para apagar)"
  exit 0
fi

tr '\n' '\0' <"$lista" | xargs -0 -r rm -f --
echo "$(date '+%F %T') apagados $n videos (> $DIAS dias) = $gb GB" | tee -a "$LOG"
