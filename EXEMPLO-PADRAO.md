# Exemplo padrão — vídeo avulso (16:9 explicativo + 9:16) do eventosextremospub

Pedido típico: "quero um vídeo eventosextremospub 16:9 e 9:16 sobre <assunto/link>, publica no lives10 e manda no v3".
Siga ESTE caminho; não copie a receita de um molde antigo sem conferir (o "Big techs" usou flux só porque o Codex estava sem
crédito em 19/10, e isso foi herdado por engano em 21/10).

Caso real completo: `~/projetos/output/explica-fim-mundo-1960/` (21/10/2026; `ESTADO.md`, `cadeia.sh`, `publicar.sh`,
`visual/gerar_visual.py`, configs em `~/projetos/explicavideos/examples/fim-mundo-1960*.json`).

## 1. Chamada e roteiro
- Mostrar ao Nei a chamada inicial (data dd/mm/aaaa + número viral com fonte) antes de produzir.
- Roteiro em `<OUT>/roteiro/pt.json` (cenas `{chapter,title,kind,labels,takeaway,source,svg:null,speech}`), números por extenso,
  "você", emoção primeiro e número/fonte na tela. **Um bloco só, ≤ 520 palavras** (o 9:16 tem teto de 160 s; o mesmo avatar
  serve os dois formatos). Nunca "morte/mortos/morreu/mortalidade" (use "vítimas", "sobreviver"). Fala não termina em número.
- Fecho: "No inema.club você pode aprender sobre inteligência artificial" + pergunta de comentário positiva.

## 2. Motor = explicavideos v2 perfil viral (não o `LAYOUT=largo`)
- Três configs: `<id>.json` (v1, HeyGen), `<id>-v2.json` (16:9, `profile_visual: viral`, `marca: INEMA · EVENTOS EXTREMOS`)
  e `<id>-v2-916.json` (9:16, `avatar_916: pip`, `pip_cena: 2`, `capa_segura: true`). `python3 explica.py --config … prepare`.
- Avatar pelo ESTÚDIO HeyGen (liberado sempre, sem pedir ok): `submeter.sh` grava o id no manifest.

## 3. Imagens = Codex image_gen PRIMEIRO
- `echo "<pedido>" | codex exec -s workspace-write --skip-git-repo-check -C <OUT>/media -` pedindo PNGs 16:9 (e outra rodada
  9:16 em `media916/`), uma imagem de impacto por tópico, luz neutra, sem marca, sem rosto reconhecível.
  A capa vem com o texto ESCRITO pelo Codex (data + gancho). Conferir cada imagem (Read).
- Depois: `refazvideo/ferramentas/cor_neutra.py corrigir media/*.png`.
- **flux2-klein só se o Codex falhar ou estiver sem crédito** (testar na hora); aí capa via `compor_titulo.py`.

## 4. Visual, montagem, QA
- `visual/gerar_visual.py` (16:9) e `… v` (9:16): cada tópico abre com `capitulo` (imagem + "PARTE n"), todo número vira
  `bignum`/`colunas`/`ranking`/`barra`, cinética nas frases fortes. `refazvideo/ferramentas/validar_visual.py` → OK.
- Abertura: capa do Codex com a manchete GRANDE desenhada (16:9 1536x1024; 9:16 VERTICAL 1024x1536, porque a capa do 9:16 é
  tela cheia 1080x1920), parada a 1ª frase inteira (`capa_segura: true` nos DOIS formatos; nada de cinética logo depois).
- Número/série = gráfico REAL (`linha`, motor 2.17) que se desenha no tempo da fala e volta continuando (`de` = onde parou);
  gráfico pode ficar até 9 s — a regra de 2 s é só para imagem (Nei 21/10). Fundo do gráfico sem curva falsa.
- Imagem: nunca > 2 s sem troca: o `capitulo` só tem `sub_at` (pôr em ~1 s) e a próxima peça ≤ 2 s depois; cada frase longa
  ganha ponto/palavra nova. **Rodar `build_block.py 1 --strict` nos dois formatos ANTES de soltar a cadeia** (21/10: reprovou 17 trechos
  só depois de 2 h esperando o avatar).
- `cadeia.sh` (systemd-run): baixa avatar → v1 → v2 16:9 e 9:16 `--strict` → `som_viral.py --sem-efeitos` → `qa_viral.py` → 720p.
- Olhar `v2*/verification/sheet-viral-*.jpg` antes de publicar.

## 5. Publicar
- `publicar.sh`: lives10 (16:9 com thumb = capa; 9:16 sem thumb, link `youtube.com/shorts/<id>`), links + "lives10" ao
  inemaytbot, arquivos 720p ao bot v3 sem links, dizendo o "msg N" no terminal.
