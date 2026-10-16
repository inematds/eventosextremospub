# Goal — viral-916

- **Início:** 2026-10-15 20:59 · **Agente:** Claude (sessão interativa)
- **Tetos:** tempo 6 h · memória 16 G por render (explica.slice)

## Resultado
Itaipu e Queimadas em 9:16 (explicavideo viral, PiP), com o MESMO avatar/áudio dos 16:9 e visual novo: mais imagens, mais gráficos, mapa com pino em todo lugar falado e voo 3D realista (satélite inclinado, de perto → visão do alto da região), entregues no bot v3.

Pedido do Nei (15/10/2026): "manda os 2 em 9:16 com mesmo avatar mas com conteudo diferente quero mais imagens e cenas graficos ... quando fala dos lugares tem [que] localizar e seria bom uma imagem 3d mapa realista com uma visao [do alto] dele."

## Critérios de pronto (verificáveis)

**Função**
- [ ] `python3 -c` contando shots em `~/projetos/output/explica-{itaipu,queimadas}-viral/visual/viral916-pt-b01.json` → Itaipu ≥ 85, Queimadas ≥ 90 (≥ 1 troca a cada 2 s)
- [ ] Lugar falado tem shot `mapa` (pino/destaque) ou clipe 3D na deixa — Itaipu: Itaipu, Ciudad del Este, Foz do Iguaçu, Puerto Iguazú, Presidente Franco, Encarnación, Posadas, Yacyretá, Cascavel, Cataratas, bacia do Paraná/Iguaçu; Queimadas: Amazônia, Pará, Amazonas, Amapá, Mato Grosso, Rondônia, Altamira, São Félix do Xingu, Itaituba, Apuí, Manaus → script de checagem lista 0 faltando
- [ ] ≥ 2 clipes 3D realistas (motor/mapa.html, pitch > 40, satélite) por vídeo, usados como `foto` .mp4
- [ ] build `--strict` → warnings `[]` nos dois
- [ ] `qa_viral.py` → sem reprovação; folha `sheet-viral-*.jpg` olhada
- [ ] ffprobe 1080×1920; duração = avatar ±1 s (Itaipu ~192,3 s; Queimadas ~167,1 s); ebur128 ≈ −14 LUFS
- [ ] bot v3: `.envio-v3.json` com message_id dos dois

**Regressão**
- [ ] entregas 16:9 (`entrega/*-16x9.mp4`) e configs `*-viral-v2.json` intocadas (mtime anterior a 20:59 de 15/10)

**Limite**
- [ ] nenhum `verification/submit*` (avatar copiado, sem HeyGen)
- [ ] nada no YouTube sem ok novo do Nei; sem palavra morte/mortos na tela

**Teste rápido por ciclo**: `SO_BUILD=1 pipe_viral916.sh <id>`
**Teste completo no final**: render + qa_viral + ffprobe + ebur128

## Restrições
- só pela assinatura (Codex image_gen; flux2-klein local de reserva); GIBS liberado
- não mexer em: vídeos publicados, 16:9 entregues, configs/visuais 16:9

## Portões humanos (parar e perguntar)
- publicar no YouTube
- 3 ciclos sem avanço
