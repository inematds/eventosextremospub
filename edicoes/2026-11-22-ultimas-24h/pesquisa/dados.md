# Dados conferidos — 22/11/2026
Fechamento da coleta: **08h30 UTC / 05h30 BRT**. Janela do resumo: 21/11 08h30 a 22/11 08h30 UTC. Todos os arquivos citados são relativos a pesquisa/.

## CEMADEN
Bruto: `bruto/cemaden_getJson2_todas_ufs.json`. Endpoint público: https://resources.cemaden.gov.br/graficos/interativo/getJson2.php?uf=SP (repetido por UF pelo coletor). O resumo automático tem 7.500,6 mm·estação, mas inclui tipos de instrumento distintos e leituras sem o filtro temporal desta edição: **não vai ao ar esse total**.

Filtro reproduzido em gerar_cena.py: tipoestacao == 1; acc24hr numérico e não negativo; fechamento menos 6 horas < datahoraUltimovalor <= fechamento, interpretado em UTC. `soma-validada.json` conserva cada UF e sua quantidade de sensores. Total validado: **6.742,15 mm·estação em 1.202 pluviômetros**. Voz e contador usam **6.742**, inteiro truncado. É soma dos pluviômetros, não lâmina territorial nem volume em litros.

| UF | Soma (mm·estação) | Sensores |
|---|---:|---:|
| MG | 2.474,19 | 347 |
| GO | 953,00 | 44 |
| RS | 644,20 | 236 |
| SP | 582,60 | 193 |
| SC | 309,34 | 87 |
| TO | 285,60 | 22 |

O arquivo JSON contém as demais UFs. Ranking na tela: inteiros truncados 2.474, 953 e 644, cada um rotulado por UF.

| Fala | Sensor / cidade | Medição de 24 h | Última atualização UTC / BRT |
|---|---|---:|---|
| f3 | 3466, Massaguaçu, Caraguatatuba/SP | 232,16 mm | 22/11 08h20 / 05h20 |
| f4 | 6764, Prédio Administrativo da Prefeitura, Aparecida de Goiânia/GO | 86,6 mm | 22/11 07h50 / 04h50 |
| f5 | 9487, Belmiro, Goiatins/TO | 93,8 mm | 22/11 08h20 / 05h20 |

Aquidabã, 382,2 no resumo: instrumento tipo 5, excluído. Não chamar essa leitura de recorde de chuva.

## INMET
`bruto/inmet_avisos_ativos.json`, https://apiprevmet3.inmet.gov.br/avisos/ativos . Seleção por descrição Tempestade e severidade Perigo Potencial, validando vigência e IDs desta rodada. Aviso 56475: 21/11 09h28 a 22/11 23h59; **3.717 municípios únicos**, 19 UFs. Aviso 56476: 23/11 00h00 a 23h59; **3.059 municípios únicos**, 19 UFs. A diferença não representa redução garantida do risco. Ambos amarelos: previsão de 20–30 mm/h ou até 50 mm/dia, vento 40–60 km/h e possibilidade de granizo.
Estações INMET: 25 respostas HTTP 204 sem dados, conforme resumo.json e inmet_estacoes_tentativas.json. Nenhum número observado de estação INMET usado. Limite registrado no hub.

## INPE
`bruto/inpe_focos_diario_br_20261121.csv`, dia **21/11 UTC completo**, https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/diario/Brasil/focos_diario_br_20261121.csv . Filtrar satelite == AQUA_M-T: **1.425 focos no Brasil**, Maranhão 684, Ceará 246, Piauí 201. Contagens recalculadas do CSV e protegidas por asserts. Pontos cartográficos: NOAA-20/21 em grade de 0,08° para visualização, não o universo da contagem. Não somar todos os satélites como incêndios únicos. CSV de 22/11 é parcial e não é usado.

## NOAA
`bruto/noaa_metar_brasil_24h.json`, https://aviationweather.gov/api/data/metar . Aeroporto **SBTE, Teresina**, 39 °C em **21/11 19h UTC / 16h BRT**. Dado de aeroporto, não recorde municipal nem máxima absoluta da cidade. Resumo traz 107 aeroportos e 2.137 observações. Não usar rajadas arredondadas do resumo na voz.

## Previsão Open-Meteo
`bruto/previsao7d.json` e `bruto/openmeteo_capitais_3d.json`, https://api.open-meteo.com/v1/forecast . best_match, 27 capitais, 22 a 28/11. Somas de pontos de capitais, não média do Brasil; a soma favorece regiões com mais capitais e não é comparável à soma de sensores CEMADEN. Toda a série, inclusive hoje, é **previsão**.

| Dia | N | NE | CO | SE | S | Soma chuva mm | Máxima média °C |
|---|---:|---:|---:|---:|---:|---:|---:|
| dom 22 | 13,4 | 1,8 | 16,5 | 26,7 | 37,7 | 96,1 | 31,5 |
| seg 23 | 16,1 | 4,7 | 26,6 | 25,5 | 29,0 | 101,9 | 31,8 |
| ter 24 | 19,5 | 15,3 | 31,5 | 40,8 | 30,2 | 137,3 | 31,5 |
| qua 25 | 32,8 | 12,5 | 34,1 | 58,2 | 29,0 | 166,6 | 31,9 |
| qui 26 | 28,4 | 5,5 | 57,0 | 74,7 | 3,9 | 169,5 | 30,2 |
| sex 27 | 40,1 | 2,4 | 31,2 | 69,5 | 0,0 | 143,2 | 29,4 |
| sáb 28 | 38,6 | 3,4 | 38,2 | 35,2 | 0,6 | 116,0 | 29,5 |

Total 7 dias: **930,6 mm somados**, inteiro truncado 930 na fala e no painel de volumes; valor exato na fonte. Regiões: N 188,9; NE 45,6; CO 235,1; SE **330,6**; S 130,4. Pico da soma diária: quinta 26, 169,5. Calor: Teresina pode atingir 40,9 °C na quarta 25; não confundir com a linha de médias das máximas das 27 capitais. BH lidera acumulado individual previsto, 143,5 mm. Totais sujeitos a décimos de diferença pela apresentação arredondada; asserts toleram <0,2 mm.

## Satélite e cartografia
NASA GIBS / NOAA GOES-19: https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi . `../sat/web/geocolor.jpg`, bbox [-76,-35,-33,7]. IR `ir00..48.jpg`, horários preservados em ir_tempos.json, **21/11 08h a 22/11 08h UTC** (05h a 05h BRT). Seleção por luminosidade remove quadros incompletos. O IR termina meia hora antes do fechamento dos sensores; rótulo diz 21–22/11, 24 h. `mundo.jpg` é o fundo Blue Marble estático copiado da edição modelo; não é observação meteorológica de hoje. Texturas `*-suave.png` derivam dos JPGs locais com alfa nas bordas, sem alterar os dados originais.
