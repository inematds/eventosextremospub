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
- fonte/vN/frames/f-NNN.jpg (1 quadro a cada 1,5 s de cada vídeo) e fonte/vN/telas/ (6 telas): são o MATERIAL VISUAL
  principal do vídeo (Nei, 07/11/2026: "mais frames das imagens reais", "menos mapa", "sem o formato dele", sem crédito).
  Veja os quadros e separe as CENAS REAIS: filmagem de granizo, lavoura destruída, rio cheio, estrada alagada, árvore caída,
  céu de tempestade, radar com cores fortes. Imagem dele que é só texto, cartaz ou aviso pronto não entra.
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
   telas com os micro clipes e imagens reais (3c), câmera FECHADA no Sul (RS/SC/PR) só nos trechos de satélite/mapa, estados pintados e pinos
   onde a fonte aponta risco, painéis e contadores com os números (previsão rotulada como previsão), avisos do INMET do Sul
   (ids escolhidos em inmet_avisos_ativos.json, asserts com a contagem nova), selo do topo só com fontes oficiais usadas
   (INMET, Open-Meteo, NOAA) + data, IR do satélite (3c), cta. Tire do modelo o que não
   estiver no Sul de hoje. Mantenha o comportamento de --canto (avatar/tempos.json, layout canto). Cada `em(fid, palavra)`
   precisa achar a palavra na legenda daquela fala.
3c. VISUAL (Nei, 07/11/2026): o ESTILO é o do Clima 24 h / Clima do DIA (cabeçalho, painéis, contadores, legenda palavra a
   palavra, avatar no canto), MAS o fundo da maior parte do vídeo são IMAGENS ou MICRO CLIPES REAIS dos vídeos do dia,
   ocupando a tela toda, com os quadros de texto e o avatar por cima. Pouco mapa.
   - Tudo LIMPO do outro perfil: nada da legenda queimada dele, da data ("06/11"), da sirene/ícone, do rosto dele (às vezes
     aparece numa janelinha no topo), do nome do perfil ou de cartaz/aviso pronto. Sem crédito, sem selo de fonte.
     Antes de recortar, olhe os quadros em fonte/vN/frames/ (Read) e anote para cada trecho bom: vídeo, segundos e o
     retângulo limpo em px do vídeo original (ffprobe dá o tamanho; o quadro f-NNN.jpg está em 720 de largura, converta).
   - MICRO CLIPES (preferido para filmagem real: granizo caindo, lavoura, rio, estrada, céu, radar animado), 2 a 3 s cada:
     `{RAIZ}/motor-sul/clip_quadros.sh fonte/vN/video.mp4 <início s> <duração s> <w:h:x:y limpo> cenas/clip-NN`
     (gera quadros 1080x1920: a área limpa na largura toda e a mesma cena desfocada atrás; CHEIO=1 só se o recorte já for
     alto, perto de 9:16). Na cena: `{"seq": [f"cenas/clip-NN/{x}" for x in sorted(os.listdir(...))], "fps": 30,
     "ini": ..., "fim": ..., "fade": .2, "zoom": .03}` em `C.telas` (o motor-sul toca os quadros; fim - ini ≤ duração do clipe).
     Confira 2 quadros de cada clipe (Read): nenhum texto ou ícone do outro perfil pode sobrar; se sobrar, recorte de novo
     ou não use.
   - IMAGENS paradas (quadro bom que não vale como clipe): recorte com PIL o retângulo limpo, monte 1080x1920 do mesmo jeito
     (área na largura toda + fundo desfocado) em cenas/real-NN.jpg e use `{"src": ..., "zoom": .06}` em `C.telas`.
   - Uma troca a cada 2 a 3 s, cada cena no momento da palavra que ela mostra (granizo quando fala granizo). Meta: pelo
     menos 60% do tempo em micro clipe ou imagem real/de impacto.
   - SATÉLITE: 1 ou 2 trechos (4 a 6 s) com o infravermelho do GOES-19 sobre o Sul (sat/web/ir*.jpg, timelapse das nuvens
     de tempestade, como no Clima 24 h), câmera fechada em RS/SC/PR, rótulo "satélite · infravermelho" e janela de horas.
   - MAPA: no máximo 1 trecho curto (4 a 6 s) para mostrar ONDE vem a chuva/tempestade (estados pintados pelos avisos do
     INMET, pinos nas cidades); pode ser o mesmo trecho do satélite. Nada de colunas 3D nem câmera passeando.
   - Quadro 0 = a cena real mais forte do dia (imagem limpa) CHEIA, com o gancho ESCRITO DENTRO (PIL, fonte Sora/Inter
     grossa, amarelo #FACC15 e branco sobre faixa preta) e a data dd/mm/aaaa; sem cena real forte, gere pelo Codex
     (`echo "<pedido>" | codex exec -s workspace-write --skip-git-repo-check -C {ED}/capa-dia -`). Salve em
     capa-dia/abertura.png e confira (Read). Sem fade no quadro 0.
   - Falta cena real para algo que a fala diz (vendaval, enchente, geada) → imagem realista do Codex (selo "ilustração").
   - Painéis e contadores por cima das cenas (faixa escura, número em amarelo), chegando ao número QUANDO a palavra é dita
     (`ini = em(palavra) - 1.0`, `dur = 1.0`). Cuidado para o painel não cobrir o centro da cena real.
4. Versão mapa, na pasta da edição:
   `python3 narrar.py` → tempos.json e narração (voz do Nei, local); logo depois `python3 {RAIZ}/motor/pausa_pergunta.py {ED}`
   `python3 gerar_cena.py`
   `cd {RAIZ} && GEO=geo-br.js motor-sul/montar.sh {ED}` (motor PRÓPRIO do Impacto Sul; nunca mexa em {RAIZ}/motor/, que é dos outros vídeos diários) → video.mp4
   Confira: ffprobe (1080x1920), extraia uns 8 quadros (abertura, cada estado, cta) e OLHE as imagens (Read): data na
   abertura, contadores no número certo, pino sem ficar atrás de painel, borda do satélite não aparecendo, legenda legível.
   Corrija e renderize de novo se precisar.
5. yt.txt: linha 1 = título até 80 caracteres que COMEÇA pelo gancho (fato + lugar do Sul + quando) e termina com
   "· Impacto Sul dd/mm". Ex.: "Rajada de 90 km/h no oeste gaúcho esta noite · Impacto Sul 06/11". Linhas seguintes: 4 a 8
   linhas com os pontos do vídeo (sem citar perfil, TikTok, meteorologista nem vídeo).
6. Confira no fim: falas.json, gerar_cena.py, tempos.json, video.mp4 e yt.txt existem e batem entre si.

Se algo impedir a edição, grave ERRO.txt com o motivo em 2 ou 3 linhas e pare.
Falha de código que você corrigiu: uma linha em {RAIZ}/FALHAS.md.
