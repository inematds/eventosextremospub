Você está rodando sozinho (sem ninguém para responder) a edição "Impacto Sul" do projeto eventosextremospub, de {DATA_BR}.
Não faça perguntas: decida e siga. Depois o script auto/rodar.sh faz o avatar (HeyGen), publica no lives10 e manda ao bot.
Você NÃO faz: git, publicação, HeyGen, bot, nada no Vercel. Só os arquivos desta edição.
PALAVRA PROIBIDA (Nei, 15/10/2026): nunca "morte", "mortes", "morto(s)", "morreu", "óbito", "faleceu" — nem na fala, nem na legenda, nem na tela (pinos, painéis, unid de contador, hero), nem no yt.txt. Use "vítimas". Se a fonte falar em mortes, reescreva com "vítimas". O portão do rodar.sh reprova.

Pasta da edição: {ED}
Edição modelo (Short 9:16 do Brasil, layout canto): {PREV}
Raiz do projeto: {RAIZ} (leia CLAUDE.md e README.md antes de tudo; as Lessons do CLAUDE.md valem)

## O QUE É O IMPACTO SUL (Nei, 07/11/2026)
Short 9:16 diário às 21 h sobre o tempo no SUL do Brasil (RS, SC, PR): o que de mais forte aconteceu HOJE ({DATA_BR}) e o que vem
nas próximas horas e dias. Nome na tela: "INEMA · IMPACTO SUL". Tom de ALERTA (eventos extremos), não boletim morno.

## A FONTE DA VERDADE
- fonte/transcript.txt = a transcrição de TODOS os vídeos publicados hoje por um perfil de meteorologia do Sul (um bloco
  "### Vídeo N · publicado hh:mm" por vídeo, com a legenda do post); fonte/video_info.txt lista id|hora|duração|legenda.
  Confie nela: NÃO precisa conferir os números em outra fonte. NUNCA cite o perfil, o TikTok, o meteorologista ou "um vídeo":
  o Nei fala como quem acompanha o tempo do Sul. Na tela, a fonte dos números dela é "Meteorologia · {DATA_BR}"; números dos
  brutos da coleta levam a fonte própria (INMET, Open-Meteo, NOAA/GOES).
- Junte os vídeos do dia num vídeo só: o fato mais forte abre; o que já aconteceu fica separado do que é previsão; o vídeo
  mais novo vale mais para a previsão (se dois vídeos discordam, vale o mais recente).
- fonte/vN/telas/tela-NN.jpg (6 telas por vídeo): OLHE as telas (Read) antes de planejar, para ver que mapa/área/sistema o
  meteorologista destacou, e refaça parecido no nosso motor (mapa 3D, câmera no Sul, áreas, setas, pinos) ou busque imagem
  de impacto do mesmo fenômeno. As telas são SÓ referência: nunca entram no vídeo, nem recortadas (marca d'água e rosto).
- Transcrição vazia ou sem nada de tempo/clima → grave ERRO.txt e pare.

## CHAMADA E TOM FORTES (mesma regra da Previsão do Dia, medida no lives10)
- Gancho = UM fato, UM lugar no Sul, UM número e QUANDO (hoje, esta noite, amanhã, até domingo). Ex. forte: "Rajada de
  noventa quilômetros por hora no oeste gaúcho esta noite". Fraco: duas ideias, datas longe, tempo bom como gancho.
- Dia calmo: ache o número mais forte do Sul na fonte e nos brutos (chuva prevista, cidades em aviso do INMET no RS/SC/PR,
  rajada, geada, calor) e abra com ele. "Tempo firme" nunca abre.
- Não repita o gancho das últimas 3 edições de Impacto Sul nem o da Previsão do Dia de hoje (linha 1 do yt.txt de
  `ls -d {RAIZ}/edicoes/*-impacto-sul {RAIZ}/edicoes/{DIA}-previsao-do-dia 2>/dev/null`). Mesmo fato → outro ângulo.
- Frases curtas, verbos fortes ("chega", "despenca", "dispara", "atenção"); diga o que muda para quem mora lá
  ("se você está na serra gaúcha, ..."). Previsão sempre dita como previsão ("deve", "pode", "a previsão é").
- O mesmo gancho vai no quadro 0 (imagem com o texto escrito), na f1 e no título.

## Já coletado pelo script (para o mapa)
- pesquisa/bruto/: resumo.json, inmet_avisos_ativos.json, previsao7d.json etc. Use os avisos do INMET do RS/SC/PR para pintar
  municípios/estados e a previsão para gráfico, se ajudar a contar o que a fonte disse.
- sat/web/: geocolor.jpg e ir00..irNN.jpg + ir_tempos.json (infravermelho GOES-19 das últimas 24 h).

## Passos
1. Leia a transcrição inteira e olhe as telas. Grave pesquisa/boletim.md (o que aconteceu hoje no Sul, o sistema que manda no
   tempo, onde e quando chove/venta/esfria nas próximas horas e dias, com números e o vídeo/tempo de onde saiu cada fato) e
   pesquisa/proposta.md (pauta e ordem).
2. Roteiro em falas.json (mesmo formato do modelo): 9 a 12 falas, 170 a 220 palavras (uns 75 s na voz do avatar; nunca
   passar de 2:40).
   - f1: começa PELO gancho e só depois a data curta. Ex.: "Granizo e rajada de noventa quilômetros por hora no oeste
     gaúcho esta noite. É o impacto no Sul desta quinta, seis de novembro." Nunca abrir com "Impacto Sul de hoje...".
   - meio: o que já aconteceu hoje (lugar + número); o porquê (o sistema) em frase simples; o que vem esta noite e amanhã,
     estado por estado (RS, SC, PR), com lugar e número; o dia do pico do risco.
   - penúltima (engajamento): "De que cidade do Sul você está assistindo? E como está o tempo aí agora? Comenta aqui."
     (card: "DE ONDE VOCÊ É?" / "COMO ESTÁ AÍ?").
   - última, sempre (CTA): "No inema ponto club você pode aprender sobre inteligência artificial." com legenda
     "No inema.club você pode aprender sobre inteligência artificial." (card: "APRENDA IA" / "inema.club").
   - CTA só o inema.club. Tratar por "você", nunca "tu/teu/tua/ti". Nunca termo de alívio ("por sorte", "felizmente",
     "ainda bem", "melhor", "boa notícia").
   - no campo "fala" números por extenso (ano também); no campo "legenda" com algarismos. Fala nunca termina em número solto
     (pôr a unidade depois). Escreva "mensagem de texto", nunca "SMS".
3. gerar_cena.py: copiado do modelo. Adapte TUDO ao Impacto Sul de hoje: DATA, cabeçalho "INEMA · IMPACTO SUL" numa linha só,
   câmeras por fala FECHADAS no Sul (RS/SC/PR) e indo às cidades/regiões citadas, municípios/estados pintados e pinos onde a
   fonte aponta impacto ou risco, painéis e contadores com os números (previsão rotulada como previsão), IR do satélite
   (rótulo e janela) mostrando as nuvens sobre o Sul, avisos do INMET do Sul (ids escolhidos em inmet_avisos_ativos.json,
   asserts com a contagem nova), fontes de cada trecho (selo com no máximo 3 fontes + data), cta. Tire do modelo o que não
   estiver no Sul de hoje. Mantenha o comportamento de --canto (avatar/tempos.json, layout canto). Cada `em(fid, palavra)`
   precisa achar a palavra na legenda daquela fala.
3c. VISUAL (mesmas regras do Clima do DIA):
   - Quadro 0 = imagem CHEIA de impacto (1080x1920) com o gancho ESCRITO DENTRO, gerada pelo Codex pela assinatura
     (`echo "<pedido>" | codex exec -s workspace-write --skip-git-repo-check -C {ED}/capa-dia -`, salvar em
     capa-dia/abertura.png; sem logotipo nem marca; luz neutra; paisagem reconhecível do Sul). Confira o texto (Read). Sem
     fade no quadro 0; sai em ~2 s para o mapa.
   - Volume de chuva grande → colunas 3D (`C.colunas`, pitch 50–60, bearing girando), altura = mm, rotulado.
   - Granizo, vendaval, enchente, geada → imagem realista de impacto do Codex (selo "ilustração") no momento da palavra;
     nunca desenho SVG do fenômeno.
   - Contador chega ao número QUANDO a palavra é dita (`ini = em(palavra) - 1.0`, `dur = 1.0`). Uma troca visual por fala.
4. Versão mapa, na pasta da edição:
   `python3 narrar.py` → tempos.json e narração (voz do Nei, local); logo depois `python3 {RAIZ}/motor/pausa_pergunta.py {ED}`
   `python3 gerar_cena.py`
   `cd {RAIZ} && GEO=geo-br.js motor/montar.sh {ED}` → video.mp4
   Confira: ffprobe (1080x1920), extraia uns 8 quadros (abertura, cada estado, cta) e OLHE as imagens (Read): data na
   abertura, contadores no número certo, pino sem ficar atrás de painel, borda do satélite não aparecendo, legenda legível.
   Corrija e renderize de novo se precisar.
5. yt.txt: linha 1 = título até 80 caracteres que COMEÇA pelo gancho (fato + lugar do Sul + quando) e termina com
   "· Impacto Sul dd/mm". Ex.: "Rajada de 90 km/h no oeste gaúcho esta noite · Impacto Sul 06/11". Linhas seguintes: 4 a 8
   linhas com os pontos do vídeo (sem citar perfil, TikTok, meteorologista nem vídeo).
6. Confira no fim: falas.json, gerar_cena.py, tempos.json, video.mp4 e yt.txt existem e batem entre si.

Se algo impedir a edição, grave ERRO.txt com o motivo em 2 ou 3 linhas e pare.
Falha de código que você corrigiu: uma linha em {RAIZ}/FALHAS.md.
