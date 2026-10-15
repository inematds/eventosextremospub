# Canal — refaz-viral-queimadas-itaipu (só acrescentar; nunca reescrever)

Conhecimento do projeto que a compactação perde: fatos descobertos, aprendizados, glossário, armadilhas, onde estão as coisas.
Não é estado da tarefa (isso vai em state/plan/progress). Preencha cedo — o hook avisa na faixa 1 (~50% do contexto).

Formato: `- AAAA-MM-DD HH:MM · fato|aprendizado|glossário|armadilha · texto`

- 2026-10-15 15:10 · fato · pedido do Nei: refazer queimadas e Itaipu no explicavideo VIRAL 16:9 (escolheu o formato 1); 1ª imagem impactante + título grande. Guia do explicavideos com os formatos 16:9 e 9:16 já publicado (e19341f).
- 2026-10-15 15:10 · fato · ponte: ~/projetos/output/explica-eventos-viral/ponte_v1.py copia avatar/avatar.mp4 da edição como v1/assets/nei-pt-b01.mp4 (sem HeyGen), manifest completed; whisper-local.
- 2026-10-15 15:20 · fato · motor: peça nova `colunas` (viral.js/css, build_block, som_viral) para série 2003–2026; base de mapa `brasil-uf` (biblioteca-mapas/brasil-uf/uf.geojson, extraído do geo-br.js).
- 2026-10-15 15:25 · armadilha · Whisper escreve números em algarismos ("1" ".500"); numeros_extenso.py reescreve por extenso antes do build.
- 2026-10-15 15:25 · fato · cadeia: pipe_viral.sh <id> <trilha> (SO_BUILD=1 só valida).
- 2026-10-15 16:30 · armadilha · `hyperframes check` reprova carimbo central sobre rótulo do bignum, título de foto ou gráfico (content_overlap). Usar carimbo com x 0,82 (acima da caixa do avatar), y 0,22–0,50, ≤ 10 caracteres.
- 2026-10-15 16:30 · armadilha · capa do Codex com data no topo bate na faixa INEMA: descer a arte 80 px (capa-orig.png guardado).
- 2026-10-15 16:30 · armadilha · mapa brasil-uf com extent muito fechado (tríplice fronteira) fica azul vazio: usar foto + bignum.
- 2026-10-15 16:35 · fato · motor explicavideos 2.10.9 commit f373eeb (push): colunas, carimbo x, brasil-uf, docs. build/check passam nos dois; render completo rodando.
- 2026-10-15 17:40 · fato · ENTREGUE no bot v3: Itaipu viral msg 1332 (192 s, −13,5 LUFS, QA aprovado) e Queimadas viral msg 1340 (167 s, −13,4 LUFS, QA aprovado na 6ª rodada). YouTube não tocado; aguarda ok do Nei.
