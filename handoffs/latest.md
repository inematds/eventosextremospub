# Handoffs — trabalhos abertos

Cada linha é um assunto em andamento: leia o snapshot do assunto que for continuar. Gravado por handoff-grava.py.

<!-- handoff-indice:inicio -->
- `clima24h-2026-10-20` · handoffs/history/2026-10-20T094646Z-clima24h-2026-10-20.md · 20/10 06:46
- `mundo-2026-10-18` · handoffs/history/2026-10-18T221922Z-mundo-2026-10-18.md · 18/10 19:19
<!-- handoff-indice:fim -->

## Parados (sem handoff há mais de 3 dias)

Fora dos abertos: o /prime não lista. Gravar um handoff com o mesmo slug volta o assunto para os abertos; `--fechado` tira daqui. Snapshots continuam em handoffs/history/.

<!-- handoff-parados:inicio -->
- `clima24h-2026-10-16` · handoffs/history/2026-10-16T210158Z-clima24h-2026-10-16.md · 16/10 18:01
- `viral-916` · handoffs/history/2026-10-16T010020Z-viral-916.md · 15/10 22:00
- `refaz-viral-queimadas-itaipu` · handoffs/history/2026-10-15T185758Z-refaz-viral-queimadas-itaipu.md · 15/10 15:57
- `queimadas-reel-3d` · handoffs/history/2026-10-15T180233Z-queimadas-reel-3d.md · 15/10 15:02
- `itaipu-ruptura` · handoffs/history/2026-10-15T120855Z-itaipu-ruptura.md · 15/10 09:08
- `previsao-do-dia` · handoffs/history/2026-10-15T100300Z-previsao-do-dia.md · 15/10 07:03
- `clima24h-2026-10-15` · handoffs/history/2026-10-15T095957Z-clima24h-2026-10-15.md · 15/10 06:59
<!-- handoff-parados:fim -->

---

Cópia integral do snapshot mais recente (handoffs/history/2026-10-20T094646Z-clima24h-2026-10-20.md):

# Handoff — Clima 24 h de 20/10/2026 (rodada automática, claude -p)

## Projeto e escopo
eventosextremospub, edição `edicoes/2026-10-20-ultimas-24h` (Short 9:16). Só os arquivos da edição; avatar HeyGen, lives10, bot v3 e git ficam com `auto/rodar.sh`.

## Objetivo atual
Entregar falas.json, gerar_cena.py, tempos.json, video.mp4 (versão mapa / plano B) e yt.txt para o rodar.sh seguir.

## Estado aceito
- [confirmed] video.mp4 1080x1920, 102,5 s (GEO=geo-br.js motor/montar.sh), renderizado 3 vezes; quadros conferidos (abertura com capa, pinos visíveis após ajuste de câmera SUL lat -24,9 e PA lat -0,6, painel f6 dividido em quarta 407 / quinta 2.745, CTA). Loudness -17,7 LUFS (ontem -17,5, padrão do montar.sh).
- [confirmed] falas.json: 10 falas (frio de décadas SC/PR → fogo 1.011 focos, PA 465 → chuva Tapauá 72 / Macarani 66 → E hoje laranja 38 / amarelo 1.144 → quarta 407 / quinta 2.745 tempestade → 7 dias → volumes MG 840+, Brasil 3.600+, capitais 593 → pergunta → CTA inema.club). f2 corrigida para não terminar em número ("…desde 1997, quando a estação foi instalada"). Pausa de 1 s antes da pergunta aplicada.
- [confirmed] Capa Codex (assinatura) capa-dia/abertura.png "FRIO DE DÉCADAS / EM PLENO OUTUBRO / -2 °C NA SERRA CATARINENSE" (termômetro com "30" repetido, aceito: selo ilustração, 2 s).
- [confirmed] pesquisa/noticias.md, dados.md, proposta.md; geocoding_openmeteo.txt em pesquisa/bruto; mundo.jpg copiado de 2026-10-19.
- [confirmed] Portões tom/CTA/morte limpos; título yt.txt 77 caracteres.
- [confirmed] LIMITES.md (wifi): linha sobre WebFetch e curl bloqueados pelo hook context-mode.

## Proposto / tentado, não confirmado
- [unverified] gerar_cena.py --canto não testado (avatar/tempos.json ainda não existe).
- [unverified] Avatar, publicação e bot: fase do rodar.sh, fora desta sessão.

## Decisões e restrições
- Fogo sem comparação com 18/10 (AQUA 222 suspeito); somas CEMADEN sem comparação com ontem (784 × 1.054 estações); sensores Rio Xopoto e Colégio Naval fora das somas.
- SP descartado (alagamentos eram de 16/10, fonte fora da lista). Calor do NE só na previsão.
- Fala com 243 palavras (acima de 230), narração 102,5 s, aceito.

## Próxima ação
Nenhuma nesta sessão; o rodar.sh segue com avatar → lives10 → bot v3 → git.


<!-- handoff-estado:inicio -->
## Estado gravado pelo script (não editar)

Gravado por handoff-grava.py no momento do handoff. `--conferir` compara com o projeto agora.

- commit: 74bbe35e12974df4e89ecebc713ba8553907fea7 · branch: main
- arquivos sujos fora de handoffs/: 943 (lista cortada)
- `CLAUDE.md` · sha256:71ffe0603e53 · sujo
- `auto/previsao-usados.txt` · sha256:183ced262218 · sujo
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
- `edicoes/2026-10-13-24h-foto/avatar/retempo.py` · sha256:8012bc9d48db · sujo
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
- `edicoes/2026-10-13-24h-foto/previa/avatar/avatar.mp4` · sha256:52eaf247a0ef · sujo
- `edicoes/2026-10-13-24h-foto/previa/avatar/foto.png` · sha256:b73f7ef0c365 · sujo
- `edicoes/2026-10-13-24h-foto/previa/avatar/tempos.json` · sha256:716d08429e04 · sujo
- `edicoes/2026-10-13-24h-foto/previa/build/mapa-avatar.mp4` · sha256:f3d77e899cfe · sujo
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
- `edicoes/2026-10-13-clima-do-dia/fonte/video.mp4` · sha256:616cb78ab572 · sujo
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
- `edicoes/2026-10-13-clima-do-dia/previa/avatar/avatar.mp4` · sha256:837f18deb29e · sujo
- `edicoes/2026-10-13-clima-do-dia/previa/avatar/foto.png` · sha256:b73f7ef0c365 · sujo
- `edicoes/2026-10-13-clima-do-dia/previa/avatar/tempos.json` · sha256:f333b9b530fc · sujo
- `edicoes/2026-10-13-clima-do-dia/previa/build/mapa-avatar.mp4` · sha256:a07815b5694f · sujo
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
- `edicoes/2026-10-13-mundo-7d/previa/avatar/avatar.mp4` · sha256:5edac8708228 · sujo
- `edicoes/2026-10-13-mundo-7d/previa/avatar/foto.png` · sha256:f00259b33535 · sujo
- `edicoes/2026-10-13-mundo-7d/previa/avatar/tempos.json` · sha256:12aa32b862a5 · sujo
- `edicoes/2026-10-13-mundo-7d/previa/cena.js` · sha256:a103de9e5009 · sujo
- `edicoes/2026-10-13-mundo-7d/previa/gerar_cena.py` · sha256:88d67f202d93 · sujo
- `edicoes/2026-10-13-mundo-7d/video-avatar-v2.mp4.envio-v3.json` · sha256:48dd2feba514 · sujo
- `edicoes/2026-10-13-mundo-7d/video-avatar.mp4.envio-v3.json` · sha256:2a68d6d22606 · sujo
- `edicoes/2026-10-13-mundo-7d/yt-original.txt` · sha256:eac4426d9051 · sujo
- `edicoes/2026-10-13-semana-foto/avatar/APROVADO_HEYGEN` · sha256:f5f47743b1d3 · sujo
- `edicoes/2026-10-13-semana-foto/avatar/fala.txt` · sha256:a666780ddf77 · sujo
- `edicoes/2026-10-13-semana-foto/avatar/retempo.py` · sha256:8012bc9d48db · sujo
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
- `edicoes/2026-10-13-semana-foto/pesquisa/proposta.md` · sha256:441edcfcec14 · sujo
- `edicoes/2026-10-13-semana-foto/previa/avatar/avatar.mp4` · sha256:90020a3ccf78 · sujo
- `edicoes/2026-10-13-semana-foto/previa/avatar/foto.png` · sha256:b73f7ef0c365 · sujo
- `edicoes/2026-10-13-semana-foto/previa/avatar/tempos.json` · sha256:1fbb83e0642a · sujo
- `edicoes/2026-10-13-semana-foto/previa/build/mapa-avatar.mp4` · sha256:4e91d223cbfc · sujo
- `edicoes/2026-10-13-semana-foto/previa/cena.js` · sha256:a0e952c5feea · sujo
- `edicoes/2026-10-13-semana-foto/previa/gerar_cena.py` · sha256:fbf2a1f36e93 · sujo
- `auto/rodar.sh` · sha256:356045ac2160 · citado
<!-- handoff-estado:fim -->
