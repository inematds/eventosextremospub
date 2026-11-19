# Dados da edição · 19/11/2026
Coleta `pesquisa/bruto/resumo.json`: 19/11 08h30 UTC (05h30 Brasília). Janela de notícias: 18/11 08h30 a 19/11 08h30 UTC. Acumulados de sensores têm janela móvel de 24 h terminando no último registro, não exatamente no horário editorial.

## Observado
| Fato ao ar | Bruto e registro | Valor original / exibição |
|---|---|---|
| Timbó, SC | cemaden_getJson2_todas_ufs.json, id 4043, Tiroleses, 19/11 08h10 UTC | 217,42 / 217,4 mm em 24 h, truncado |
| Chapada do Norte, MG | mesmo arquivo, id 9327, Centro, 19/11 08h20 UTC | 106,8 mm em 24 h |
| Dueré, TO | mesmo arquivo, Dona Constanci, 19/11 08h10 UTC | 65,4 mm em 24 h |
| Vento no aeroporto de Cuiabá | noaa_metar_brasil_24h.json + resumo.json, SBCY, 18/11 11h25 UTC, 17017G32KT | 32 nós × 1,852 = 59,264; truncado para 59,2 km/h |
| Calor no aeroporto de Teresina | mesmos brutos, SBTE, 18/11 17h UTC | 37 °C; não é média municipal |
| Focos do dia anterior | inpe_focos_diario_br_20261118.csv, data UTC de 18/11, somente AQUA_M-T | Brasil 441; CE 111; MA 108; RR 54. Foco não equivale a incêndio individual. Pontos no mapa vêm de VIIRS agregados em grade de 0,08 grau; não usar sua quantidade como o contador AQUA. |

## Soma observada validada
`pesquisa/soma-validada.json`: 15.448,67 mm·estação, 1.665 sensores de 24 UFs. Tela/fala mostram 15.448 (truncamento inteiro). Soma dos pluviômetros, não lâmina média do país nem volume físico em litros. Somar sensores de densidades diferentes não mede qual estado recebeu maior chuva por área.

Recálculo: aceitar último registro entre corte menos 6 h e o corte inclusive, valor numérico não negativo, excluir id 8327. O resumo automático soma 16.817,6 mm·estação, mas inclui relógios posteriores ao corte e esse sensor. Excluído Pedro Alexandre: acc24=360,2; acc48=17.640,2; acc72=21.491,6; acc96=26.563 mm, sequência incompatível com uso editorial sem validação. Não tratar 360,2 mm como evento confirmado.

| UF | soma dos pluviômetros (mm·estação) | sensores |
|---|---:|---:|
| MG | 6719.86 | 486 |
| SP | 2873.92 | 338 |
| BA | 1643.06 | 218 |
| RJ | 1463.21 | 120 |
| SC | 1067.46 | 147 |
| GO | 258.40 | 35 |
| MA | 208.14 | 20 |
| TO | 178.68 | 19 |
| MT | 151.40 | 10 |
| RS | 132.20 | 88 |
| PR | 121.00 | 49 |
| RO | 108.80 | 11 |
| PI | 89.20 | 16 |
| AC | 78.40 | 14 |
| PE | 66.85 | 26 |
| SE | 62.40 | 7 |
| PA | 57.20 | 13 |
| ES | 51.48 | 15 |
| AM | 48.41 | 13 |
| MS | 36.20 | 5 |
| AP | 21.40 | 8 |
| DF | 6.40 | 3 |
| AL | 3.60 | 1 |
| CE | 1.00 | 3 |

## Avisos oficiais e previsão
`inmet_avisos_ativos.json`: selecionar pelo tipo Tempestade e severidade, conferir ids e geocodes únicos. Hoje 56446 (amarelo), 19/11 00h–23h59: 3.437 municípios; amanhã 56447 (amarelo), 20/11 00h–23h59: 3.372. Prevê 20–30 mm/h ou até 50 mm/dia, ventos de 40–60 km/h e granizo. Laranja 56449: 140 municípios de MT/MS/RO até 19/11 07h20; risco previsto de 30–60 mm/h ou 50–100 mm/dia e ventos de 60–100 km/h. Não somar amarelo e laranja, pois há sobreposição. URLs https://avisos.inmet.gov.br/56446 e https://avisos.inmet.gov.br/56447 e https://avisos.inmet.gov.br/56449 .

`previsao7d.json`: modelo Open-Meteo best_match, 27 capitais, 19 a 25/11. Toda chuva abaixo é soma dos pontos das capitais, nunca lâmina de área ou média regional. Total 886,1 mm. Soma regional: N 189,6; NE 58,0; CO 193,4; SE 230,3; S 214,8 mm. Máxima soma diária: 178,0 na quarta (25). Pico de temperatura previsto na terça (24): 40,8 °C em Teresina; média das máximas usa as 27 capitais. https://open-meteo.com/ .

| dia | N | NE | CO | SE | S | soma mm | média máximas °C |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-11-19 | 17.4 | 4.0 | 13.7 | 50.7 | 30.1 | 115.9 | 31.2 |
| 2026-11-20 | 36.0 | 7.8 | 26.7 | 21.9 | 35.5 | 127.9 | 31.3 |
| 2026-11-21 | 33.1 | 5.3 | 27.8 | 6.3 | 9.7 | 82.2 | 31.4 |
| 2026-11-22 | 7.4 | 9.6 | 19.9 | 23.0 | 45.6 | 105.5 | 31.2 |
| 2026-11-23 | 36.0 | 9.9 | 38.5 | 15.1 | 43.1 | 142.6 | 31.3 |
| 2026-11-24 | 17.9 | 7.8 | 31.0 | 60.1 | 17.2 | 134.0 | 31.4 |
| 2026-11-25 | 41.8 | 13.6 | 35.8 | 53.2 | 33.6 | 178.0 | 31.3 |

## Satélite e limite da coleta
NASA GIBS / NOAA GOES-19: `sat/web/geocolor.jpg`, IR e `ir_tempos.json`: 18/11 08h UTC até 19/11 08h UTC (05h–05h Brasília), 49 horários. Filtrar quadros sem informação usando luminosidade, conforme o motor. Base mundial Blue Marble reutilizada da edição anterior, imagem estática, sem alegar nova medição.

INMET estações: 25 pedidos HTTP 204 sem dados, registrado em resumo.json e inmet_estacoes_tentativas.json; sem dado de estação INMET ao ar, sem chave ou API alternativa. Limite anotado no hub. As medições de chuva usam CEMADEN e vento/temperatura usam NOAA.
