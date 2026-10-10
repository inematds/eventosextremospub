Você está rodando sozinho (sem ninguém para responder) a edição diária "Clima 24 h" do projeto eventosextremospub, de {DATA_BR}.
Não faça perguntas: decida e siga. Ao final o script em auto/rodar.sh faz o avatar (HeyGen), publica no YouTube e manda ao bot.
Você NÃO faz: git, publicação, HeyGen, bot, nada no Vercel. Só os arquivos desta edição.

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
- sat/web/: geocolor.jpg (bbox -76,-35,-33,7) e ir00..irNN.jpg + ir_tempos.json (infravermelho GOES-19 das últimas 24 h).

## Passos
1. Pesquisa: leia os brutos e busque as notícias de clima/tempo do Brasil das últimas 24 h (desastre, chuva forte, vento, granizo, enchente, seca, fumaça, calor, frio, desalojados, mortes, alertas) e a previsão de hoje e amanhã. Grave pesquisa/noticias.md (fato, número, fonte, URL, data/hora), pesquisa/dados.md (o que veio dos brutos) e pesquisa/proposta.md (pauta escolhida e por quê). Use a edição modelo como exemplo de profundidade.
2. Roteiro em falas.json (mesmo formato do modelo): 9 a 11 falas, 150 a 190 palavras no total (uns 65 s na voz do avatar).
   - f1 abre com o dia da semana e a data por extenso + os 2 ou 3 fatos mais fortes do dia (gancho).
   - falas do meio: um fato forte por região, com número e lugar; ordem do mais grave ao menos grave, ou geográfica se ajudar o mapa.
   - uma fala "E hoje?" com os alertas oficiais vigentes (INMET) e a previsão.
   - penúltima: pergunta para comentar ("Comenta a tua cidade").
   - última, sempre: "Segue o canal: todo dia tem o clima das últimas vinte e quatro horas. E no inema ponto club tem curso gratuito." com legenda "Segue o canal: todo dia tem o clima das últimas 24 horas. E no inema.club tem curso gratuito."
   - no campo "fala" os números vão por extenso (a voz lê); no campo "legenda" com algarismos. Tom: Nei falando com o povo, frases curtas, "tu"/"teu".
3. gerar_cena.py: já copiado do modelo. Adapte TUDO ao dia de hoje: DATA, câmeras por fala, IR (rótulo e janela), focos do INPE (arquivo do dia anterior em pesquisa/bruto e os asserts com a contagem nova), avisos do INMET (escolha os ids pelo tipo e severidade em inmet_avisos_ativos.json, não copie os ids do modelo; asserts com a contagem nova), estados pintados, pinos, hero, painéis, contadores, cta, fontes de cada trecho, cores da legenda, marca/selo. Mantenha o comportamento de --canto (usa avatar/tempos.json, layout canto). Cada `em(fid, palavra)` precisa achar a palavra na legenda daquela fala.
4. Versão mapa (é também o plano B se o avatar falhar), na pasta da edição:
   `python3 narrar.py` → tempos.json e narração (voz do Nei, local)
   `python3 gerar_cena.py`
   `cd {RAIZ} && GEO=geo-br.js motor/montar.sh {ED}` → video.mp4
   Confira: ffprobe (1080x1920), e extraia uns 8 quadros (abertura, cada painel, cta) com ffmpeg e OLHE as imagens (Read). Verifique: data grande na abertura, contadores terminando no número certo, pino sem ficar atrás de painel, borda da imagem de satélite não aparecendo, legenda legível. Corrija e renderize de novo se precisar.
5. yt.txt: linha 1 = título do YouTube em português, até 80 caracteres, sem #Shorts (o script põe), com "Clima 24 h" e os fatos principais e a data dd/mm. Linhas seguintes: de 4 a 8 linhas com os fatos e números do vídeo e as fontes (vira contexto da descrição).
6. Confira no fim: falas.json, gerar_cena.py, tempos.json, video.mp4 e yt.txt existem e batem entre si.

Se algo impedir a edição (sem dados, render quebrado sem conserto), grave ERRO.txt com o motivo em 2 ou 3 linhas e pare.
Se uma fonte falhar ou bloquear, anote uma linha em ~/projetos/wifi/LIMITES.md (o que tentou, o que barrou, contorno, proposta, aberto). Falha de código que você corrigiu: uma linha em {RAIZ}/FALHAS.md.
