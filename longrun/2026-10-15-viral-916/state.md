# State — viral-916 (15/10/2026 ~23h)

## Feito
- Itaipu 916b enviado ao v3 (msg 1346). Virais 16:9 publicados no lives10: FFVTl8BMzQM (Itaipu), 9ITphwr5ceI (Queimadas).
- Voos 3D: Itaipu 9 clipes (`output/explica-itaipu-viral/3d/`), Queimadas 7 (`output/explica-queimadas-viral/3d/`, MODIS 08/10 + focos INPE). Ferramentas em `output/explica-eventos-viral/3d/` (gerar_3d.py, limpa_sat.py, tempo.py).
- Imagens verticais Codex: media916/ (14+14) + capa-v.png; capa-v-desce.png = capa com faixa escura no topo (a faixa da marca cobria a data).
- explicavideos (NÃO commitado; o repo já tinha mudanças de outra sessão): foto .mp4 (vfull) em build_block.py + runtime/viral.js; build conta vfull como movimento; vfull entra em `mapas` (QA não mede área lisa no voo).
- motor/mapa.html (eventosextremospub, não commitado): modo `limpo`.
- Configs: explicavideos/examples/{itaipu,queimadas}-viral-v2-916.json. Cadeia: output/explica-eventos-viral/pipe_viral916.sh <id> sombrio-pulso (SO_BUILD=1 só valida).
- Itaipu: build ok 85 shots, check ok, render feito (entrega/itaipu-viral-9x16.mp4) mas qa_viral REPROVADO área lisa (165/385 amostras, médio 0,40). 916b anterior também reprovou (0,29).
- Queimadas: build ok 78 shots, check ok; render NÃO feito.

## Próximo
1. SO_BUILD=1 itaipu (regera relatório com vfull em mapas e capa descida) → rerodar qa_viral no mp4 existente para medir quanto era voo.
2. Medir piso do layout (quadro bem texturizado, métrica 8×8 std<6).
3. Trocar fundos lisos (lago-imenso, v-chuva-oeste, r v-chuva, v-yacyreta, v-vertedouro em bignum/ranking/cinetica/capitulo) por texturizados (v-ciudad-del-este, v-galeria, v-foz-ponte, v-puerto-iguazu, v-encarnacion, barragem-aerea); idem Queimadas antes do render.
4. Re-render Itaipu → se ainda reprovar, perguntar ao Nei (QA calibrado para 16:9) ship × calibrar.
5. ffprobe/ebur128, 720p ≤49 MB, enviar_bot_v3.mjs; Queimadas depois (nunca em paralelo).
