# Handoff — 2026-10-15 — refazer 3 vídeos tirando a palavra morte (corte, sem avatar novo)

## Projeto e escopo
eventosextremospub, raiz ~/projetos/eventosextremospub. O Nei pediu refazer os 3 vídeos que falam em morte cortando a fala (mesmo avatar, sem gerar novo), usar "vítimas" na tela, capa de impacto no quadro 0, manter o vídeo dinâmico, e mandar de novo (bot v3). Regra durável: nunca usar a palavra morte.

## Objetivo atual
Entregar ao bot v3: 2026-10-13-mundo-7d/video-avatar-v2.mp4, 2026-10-14-mundo-7d/video.mp4 (versão mapa, cortada), 2026-10-15-ultimas-24h/video-avatar-v2.mp4. Pronto = os 3 enviados, sem "mort*" na fala (Whisper) nem na tela.

## Estado aceito
- [confirmed] Regra no ar: portão MORTE no auto/rodar.sh, linha PALAVRA PROIBIDA em todos os auto/roteiro*.md, lição no CLAUDE.md — commit f53e07e, push feito.
- [confirmed] 15/10: avatar cortado (1.43-2.06, 9.62-11.42), retempo 95%, sem "morte" ouvida; video-avatar-v2.mp4 69 s, -13.7 LUFS, quadros conferidos.
- [confirmed] 13/10: avatar cortado (2.99-3.29, 12.80-13.18, 23.20-24.23), retempo 97% ("71 na Tailândia", "contou 71"); video-avatar-v2.mp4 68.6 s, -13.4 LUFS, quadros conferidos.
- [confirmed] 3 capas Codex 1080x1920 em <ed>/capa-dia/abertura.png (texto conferido), ligadas por CAPA/telas no gerar_cena.py.

## Proposto / tentado, não confirmado
- [unverified] 14/10: narração cortada (2.70-3.62, 16.20-16.69, 31.18-32.05, 39.42-42.02, 49.71-51.62), cada corte testado por Whisper em trecho; render video.mp4 rodando (task bkck9gsj4). Falta conferir quadros/LUFS.

## Decisões e restrições
- Nada de avatar novo (Nei, mid-task). Um envio ao estúdio do 14/10 já tinha saído (id em avatar/video_id-nao-usado.txt); download morto, não usar.
- Tempos de palavra do Whisper erram ~0,3 s: cortes afinados testando trechos com cs.transcrever.
- 14/10 nunca foi ao lives10 (falhou por créditos em 14/10); 13/10 = DfdtX9HbkWg e 15/10 = mtxeOkz6r2I estão no lives10. Republicar/remover no lives10 NÃO feito: precisa ok do Nei.

## Arquivos alterados
- `auto/rodar.sh`, `auto/roteiro*.md`, `CLAUDE.md` — regra (commitado).
- `motor/cortar_avatar.py`, `motor/cortar_narracao.py` — novos (não commitados).
- `edicoes/2026-10-1{3,4}-mundo-7d/`, `edicoes/2026-10-15-ultimas-24h/` — falas.json, gerar_cena.py, yt.txt, avatar/*, capa-dia/, *-original.* (backups) (não commitados).
- Fora do projeto: nenhum.

## Memória e regras duráveis tocadas
- `CLAUDE.md` do projeto — lição: palavra morte proibida.

## Verificação
- Rodado: retempo.py 15/10 → semelhança 95%, sem mort; 13/10 → 97%, sem mort (grep transcript).
- Rodado: ebur128 13/10 -13.4, 15/10 -13.7 LUFS; ffprobe 1080x1920.
- Rodado: Whisper da narração cortada do 14/10 (versão anterior) → sem "mortos".
- Não rodado: quadros/LUFS do 14/10 novo (render em curso).

## Estado em execução
- Processos em segundo plano: task bkck9gsj4 (montar.sh 14/10, log edicoes/2026-10-14-mundo-7d/build-mapa-v2.log).
- Servidores / portas: nenhum
- Worktrees / branches abertos: nenhum

## Perguntas abertas e adiados
- Aberta: republicar no lives10 (e tirar os antigos) — perguntar ao Nei.
- Aberta: outros vídeos com "mortos" só no bot (2026-10-10-el-nino-explicado, 2026-10-12-mundo-clima, 2026-10-13-semana-mundo) — perguntar se refaz.

## Próxima ação exata
Conferir quadros/LUFS do 14/10, enviar os 3 ao bot v3 (node ~/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs <mp4> "<legenda>"), commitar scripts e edições (autor inematds) + push.

## Mapa de retomada
- `CLAUDE.md` — regra e lições
- `motor/cortar_avatar.py` — como o corte foi feito
- `edicoes/2026-10-14-mundo-7d/build-mapa-v2.log` — render pendente

## Checagem de compartilhamento
- Sem segredos, tokens, cookies, dados pessoais ou endpoints privados: sim.
