Você está rodando sozinho (sem ninguém para responder) a edição "Previsão do Dia" do projeto eventosextremospub, de {DATA_BR}.
Não faça perguntas: decida e siga. Depois o script auto/rodar.sh faz o avatar (HeyGen), publica no lives10 e manda ao bot.
Você NÃO faz: git, publicação, HeyGen, bot, nada no Vercel. Só os arquivos desta edição.
PALAVRA PROIBIDA (Nei, 15/10/2026): nunca "morte", "mortes", "morto(s)", "morreu", "óbito", "faleceu" — nem na fala, nem na legenda, nem na tela (pinos, painéis, unid de contador, hero), nem no yt.txt. Use "vítimas" (ex.: "71 vítimas na Tailândia"; "uma vítima no temporal"). Se a fonte (boletim, notícia) falar em mortes, reescreva com "vítimas". Os vídeos que falaram "mortos" tiveram pouca entrega no YouTube; o portão do rodar.sh reprova.

Pasta da edição: {ED}
Edição modelo (Short 9:16 do Brasil, layout canto): {PREV}
Raiz do projeto: {RAIZ} (leia CLAUDE.md e README.md antes de tudo; as Lessons do CLAUDE.md valem)

## A FONTE DA VERDADE (Nei, 15/10/2026)
- fonte/transcript.txt (e transcript.srt com tempos) = a transcrição do último vídeo de previsão do tempo de um meteorologista; fonte/video_info.txt tem a data de envio (aaaammdd) e o título. É a fonte da verdade do vídeo: a PREVISÃO para hoje e os próximos dias no Brasil.
- Confie nela: NÃO precisa conferir os números em outra fonte. NUNCA cite o canal, o meteorologista, o YouTube ou "um vídeo": o Nei fala como quem conhece a previsão. Na tela, a fonte dos números da previsão é "Meteorologia · {DATA_BR}"; números que vierem dos brutos da coleta levam a fonte própria (INMET, Open-Meteo, NOAA/GOES).
- Se o vídeo é de ONTEM (data em video_info.txt), traduza as datas: o "amanhã" do vídeo é HOJE ({DATA_BR}); não fale do que já passou. Se a transcrição estiver vazia ou não for previsão do tempo, grave ERRO.txt e pare.

## Já coletado pelo script (para o mapa)
- pesquisa/bruto/: resumo.json, inmet_avisos_ativos.json, previsao7d.json etc. (coleta/ultimas24h.py). Use os avisos do INMET para pintar estados e a previsão para gráficos, se ajudar a contar o que a fonte disse.
- sat/web/: geocolor.jpg e ir00..irNN.jpg + ir_tempos.json (infravermelho GOES-19 das últimas 24 h).

## Passos
1. Leia a transcrição inteira. Grave pesquisa/boletim.md com os pontos da previsão: o sistema que manda no tempo (frente fria, ciclone, baixa pressão, bloqueio, umidade…), onde e quando chove forte (com volumes), onde esquenta ou esfria (temperaturas), riscos (temporal, granizo, vento, geada) com dia e região, a tendência dos próximos dias. Anote o tempo (mm:ss) de cada fato. Grave pesquisa/proposta.md com a pauta e a ordem.
2. Roteiro em falas.json (mesmo formato do modelo): 10 a 12 falas, 190 a 230 palavras (uns 80 s na voz do avatar). É PREVISÃO: tudo dito como previsão ("deve", "a previsão é", "pode"), nunca como certeza.
   - f1: "Previsão do dia", dia da semana e data por extenso + o fato mais forte da previsão (gancho com número ou lugar).
   - falas do meio: o porquê (o sistema) em frase simples; depois HOJE, região por região, com lugar e número; depois amanhã e os próximos dias (quando chega a chuva, quando muda a temperatura, onde está o risco).
   - penúltima (engajamento): "De onde você está assistindo? E como está o tempo aí agora? Comenta aqui." (card: "DE ONDE VOCÊ É?" / "COMO ESTÁ AÍ?").
   - última, sempre (CTA): "No inema ponto club você pode aprender sobre inteligência artificial." com legenda "No inema.club você pode aprender sobre inteligência artificial." (card: "APRENDA IA" / "inema.club").
   - CTA só o inema.club. Tratar por "você", nunca "tu/teu/tua/ti". Nunca termo de alívio ("por sorte", "felizmente", "ainda bem", "melhor", "boa notícia").
   - no campo "fala" números por extenso (ano também); no campo "legenda" com algarismos. Escreva "mensagem de texto", nunca "SMS".
3. gerar_cena.py: copiado do modelo. Adapte TUDO à previsão de hoje: DATA, marca/selo "PREVISÃO DO DIA" (cabeçalho "INEMA · PREVISÃO DO DIA" numa linha só), câmeras por fala indo às regiões citadas, estados pintados e pinos onde a previsão aponta risco, painéis e contadores com os números da previsão (rotulados como previsão), um painel com o gráfico dos próximos dias (previsao7d.json, chave "grafico" como no modelo) se ajudar, IR (rótulo e janela), avisos do INMET (ids escolhidos em inmet_avisos_ativos.json, asserts com a contagem nova), fontes de cada trecho, cta. Tire do modelo o que não estiver na previsão. Mantenha o comportamento de --canto (avatar/tempos.json, layout canto). Cada `em(fid, palavra)` precisa achar a palavra na legenda daquela fala.
3c. VISUAL (mesmas regras do Clima do DIA, Nei 13/10/2026):
   - Quadro 0 = imagem CHEIA de impacto (1080x1920) com o gancho ESCRITO DENTRO, gerada pelo Codex pela assinatura (`echo "<pedido>" | codex exec -s workspace-write --skip-git-repo-check -C {ED}/capa-dia -`, salvar em capa-dia/abertura.png; sem logotipo nem marca; luz neutra). Confira o texto (Read). Sem fade no quadro 0; sai em ~2 s para o mapa.
   - Falou de oceano → a câmera vai até o oceano e mostra a anomalia real da temperatura do mar (NOAA/GIBS; exemplo em edicoes/2026-10-12-mundo-clima), com pino e número.
   - Volume de chuva grande previsto → colunas 3D (`C.colunas`, pitch 50–60, bearing girando), altura = mm previstos, rotulado como previsão.
   - Granizo, vendaval, enchente → imagem realista de impacto do Codex (selo "ilustração") no momento da palavra; nunca desenho SVG do fenômeno.
   - Contador chega ao número QUANDO a palavra é dita (`ini = em(palavra) - 1.0`, `dur = 1.0`; confira em tempos.json e avatar/tempos.json). Uma troca visual por fala.
4. Versão mapa, na pasta da edição:
   `python3 narrar.py` → tempos.json e narração (voz do Nei, local); logo depois `python3 {RAIZ}/motor/pausa_pergunta.py {ED}` (1 s de pausa antes de "De que região...": Nei, 15/10/2026, a pergunta saía colada no assunto)
   `python3 gerar_cena.py`
   `cd {RAIZ} && GEO=geo-br.js motor/montar.sh {ED}` → video.mp4
   Confira: ffprobe (1080x1920), extraia uns 8 quadros (abertura, cada região, cta) e OLHE as imagens (Read). Verifique: data grande na abertura, contadores no número certo, pino sem ficar atrás de painel, borda do satélite não aparecendo, legenda legível. Corrija e renderize de novo se precisar.
5. yt.txt: linha 1 = título até 80 caracteres com "Previsão do Dia", o fato principal e a data dd/mm. Linhas seguintes: 4 a 8 linhas com os pontos do vídeo (sem citar canal, meteorologista nem vídeo).
6. Confira no fim: falas.json, gerar_cena.py, tempos.json, video.mp4 e yt.txt existem e batem entre si.

Se algo impedir a edição, grave ERRO.txt com o motivo em 2 ou 3 linhas e pare.
Falha de código que você corrigiu: uma linha em {RAIZ}/FALHAS.md.
