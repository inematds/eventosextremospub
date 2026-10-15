# Handoffs — trabalhos abertos

Cada linha é um assunto em andamento: leia o snapshot do assunto que for continuar. Gravado por handoff-grava.py.

<!-- handoff-indice:inicio -->
- `queimadas-reel-3d` · handoffs/history/2026-10-15T180233Z-queimadas-reel-3d.md · 15/10 15:02
- `itaipu-ruptura` · handoffs/history/2026-10-15T120855Z-itaipu-ruptura.md · 15/10 09:08
- `previsao-do-dia` · handoffs/history/2026-10-15T100300Z-previsao-do-dia.md · 15/10 07:03
- `clima24h-2026-10-15` · handoffs/history/2026-10-15T095957Z-clima24h-2026-10-15.md · 15/10 06:59
<!-- handoff-indice:fim -->

---

Cópia integral do snapshot mais recente (handoffs/history/2026-10-15T180233Z-queimadas-reel-3d.md):

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
