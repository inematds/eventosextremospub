# Handoffs — trabalhos abertos

Cada linha é um assunto em andamento: leia o snapshot do assunto que for continuar. Gravado por handoff-grava.py.

<!-- handoff-indice:inicio -->
- `queimadas-amazonia` · handoffs/history/2026-10-15T100340Z-queimadas-amazonia.md · 15/10 07:03
- `previsao-do-dia` · handoffs/history/2026-10-15T100300Z-previsao-do-dia.md · 15/10 07:03
- `clima24h-2026-10-15` · handoffs/history/2026-10-15T095957Z-clima24h-2026-10-15.md · 15/10 06:59
<!-- handoff-indice:fim -->

---

Cópia integral do snapshot mais recente (handoffs/history/2026-10-15T100340Z-queimadas-amazonia.md):

# Handoff — 2026-10-15 (5) — Queimadas na Amazônia 16:9 com avatar → lives10 + bot v3

Edição `edicoes/2026-10-15-queimadas-amazonia/`. Dados/plano: snapshot 090808Z.

## Estado aceito
- [confirmed] Prévia conferida em quadros (layout avatar, `PREVIA_AVATAR=1 python3 gerar_cena.py`): capa, hero, série 2003–2026, estados, outubro, dias, ranking estados, Pará, quadro "quem combate", municípios, Manaus, CTA. Corrigidos: capa `capa/abertura-v.png` (faixa de 90 px sob a marca), milhar nos gráficos, `marcar_x`, margem do eixo (L=58), pino de Manaus removido.
- [confirmed] Narração local ABANDONADA (GPU disputada, falhas): `tempos.json` atual é ESTIMADO (só prévia). O vídeo final usa `avatar/tempos.json` (medido no áudio do HeyGen).
- [running] systemd `queimadas-avatar` (DISPLAY=:99): download do avatar na fila do perfil HeyGen; depois gerar_cena --avatar → compor → lives10 → inemaytbot → bot v3. Estado: AVATAR-STATUS.txt.
- motor/mapa.html alterado (marcar/marcar_x, milhar, L=58, painel.g largo no lg) — não commitado.

## Próxima ação
Quando AVATAR-STATUS.txt tiver "video-avatar.mp4 pronto": extrair 4–6 quadros do video-avatar.mp4 e conferir (avatar à direita, gráficos, legenda). Ao "fim": conferir link no publicar.log, commitar edição + motor (autor inematds), avisar "Terminei:"/"Falhou:".
