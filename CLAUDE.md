# CLAUDE.md — eventosextremospub

Conta/autor: `inematds <inematds@gmail.com>`.

- Fluxo e regras: README.md. Fontes de clima: fontes-clima.md. APIs de clima gratuitas liberadas pelo Nei em 09/10/2026 (GIBS, Open-Meteo, INMET, CPTEC, CEMADEN, NOAA); qualquer outra API (modelos de IA, serviços pagos) precisa de autorização.
- Avatar do Nei pelo ESTÚDIO HeyGen (assinatura) está SEMPRE liberado, sem pedir ok (Nei, 12/10/2026: "avatar no estudio nao gasta assinatura entao ta liberado sempre"); nunca pela API. O clima 24h diário sai pronto sem aprovação (avatar incluso), vai ao bot v3 e é publicado no lives10 (10/10/2026).
- Clima 24h diário automático: timer `clima24h-diario.timer` (05:30) → `auto/rodar.sh` (coleta → `claude -p` com `auto/roteiro.md` → `auto/avatar.sh` → lives10 + bot v3 → git). Log em `edicoes/<dia>-ultimas-24h/rodada.log`; pular dia em `auto/pular.txt`; teste isolado: `ED=<pasta> SEM_AVATAR=1 SEM_YT=1 SEM_BOT=1 SEM_GIT=1 auto/rodar.sh`.
- Diário 24h PREVÊ (Nei, 13/10/2026): `coleta/ultimas24h.py` grava `pesquisa/bruto/previsao7d.json` (7 dias nas capitais, chuva somada por dia/região/acumulada) e CEMADEN `soma_por_uf`; o painel aceita `grafico` (barras empilhadas + linha de temperatura, `motor/mapa.html`); o `auto/roteiro.md` exige as falas "próximos 7 dias" e "volumes somados".
- Clima da semana + 15 dias (Nei, 11/10/2026): timer `clima-semana.timer` (domingo 15:00) → `auto/rodar.sh <dia> semana` (mesmo fluxo; coleta extra `coleta/previsao15d.py` → `om/prev15_resumo.json`; prompt `auto/roteiro-semana.md` com quadro 0 provocante; dias 8–15 sempre ditos como tendência). Pasta `edicoes/<dia>-semana`; pular com a linha `AAAA-MM-DD semana` em `auto/pular.txt`. Avatar incluso, sem aprovação, como o diário.
- O clima no mundo · 7 dias APROVADO (Nei, 13/10/2026, versão com avatar de `edicoes/2026-10-13-mundo-7d`, 70 s, −13,4 LUFS): Short 9:16 com os eventos mais graves do mundo nos últimos 7 dias, priorizando as últimas 48 h; prompt `auto/roteiro-mundo.md`, modelo `edicoes/2026-10-12-amazonia-reel` (mapa do mundo, layout canto). Nome: **Clima no Mundo**. Diário às 18:00 (`clima-mundo.timer` → `auto/rodar.sh <dia> mundo`, pasta `edicoes/<dia>-mundo-7d`, sem a coleta do Brasil), publica no lives10 + bot v3, avatar incluso sem aprovação; pular com `AAAA-MM-DD mundo` em `auto/pular.txt`.
- Clima do DIA (em teste desde 13/10/2026): fonte da verdade = boletim diário do canal de meteorologia (YouTube, por volta do meio-dia), baixado e transcrito pelo inemavox; o canal NUNCA é citado e os números não precisam de conferência (Nei confia). Prompt `auto/roteiro-dia.md`; engajamento "de onde você está assistindo e como está o tempo aí"; CTA inema.club. Os outros vídeos do projeto não mudam.
- Render: `GL` padrão é Vulkan; swiftshader é 30× mais lento (3 s/quadro).
- O GIBS repete o último quadro quando a hora pedida ainda não existe: `satelite_gibs.py` tira repetidos.
- Open-Meteo grátis devolve 429 se mandar muitos pontos por minuto: lotes de 40 com pausa.

## Self-learning

When I correct you, or you catch yourself making a mistake: before continuing, add the lesson as a one-line rule under ## Lessons, so it never happens again.

## Lessons

- 16:9 "largo" SEM avatar: `"coluna": True` na cena (cards e manchete na coluna da direita, mapa livre à esquerda); sem isso a coluna do avatar fica vazia e todo card cai em cima do mapa. Reel 9:16 sem avatar: `padding_topo` ~560 desce o mapa para baixo dos cards. O Nei reprovou o Amazônia e o mundo (12/10/2026).
- Fogo na Amazônia: 2024 NÃO é recorde de focos (140 mil; 2004 teve 218 mil) — é o "pior ano desde 2007"; antes de chamar um ano de recorde, contar a série sat_ref desde 2003. Mínima do Rio Negro em 2024 diverge (12,11 m Portal Amazônia × 12,26 m tabela SGB): dizer "pouco acima de 12 m". Quase saiu errado no Amazônia e o mundo (12/10/2026).
- Tratar por "você" (nunca "tu/teu/ti/te prepara") e CTA SEMPRE só o inema.club — nada de "segue o canal", vídeo longo ou canal do YouTube; o portão (checar.py / rodar.sh) reprova. (Nei, 11/10/2026)
- Quadro 0 nunca pode entrar com fade: `vis()` não faz fade-in quando `ini <= 0`, e os alertas da abertura começam com `ini` negativo. A v2 de 09/10 começava com o mapa vazio. (09/10/2026)
- Abertura de vídeo de clima: data dd/mm/aaaa + número viral com fonte (pedido do Nei, 09/10/2026).
- A voz do HeyGen chega ~-26 dB: o compor_avatar.sh normaliza a -14 LUFS (loudnorm) antes de mixar. O Alerta NNE com avatar saiu a -20,8 LUFS (voz baixa). Medir com `ebur128` antes de enviar. (09/10/2026)
- Notícia de clima é só Short 9:16 (sem versão longa/16:9); explicação longa (3–5 min, ex. El Niño) é 16:9. Link do YouTube: `youtube.com/shorts/<id>` — o `watch?v=` abre no player largo e parece 16:9. (10/10/2026)
- Clima/evento extremo: nunca termo positivo ou de alívio ("por sorte", "felizmente", "melhor") ao falar de tragédia; a pergunta de comentário é SEMPRE "de que região/cidade você é?" e o fecho é "No inema.club você pode aprender sobre inteligência artificial" (sem "painel de chuva", "alerta", "curso pra você"). O portão do rodar.sh reprova os termos. Valeu pro Mundo e clima (12/10) e Amazônia e o mundo. (Nei, 13/10/2026)
