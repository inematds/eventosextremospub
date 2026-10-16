# Canal — viral-916 (só acrescentar; nunca reescrever)

Conhecimento do projeto que a compactação perde: fatos descobertos, aprendizados, glossário, armadilhas, onde estão as coisas.
Não é estado da tarefa (isso vai em state/plan/progress). Preencha cedo — o hook avisa na faixa 1 (~50% do contexto).

Formato: `- AAAA-MM-DD HH:MM · fato|aprendizado|glossário|armadilha · texto`


## 15/10 ~22h (Claude)
- Voos 3D: `output/explica-eventos-viral/3d/gerar_3d.py` (motor/mapa.html em modo `limpo`) + `limpa_sat.py` (Landsat WELD anual tem listras SLC-off; perto = inpaint, largo = MODIS Aqua 21/08/2026 de preenchimento) + borda transparente de 8% nas camadas (sem emenda). HLS no GIBS veio vazio; WELD mensal vazio.
- explicavideos: `foto` aceita .mp4 (vfull) — build_block + viral.js; build conta o clipe como movimento a cada 1 s.
- Snapshot sem API: `hyperframes snapshot --describe false` (sem isso chama Gemini se GEMINI_API_KEY existir).
- Itaipu 916: build ok 85 shots/9 voos/4 mapas; render em `explica-itaipu-viral/pipe916.out`.
