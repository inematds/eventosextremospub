Você está rodando sozinho (sem ninguém para responder) a edição diária "Clima no Mundo" (últimos 7 dias) do projeto eventosextremospub, de {DATA_BR}.
Não faça perguntas: decida e siga. Depois o script auto/rodar.sh faz o avatar (HeyGen), publica no lives10 e manda ao bot.
Você NÃO faz: git, publicação, HeyGen, bot, nada no Vercel. Só os arquivos desta edição.

Pasta da edição: {ED}
Edição modelo (a última do Clima no Mundo, Short 9:16 com mapa do mundo, layout canto; aprovada pelo Nei em 13/10/2026): {PREV}
Ponto de partida da pesquisa: {PREV}/pesquisa/noticias.md (ATUALIZE: tire o que saiu da janela de 7 dias, confira se os números mudaram, acrescente o novo).
Raiz do projeto: {RAIZ} (leia CLAUDE.md e README.md antes de tudo; as Lessons do CLAUDE.md valem)

## Regras duras
- APIs: só as de clima gratuitas liberadas (NASA GIBS, Open-Meteo, INMET, CPTEC, CEMADEN, NOAA, INPE Queimadas), por curl/python. Nenhuma outra API, nenhuma chave, nenhum modelo de IA por API. Busca e leitura de notícias pela web (WebSearch/WebFetch) pode.
- Fontes de notícia confiáveis: agências oficiais (NOAA/NHC, JMA, USGS, GDACS, ReliefWeb, OCHA, WMO, Copernicus/EMSDI, defesas civis), Reuters, AP, AFP, BBC, CNN, Al Jazeera, g1, Agência Brasil, Folha, Estadão, UOL.
- Todo número que vai ao ar tem fonte com URL anotada em pesquisa/. Não invente, não arredonde para cima, não junte eventos diferentes. Na dúvida, deixe de fora.
- Formato: Short 9:16 (nunca 16:9).

## Passos
1. Pesquisa: o que de mais grave aconteceu no clima/tempo e desastres naturais NO MUNDO nos últimos 7 dias ({DATA_BR} e os 6 dias antes), com prioridade ao que é MAIS RECENTE (últimas 48 h) e ao que ainda está em andamento (tempestade ativa, enchente que continua, onda de calor, fogo, seca). Parta da pesquisa da edição modelo e confira se cada número mudou (mortos, atingidos, desabrigados); acrescente o que surgiu depois dela. Não repita o vídeo de ontem: a abertura (f1) traz o fato mais NOVO ou que mais mudou. Inclua o Brasil só se estiver entre os mais graves. Grave pesquisa/noticias.md (fato, número, fonte, URL, data/hora), pesquisa/proposta.md (os 5 a 7 eventos escolhidos, ordem e por quê).
2. Roteiro em falas.json (mesmo formato do modelo): 10 a 12 falas, 190 a 230 palavras no total (uns 80 s na voz do avatar).
   - f1 abre com a data por extenso + os 2 ou 3 fatos mais fortes da semana no mundo (gancho com número).
   - falas do meio: um evento por fala, com número, país e lugar, do mais grave ao menos grave; diga quando foi ("na quinta", "desde domingo").
   - uma fala "E agora?" com o que continua em andamento ou o que vem (tempestade prevista, alerta oficial vigente), dito como previsão.
   - penúltima: "De que região e de que cidade você é? Comenta aqui."
   - última, sempre: "No inema ponto club você pode aprender sobre inteligência artificial." com legenda "No inema.club você pode aprender sobre inteligência artificial." (card: "APRENDA IA" / "inema.club").
   - CTA só o inema.club (nunca "segue o canal", "se inscreva"). Tratar por "você", nunca "tu/teu/tua/ti". Tragédia: nunca termo positivo ou de alívio ("por sorte", "felizmente", "ainda bem", "melhor", "boa notícia").
   - no campo "fala" números por extenso (a voz lê, ano também por extenso); no campo "legenda" com algarismos.
3. gerar_cena.py: copiado do modelo (mapa do mundo, 9:16). Adapte TUDO: DATA, câmeras por fala voando de país em país, pinos e rótulos de cada evento, painéis com contadores (o número certo de cada evento), fontes de cada trecho, cta. Mantenha o comportamento de --canto (usa avatar/tempos.json, layout canto). Cada `em(fid, palavra)` precisa achar a palavra na legenda daquela fala. Satélite: se usar imagem do GIBS de um evento, só a camada liberada, guardada em sat/.
4. Versão mapa, na pasta da edição:
   `python3 narrar.py` → tempos.json e narração (voz do Nei, local)
   `python3 gerar_cena.py`
   `cd {RAIZ} && GEO=geo-br.js motor/montar.sh {ED}` → video.mp4
   Confira: ffprobe (1080x1920), extraia uns 8 quadros (abertura, cada evento, cta) e OLHE as imagens (Read). Verifique: data grande na abertura, contadores no número certo, câmera no país certo, pino sem ficar atrás de painel, legenda legível. Corrija e renderize de novo se precisar.
5. yt.txt: linha 1 = título até 80 caracteres com "O clima no mundo" e os fatos principais e a data dd/mm. Linhas seguintes: 4 a 8 linhas com fatos, números e fontes.
6. Confira no fim: falas.json, gerar_cena.py, tempos.json, video.mp4 e yt.txt existem e batem entre si.

Se algo impedir a edição, grave ERRO.txt com o motivo em 2 ou 3 linhas e pare.
Se uma fonte falhar ou bloquear, anote uma linha em ~/projetos/wifi/LIMITES.md. Falha de código que você corrigiu: uma linha em {RAIZ}/FALHAS.md.
