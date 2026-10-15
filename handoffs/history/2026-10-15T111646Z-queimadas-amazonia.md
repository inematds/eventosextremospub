# Handoff — 2026-10-15 (8) — Queimadas na Amazônia 16:9 com avatar → lives10 + bot v3

Edição `edicoes/2026-10-15-queimadas-amazonia/`. Snapshot 110355Z vale.
- [confirmed] 1ª cadeia: render ok (`build/mapa-avatar.mp4`, 168,8 s) mas "FALHOU compor" na limpeza do `.mapa.html` (prévia paralela minha apagou). Corrigido: render.mjs `fs.rmSync(force)`; compor_avatar.sh `PULA_RENDER=1`. FALHAS.md registrado.
- [running] 2ª cadeia `queimadas-avatar` (DISPLAY=:99, PULA_RENDER=1) desde 08:16: retempo → gerar_cena → montar → lives10 → inemaytbot → bot v3. Esperando "pronto (" depois da linha "retomada" no AVATAR-STATUS.txt.

## Próxima ação
Conferir quadros do video-avatar.mp4; ao "fim", link (youtube-lives10.txt) e msg v3; commit edição + motor (inematds); "Terminei:"/"Falhou:".
