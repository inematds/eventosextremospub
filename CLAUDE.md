# CLAUDE.md — eventosextremospub

Conta/autor: `inematds <inematds@gmail.com>`.

- Fluxo e regras: README.md. Fontes de clima: fontes-clima.md. APIs de clima gratuitas liberadas pelo Nei em 09/10/2026 (GIBS, Open-Meteo, INMET, CPTEC, CEMADEN, NOAA); qualquer outra API (modelos de IA, serviços pagos) precisa de autorização.
- HeyGen (avatar) gasta crédito: confirmar o custo com o Nei antes de cada render. Exceção (Nei, 10/10/2026): o clima 24h diário sai pronto sem aprovação (avatar incluso), vai ao bot v3 e é publicado no lives10.
- Render: `GL` padrão é Vulkan; swiftshader é 30× mais lento (3 s/quadro).
- O GIBS repete o último quadro quando a hora pedida ainda não existe: `satelite_gibs.py` tira repetidos.
- Open-Meteo grátis devolve 429 se mandar muitos pontos por minuto: lotes de 40 com pausa.

## Self-learning

When I correct you, or you catch yourself making a mistake: before continuing, add the lesson as a one-line rule under ## Lessons, so it never happens again.

## Lessons

- Quadro 0 nunca pode entrar com fade: `vis()` não faz fade-in quando `ini <= 0`, e os alertas da abertura começam com `ini` negativo. A v2 de 09/10 começava com o mapa vazio. (09/10/2026)
- Abertura de vídeo de clima: data dd/mm/aaaa + número viral com fonte (pedido do Nei, 09/10/2026).
- A voz do HeyGen chega ~-26 dB: o compor_avatar.sh normaliza a -14 LUFS (loudnorm) antes de mixar. O Alerta NNE com avatar saiu a -20,8 LUFS (voz baixa). Medir com `ebur128` antes de enviar. (09/10/2026)
- Notícia de clima é só Short 9:16 (sem versão longa/16:9); explicação longa (3–5 min, ex. El Niño) é 16:9. Link do YouTube: `youtube.com/shorts/<id>` — o `watch?v=` abre no player largo e parece 16:9. (10/10/2026)
