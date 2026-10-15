# Handoffs — trabalhos abertos

Cada linha é um assunto em andamento: leia o snapshot do assunto que for continuar. Gravado por handoff-grava.py.

<!-- handoff-indice:inicio -->
- `queimadas-amazonia` · handoffs/history/2026-10-15T114237Z-queimadas-amazonia.md · 15/10 08:42
- `previsao-do-dia` · handoffs/history/2026-10-15T100300Z-previsao-do-dia.md · 15/10 07:03
- `clima24h-2026-10-15` · handoffs/history/2026-10-15T095957Z-clima24h-2026-10-15.md · 15/10 06:59
<!-- handoff-indice:fim -->

---

Cópia integral do snapshot mais recente (handoffs/history/2026-10-15T114237Z-queimadas-amazonia.md):

# Handoff — 2026-10-15 (9) — Queimadas na Amazônia 16:9 com avatar → lives10 + bot v3

Edição `edicoes/2026-10-15-queimadas-amazonia/`. Snapshot 111646Z vale.
- [confirmed] 2ª cadeia falhou no retempo (transcrição de novo, GPU cheia). avatar-e-publica.sh agora pula avatar.sh quando avatar.mp4 + tempos.json existem e PULA_RENDER=1.
- [running] 3ª cadeia `queimadas-avatar` (DISPLAY=:99, PULA_RENDER=1), linha "retomada 2" no AVATAR-STATUS.txt: gerar_cena → montar → lives10 → inemaytbot → bot v3.

## Próxima ação
Ao "pronto (" depois de "retomada 2": quadros do video-avatar.mp4; ao "fim": link + msg v3; commit edição + motor (inematds); "Terminei:"/"Falhou:".
