Você está rodando sozinho (sem ninguém para responder) a edição de DOMINGO À TARDE "Clima da semana + 15 dias" do projeto eventosextremospub, de {DATA_BR}.
Não faça perguntas: decida e siga. Ao final o script em auto/rodar.sh faz o avatar (HeyGen), publica no YouTube e manda ao bot.
Você NÃO faz: git, publicação, HeyGen, bot, nada no Vercel. Só os arquivos desta edição.

Pasta da edição: {ED}
Edição modelo (a última de domingo ou, se ainda não houver, a última "Clima 24 h"): {PREV}
Raiz do projeto: {RAIZ} (leia CLAUDE.md e README.md antes de tudo; as Lessons do CLAUDE.md valem)

## O que é este vídeo
Previsão: o que vem na SEMANA de segunda a domingo (dias 1 a 7) e a TENDÊNCIA dos 15 dias (dias 8 a 15), no Brasil todo.
Não é o resumo das últimas 24 h. O que já aconteceu entra só se ajudar a entender o que vem (ex.: "depois da enchente, mais chuva").

## Regras duras
- APIs: só as de clima gratuitas liberadas (NASA GIBS, Open-Meteo, INMET, CPTEC, CEMADEN, NOAA, INPE Queimadas), por curl/python. Nenhuma outra API, nenhuma chave, nenhum modelo de IA por API. Busca e leitura de notícias pela web (WebSearch/WebFetch) pode (MetSul, Climatempo, INMET, Meteored, CPTEC: previsão da semana e tendência).
- Todo número que vai ao ar tem fonte com URL ou arquivo bruto anotado em pesquisa/. Não invente, não arredonde para cima. Número de previsão é sempre "previsto"/"pode chegar a", com a fonte (modelo Open-Meteo ou órgão).
- Dias 8 a 15 são TENDÊNCIA: diga isso na fala ("a tendência", "pode mudar") e na tela. Nunca apresente a tendência como certeza.
- Escreva "mensagem de texto", nunca "SMS". Formato: Short 9:16 (nunca 16:9).

## Já coletado pelo script
- om/prev15_resumo.json — o principal: semana (dias 1–7) e tendencia_8a15, por capital e por ponto da grade (1,5°): chuva acumulada top, calor top, frio top, rajada top, e por UF. om/prev15_grade.json (dia a dia, para mapa/colunas) e om/prev15_capitais.json.
- pesquisa/bruto/: resumo.json de coleta/ultimas24h.py (avisos INMET vigentes, Open-Meteo 3 dias nas capitais, etc.).
- sat/web/: geocolor.jpg e infravermelho das últimas 24 h (use só se servir de fundo).

## QUADRO 0 (frame 0) — PROVOCANTE
É o que faz a pessoa parar de rolar. O hero da abertura tem, grande, do t=0 até o fim da f1:
- a data dd/mm/aaaa e "PREVISÃO DA SEMANA + 15 DIAS";
- o NÚMERO mais forte da semana (ex.: "166 MM EM 7 DIAS", "41 °C") com o lugar;
- uma pergunta ou frase provocante que fala com quem assiste, curta, em letra enorme (ex.: "A SUA CIDADE ESTÁ NO CAMINHO?", "VAI FALTAR GUARDA-CHUVA NO SUL", "O CALOR NÃO VAI DAR TRÉGUA");
- sem exagero falso: a provocação tem de ser verdadeira pelos números coletados.
O quadro 0 não entra com fade (Lesson do CLAUDE.md). Confira o quadro 0 extraído (ffmpeg -frames:v 1) e OLHE a imagem antes de terminar.

## Passos
1. Pesquisa: leia om/prev15_resumo.json e os brutos; busque a previsão da semana e a tendência de 15 dias nas fontes confiáveis (frentes frias, ciclone, onda de calor, chuva volumosa, retorno da chuva, El Niño/La Niña). Grave pesquisa/noticias.md (fato, número, fonte, URL, data), pesquisa/dados.md (o que veio do Open-Meteo, com os números exatos) e pesquisa/proposta.md (pauta e por quê; qual o gancho do quadro 0).
2. Roteiro em falas.json (mesmo formato do modelo): 10 a 12 falas, 190 a 240 palavras (uns 85 s na voz do avatar).
   - f1: o gancho provocante, falando com quem assiste, com o número mais forte da semana e o lugar ("Domingo, onze de outubro: ...").
   - semana (dias 1–7): por região, o mais grave primeiro; chuva acumulada, calor, frio, vento; com os dias da semana ("na terça e na quarta").
   - uma fala de virada "E nos próximos 15 dias?": a tendência, dita como tendência.
   - uma fala com os alertas oficiais vigentes (INMET) se houver.
   - penúltima: pergunta para comentar ("De que região e de que cidade você é? Comenta aqui como está o tempo aí").
   - última, sempre: "No inema ponto club você pode aprender sobre inteligência artificial." com legenda "No inema.club você pode aprender sobre inteligência artificial." (Nei, 13/10/2026). Vocabulário: nunca termo positivo/de alívio para tragédia ("por sorte", "felizmente", "ainda bem", "melhor") CTA SEMPRE só o inema.club: nunca "segue o canal", "se inscreva" nem canal do YouTube.
   - no campo "fala" os números vão por extenso (a voz lê; ano por extenso); no campo "legenda" com algarismos. Tom: Nei falando com o povo, frases curtas, "você" (você, seu, sua), NUNCA "tu", "teu", "tua", "ti" — vale também para os textos na tela.
3. gerar_cena.py: já copiado do modelo. Adapte TUDO a esta edição: DATA, hero do quadro 0 (acima), câmeras por fala no mapa do Brasil, estados pintados pela chuva/calor previstos (om/prev15_resumo.json → por_uf), pinos nas cidades citadas, painéis/contadores com os números previstos (rótulo "previsto 12 a 18/10" / "tendência 19 a 26/10"), fontes de cada trecho ("Open-Meteo, previsão lida em {DATA_BR}"), cta, marca/selo ("PREVISÃO · 12 A 18/10"). Tire o que for das últimas 24 h que não estiver no roteiro (IR, focos, METAR). Mantenha o comportamento de --canto (usa avatar/tempos.json, layout canto). Cada `em(fid, palavra)` precisa achar a palavra na legenda daquela fala.
4. Versão mapa (é também o plano B se o avatar falhar), na pasta da edição:
   `python3 narrar.py` → tempos.json e narração (voz do Nei, local)
   `python3 gerar_cena.py`
   `cd {RAIZ} && GEO=geo-br.js motor/montar.sh {ED}` → video.mp4
   Confira: ffprobe (1080x1920), e extraia uns 8 quadros (o quadro 0, cada painel, a virada dos 15 dias, cta) com ffmpeg e OLHE as imagens (Read). Verifique: quadro 0 cheio e provocante, data grande, contadores terminando no número certo, pino sem ficar atrás de painel, legenda legível. Corrija e renderize de novo se precisar.
5. yt.txt: linha 1 = título do YouTube em português, até 80 caracteres, sem #Shorts (o script põe), com "Previsão da semana" e o gancho (número + lugar) e a data dd/mm. Linhas seguintes: de 4 a 8 linhas com os números do vídeo e as fontes (vira contexto da descrição), dizendo que 8 a 15 dias é tendência.
6. Confira no fim: falas.json, gerar_cena.py, tempos.json, video.mp4 e yt.txt existem e batem entre si.

Se algo impedir a edição (sem dados, render quebrado sem conserto), grave ERRO.txt com o motivo em 2 ou 3 linhas e pare.
Se uma fonte falhar ou bloquear, anote uma linha em ~/projetos/wifi/LIMITES.md (o que tentou, o que barrou, contorno, proposta, aberto). Falha de código que você corrigiu: uma linha em {RAIZ}/FALHAS.md.
