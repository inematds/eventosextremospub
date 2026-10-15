# Handoff — 2026-10-15 (4) — Queimadas na Amazônia 16:9 com avatar → lives10 + bot v3

Dados/plano: snapshot 2026-10-15T090808Z. Edição: `edicoes/2026-10-15-queimadas-amazonia/`.

## Estado aceito
- [confirmed] falas.json (13 falas), yt.txt, gerar_cena.py (gráficos: série 2003–2026, estados 2019–2026, outubro 2019–2026, Pará outubro; rankings; telas Codex; painel "QUEM COMBATE O FOGO NO AMAZONAS" não narrado em f8), base.md (inclui seção bombeiros).
- [confirmed] 6 fotos Codex em capa/ revisadas (capa com texto certo, terço direito livre).
- [confirmed] motor/mapa.html: `g.marcar` no grafico + `body.lg .painel.g{width:1180px}`.
- [running] narração `narrar.py` (build-narrar.log; GPU dividida com diários) → tempos.json ainda não existe.
- [running] systemd `queimadas-avatar` (avatar-e-publica.sh, DISPLAY=:99): avatar enviado (video_id.txt), baixando; depois gerar_cena --avatar → compor → lives10 → inemaytbot → bot v3 720p. Estado em AVATAR-STATUS.txt.
- Pendência separada (Nei: "guarda pra outro momento"): gráfico focos × temperatura × área queimada → `~/projetos/wifi/pendencias.md`.

## Próxima ação
Quando tempos.json existir: `python3 gerar_cena.py` + `node motor/render.mjs <E> --quadros …` nos tempos dos gráficos (f2, f4+2.6, f5, f6+2.6, f7, f8 combate, f10) e LER os quadros; corrigir gerar_cena antes de o avatar chegar. Depois acompanhar AVATAR-STATUS.txt até "fim"; avisar "Terminei:" ou "Falhou:".
