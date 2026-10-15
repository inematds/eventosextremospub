# Handoff — 2026-10-15 — refazer 3 vídeos sem a palavra morte (fechado)

## Projeto e escopo
eventosextremospub, raiz ~/projetos/eventosextremospub. Refazer os 3 vídeos que falavam em morte cortando a fala (sem avatar novo), "vítimas" na tela, capa de impacto no quadro 0, enviar ao bot v3.

## Objetivo atual
Concluído.

## Estado aceito
- [confirmed] Regra: portão no auto/rodar.sh + linha em auto/roteiro*.md + CLAUDE.md (f53e07e).
- [confirmed] Enviados ao bot v3: 13/10 video-avatar-v2.mp4 (msg 1314), 14/10 video-v2.mp4 (1316), 15/10 video-avatar-v2.mp4 (1318). Commit 0c01312, push feito.

## Proposto / tentado, não confirmado
- nenhum

## Decisões e restrições
- Sem avatar novo; o envio ao estúdio do 14/10 ficou sem uso (avatar/video_id-nao-usado.txt).
- lives10: não republicado nem removido; depende do Nei.

## Arquivos alterados
- `motor/cortar_avatar.py`, `motor/cortar_narracao.py`, `CLAUDE.md`, `FALHAS.md`, edições 13/14 mundo-7d e 15 ultimas-24h.
- Fora do projeto: nenhum

## Memória e regras duráveis tocadas
- `CLAUDE.md` — palavra morte proibida; testar cortes transcrevendo o trecho.

## Verificação
- Rodado: retempo/Whisper nos 3 → sem "mort*"; ebur128 13/10 -13.4, 14/10 -14.9, 15/10 -13.7 LUFS; quadros conferidos.

## Estado em execução
- nenhum

## Perguntas abertas e adiados
- Aberta: republicar no lives10 e tirar DfdtX9HbkWg / mtxeOkz6r2I (remoção exige ok individual).
- Aberta: el-nino-explicado, mundo-clima 12/10 e semana-mundo 13/10 (só no bot) também falam "mortos".

## Próxima ação exata
Aguardar resposta do Nei sobre lives10 e os outros 3 vídeos.

## Mapa de retomada
- `CLAUDE.md`
- `motor/cortar_avatar.py`

## Checagem de compartilhamento
- Sem segredos ou dados pessoais: sim.
