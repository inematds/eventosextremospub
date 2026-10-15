# Handoff — 2026-10-15 (2) — Vídeo "Queimadas na Amazônia, ano a ano" (16:9 com avatar) → lives10 + bot v3

## Pedido do Nei (15/10, literal)
"quero q faca um video eventosextremospub sobre as quemaids da amazonia, mostra grafisocs de varios anos compare ano a no bore os graficos, tambem analisa os estados e tambem colouqe entre um e outro imagens, faca ele impactante e publiuqe no lives10 e mande par ao v3"

## Estado aceito
- [confirmed] Dados INPE (anuais sat_ref 2003–2025 + mensais 2026, AQUA_M-T, bioma Amazônia) em `edicoes/2026-10-15-queimadas-amazonia/pesquisa/bruto/`; `pesquisa/contar.py 14/10` → `serie.json`; `out_estados.json` (01–14/10 por estado, 2015–2026).
- [confirmed] Base conferida com fontes: `edicoes/2026-10-15-queimadas-amazonia/base.md` — LER PRIMEIRO.
- [confirmed] 14/10/2026 = 1.500 focos = dia com MAIS focos de 2026 (conferido no ano inteiro; depois 12/10 1.335, 09/10 1.282). Na tela, pôr junto o pior dia de 2024 (3.445 em 02/09) para não soar recorde.
- [confirmed] Codex responde (15/10 09h).
- Nada de falas, narração, imagem ou render feito ainda.

## Plano (revisado pelo advisor)
1. Ler `~/projetos/inema-design/DESIGN.md`, `video/style.md`, `video/camera.md`, `memoria/correcoes.md` (style.md já lido: dissolve, zoom ≤ 1,25, amarelo #FACC15).
2. 16:9 largo com avatar, ~3 min, modelo `edicoes/2026-10-12-amazonia-mundo/` (falas.json, narrar.py, gerar_cena.py, avatar-e-monta.sh, publicar.sh). NÃO herdar: contador/gráfico `ini = em(palavra) - 1.0, dur 1.0`; amarelo só `#FACC15`/`rgba(250,204,21,…)`; copiar `sat/web/mundo.jpg`; `GEO=geo-br.js`.
3. Gráficos (`grafico` do motor/mapa.html: W=620, imprime valor cru): passar valores em MIL (174.4…) com unid "mil focos". (a) série anual 2003→2026 — 24 barras não cabem: adicionar guard `g.marcar=[índices]` p/ rótulos só em 2004, 2007, 2024, 2025, 2026, ou cortar para 2015–2026; 2026 "até 14/10" hachurado (`previsto_a_partir`). (b) 01/01–14/10 empilhado por estado 2019–2026. (c) outubro 01–14 por ano 2019–2026 ("sobe quando devia cair"). `ranking` para estados 2026 e municípios. `estados` pinta PA/AM/AP.
4. Imagens entre gráficos: VIIRS true-color 14/10 (`coleta/gibs_camada.py`, legenda "NASA VIIRS 14/10") + fotos Codex em `telas` (selo "ilustração", luz neutra): mata em chamas, Manaus sob fumaça, brigadista. Quadro 0 tela `ini: -1.0`, data 15/10/2026 + "1.500 FOCOS EM UM DIA".
5. Falas: MT −9% e RO −24% sem termo de alívio; após número de estado, total da Amazônia; sem ângulo eleitoral; pergunta "de que região/cidade você é?"; fecho "No inema.club você pode aprender sobre inteligência artificial". Rodar o portão de texto (grep checar/portão em auto/rodar.sh) ANTES de narrar.
6. narrar.py → gerar_cena.py → prévia `node motor/render.mjs $E --quadros …` (LER frames dos gráficos) → render → avatar estúdio + montagem + publicação lives10 numa cadeia systemd (adaptar avatar-e-monta.sh + publicar.sh) → links ao inemaytbot ("Publicado no lives10"), 720p ao bot v3. Se lives10 falhar ("out of credits" do yt-pubx em 14/10), ainda mandar arquivo ao v3 e avisar "Falhou: …".

## Observação lateral
- `edicoes/2026-10-15-ultimas-24h/rodada.log` parou em 2 linhas às 05:30 — conferir se o diário de hoje travou.

## Próxima ação exata
Sessão nova + /prime no eventosextremospub; ler base.md e o passo 1; escrever `edicoes/2026-10-15-queimadas-amazonia/falas.json`.
