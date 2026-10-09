# CLAUDE.md — eventosextremospub

Conta/autor: `inematds <inematds@gmail.com>`.

- Fluxo e regras: README.md. Fontes de clima: fontes-clima.md. APIs de clima gratuitas liberadas pelo Nei em 09/10/2026 (GIBS, Open-Meteo, INMET, CPTEC, CEMADEN, NOAA); qualquer outra API (modelos de IA, serviços pagos) precisa de autorização.
- HeyGen (avatar) gasta crédito: confirmar o custo com o Nei antes de cada render.
- Render: `GL` padrão é Vulkan; swiftshader é 30× mais lento (3 s/quadro).
- O GIBS repete o último quadro quando a hora pedida ainda não existe: `satelite_gibs.py` tira repetidos.
- Open-Meteo grátis devolve 429 se mandar muitos pontos por minuto: lotes de 40 com pausa.

## Self-learning

When I correct you, or you catch yourself making a mistake: before continuing, add the lesson as a one-line rule under ## Lessons, so it never happens again.

## Lessons

- Quadro 0 nunca pode entrar com fade: `vis()` não faz fade-in quando `ini <= 0`, e os alertas da abertura começam com `ini` negativo. A v2 de 09/10 começava com o mapa vazio. (09/10/2026)
- Abertura de vídeo de clima: data dd/mm/aaaa + número viral com fonte (pedido do Nei, 09/10/2026).
