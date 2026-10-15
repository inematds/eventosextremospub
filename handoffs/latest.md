# Handoffs — trabalhos abertos

Cada linha é um assunto em andamento: leia o snapshot do assunto que for continuar. Gravado por handoff-grava.py.

<!-- handoff-indice:inicio -->
- `queimadas-amazonia` · handoffs/history/2026-10-15T111646Z-queimadas-amazonia.md · 15/10 08:16
- `previsao-do-dia` · handoffs/history/2026-10-15T100300Z-previsao-do-dia.md · 15/10 07:03
- `clima24h-2026-10-15` · handoffs/history/2026-10-15T095957Z-clima24h-2026-10-15.md · 15/10 06:59
<!-- handoff-indice:fim -->

---

Cópia integral do snapshot mais recente (handoffs/history/2026-10-15T111646Z-queimadas-amazonia.md):

# Handoff — 2026-10-15 (8) — Queimadas na Amazônia 16:9 com avatar → lives10 + bot v3

Edição `edicoes/2026-10-15-queimadas-amazonia/`. Snapshot 110355Z vale.
- [confirmed] 1ª cadeia: render ok (`build/mapa-avatar.mp4`, 168,8 s) mas "FALHOU compor" na limpeza do `.mapa.html` (prévia paralela minha apagou). Corrigido: render.mjs `fs.rmSync(force)`; compor_avatar.sh `PULA_RENDER=1`. FALHAS.md registrado.
- [running] 2ª cadeia `queimadas-avatar` (DISPLAY=:99, PULA_RENDER=1) desde 08:16: retempo → gerar_cena → montar → lives10 → inemaytbot → bot v3. Esperando "pronto (" depois da linha "retomada" no AVATAR-STATUS.txt.

## Próxima ação
Conferir quadros do video-avatar.mp4; ao "fim", link (youtube-lives10.txt) e msg v3; commit edição + motor (inematds); "Terminei:"/"Falhou:".
