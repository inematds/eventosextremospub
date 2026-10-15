Você está rodando sozinho (sem ninguém para responder) a edição especial "Ventos extremos: últimas 24 h" do projeto eventosextremospub (pedido do Nei), de {DATA_BR}.
Não faça perguntas: decida e siga. Ao final o script em auto/rodar.sh faz o avatar (HeyGen), publica no YouTube e manda ao bot.
Você NÃO faz: git, publicação, HeyGen, bot, nada no Vercel. Só os arquivos desta edição.
PALAVRA PROIBIDA (Nei, 15/10/2026): nunca "morte", "mortes", "morto(s)", "morreu", "óbito", "faleceu" — nem na fala, nem na legenda, nem na tela (pinos, painéis, unid de contador, hero), nem no yt.txt. Use "vítimas" (ex.: "71 vítimas na Tailândia"; "uma vítima no temporal"). Se a fonte (boletim, notícia) falar em mortes, reescreva com "vítimas". Os vídeos que falaram "mortos" tiveram pouca entrega no YouTube; o portão do rodar.sh reprova.

Pasta da edição: {ED}
Edição modelo (ontem ou o último dia): {PREV}
Raiz do projeto: {RAIZ} (leia CLAUDE.md e README.md antes de tudo; as Lessons do CLAUDE.md valem)

## Regras duras
- APIs: só as de clima gratuitas liberadas (NASA GIBS, Open-Meteo, INMET, CPTEC, CEMADEN, NOAA, INPE Queimadas), por curl/python. Nenhuma outra API, nenhuma chave, nenhum modelo de IA por API. Busca e leitura de notícias pela web (WebSearch/WebFetch) pode.
- Fontes de notícia confiáveis: Defesa Civil (estaduais e nacional), INMET, INPE, CEMADEN, MetSul, Climatempo, Meteored, g1, Agência Brasil, CNN Brasil, UOL, Folha, Estadão, governos estaduais. Rede social só de órgão oficial.
- Todo número que vai ao ar tem fonte com URL ou arquivo bruto anotado em pesquisa/. Não invente, não arredonde para cima, não junte dias diferentes. Na dúvida, deixe o fato de fora.
- Escreva "mensagem de texto", nunca "SMS".
- Formato: Short 9:16 (nunca 16:9).

## Já coletado pelo script
- pesquisa/bruto/: resumo.json e brutos de coleta/ultimas24h.py (INMET avisos, INPE focos do dia anterior, METAR da NOAA, CEMADEN, Open-Meteo das capitais). Falhas da coleta estão em resumo.json → falhas.
- pesquisa/bruto/previsao7d.json (Open-Meteo, 7 dias nas 27 capitais): chuva SOMADA por dia, por região (N/NE/CO/SE/S) e acumulada em 7 dias, máxima média e pico por dia, top acumulado. resumo.json → cemaden.soma_por_uf / soma_mm_estacoes: volume somado dos pluviômetros nas últimas 24 h (mm·estação: rotule "soma dos pluviômetros", nunca como lâmina de área).
- sat/web/: geocolor.jpg (bbox -76,-35,-33,7) e ir00..irNN.jpg + ir_tempos.json (infravermelho GOES-19 das últimas 24 h).

## Foco desta edição: o geral de sempre, com DESTAQUE no VENTO (Nei, 13/10/2026)
É o Clima 24 h completo de sempre: o geral de tudo o que aconteceu nas últimas 24 h no Brasil e o que vai acontecer (hoje, amanhã e os 7 dias), com mapa, satélite, gráficos, contadores e movimento de câmera, como na edição modelo. NÃO corte nada do diário: chuva, calor, ar seco, fogo, avisos, previsão de 7 dias com gráfico e volumes somados continuam (todos os passos abaixo valem).
O que muda é o DESTAQUE no vento extremo:
- Quadro 0: data dd/mm/aaaa grande + manchete com a MAIOR rajada medida, com lugar e fonte (ex.: "RAJADA DE 77 KM/H"). f1 abre pelo vento e já anuncia o resto do dia.
- Rajadas medidas: METAR da NOAA (noaa_metar_brasil_24h.json; rajada = número depois do G, em nós; 1 nó = 1,852 km/h, arredonde para baixo); estações do INMET se vieram; avisos do INMET de vento/tempestade com a faixa de km/h; notícias de estrago por vento (destelhamento, queda de árvore, falta de luz, ciclone, tornado, microexplosão) com data/hora confirmada nas 24 h.
- Uma fala e um painel a mais "Onde ventou mais": ranking das maiores rajadas medidas nas 24 h, com pinos no mapa e fonte na tela (painel "ranking" do motor, se ajudar).
- Na previsão, além do gráfico de chuva de 7 dias, um painel de rajadas máximas previstas (Open-Meteo, API liberada: wind_gusts_10m_max diário de 7 dias nas capitais, lotes pequenos para não levar 429), por região em km/h.
- Pode passar um pouco do tamanho do diário: 12 a 14 falas, 230 a 280 palavras.
- Título do yt.txt começa com "Ventos extremos 24 h" e cita também o geral do dia.

## Passos
1. Pesquisa: leia os brutos e busque as notícias de clima/tempo do Brasil das últimas 24 h (desastre, chuva forte, vento, granizo, enchente, seca, fumaça, calor, frio, desalojados, vítimas, alertas) e a previsão de hoje e amanhã. Grave pesquisa/noticias.md (fato, número, fonte, URL, data/hora), pesquisa/dados.md (o que veio dos brutos) e pesquisa/proposta.md (pauta escolhida e por quê). Use a edição modelo como exemplo de profundidade.
2. Roteiro em falas.json (mesmo formato do modelo): 12 a 14 falas, 230 a 280 palavras no total (uns 95 s na voz do avatar). OBRIGATÓRIO (Nei, 13/10/2026): o diário não é só resumo, ele PREVÊ. Inclua duas falas novas: (a) "Os próximos sete dias": a previsão com o gráfico (dia mais chuvoso, região que mais acumula, onde o calor aperta) e (b) "Volumes somados": o total de chuva das últimas 24 h somado (pluviômetros CEMADEN por UF) e o total previsto em 7 dias (previsao7d.json). Toda previsão é dita como previsão ("deve", "previsto"), com a fonte Open-Meteo na tela; nunca como certeza.
   - f1 abre com o dia da semana e a data por extenso + os 2 ou 3 fatos mais fortes do dia (gancho).
   - falas do meio: um fato forte por região, com número e lugar; ordem do mais grave ao menos grave, ou geográfica se ajudar o mapa.
   - uma fala "E hoje?" com os alertas oficiais vigentes (INMET) e a previsão.
   - penúltima: pergunta para comentar ("De que região e de que cidade você é? Comenta aqui" — a pergunta de clima é SEMPRE de onde a pessoa mora).
   - última, sempre: "No inema ponto club você pode aprender sobre inteligência artificial." com legenda "No inema.club você pode aprender sobre inteligência artificial." (Nei, 13/10/2026; no card da cena: "APRENDA IA" / "inema.club"; nada de "painel de chuva", "alerta" ou "curso pra você") O CTA é SEMPRE só o inema.club: nunca "segue o canal", "se inscreva" nem canal do YouTube (Nei, 11/10/2026; as edições até 10/10 ainda dizem "Segue o canal": não copie).
   - no campo "fala" os números vão por extenso (a voz lê); no campo "legenda" com algarismos. Vocabulário: o assunto é tragédia (vítimas, desabrigados, fogo) — NUNCA termo positivo ou de alívio ("por sorte", "felizmente", "ainda bem", "melhor", "boa notícia", "graças a"); dizer só o fato, sem juízo (Nei, 13/10/2026). Tom: Nei falando com o povo, frases curtas, tratando por "você" (você, seu, sua), NUNCA "tu", "teu", "tua", "ti" — vale também para os textos na tela (ex.: "Sua cidade", não "Tua cidade"); as edições até 10/10 usam "tu": não copie.
3. gerar_cena.py: já copiado do modelo. Adapte TUDO ao dia de hoje: DATA, câmeras por fala, IR (rótulo e janela), focos do INPE (arquivo do dia anterior em pesquisa/bruto e os asserts com a contagem nova), avisos do INMET (escolha os ids pelo tipo e severidade em inmet_avisos_ativos.json, não copie os ids do modelo; asserts com a contagem nova), estados pintados, pinos, hero, painéis, contadores, cta, fontes de cada trecho, cores da legenda, marca/selo. Mantenha o comportamento de --canto (usa avatar/tempos.json, layout canto). Cada `em(fid, palavra)` precisa achar a palavra na legenda daquela fala.
3b. Painéis de previsão e volume (novo motor, motor/mapa.html): no painel acrescente a chave "grafico", exemplo:
   {"ini":..., "fim":..., "k":"CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)", "contador":{... "ate": <soma_7d_mm arredondada>, "unid":"MM EM 7 DIAS"},
    "grafico":{"rotulos":["ter","qua",...], "series":[{"nome":"N","cor":"#2dd4bf","v":[...por_regiao_mm.N de cada dia]}, ... NE #facc15, CO #fb923c, SE #f472b6, S #5ec8ff],
               "previsto_a_partir":1, "ini":<t>, "dur":1.6, "linha":{"nome":"máx. °C (média)","cor":"#ff2a1f","v":[tmax_media de cada dia]}}, "l":"fonte e o que a soma significa"}
   Use os valores de previsao7d.json, os rótulos dos dias da semana de verdade (o primeiro dia é hoje), e confira nos asserts do gerar_cena.py que os totais batem. Um painel para a previsão (barras empilhadas por região + linha de temperatura) e outro para volumes somados 24 h (contador com soma_mm_estacoes ou por UF) + 7 dias. Confira nos quadros extraídos que o painel não cobre a legenda nem a fonte.
4. Versão mapa (é também o plano B se o avatar falhar), na pasta da edição:
   `python3 narrar.py` → tempos.json e narração (voz do Nei, local)
   `python3 gerar_cena.py`
   `cd {RAIZ} && GEO=geo-br.js motor/montar.sh {ED}` → video.mp4
   Confira: ffprobe (1080x1920), e extraia uns 8 quadros (abertura, cada painel, cta) com ffmpeg e OLHE as imagens (Read). Verifique: data grande na abertura, contadores terminando no número certo, pino sem ficar atrás de painel, borda da imagem de satélite não aparecendo, legenda legível. Corrija e renderize de novo se precisar.
5. yt.txt: linha 1 = título do YouTube em português, até 80 caracteres, sem #Shorts (o script põe), com "Clima 24 h" e os fatos principais e a data dd/mm. Linhas seguintes: de 4 a 8 linhas com os fatos e números do vídeo e as fontes (vira contexto da descrição).
6. Confira no fim: falas.json, gerar_cena.py, tempos.json, video.mp4 e yt.txt existem e batem entre si.

Se algo impedir a edição (sem dados, render quebrado sem conserto), grave ERRO.txt com o motivo em 2 ou 3 linhas e pare.
Se uma fonte falhar ou bloquear, anote uma linha em ~/projetos/wifi/LIMITES.md (o que tentou, o que barrou, contorno, proposta, aberto). Falha de código que você corrigiu: uma linha em {RAIZ}/FALHAS.md.
