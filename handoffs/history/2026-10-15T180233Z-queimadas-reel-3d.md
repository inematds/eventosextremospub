# Handoff — 2026-10-15 — Queimadas 9:16 com mapa 3D (pedido após o 16:9 "ficou muito ruim")

## Pedido
Nei: o 16:9 das queimadas (lives10 dHYmVqPTw44) ficou ruim — mapa liso, pouco movimento; quer 3D realista. "Faça primeiro um estilo eventosextremospub 9x16 e me manda". O refazer do 16:9 é decisão posterior (perguntar antes de republicar).

## Estado aceito
- [confirmed] edicoes/2026-10-15-queimadas-reel: falas.json (6 falas, ~65 s), gerar_cena.py (Blue Marble NG do GIBS 4096 px, céu C.ceu, colunas 3D de fogo em grade 0,5° com brilho, câmera pitch 50–62 com órbita), estimar.py, avatar-e-manda.sh. Commit f1ab744 + push.
- [confirmed] motor/mapa.html: opções novas C.ceu, C.uf_cor/uf_largura, colunas[].brilho (opt-in, não afeta outras edições).
- [confirmed] prévia sem voz enviada ao bot v3 (build/previa-bot.mp4).
- [running] systemd `queimadas-reel-avatar` (estúdio HeyGen, id 5e9fb86336574cfa82f2d4344b5fd45d) → `queimadas-reel-manda` (gerar_cena --canto → compor canto → guarda de branco → bot v3, SEM YouTube). Estado: AVATAR-STATUS.txt.

## Próxima ação
Ao "fim" no AVATAR-STATUS.txt: conferir quadros do video-avatar.mp4, avisar "Terminei:" e esperar o Nei aprovar antes de publicar (lives10) ou refazer o 16:9. Não rodar dois render.mjs em paralelo (mapa sai branco).
