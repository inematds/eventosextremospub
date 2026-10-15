# Handoffs — trabalhos abertos

Cada linha é um assunto em andamento: leia o snapshot do assunto que for continuar. Gravado por handoff-grava.py.

<!-- handoff-indice:inicio -->
- `refaz-viral-queimadas-itaipu` · handoffs/history/2026-10-15T180928Z-refaz-viral-queimadas-itaipu.md · 15/10 15:09
- `refazer-sem-morte` · handoffs/history/2026-10-15T180421Z-refazer-sem-morte.md · 15/10 15:04
- `queimadas-reel-3d` · handoffs/history/2026-10-15T180233Z-queimadas-reel-3d.md · 15/10 15:02
- `itaipu-ruptura` · handoffs/history/2026-10-15T120855Z-itaipu-ruptura.md · 15/10 09:08
- `previsao-do-dia` · handoffs/history/2026-10-15T100300Z-previsao-do-dia.md · 15/10 07:03
- `clima24h-2026-10-15` · handoffs/history/2026-10-15T095957Z-clima24h-2026-10-15.md · 15/10 06:59
<!-- handoff-indice:fim -->

---

Cópia integral do snapshot mais recente (handoffs/history/2026-10-15T180928Z-refaz-viral-queimadas-itaipu.md):

# Handoff — 2026-10-15 — Queimadas + Itaipu refeitos no explicavideo VIRAL 16:9

## Pedido do Nei
Refazer queimadas e Itaipu no formato 1 (explicavideo viral 16:9): 1ª imagem impactante + título grande, imagens/gráficos tela cheia, avatar em caixa no canto. Documentar formatos no guia do explicavideos (FEITO: e19341f, #formatos PT/EN/ES).

## Estado
- Ponte sem HeyGen: ~/projetos/output/explica-eventos-viral/ponte_v1.py (avatar da edição → v1/assets/nei-pt-b01.mp4). Saídas: ~/projetos/output/explica-{queimadas,itaipu}-viral. Configs explicavideos/examples/{id}.json e {id}-v2.json.
- Em execução (bg): v1_dois.sh (render+assemble v1, whisper-local) e Codex image_gen (media/pedido.txt, 10 imagens cada, capa.png nova).
- Motor (NÃO commitado ainda): explicavideos viral.js/viral.css peça `colunas`, build_block VIRAL_TYPES+colunas, som_viral boom em colunas, mapa_geo base `brasil-uf` (biblioteca-mapas/brasil-uf/uf.geojson). Repo tem mudanças de outras sessões em build_block.py e v2.js — commitar só os hunks meus.
- Roteiros visuais: <out>/visual/gerar_visual.py (59 e 58 shots).
- numeros_extenso.py corrige algarismos do Whisper (testado: 53 trocas).
- Lições gravadas: wifi/LESSONS.md (largo inventado) e eventosextremospub/CLAUDE.md.

## Próxima ação
Quando v1 (assembled-pt.json) e imagens existirem: olhar as capas, cor_neutra.py nas imagens, `SO_BUILD=1 pipe_viral.sh queimadas-viral sombrio-pulso` até 0 avisos, depois sem SO_BUILD; folha de quadros; bot v3; repetir Itaipu (noticia-urgente). YouTube só com ok do Nei. Longrun: longrun/2026-10-15-refaz-viral-queimadas-itaipu.
