# Goal — refaz-viral-queimadas-itaipu

- **Início:** 2026-10-15 15:03 · **Agente:** Claude (sessão wifi)
- **Tetos:** tempo 6 h · memória 16 G por render (explica.slice) · zero HeyGen novo · zero API

## Resultado
Queimadas e Itaipu refeitos no formato explicavideo VIRAL 16:9 (capa com imagem impactante + título grande, imagens e gráficos em tela cheia, avatar em caixa no canto), reaproveitando os avatares já gravados, entregues no bot v3. YouTube só com ok do Nei.

## Critérios de pronto (verificáveis)

**Função**
- [x] `ls ~/projetos/output/explica-{queimadas,itaipu}-viral/entrega/*-16x9.mp4` → 2 arquivos
- [x] `python3 -c "json.load(build-v2-pt-b01.json)['warnings']"` de cada → `[]` (build --strict viral)
- [x] `qa_viral.py` de cada → sem reprovação (liso ≤ 40%, nada parado > 2 s); folha `verification/sheet-viral-*.jpg` olhada
- [x] ffprobe duração de cada ≈ duração do avatar (167,1 s / 192,3 s ± 1 s); ebur128 ≈ −14 LUFS
- [x] bot v3 recebeu os 2 (message_id no `.envio-v3.json`)

**Regressão**
- [x] `cd ~/projetos/explicavideos && python3 -m unittest discover -s tests` → OK (peça `colunas` e base `brasil-uf` novas não quebram)

**Limite**
- [x] `ls ~/projetos/output/explica-*-viral/v1/verification/submit*` → nenhum envio ao HeyGen (avatar copiado da edição)
- [x] vídeos atuais do lives10 (dHYmVqPTw44, QLoX7W8uEiY) intocados; nada publicado sem ok

## Escala
nível 3 = comando + saída esperada cobrindo função, regressão e limite.
