# Handoff — 2026-10-15 (3) — Queimadas na Amazônia 16:9 com avatar → lives10 + bot v3 (Nei mandou continuar)

Ver snapshot anterior (2026-10-15T090808Z) para dados e plano completo. Progresso desde então:
- [confirmed] `edicoes/2026-10-15-queimadas-amazonia/falas.json` (13 falas, f1 gancho 1.500 focos/14/10 … f13 CTA), passou no portão de tom.
- [running] narração: `python3 narrar.py` → `build-narrar.log`, `tempos.json`, `narracao.wav`.
- [running] Codex image_gen em `capa/` (pedido.txt, codex.log): abertura.png (texto na arte), mata-chamas, manaus-fumaca, brigadista, cinzas, rio-seco.
- [confirmed] VIIRS 14/10 em `sat/web/v_NOAA20_2026-10-14.jpg` (bbox -76,-16,-42,6) e `_zoom` (-62,-9,-50,-1); `sat/web/mundo.jpg` copiado.

## Próxima ação
Escrever `gerar_cena.py` (base: 12/10 amazonia-mundo; gráficos em mil focos, guard `marcar` no grafico do motor ou série 2015–2026; contadores ini=em-1.0; #FACC15; telas entre gráficos), prévia de quadros, render, cadeia avatar+publica (adaptar avatar-e-monta.sh/publicar.sh).
