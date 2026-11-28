# Handoff — Rede INEMA /parceiros (portal + agente + divulgação) · 28/11/2026

## Objetivo
Página inema.club/parceiros (Rede INEMA) com visual profissional, página de cada parceiro só dele, 3 idiomas, e divulgação no Telegram.

## Feito (tudo com push)
- Portal (NeiMaldaner/portal, autor NeiMaldaner): último push 38568ef. Lista = capa com busca de verdade (filtra a vitrine) + painel com a cena Codex `public/doc/rede/capa-rede-painel.jpg`; vitrine larga "quem já está"; para membros (checagem), passos, critérios, FAQ em duas colunas. Página do parceiro só dele (sem cena nossa, sem convite INEMA; foto só se o parceiro tiver). Menu `src/components/rede/MenuRede.tsx`: uma faixa "🤝 Parceiros | INEMA.CLUB - PRO" + PT EN ES, só nas páginas da Rede (menu global do portal foi removido: "complicou"). CSS `src/components/rede/rede.css` (classes rd-*). Textos em `src/data/rede-pagina.json` (blocos `vitrine`, `capa`). Notas no CLAUDE.md do portal (seção Rede INEMA).
- Agente da Rede (inematds/rede-inema-pro): `agente/traduz.mjs` traduz EN/ES pelo inema-traduz com cache (dados/traducoes); `agente/divulga.mjs` dispara UMA vez a divulgação para NÃO membros quando houver >10 empresas no ar (autorizado pelo Nei: "pode mandar direto"), via rota do Enviar Agora do TLGruposVIP + aviso no v3; trava em dados/divulgacao-nao-membros.json + nome no banco. Testes 25/25; teste.mjs corrigido (gravava na pasta real — FALHAS.md). Commits 6047f71, 62e2a66, 0be289c.
- Telegram: tópico publicado no INEMA.VIP https://t.me/c/2405283087/35043 (MENU 306). Texto: ~/projetos/output/posts-telegram/2026-11-28-rede-inema.md (1ª msg informal backlink/SEO/GEO/AEO/WebMCP + só o link https://eventos.inema.pro/inemaseo/; 2ª o post). Capa pública: inematds.github.io/rede-inema/guia/assets/divulgacao-rede.jpg.
- TLGruposVIP: campanha de DM para membros em RASCUNHO, 365 assinantes, 2 mensagens, id 92e64baf-ece4-411f-8068-21e55475d022 (script scripts/preparar-rede-inema-20261128.js, relatório docs/RELATORIO_CAMPANHA_REDE_INEMA_20261128.md, commit 6392f3c).

## Pendente / decisão do Nei
1. Disparar a campanha dos 365 membros: Nei pelo painel (Envio → Enviar Agora) OU autorizar disparo daqui. Pergunta feita, sem resposta.
2. Proteger a rota pública /api/envio do TLGruposVIP com chave (está em publicRoutes do middleware; qualquer um com o id dispara). Perguntado, sem resposta.
3. Nei ainda não aprovou o visual final no ar; última crítica atendida: menu na ordem dos projetos.

## Não fazer
- Não editar src/data/parceiros.json à mão (gerado pelo agente).
- Não disparar campanha sem autorização; não consultar Vercel; commits do portal com autor NeiMaldaner.
- Página do parceiro sem conteúdo promocional do INEMA.

## Verificação
Roteiro de conferência usado: playwright de ~/projetos/agent-browser/node_modules, `next start -p 3417`, medir scrollWidth == viewport e margens esquerda/direita iguais (.rd-capa-g, .rd-p-capa h1, .rd-historia).


<!-- handoff-estado:inicio -->
## Estado gravado pelo script (não editar)

Gravado por handoff-grava.py no momento do handoff. `--conferir` compara com o projeto agora.

- commit: 5431f88aa0673c0720733f261f8ae63145c61ca8 · branch: main
- arquivos sujos fora de handoffs/: 41172 (lista cortada)
- `"edicoes/2026-10-23-mundo-7d/pesquisa/bruto/gn_DANA_Adam_v\303\255ctimas.xml"` · sha256:apagado · sujo
- `"edicoes/2026-10-23-mundo-7d/pesquisa/bruto/gn_temp\303\252te_Austen.xml"` · sha256:apagado · sujo
- `"edicoes/2026-10-24-mundo-7d/pesquisa/bruto/gn_temp\303\252te_Austen.xml"` · sha256:apagado · sujo
- `"edicoes/2026-10-25-mundo-7d/pesquisa/bruto/gn_temp\303\252te_Austen.xml"` · sha256:apagado · sujo
- `"edicoes/2026-11-06-mundo-7d/pesquisa/bruto/gn_Ecuador_r\303\255os_desbordados.xml"` · sha256:apagado · sujo
- `"edicoes/2026-11-07-mundo-7d/pesquisa/bruto/gn_Ecuador_r\303\255os_desbordados.xml"` · sha256:apagado · sujo
- `"edicoes/2026-11-08-mundo-7d/pesquisa/bruto/gn_Ecuador_r\303\255os_desbordados.xml"` · sha256:apagado · sujo
- `"edicoes/2026-11-15-semana/pesquisa/quadros/legenda-mil\303\255metros.jpg"` · sha256:apagado · sujo
- `"edicoes/2026-11-15-semana/pesquisa/quadros/legenda-quil\303\264metros.jpg"` · sha256:apagado · sujo
- `"edicoes/2026-11-25-mundo-7d/quadros/pino-sul-da-tail\303\242ndia.png"` · sha256:apagado · sujo
- `FALHAS.md` · sha256:c18f6a740e48 · sujo
- `auto/ia.yaml.antes-claude-20261124` · sha256:a348d65c5aa5 · sujo
- `auto/ia.yaml.antes-claude-20261124.antes-niveis-20261124` · sha256:85911659fa09 · sujo
- `auto/ia.yaml.antes-niveis-20261124` · sha256:a44765223c51 · sujo
- `auto/ia_motor.py.antes-niveis-20261124` · sha256:de4a441507cb · sujo
- `auto/previsao-usados.txt` · sha256:e5fdbdfc2581 · sujo
- `auto/roteiro-semana.md` · sha256:e453440e4ede · sujo
- `auto/roteiro-sul.md` · sha256:a30f4d1006d0 · sujo
- `edicoes/2026-10-09-alerta-norte-nordeste/video-avatar.mp4.envio-v3.json` · sha256:d3fec43b751f · sujo
- `edicoes/2026-10-09-alerta-norte-nordeste/video.mp4.envio-v3.json` · sha256:356bde79342d · sujo
- `edicoes/2026-10-09-el-nino/avatar/foto.jpg` · sha256:4a387696d84d · sujo
- `edicoes/2026-10-09-el-nino/fonte/painel-el-nino-4.pdf` · sha256:8058947c242b · sujo
- `edicoes/2026-10-09-el-nino/previa-16x9.mp4.envio-v3.json` · sha256:152d7f71b582 · sujo
- `edicoes/2026-10-09-el-nino/previa.mp4.envio-v3.json` · sha256:c99530b92148 · sujo
- `edicoes/2026-10-09-el-nino/sat/web/anomalia.png` · sha256:87c7e4f6737b · sujo
- `edicoes/2026-10-09-el-nino/video-avatar.mp4.envio-v3.json` · sha256:74c69c4a617b · sujo
- `edicoes/2026-10-10-el-nino-explicado/avatar/video_id.txt` · sha256:7bd8bef1f42e · sujo
- `edicoes/2026-10-10-el-nino-explicado/sat/web/anomalia.png` · sha256:3cf05867665b · sujo
- `edicoes/2026-10-10-el-nino-explicado/video-avatar-bot.mp4.envio-v3.json` · sha256:c222bf494599 · sujo
- `edicoes/2026-10-10-ultimas-24h/sat/web/ir_tempos.json` · sha256:0093b9fbcc3b · sujo
- `edicoes/2026-10-10-ultimas-24h/video-avatar.mp4.envio-v3.json` · sha256:93d5275dc291 · sujo
- `edicoes/2026-10-10-ultimas-24h/video.mp4.envio-v3.json` · sha256:3b73ea0d4b44 · sujo
- `edicoes/2026-10-11-semana/om/prev15_capitais.json` · sha256:de2d6ea61b90 · sujo
- `edicoes/2026-10-11-semana/om/prev15_grade.json` · sha256:a12abf1c36ec · sujo
- `edicoes/2026-10-11-semana/pesquisa/bruto/cemaden_getJson2_todas_ufs.json` · sha256:024651b3971b · sujo
- `edicoes/2026-10-11-semana/pesquisa/bruto/inmet_avisos_ativos.json` · sha256:70740ae45e49 · sujo
- `edicoes/2026-10-11-semana/pesquisa/bruto/inmet_estacoes_tentativas.json` · sha256:8139abb88947 · sujo
- `edicoes/2026-10-11-semana/pesquisa/bruto/noaa_metar_brasil_24h.json` · sha256:ed0d7c1f0a1f · sujo
- `edicoes/2026-10-11-semana/pesquisa/bruto/openmeteo_capitais_3d.json` · sha256:06611266fcbb · sujo
- `edicoes/2026-10-11-semana/sat/web/ir_tempos.json` · sha256:e5c7c26860b8 · sujo
- `edicoes/2026-10-11-semana/video-avatar.mp4.envio-v3.json` · sha256:2735f7759277 · sujo
- `edicoes/2026-10-11-ultimas-24h/pesquisa/bruto/cemaden_getJson2_todas_ufs.json` · sha256:b14ba84c80c4 · sujo
- `edicoes/2026-10-11-ultimas-24h/pesquisa/bruto/inmet_avisos_ativos.json` · sha256:7a36901321eb · sujo
- `edicoes/2026-10-11-ultimas-24h/pesquisa/bruto/inmet_estacoes_tentativas.json` · sha256:b33519abe086 · sujo
- `edicoes/2026-10-11-ultimas-24h/pesquisa/bruto/noaa_metar_brasil_24h.json` · sha256:d4d660256cf4 · sujo
- `edicoes/2026-10-11-ultimas-24h/pesquisa/bruto/openmeteo_capitais_3d.json` · sha256:d5c28f4d9663 · sujo
- `edicoes/2026-10-11-ultimas-24h/sat/web/ir_tempos.json` · sha256:9898057fe396 · sujo
- `edicoes/2026-10-11-ultimas-24h/video-avatar.mp4.envio-v3.json` · sha256:ebbd75b5e6b0 · sujo
- `edicoes/2026-10-12-amazonia-mundo/AVATAR-STATUS.txt` · sha256:58973896896b · sujo
- `edicoes/2026-10-12-amazonia-mundo/avatar/APROVADO_HEYGEN` · sha256:f5f47743b1d3 · sujo
- `edicoes/2026-10-12-amazonia-mundo/avatar/video_id.txt` · sha256:8d2b0205a515 · sujo
- `edicoes/2026-10-12-amazonia-mundo/video-avatar-bot.mp4.envio-v3.json` · sha256:3c7806a71744 · sujo
- `edicoes/2026-10-12-amazonia-mundo/video-bot.mp4.envio-v3.json` · sha256:005b1a70c6df · sujo
- `edicoes/2026-10-12-amazonia-reel/avatar/APROVADO_HEYGEN` · sha256:f5f47743b1d3 · sujo
- `edicoes/2026-10-12-amazonia-reel/avatar/video_id.txt` · sha256:fb51897b4973 · sujo
- `edicoes/2026-10-12-amazonia-reel/video-avatar.mp4.envio-v3.json` · sha256:06e8b61ab915 · sujo
- `edicoes/2026-10-12-amazonia-reel/video.mp4.envio-v3.json` · sha256:a9e6d3e9b0fa · sujo
- `edicoes/2026-10-12-mundo-clima/AVATAR-STATUS.txt` · sha256:f73b37dbbcd3 · sujo
- `edicoes/2026-10-12-mundo-clima/avatar/APROVADO_HEYGEN` · sha256:f5f47743b1d3 · sujo
- `edicoes/2026-10-12-mundo-clima/avatar/fala.txt` · sha256:f8371ab6656c · sujo
- `edicoes/2026-10-12-mundo-clima/avatar/tempos.json` · sha256:45957a78d8ba · sujo
- `edicoes/2026-10-12-mundo-clima/avatar/video_id.txt` · sha256:2e18a64b6eee · sujo
- `edicoes/2026-10-12-mundo-clima/sat/web/anomalia.png` · sha256:93a6cd64b51a · sujo
- `edicoes/2026-10-12-mundo-clima/video-avatar-bot.mp4.envio-v3.json` · sha256:605d104a4328 · sujo
- `edicoes/2026-10-12-ultimas-24h/pesquisa/bruto/cemaden_getJson2_todas_ufs.json` · sha256:cc4897ad649e · sujo
- `edicoes/2026-10-12-ultimas-24h/pesquisa/bruto/inmet_avisos_ativos.json` · sha256:28bd35263839 · sujo
- `edicoes/2026-10-12-ultimas-24h/pesquisa/bruto/inmet_estacoes_tentativas.json` · sha256:7b901359f016 · sujo
- `edicoes/2026-10-12-ultimas-24h/pesquisa/bruto/noaa_metar_brasil_24h.json` · sha256:0748fabcb069 · sujo
- `edicoes/2026-10-12-ultimas-24h/pesquisa/bruto/openmeteo_capitais_3d.json` · sha256:a9d4ee964f96 · sujo
- `edicoes/2026-10-12-ultimas-24h/sat/web/ir_tempos.json` · sha256:848644d2d9b0 · sujo
- `edicoes/2026-10-12-ultimas-24h/video-avatar.mp4.envio-v3.json` · sha256:7600d935ee46 · sujo
- `edicoes/2026-10-13-24h-foto/avatar/APROVADO_HEYGEN` · sha256:f5f47743b1d3 · sujo
- `edicoes/2026-10-13-24h-foto/avatar/fala.txt` · sha256:35f7d5d5085f · sujo
- `edicoes/2026-10-13-24h-foto/avatar/retempo.py` · sha256:41e4acfe252f · sujo
- `edicoes/2026-10-13-24h-foto/avatar/tempos.json` · sha256:e756e0286f71 · sujo
- `edicoes/2026-10-13-24h-foto/avatar/video_id.txt` · sha256:8846c538f621 · sujo
- `edicoes/2026-10-13-24h-foto/falas.json` · sha256:bd7cacaca636 · sujo
- `edicoes/2026-10-13-24h-foto/gerar_cena.py` · sha256:a628ff9fa682 · sujo
- `edicoes/2026-10-13-24h-foto/narrar.py` · sha256:b2dc0ad38dc1 · sujo
- `edicoes/2026-10-13-24h-foto/pesquisa/bruto/cemaden_getJson2_todas_ufs.json` · sha256:8d45b4a93ef9 · sujo
- `edicoes/2026-10-13-24h-foto/pesquisa/bruto/inmet_avisos_ativos.json` · sha256:73ddac0caa79 · sujo
- `edicoes/2026-10-13-24h-foto/pesquisa/bruto/inmet_estacoes_tentativas.json` · sha256:802a051b6c1e · sujo
- `edicoes/2026-10-13-24h-foto/pesquisa/bruto/noaa_metar_brasil_24h.json` · sha256:47173b7139ce · sujo
- `edicoes/2026-10-13-24h-foto/pesquisa/bruto/openmeteo_capitais_3d.json` · sha256:36bf59ffe2e2 · sujo
- `edicoes/2026-10-13-24h-foto/pesquisa/bruto/previsao7d.json` · sha256:a6412fc8a1cb · sujo
- `edicoes/2026-10-13-24h-foto/pesquisa/bruto/resumo.json` · sha256:474fd69f9176 · sujo
- `edicoes/2026-10-13-24h-foto/pesquisa/dados.md` · sha256:508e8bad69eb · sujo
- `edicoes/2026-10-13-24h-foto/pesquisa/noticias.md` · sha256:b71c6c80d7af · sujo
- `edicoes/2026-10-13-24h-foto/pesquisa/proposta.md` · sha256:0bccc7e17577 · sujo
- `edicoes/2026-10-13-24h-foto/previa/avatar/foto.png` · sha256:b73f7ef0c365 · sujo
- `edicoes/2026-10-13-24h-foto/previa/avatar/tempos.json` · sha256:716d08429e04 · sujo
- `edicoes/2026-10-13-24h-foto/previa/cena.js` · sha256:d230ba23e43c · sujo
- `edicoes/2026-10-13-24h-foto/previa/gerar_cena.py` · sha256:a628ff9fa682 · sujo
- `edicoes/2026-10-13-24h-foto/sat/web/ir_tempos.json` · sha256:a3a07cc5dacf · sujo
- `edicoes/2026-10-13-24h-foto/tempos.json` · sha256:716d08429e04 · sujo
- `edicoes/2026-10-13-24h-foto/video-avatar.mp4.envio-v3.json` · sha256:02f8c7e17e1d · sujo
- `edicoes/2026-10-13-24h-foto/video-previa.mp4.envio-v3.json` · sha256:b21b24b100e3 · sujo
- `edicoes/2026-10-13-24h-foto/yt.txt` · sha256:91f6e04c661d · sujo
- `edicoes/2026-10-13-clima-do-dia/REFAZER-VISUAL.md` · sha256:76732fdd5557 · sujo
- `edicoes/2026-10-13-clima-do-dia/VISUAL-OK.txt` · sha256:8ae3d17ddc35 · sujo
- `edicoes/2026-10-13-clima-do-dia/avatar/APROVADO_HEYGEN` · sha256:f5f47743b1d3 · sujo
- `edicoes/2026-10-13-clima-do-dia/avatar/fala.txt` · sha256:aeb87eaedf74 · sujo
- `edicoes/2026-10-13-clima-do-dia/avatar/retempo.py` · sha256:8012bc9d48db · sujo
- `edicoes/2026-10-13-clima-do-dia/avatar/tempos.json` · sha256:81a3924aa399 · sujo
- `edicoes/2026-10-13-clima-do-dia/avatar/video_id.txt` · sha256:745189a6ee43 · sujo
- `edicoes/2026-10-13-clima-do-dia/capa-dia/LIMITES.md` · sha256:bdbf1caf92e5 · sujo
- `edicoes/2026-10-13-clima-do-dia/capa-dia/abertura.png` · sha256:21c07d0154ae · sujo
- `edicoes/2026-10-13-clima-do-dia/capa-dia/granizo.png` · sha256:95549d1f976a · sujo
- `edicoes/2026-10-13-clima-do-dia/coleta_colunas.py` · sha256:eea4295ead46 · sujo
- `edicoes/2026-10-13-clima-do-dia/dub_work/audio.wav` · sha256:35cfaf1576bc · sujo
- `edicoes/2026-10-13-clima-do-dia/dub_work/checkpoint.json` · sha256:abde5e7b34ef · sujo
- `edicoes/2026-10-13-clima-do-dia/dub_work/whisper_gpu_result.json` · sha256:734e3ec2f652 · sujo
- `edicoes/2026-10-13-clima-do-dia/fonte/transcript.json` · sha256:b08e4adba833 · sujo
- `edicoes/2026-10-13-clima-do-dia/fonte/transcript.srt` · sha256:dfe4f8b8db34 · sujo
- `edicoes/2026-10-13-clima-do-dia/fonte/transcript.txt` · sha256:57bb75176895 · sujo
- `edicoes/2026-10-13-clima-do-dia/fonte/transcript_summary.json` · sha256:a1a31002e897 · sujo
- `edicoes/2026-10-13-clima-do-dia/gerar_cena.v1.py` · sha256:f22d34263f8c · sujo
- `edicoes/2026-10-13-clima-do-dia/narrar.py` · sha256:b2dc0ad38dc1 · sujo
- `edicoes/2026-10-13-clima-do-dia/pesquisa/boletim.md` · sha256:b8fcc50116d7 · sujo
- `edicoes/2026-10-13-clima-do-dia/pesquisa/bruto/cemaden_getJson2_todas_ufs.json` · sha256:ea604d7b7891 · sujo
- `edicoes/2026-10-13-clima-do-dia/pesquisa/bruto/colunas_sul_16d.json` · sha256:805795a5bba5 · sujo
- `edicoes/2026-10-13-clima-do-dia/pesquisa/bruto/inmet_avisos_ativos.json` · sha256:73ddac0caa79 · sujo
- `edicoes/2026-10-13-clima-do-dia/pesquisa/bruto/inmet_estacoes_tentativas.json` · sha256:ed0f6b0eb2e1 · sujo
- `edicoes/2026-10-13-clima-do-dia/pesquisa/bruto/noaa_metar_brasil_24h.json` · sha256:d84b7bd78035 · sujo
- `edicoes/2026-10-13-clima-do-dia/pesquisa/bruto/openmeteo_capitais_3d.json` · sha256:7a886f5f4547 · sujo
- `edicoes/2026-10-13-clima-do-dia/pesquisa/bruto/previsao7d.json` · sha256:a6412fc8a1cb · sujo
- `edicoes/2026-10-13-clima-do-dia/pesquisa/bruto/resumo.json` · sha256:4c3e311968cd · sujo
- `edicoes/2026-10-13-clima-do-dia/pesquisa/proposta.md` · sha256:14b81c105bc4 · sujo
- `edicoes/2026-10-13-clima-do-dia/previa/avatar/foto.png` · sha256:b73f7ef0c365 · sujo
- `edicoes/2026-10-13-clima-do-dia/previa/avatar/tempos.json` · sha256:f333b9b530fc · sujo
- `edicoes/2026-10-13-clima-do-dia/previa/cena.js` · sha256:f477d8b8a95e · sujo
- `edicoes/2026-10-13-clima-do-dia/previa/gerar_cena.py` · sha256:f22d34263f8c · sujo
- `edicoes/2026-10-13-clima-do-dia/refazer-visual.sh` · sha256:4a952f0a007d · sujo
- `edicoes/2026-10-13-clima-do-dia/sat/web/anomalia.png` · sha256:37a492aa6cab · sujo
- `edicoes/2026-10-13-clima-do-dia/sat/web/ir_tempos.json` · sha256:fa8e52f6c9bd · sujo
- `edicoes/2026-10-13-clima-do-dia/tempos.json` · sha256:f333b9b530fc · sujo
- `edicoes/2026-10-13-clima-do-dia/video-avatar.mp4.envio-v3.json` · sha256:3a758fdd1171 · sujo
- `edicoes/2026-10-13-clima-do-dia/video-previa.mp4.envio-v3.json` · sha256:5f9a8b87ce66 · sujo
- `edicoes/2026-10-13-mundo-7d/avatar/APROVADO_HEYGEN` · sha256:f5f47743b1d3 · sujo
- `edicoes/2026-10-13-mundo-7d/avatar/retempo.py` · sha256:8012bc9d48db · sujo
- `edicoes/2026-10-13-mundo-7d/avatar/tempos-original.json` · sha256:49e2c64aef94 · sujo
- `edicoes/2026-10-13-mundo-7d/avatar/video_id.txt` · sha256:5156f7e0f4d9 · sujo
- `edicoes/2026-10-13-mundo-7d/falas-original.json` · sha256:57e3ddd50803 · sujo
- `edicoes/2026-10-13-mundo-7d/gerar_cena-original.py` · sha256:88d67f202d93 · sujo
- `edicoes/2026-10-13-mundo-7d/narrar.py` · sha256:589de45d4fd8 · sujo
- `edicoes/2026-10-13-mundo-7d/pesquisa/noticias.md` · sha256:76e7fc608c15 · sujo
- `edicoes/2026-10-13-mundo-7d/pesquisa/proposta.md` · sha256:dd12796b350c · sujo
- `edicoes/2026-10-13-mundo-7d/previa/.mapa.html` · sha256:f607bc88a497 · sujo
- `edicoes/2026-10-13-mundo-7d/previa/avatar/foto.png` · sha256:f00259b33535 · sujo
- `edicoes/2026-10-13-mundo-7d/previa/avatar/tempos.json` · sha256:12aa32b862a5 · sujo
- `edicoes/2026-10-13-mundo-7d/previa/cena.js` · sha256:a103de9e5009 · sujo
- `edicoes/2026-10-13-mundo-7d/previa/gerar_cena.py` · sha256:88d67f202d93 · sujo
- `edicoes/2026-10-13-mundo-7d/video-avatar-v2.mp4.envio-v3.json` · sha256:48dd2feba514 · sujo
- `edicoes/2026-10-13-mundo-7d/video-avatar.mp4.envio-v3.json` · sha256:2a68d6d22606 · sujo
- `edicoes/2026-10-13-mundo-7d/yt-original.txt` · sha256:eac4426d9051 · sujo
- `edicoes/2026-10-13-semana-foto/avatar/APROVADO_HEYGEN` · sha256:f5f47743b1d3 · sujo
- `edicoes/2026-10-13-semana-foto/avatar/fala.txt` · sha256:a666780ddf77 · sujo
- `edicoes/2026-10-13-semana-foto/avatar/retempo.py` · sha256:41e4acfe252f · sujo
- `edicoes/2026-10-13-semana-foto/avatar/tempos.json` · sha256:6904d4f879a1 · sujo
- `edicoes/2026-10-13-semana-foto/avatar/video_id.txt` · sha256:2ed9030782ec · sujo
- `edicoes/2026-10-13-semana-foto/falas.json` · sha256:cf0502b393d3 · sujo
- `edicoes/2026-10-13-semana-foto/gerar_cena.py` · sha256:fbf2a1f36e93 · sujo
- `edicoes/2026-10-13-semana-foto/narrar.py` · sha256:b2dc0ad38dc1 · sujo
- `edicoes/2026-10-13-semana-foto/om/prev15_capitais.json` · sha256:f355ea5f94e2 · sujo
- `edicoes/2026-10-13-semana-foto/om/prev15_grade.json` · sha256:17c90fd9fc30 · sujo
- `edicoes/2026-10-13-semana-foto/om/prev15_resumo.json` · sha256:8374f57d120d · sujo
- `edicoes/2026-10-13-semana-foto/pesquisa/bruto/cemaden_getJson2_todas_ufs.json` · sha256:62b683e1db2f · sujo
- `edicoes/2026-10-13-semana-foto/pesquisa/bruto/inmet_avisos_ativos.json` · sha256:73ddac0caa79 · sujo
- `edicoes/2026-10-13-semana-foto/pesquisa/bruto/inmet_estacoes_tentativas.json` · sha256:ed0f6b0eb2e1 · sujo
- `edicoes/2026-10-13-semana-foto/pesquisa/bruto/noaa_metar_brasil_24h.json` · sha256:03f32480e20e · sujo
- `edicoes/2026-10-13-semana-foto/pesquisa/bruto/openmeteo_capitais_3d.json` · sha256:402694e4b665 · sujo
- `edicoes/2026-10-13-semana-foto/pesquisa/bruto/previsao7d.json` · sha256:16a240552e84 · sujo
- `edicoes/2026-10-13-semana-foto/pesquisa/bruto/resumo.json` · sha256:1e1211248eaf · sujo
- `edicoes/2026-10-13-semana-foto/pesquisa/dados.md` · sha256:fadeeb411aa5 · sujo
- `edicoes/2026-10-13-semana-foto/pesquisa/noticias.md` · sha256:41b9d3ba0d16 · sujo
<!-- handoff-estado:fim -->
