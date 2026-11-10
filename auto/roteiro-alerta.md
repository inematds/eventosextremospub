Você está rodando sozinho (sem ninguém para responder) a edição diária das 14h "ALERTA DA SEMANA" do projeto eventosextremospub, de {DATA_BR}.
Não faça perguntas: decida e siga. Ao final o script em auto/rodar.sh faz o avatar (HeyGen), publica no YouTube (lives10) e no Instagram + TikTok eventos.extremos (metritds) e manda ao bot.
Você NÃO faz: git, publicação, HeyGen, bot, nada no Vercel. Só os arquivos desta edição.
PALAVRA PROIBIDA (Nei, 15/10/2026): nunca "morte", "mortes", "morto(s)", "morreu", "óbito", "faleceu" — nem na fala, nem na legenda, nem na tela (pinos, painéis, unid de contador, hero), nem no yt.txt. Use "vítimas". O portão do rodar.sh reprova.

Pasta da edição: {ED}
Edição modelo (o alerta de ontem ou, se ainda não houver, o último domingo "Clima da semana"): {PREV}
Raiz do projeto: {RAIZ} (leia CLAUDE.md e README.md antes de tudo; as Lessons do CLAUDE.md valem)

## O que é este vídeo (Nei, 05/11/2026)
Todo dia (segunda a sábado) às 14h: o ALERTA do que vai acontecer nos PRÓXIMOS 7 DIAS, a partir de AMANHÃ (ou desta madrugada), no Brasil todo.
"Sempre uma cena e chamada impressionando, também a linguagem como alerta."
- Não é a previsão de hoje (essa é a Previsão do Dia, às 10h) nem o resumo das últimas 24 h. O que já aconteceu entra só se ajudar a entender o que vem.
- Sem a tendência de 15 dias (essa fica para o domingo). Foco: o que ameaça quem assiste nos próximos 7 dias e QUANDO.
- No domingo este vídeo não sai: sai o "Clima da semana + 15 dias".

## Regras duras
- APIs: só as de clima gratuitas liberadas (NASA GIBS, Open-Meteo, INMET, CPTEC, CEMADEN, NOAA, INPE Queimadas), por curl/python. Nenhuma outra API, nenhuma chave, nenhum modelo de IA por API. Busca e leitura de notícias pela web (WebSearch/WebFetch) pode (MetSul, Climatempo, INMET, Meteored, CPTEC: previsão dos próximos dias, frentes, ciclones, ondas de calor).
- Todo número que vai ao ar tem fonte com URL ou arquivo bruto anotado em pesquisa/. Não invente, não arredonde para cima. Número de previsão é sempre "previsto"/"pode chegar a", com a fonte (modelo Open-Meteo ou órgão).
- Alerta forte não é alarme falso: a ameaça tem de estar nos números coletados ou num aviso oficial.
- Escreva "mensagem de texto", nunca "SMS". Formato: Short 9:16 (nunca 16:9).

## Já coletado pelo script
- om/prev15_resumo.json — o principal: bloco "semana" = dias 1 a 7 a partir de AMANHÃ, por capital e por ponto da grade (1,5°): chuva acumulada top, calor top, frio top, rajada top, e por UF. (Ignore "tendencia_8a15".) om/prev15_grade.json (dia a dia, para mapa/colunas e para dizer QUAL dia) e om/prev15_capitais.json.
- pesquisa/bruto/: resumo.json de coleta/ultimas24h.py (avisos INMET vigentes, Open-Meteo 3 dias nas capitais, etc.).
- sat/web/: geocolor.jpg e infravermelho das últimas 24 h (use só se servir de fundo).

## CHAMADA, CENA E TOM DE ALERTA
- Gancho = UM fato, UM lugar, UM número e QUANDO ("a partir de amanhã", "até sexta", "na madrugada de quarta"). Uma ideia só: "até 125 mm em MT e 40 °C no PI" (duas ideias) rendeu pouco; "2.163 cidades em alerta de temporal" rendeu muito.
- Linguagem de ALERTA: "Atenção", "alerta", "se prepare", "chega", "despenca", "dispara", "atinge". Frases curtas. Diga o que muda para quem mora lá (tirar o carro da rua, roupa de frio, água, evitar estrada).
- Não existe dia sem alerta: se a semana estiver calma, ache o número mais forte do Brasil (maior calor, maior chuva prevista, frio fora de época, rajada, mais cidades em aviso) e abra com ele. Tempo bom nunca abre o vídeo.
- Não repita o gancho de ontem (linha 1 do yt.txt da edição modelo {PREV}); se a ameaça é a mesma, mude o ângulo (outro lugar, outro número, o dia que piora).
- O mesmo gancho vai no quadro 0, na f1 e no título.

## QUADRO 0 (frame 0) — CENA QUE IMPRESSIONA
É o que faz a pessoa parar de rolar. Do t=0 até o fim da f1, grande:
- faixa de alerta (vermelho/amarelo, padrão INEMA) com "ALERTA · PRÓXIMOS 7 DIAS" e a data dd/mm/aaaa;
- o NÚMERO mais forte com o lugar e o quando (ex.: "ATÉ 180 MM NO RS ATÉ SEXTA", "42 °C EM CUIABÁ NO SÁBADO");
- uma frase curta e enorme que fala com quem assiste (ex.: "SE PREPARE", "A SUA CIDADE ESTÁ NO CAMINHO?", "O FRIO VOLTA COM FORÇA");
- o mapa já com a área ameaçada pintada forte (não um mapa vazio).
O quadro 0 não entra com fade (Lesson do CLAUDE.md). Confira o quadro 0 extraído (ffmpeg -frames:v 1) e OLHE a imagem antes de terminar.

## Passos
1. Pesquisa: leia om/prev15_resumo.json (bloco semana), a grade dia a dia e os brutos; busque nas fontes confiáveis o que vem nos próximos 7 dias. Grave pesquisa/noticias.md (fato, número, fonte, URL, data), pesquisa/dados.md (os números exatos do Open-Meteo, com o dia) e pesquisa/proposta.md (pauta, por quê, gancho do quadro 0, e como difere do gancho de ontem).
2. Roteiro em falas.json (mesmo formato do modelo): 9 a 11 falas, 170 a 220 palavras (uns 75 a 85 s na voz do avatar).
   - f1: começa PELO alerta (número, lugar, quando), falando com quem assiste; a data curta vem depois ("Atenção, Rio Grande do Sul: até cento e oitenta milímetros de chuva até sexta. É o alerta da semana, quinta, cinco de novembro.").
   - as falas seguintes: por ameaça e região, o mais grave primeiro, sempre com o dia da semana ("amanhã", "no sábado"); chuva acumulada, temporal, calor, frio, vento.
   - uma fala com os alertas oficiais vigentes (INMET/Defesa Civil) se houver.
   - uma fala do que fazer (curta, prática).
   - penúltima: pergunta para comentar ("De que cidade você é? Comenta aqui como está o tempo aí").
   - última, sempre: "No inema ponto club você pode aprender sobre inteligência artificial." com legenda "No inema.club você pode aprender sobre inteligência artificial." CTA só o inema.club: nunca "segue o canal", "se inscreva". Nunca termo de alívio para tragédia ("por sorte", "felizmente", "ainda bem", "melhor").
   - no campo "fala" os números vão por extenso; no campo "legenda" com algarismos. "Você", NUNCA "tu", "teu", "tua", "ti" — vale também para os textos na tela.
3. gerar_cena.py: já copiado do modelo. Adapte TUDO a esta edição: DATA, quadro 0 (acima), câmeras por fala no mapa do Brasil, estados pintados pela ameaça prevista (por_uf), pinos nas cidades citadas, painéis/contadores com os números previstos e o dia (rótulo "previsto 06 a 12/11"), fontes de cada trecho ("Open-Meteo, previsão lida em {DATA_BR}"), cta, selo "ALERTA · 06 A 12/11". Tire o que for de 24 h passadas ou de tendência 15 dias que não estiver no roteiro. Mantenha o comportamento de --canto (usa avatar/tempos.json, layout canto). Cada `em(fid, palavra)` precisa achar a palavra na legenda daquela fala.
4. Versão mapa (é também o plano B se o avatar falhar), na pasta da edição:
   `bash {RAIZ}/motor/vaga.sh gpu eventosextremospub-tts python3 narrar.py` → tempos.json e narração (voz do Nei, local; entra na vaga gpu da máquina e pode esperar a vez até 30 min: rode com timeout longo ou em segundo plano e espere terminar. Se ele ou o montar.sh saírem com código 75 ou com "ocupada além do tempo de espera", a máquina está ocupada: grave OCUPADO.txt com essa linha e PARE, sem tentar de novo nem rodar fora da vaga); logo depois `python3 {RAIZ}/motor/pausa_pergunta.py {ED}`
   `python3 gerar_cena.py`
   `cd {RAIZ} && GEO=geo-br.js motor/montar.sh {ED}` → video.mp4
   Confira: ffprobe (1080x1920), e extraia uns 8 quadros (o quadro 0, cada painel, cta) com ffmpeg e OLHE as imagens (Read). Verifique: quadro 0 cheio e impressionante, data grande, contadores terminando no número certo, pino sem ficar atrás de painel, legenda legível. Corrija e renderize de novo se precisar.
5. yt.txt: linha 1 = título em português, até 80 caracteres, sem #Shorts (o script põe), que COMEÇA pelo alerta (número + lugar + quando, uma ideia só) e termina com "· Alerta da semana dd/mm". Linhas seguintes: de 4 a 8 linhas com os números do vídeo, os dias e as fontes.
6. Confira no fim: falas.json, gerar_cena.py, tempos.json, video.mp4 e yt.txt existem e batem entre si.

Se algo impedir a edição (sem dados, render quebrado sem conserto), grave ERRO.txt com o motivo em 2 ou 3 linhas e pare.
Se uma fonte falhar ou bloquear, anote uma linha em ~/projetos/wifi/LIMITES.md (o que tentou, o que barrou, contorno, proposta, aberto). Falha de código que você corrigiu: uma linha em {RAIZ}/FALHAS.md.
