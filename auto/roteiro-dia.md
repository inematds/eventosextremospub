Você está rodando sozinho (sem ninguém para responder) a edição "Clima do DIA" do projeto eventosextremospub, de {DATA_BR}.
Não faça perguntas: decida e siga. Depois o script auto/rodar.sh faz o avatar (HeyGen), publica no lives10 e manda ao bot.
Você NÃO faz: git, publicação, HeyGen, bot, nada no Vercel. Só os arquivos desta edição.
PALAVRA PROIBIDA (Nei, 15/10/2026): nunca "morte", "mortes", "morto(s)", "morreu", "óbito", "faleceu" — nem na fala, nem na legenda, nem na tela (pinos, painéis, unid de contador, hero), nem no yt.txt. Use "vítimas" (ex.: "71 vítimas na Tailândia"; "uma vítima no temporal"). Se a fonte (boletim, notícia) falar em mortes, reescreva com "vítimas". Os vídeos que falaram "mortos" tiveram pouca entrega no YouTube; o portão do rodar.sh reprova.

Pasta da edição: {ED}
Edição modelo (Short 9:16 do Brasil, layout canto): {PREV}
Raiz do projeto: {RAIZ} (leia CLAUDE.md e README.md antes de tudo; as Lessons do CLAUDE.md valem)

## A FONTE DA VERDADE (Nei, 13/10/2026)
- fonte/transcript.txt (e transcript.srt com tempos) = a transcrição do boletim de meteorologia do dia, publicado por volta do meio-dia. É a fonte da verdade do vídeo: a situação do tempo de HOJE e dos próximos dias no Brasil, como os meteorologistas explicaram.
- Confie nela: NÃO precisa conferir os números em outra fonte. NUNCA cite o canal, os apresentadores, o YouTube ou "um vídeo": o Nei fala como quem conhece a situação. Na tela, a fonte dos números do boletim é "Meteorologia · {DATA_BR}"; números que vierem dos brutos da coleta levam a fonte própria (INMET, Open-Meteo, NOAA/GOES).
- Se a transcrição citar data diferente de hoje ou estiver vazia, grave ERRO.txt e pare.

## Já coletado pelo script (para o mapa)
- pesquisa/bruto/: resumo.json, inmet_avisos_ativos.json, previsao7d.json etc. (coleta/ultimas24h.py). Use os avisos do INMET para pintar estados e a previsão para gráficos, se ajudar a contar o que o boletim disse.
- sat/web/: geocolor.jpg e ir00..irNN.jpg + ir_tempos.json (infravermelho GOES-19 das últimas 24 h).

## Passos
1. Leia a transcrição inteira. Grave pesquisa/boletim.md com os pontos do dia: o sistema que manda no tempo (frente fria, ciclone, bloqueio, umidade…), onde chove forte, onde faz calor ou frio (com temperaturas), riscos (temporal, granizo, vento, geada), o que muda nos próximos dias, por região. Anote o tempo (mm:ss) de cada fato. Grave pesquisa/proposta.md com a pauta e a ordem.
2. Roteiro em falas.json (mesmo formato do modelo): 10 a 12 falas, 190 a 230 palavras (uns 80 s na voz do avatar).
   - f1: dia da semana e data por extenso + o fato mais forte do tempo hoje (gancho com número ou lugar).
   - falas do meio: o porquê (o sistema) em frase simples, depois região por região o que acontece hoje, com lugar e número (temperatura, chuva, vento); depois o que vem nos próximos dias (dito como previsão: "deve", "a previsão é").
   - penúltima (engajamento, Nei 13/10/2026): pedir de onde a pessoa está e como está o tempo aí, ex.: "De onde você está assistindo? E como está o tempo aí agora? Comenta aqui." (card: "DE ONDE VOCÊ É?" / "COMO ESTÁ AÍ?").
   - última, sempre (CTA): dizer que a pessoa pode aprender no inema.club: "No inema ponto club você pode aprender sobre inteligência artificial." com legenda "No inema.club você pode aprender sobre inteligência artificial." (card: "APRENDA IA" / "inema.club").
   - CTA só o inema.club. Tratar por "você", nunca "tu/teu/tua/ti". Nunca termo de alívio sobre tragédia ("por sorte", "felizmente", "ainda bem", "melhor", "boa notícia").
   - no campo "fala" números por extenso (ano também); no campo "legenda" com algarismos. Escreva "mensagem de texto", nunca "SMS".
3. gerar_cena.py: copiado do modelo. Adapte TUDO ao boletim de hoje: DATA, marca/selo "CLIMA DO DIA", câmeras por fala indo às regiões citadas, estados pintados e pinos onde o boletim aponta risco, painéis e contadores com os números do boletim, IR (rótulo e janela), avisos do INMET (ids escolhidos em inmet_avisos_ativos.json, asserts com a contagem nova), fontes de cada trecho, cta. Tire o que for do Clima 24 h e não estiver no boletim (focos do INPE, volumes somados) se não ajudar. Mantenha o comportamento de --canto (avatar/tempos.json, layout canto). Cada `em(fid, palavra)` precisa achar a palavra na legenda daquela fala.
3c. VISUAL OBRIGATÓRIO (Nei, 13/10/2026, revisão do 1º Clima do DIA):
   - Quadro 0 = imagem CHEIA de impacto (1080x1920) com o gancho ESCRITO DENTRO, gerada pelo Codex pela assinatura (`echo "<pedido>" | codex exec -s workspace-write --skip-git-repo-check -C {ED}/capa-dia -`, salvar em capa-dia/abertura.png; sem logotipo nem marca; luz neutra). Confira o texto (Read). Sem fade no quadro 0; sai em ~2 s para o mapa.
   - Falou de oceano (El Niño, Pacífico, Atlântico) → a câmera VAI até o oceano e mostra a anomalia real da temperatura do mar (NOAA/GIBS; exemplo em edicoes/2026-10-12-mundo-clima), com pino e número.
   - Volume de chuva grande (chuva de um mês, acumulado) → colunas 3D (`C.colunas`, câmera com pitch 50–60 e bearing girando), altura = mm previstos, rotulado como previsão.
   - Granizo, vendaval, enchente, fogo → imagem realista de impacto do Codex (selo "ilustração") no momento da palavra; nunca desenho SVG do fenômeno.
   - Número de um estado → depois o TOTAL do Brasil com o mesmo destaque (ex.: focos do Pará e total do país).
   - Cabeçalho "INEMA · CLIMA DO DIA" numa linha só (sem corte no topo). Contador chega ao número QUANDO a palavra é dita (confira em tempos.json e avatar/tempos.json). Uma troca visual por fala.
4. Versão mapa, na pasta da edição:
   `python3 narrar.py` → tempos.json e narração (voz do Nei, local)
   `python3 gerar_cena.py`
   `cd {RAIZ} && GEO=geo-br.js motor/montar.sh {ED}` → video.mp4
   Confira: ffprobe (1080x1920), extraia uns 8 quadros (abertura, cada região, cta) e OLHE as imagens (Read). Verifique: data grande na abertura, contadores no número certo, pino sem ficar atrás de painel, borda do satélite não aparecendo, legenda legível. Corrija e renderize de novo se precisar.
5. yt.txt: linha 1 = título até 80 caracteres com "Clima do dia", o fato principal e a data dd/mm. Linhas seguintes: 4 a 8 linhas com os pontos do vídeo (sem citar canal nem vídeo).
6. Confira no fim: falas.json, gerar_cena.py, tempos.json, video.mp4 e yt.txt existem e batem entre si.

Se algo impedir a edição, grave ERRO.txt com o motivo em 2 ou 3 linhas e pare.
Falha de código que você corrigiu: uma linha em {RAIZ}/FALHAS.md.
