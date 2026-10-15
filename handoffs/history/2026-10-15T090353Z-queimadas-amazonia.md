# Handoff — 2026-10-15 — Vídeo "Queimadas na Amazônia, ano a ano" (16:9 com avatar) → lives10 + bot v3

## Pedido
Nei: vídeo eventosextremospub sobre queimadas da Amazônia; gráficos de vários anos comparando ano a ano; análise dos estados; imagens entre um gráfico e outro; impactante; publicar no lives10 e mandar ao bot v3 (links → inemaytbot, v3 só arquivo).

## Estado aceito
- [confirmed] Dados INPE baixados (anuais sat_ref 2003–2025 + mensais 2026) em `edicoes/2026-10-15-queimadas-amazonia/pesquisa/bruto/`; contagem `pesquisa/contar.py 14/10` → `serie.json`, `out_estados.json`.
- [confirmed] Base conferida: `edicoes/2026-10-15-queimadas-amazonia/base.md` (série anual, ytd, outubro, estados, municípios, contexto).
- [confirmed] Codex responde (teste 15/10 09h) — falha "workspace out of credits" de 14/10 não se repetiu.

## Plano
Formato 16:9 largo com avatar (modelo `edicoes/2026-10-12-amazonia-mundo`: falas.json, narrar.py, gerar_cena.py, avatar-e-monta.sh, publicar.sh). Painéis `grafico` (barras por ano; séries = estados) e `ranking`; `telas` com fotos do Codex (selo "ilustração") e satélite VIIRS (GIBS) entre os gráficos; `estados` pintando PA/AM/AP. Gancho quadro 0: 15/10/2026 + "1.500 FOCOS EM 1 DIA" (14/10, pior dia de 2026). Sem ângulo eleitoral. CTA só inema.club; pergunta "de que região/cidade você é?".

## Próxima ação exata
Escrever falas.json (~12 falas, ~3 min), gerar imagens Codex em `capa/`, narrar.py, gerar_cena.py, render mapa, avatar pelo estúdio (avatar-e-monta adaptado), revisar frames, publicar lives10 + inemaytbot + bot v3.
