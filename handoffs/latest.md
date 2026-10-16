# Handoffs — trabalhos abertos

Cada linha é um assunto em andamento: leia o snapshot do assunto que for continuar. Gravado por handoff-grava.py.

<!-- handoff-indice:inicio -->
- `clima24h-2026-10-16` · handoffs/history/2026-10-16T210158Z-clima24h-2026-10-16.md · 16/10 18:01
- `viral-916` · handoffs/history/2026-10-16T010020Z-viral-916.md · 15/10 22:00
- `refaz-viral-queimadas-itaipu` · handoffs/history/2026-10-15T185758Z-refaz-viral-queimadas-itaipu.md · 15/10 15:57
- `queimadas-reel-3d` · handoffs/history/2026-10-15T180233Z-queimadas-reel-3d.md · 15/10 15:02
- `itaipu-ruptura` · handoffs/history/2026-10-15T120855Z-itaipu-ruptura.md · 15/10 09:08
- `previsao-do-dia` · handoffs/history/2026-10-15T100300Z-previsao-do-dia.md · 15/10 07:03
- `clima24h-2026-10-15` · handoffs/history/2026-10-15T095957Z-clima24h-2026-10-15.md · 15/10 06:59
<!-- handoff-indice:fim -->

---

Cópia integral do snapshot mais recente (handoffs/history/2026-10-16T210158Z-clima24h-2026-10-16.md):

# Handoff — Clima 24 h de 16/10/2026 (rodada automática, claude -p)

## Projeto e escopo
eventosextremospub, edição `edicoes/2026-10-16-ultimas-24h` (Short 9:16). Só os arquivos da edição; avatar, YouTube, bot e git ficam com `auto/rodar.sh`.

## Objetivo atual
Entregar falas.json, gerar_cena.py, tempos.json, video.mp4 (versão mapa / plano B) e yt.txt para o rodar.sh seguir com o HeyGen e a publicação.

## Estado aceito
- [confirmed] video.mp4 1080x1920, 95,7 s, renderizado com GEO=geo-br.js motor/montar.sh; 14 quadros conferidos (contadores 29/65/86,8/92,8/569/563/7.435; data na abertura; pino de Viracopos fora do painel).
- [confirmed] falas.json com 11 falas e 225 palavras; inclui "Os próximos 7 dias" e "Volumes somados"; pergunta + CTA inema.club; pausa de 1 s antes da pergunta (pausa_pergunta.py).
- [confirmed] Capa do Codex (assinatura) em capa-dia/abertura.png: "ENXURRADA EM SÃO PAULO · 29 CARROS ARRASTADOS".
- [confirmed] gerar_cena.py --canto roda sem erro (testado com tempos.json copiado; cópia apagada e cena.js cheio refeito).
- [confirmed] Portão de palavras (tu/melhor/morte/SMS) limpo em falas.json, gerar_cena.py e yt.txt; título com 77 caracteres.
- [confirmed] pesquisa/noticias.md, dados.md e proposta.md gravados.

## Proposto / tentado, não confirmado
- [unverified] Avatar HeyGen, publicação no lives10 e envio ao bot v3: fase do rodar.sh, fora desta sessão.

## Decisões e restrições
- CEMADEN Mauá/Vila Magini (391,8) e Visconde do Rio Branco (275,8) descartados e fora das somas: SP 7.435,8 ("mais de 7.400", 414 estações); Brasil 20.638 ("mais de 20 mil").
- Campo Grande 86,8 mm atribuído à Prefeitura (via A Crítica) e dito "temporal de quinta": pelo METAR SBCG, o grosso caiu em 15/10 à tarde, antes da janela.
- Calor (Petrolina 39 °C) cortado para caber no tempo.
- f9 reescrita para o número 788 não ficar na última palavra, porque a narração cortava "e oito".

## Arquivos alterados
- edicoes/2026-10-16-ultimas-24h/: falas.json, gerar_cena.py (+ gerar_cena-original.py), tempos.json, narracao.wav, cena.js, video.mp4, yt.txt, capa-dia/, sat/web/mundo.jpg (copiado de 15/10), pesquisa/*.md, build-*.log.
- FALHAS.md: linha do corte da narração no número final.
- Fora do projeto: ~/projetos/wifi/LIMITES.md, linha do HTTP 403 da Midiamax.

## Memória e regras duráveis tocadas
- Nenhuma memória nova. Regra candidata: número nunca como última palavra da fala.

## Verificação
- ffprobe → 1080,1920 · 95.71 s; gerar_cena.py e --canto → "cena.js ok"; quadros em /tmp/q1610/.

## Próxima ação
Nenhuma pendente nesta sessão: o rodar.sh segue com avatar → lives10 → bot v3 → git. Se o avatar falhar, video.mp4 é o plano B.
