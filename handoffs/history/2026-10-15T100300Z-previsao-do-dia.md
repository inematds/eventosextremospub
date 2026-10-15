# Handoff — 2026-10-15 — Previsão do Dia (novo modo diário 10:00) + piloto + teto de 3 h no claude -p

## Projeto e escopo
eventosextremospub (~/projetos/eventosextremospub), sessão aberta em ~/projetos/wifi. O Nei pediu: todo dia às 10:00 pegar o último vídeo do canal de previsão (YouTube UCGEnQh_FXX9Qny0BqmUbZ2g, Piter Scheuer) e fazer o Short "Previsão do Dia" no padrão do Clima do DIA, publicar no lives10 e mandar ao bot v3; piloto hoje, automático a partir de 16/10. Depois: tabela de horários no painel e teto de 3 h no claude -p dos sistemas com HeyGen.

## Objetivo atual
Piloto de 15/10 chegar ao bot v3 e ao lives10; a partir de 16/10 a rodada das 10:00 sai sozinha.

## Estado aceito
- [confirmed] Modo `previsao` em `auto/rodar.sh` (pasta `edicoes/<dia>-previsao-do-dia`, trava espera até 6 h, `SEM_TRAVA=1` para piloto) — commits 729d572, 4a2475f
- [confirmed] `auto/fonte-previsao.sh`: prefere vídeo de hoje (espera até 12:00), senão o de ontem não usado; usados em `auto/previsao-usados.txt`; `FONTE_ID` força
- [confirmed] `auto/roteiro-previsao.md` (prompt do claude -p), regra no `CLAUDE.md`
- [confirmed] Timer `previsao-dia.timer` 10:00 instalado em ~/.config/systemd/user; parado hoje de propósito, religado por `previsao-religa.timer` (systemd-run, 15/10 10:05)
- [confirmed] claude -p com `timeout 10800` em eventosextremospub (rodar.sh, validar.sh), finviral, saudeviral, advviral; serviços clima* 12h, *viral-diario 10h — commits bc4bf34, 4c08822, 63855de, c4565d8 (push feito)
- [confirmed] ccdashboard: aba Agenda com "Horários fixos por projeto" — commit a003aa6, telemetria-painel reiniciado

## Proposto / tentado, não confirmado
- [?] Piloto Previsão do Dia (unit `previsao-piloto`, FONTE_ID=-J80lLzxgGc): em 06:57 estava transcrevendo; resto (claude -p, avatar, lives10, bot) não visto
- [?] Clima 24h de hoje: claude -p cortado às 07:02 pelo limite antigo de 90 min; falas.json já tem o roteiro corrigido; seguiu para o avatar. Se o avatar falhar, publica a versão mapa antiga (com 3 erros apontados pelo próprio claude -p). Ver handoff `clima24h-2026-10-15` de outra sessão.

## Decisões e restrições
- Previsão do Dia e Clima do DIA coexistem (Nei: abordagens diferentes)
- Canal-fonte nunca citado; avatar pelo estúdio HeyGen liberado sem aprovação
- Hoje não roda às 10:00 (o piloto substitui); não usar pular.txt para isso
- Edição de rodar.sh em execução: sempre cópia + mv (nunca in-place)

## Arquivos alterados
- `auto/rodar.sh`, `auto/validar.sh`, `auto/fonte-previsao.sh`, `auto/roteiro-previsao.md`, `auto/previsao-usados.txt`, `auto/systemd/previsao-dia.{service,timer}`, `auto/systemd/clima*.service`, `CLAUDE.md`
- `auto/roteiro-ventos.md` — pré-existente (outra sessão, 13/10), entrou no commit bc4bf34 sem querer
- Fora do projeto: `~/projetos/ccdashboard/telemetria/painel/{servidor.py,painel.html}`; `~/projetos/{finviral,saudeviral,advviral}/auto/rodar.sh` e `systemd/*-diario.service`; `~/.config/systemd/user/{previsao-dia.*,clima*.service,*viral-diario.service}`

## Memória e regras duráveis tocadas
- `CLAUDE.md` do projeto — bullet "Previsão do Dia"

## Verificação
- Rodado: `SO_ESCOLHER=1 ESPERA=06:00 auto/fonte-previsao.sh` → escolheu -J80lLzxgGc (ontem); com o id em usados → exit 3
- Rodado: `bash -n` nos rodar.sh alterados → ok; `node --check` no JS do painel → ok; screenshot da aba Agenda → tabela renderiza
- Rodado: API /api/agenda → 5 linhas do eventosextremospub com horários certos
- Não rodado: fluxo completo da Previsão do Dia (é o piloto em andamento)

## Estado em execução
- `systemctl --user status previsao-piloto` — piloto (log `edicoes/2026-10-15-previsao-do-dia/rodada.log`)
- `previsao-religa.timer` — religa previsao-dia.timer às 10:05 de 15/10
- clima24h-diario (PID 3388673) em avatar; saudeviral e queimadas-amazonia de outras sessões
- Painel telemetria: 127.0.0.1 / 192.168.2.99:8766

## Perguntas abertas e adiados
- Aberta: Nei quer que se segure a publicação do Clima 24h se cair na versão mapa antiga? (ofertado, sem resposta)
- Adiado: commit automático do rodar.sh falha com `git pull --rebase` quando há mudanças não staged no repo

## Próxima ação exata
Acompanhar `edicoes/2026-10-15-previsao-do-dia/rodada.log` até "publicado no lives10" e avisar o Nei; se falhar, ler o motivo e corrigir. Conferir em 16/10 10:00 que a rodada automática partiu.

## Mapa de retomada
- `CLAUDE.md` — regra da Previsão do Dia
- `auto/rodar.sh` — modo previsao
- `auto/fonte-previsao.sh` — escolha da fonte
- `edicoes/2026-10-15-previsao-do-dia/rodada.log` — piloto

## Checagem de compartilhamento
- Sem segredos, tokens, cookies, dados pessoais ou endpoints privados: sim (IP de LAN do painel apenas)
