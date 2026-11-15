# IA independente por etapa

Cada modo de clima e cada correção tem uma entrada em `auto/ia.yaml`. Edite tipo, motor, modelo e esforco; as alternativas estão documentadas com #. O cron lê a configuração em cada execução, sem reiniciar timer.

```bash
python3 auto/ia_motor.py ver
python3 auto/ia_motor.py validar
python3 auto/ia_motor.py configurar roteiro_mundo --tipo assinatura --motor claude --modelo claude-opus-5-5 --esforco high
python3 auto/ia_motor.py configurar roteiro_mundo --tipo assinatura --motor codex --modelo gpt-6.1-sol --esforco medium
```

Os roteiristas também pesquisam, geram código e executam render. Por isso estas etapas exigem assinatura Claude/Codex com ferramentas; API de texto não executa esse contrato e é recusada antes de ler chaves. Adaptadores de API existem para futuros contratos de texto/visão isolados, mas todas as APIs de modelos ficam desativadas neste projeto. As APIs de clima já autorizadas são preservadas. Não há fallback pago.

Operação: Codex assinatura em todos os roteiros/correções e Metricool. Imagens continuam Codex image_gen; avatar continua no estúdio HeyGen. Publicação YouTube permanece yt-pubx lives10. Preservados horários, validação de avatar obrigatório, tom, duração, palavras proibidas, portão visual Sul e filas de recursos. Cada etapa registra tipo/modelo/esforço/duração em ia-execucoes.jsonl na edição, sem credenciais.

Metricool usa o perfil ~/.codex-2 e o conector metricool-inematds, conta inematds@gmail.com, exclusivamente marca eventosextremos (Instagram/TikTok eventos.extremos). A escolha das redes e o avatar obrigatório continuam no publicador. Trava por marca cobre consulta, agendamento e recibo; intervalo de uma hora mantido por cópia local do validador, com o mesmo registro compartilhado. A consulta sem sucesso impede o agendamento. Nunca usar marca inema.tds para o clima.

Validação 15/11/2026: cinco testes locais passaram; teste real Codex criou e releu arquivo isolado; teste real MCP confirmou conta e marca eventosextremos/7800440, somente leitura. Evidências em `~/projetos/output/crons-multiprovedor-2026-11-15/clima-agente/` e `clima-metricool/`. Não foi feita uma nova produção completa de clima nem publicação neste teste.

A ingestão de vídeo recebe uma cópia social 720p compactada na fila de render, preservando o master. A URL pública GitHub é resolvida antes de chamar o MCP; links assinados não entram nos recibos/documentação.
