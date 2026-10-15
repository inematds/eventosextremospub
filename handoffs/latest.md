# Handoffs — trabalhos abertos

Cada linha é um assunto em andamento: leia o snapshot do assunto que for continuar. Gravado por handoff-grava.py.

<!-- handoff-indice:inicio -->
- `refaz-viral-queimadas-itaipu` · handoffs/history/2026-10-15T185758Z-refaz-viral-queimadas-itaipu.md · 15/10 15:57
- `queimadas-reel-3d` · handoffs/history/2026-10-15T180233Z-queimadas-reel-3d.md · 15/10 15:02
- `itaipu-ruptura` · handoffs/history/2026-10-15T120855Z-itaipu-ruptura.md · 15/10 09:08
- `previsao-do-dia` · handoffs/history/2026-10-15T100300Z-previsao-do-dia.md · 15/10 07:03
- `clima24h-2026-10-15` · handoffs/history/2026-10-15T095957Z-clima24h-2026-10-15.md · 15/10 06:59
<!-- handoff-indice:fim -->

---

Cópia integral do snapshot mais recente (handoffs/history/2026-10-15T185758Z-refaz-viral-queimadas-itaipu.md):

# Handoff — 2026-10-15 (2) — Queimadas + Itaipu no explicavideo VIRAL 16:9

## Estado
- Motor explicavideos 2.10.9 (f373eeb, push): peça `colunas`, carimbo `x` (lado), base `brasil-uf`; PADRAO-VIRAL e README atualizados. Guia formatos e19341f.
- Saídas: ~/projetos/output/explica-{queimadas,itaipu}-viral; cadeia ~/projetos/output/explica-eventos-viral/pipe_viral.sh <id> <trilha> (SO_BUILD=1 só valida); lacunas.py ajuda a achar deixas; numeros_extenso.py.
- Build --strict 0 avisos e hyperframes check ok nos dois. 1º render: QA viral REPROVOU por área lisa (fundos escuros/fumaça); fundos trocados; 2º render rodando (bg), saída em <out>/pipe.out e entrega/<id>-16x9.mp4.

## Próxima ação
Ler pipe.out (APROVADO/REPROVADO). Se reprovar, agrupar quadros_vazios por tempo, mapear à cena (starts no build-v2-pt-b01.json) e trocar src. Aprovado: olhar sheet-viral-*.jpg, medir LUFS/duração, enviar ao bot v3 (refazvideo/ferramentas/enviar_bot_v3.mjs, ≤49 MB → 720p). YouTube só com ok do Nei (atuais dHYmVqPTw44 e QLoX7W8uEiY intocados).
