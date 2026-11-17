# Dados e rastreabilidade — 17/11/2026

Coleta às 08h30 UTC / 05h30 Brasília. Arquivos brutos preservados em bruto/. Janela editorial de 24 h. Os acumulados de cada estação terminam na última leitura indicada, até 30 minutos antes do corte para as estações narradas.

## CEMADEN
Fonte: https://resources.cemaden.gov.br/graficos/interativo/getJson2.php?uf=BA (uma consulta por UF); arquivo cemaden_getJson2_todas_ufs.json. Campos acc24hr e datahoraUltimovalor; relógio UTC. Candiba 134,4 mm às 08h00; Cristália G2-312030001A 127,2 e G2-312030002A 127,0 às 08h10; Rio Maria sensor 6802 126,2 às 08h30; Medianeira G2-411580402A 56,4 às 08h10; Niquelândia Belo Horizonte 39 às 07h50. Todos em 17/11 UTC, acumulados móveis de 24 h, sem somar sensores de uma cidade para representar sua chuva.

O resumo automático soma 33.682,5 mm·estação. Não usar esse total: contém o sensor 8327 Pedro Alexandre (3.851,6 mm) já rejeitado na edição anterior e relógios adiantados. Recalcular com leitura estritamente posterior a 02h30 UTC e até 08h30 UTC, excluir 8327. Resultado em soma-validada.json: 28.620,34 mm·estação, 2.123 sensores, 27 UFs. Zero válido entra; campo ausente/não numérico não entra. É soma dos pluviômetros, nunca chuva média/volume físico do país. Contador visual truncado em 28.620 (total exato 28.620,34 na fonte), fala conservadora 'mais de 28 mil'.

| UF | Soma mm·estação | Sensores |
|---|---:|---:|
| MG | 9090.63 | 529 |
| BA | 7720.50 | 278 |
| RJ | 2229.67 | 154 |
| PE | 1518.66 | 137 |
| SP | 1206.05 | 283 |
| TO | 1136.38 | 33 |
| CE | 960.97 | 77 |
| ES | 880.33 | 62 |
| MA | 605.60 | 67 |
| SC | 593.11 | 140 |
| SE | 489.20 | 42 |
| PA | 442.60 | 20 |
| AL | 344.47 | 33 |
| GO | 274.20 | 47 |
| PI | 247.80 | 43 |
| MT | 239.60 | 13 |
| AP | 214.20 | 11 |
| PB | 139.40 | 23 |
| PR | 115.02 | 40 |
| MS | 53.00 | 8 |
| RS | 48.00 | 37 |
| RO | 36.60 | 15 |
| AM | 17.76 | 15 |
| RN | 5.79 | 6 |
| DF | 5.40 | 4 |
| RR | 4.00 | 1 |
| AC | 1.40 | 5 |

## INPE
Arquivo inpe_focos_diario_br_20261116.csv: somente 16/11 UTC fechado, AQUA_M-T de referência: 317 focos, Pará 158, Maranhão 79, Amazonas 28. Mapa usa pontos VIIRS agregados; pontos não são a contagem AQUA. Não usar CSV parcial de 17/11. Fonte: https://terrabrasilis.dpi.inpe.br/queimadas/portal/

## INMET
inmet_avisos_ativos.json: selecionar por descrição, severidade e início. Hoje 56430 Tempestade/Perigo: 569 municípios, 30–60 mm/h ou 50–100 mm/dia e vento 60–100 km/h; válidos até 23h59. Amanhã 56432 (387) e 56433 (658 no Sul) em Perigo. União laranja amanhã 1.045 municípios. Amarelos hoje 56428 e 56429; 56429 só começa ao meio-dia; Vendaval 56425 em RS/SC. Não chamar todos de avisos já vigentes às 05h30. Fonte https://avisos.inmet.gov.br/ . Dados de estação INMET indisponíveis (204 em 25 pedidos); nenhum número medido vem deles.

## Previsão Open-Meteo
previsao7d.json, 17–23/11, best_match. Somar os pontos das 27 capitais, nunca rotular lâmina regional. Total 734,6 mm; Norte 189,3; CO 181,6; Sul 144,9; SE 119,5; NE 99,3 mm. Hoje 153,0 mm é o maior total diário. Teresina 40,2 °C em 20/11, sexta. Top acumulado Goiânia 64,8 mm. Fonte https://open-meteo.com/ .

[
  {
    "dia": "2026-11-17",
    "soma_chuva_mm": 153.0,
    "por_regiao_mm": {
      "N": 26.4,
      "NE": 49.7,
      "CO": 58.5,
      "SE": 13.5,
      "S": 4.9
    },
    "capitais_ge_30mm": [],
    "tmax_media": 30.1,
    "tmax_pico": [
      36.1,
      "Teresina"
    ]
  },
  {
    "dia": "2026-11-18",
    "soma_chuva_mm": 109.1,
    "por_regiao_mm": {
      "N": 36.6,
      "NE": 14.1,
      "CO": 17.5,
      "SE": 23.3,
      "S": 17.6
    },
    "capitais_ge_30mm": [],
    "tmax_media": 30.8,
    "tmax_pico": [
      39.3,
      "Teresina"
    ]
  },
  {
    "dia": "2026-11-19",
    "soma_chuva_mm": 69.7,
    "por_regiao_mm": {
      "N": 15.8,
      "NE": 3.1,
      "CO": 25.6,
      "SE": 12.4,
      "S": 12.8
    },
    "capitais_ge_30mm": [],
    "tmax_media": 31.2,
    "tmax_pico": [
      39.3,
      "Teresina"
    ]
  },
  {
    "dia": "2026-11-20",
    "soma_chuva_mm": 132.0,
    "por_regiao_mm": {
      "N": 36.0,
      "NE": 18.2,
      "CO": 19.5,
      "SE": 21.8,
      "S": 36.5
    },
    "capitais_ge_30mm": [],
    "tmax_media": 30.9,
    "tmax_pico": [
      40.2,
      "Teresina"
    ]
  },
  {
    "dia": "2026-11-21",
    "soma_chuva_mm": 82.3,
    "por_regiao_mm": {
      "N": 28.0,
      "NE": 6.8,
      "CO": 16.8,
      "SE": 19.6,
      "S": 11.1
    },
    "capitais_ge_30mm": [],
    "tmax_media": 31.1,
    "tmax_pico": [
      40.1,
      "Teresina"
    ]
  },
  {
    "dia": "2026-11-22",
    "soma_chuva_mm": 77.9,
    "por_regiao_mm": {
      "N": 13.3,
      "NE": 3.8,
      "CO": 11.1,
      "SE": 12.7,
      "S": 37.0
    },
    "capitais_ge_30mm": [
      "Florianópolis"
    ],
    "tmax_media": 31.1,
    "tmax_pico": [
      39.9,
      "Teresina"
    ]
  },
  {
    "dia": "2026-11-23",
    "soma_chuva_mm": 110.6,
    "por_regiao_mm": {
      "N": 33.2,
      "NE": 3.6,
      "CO": 32.6,
      "SE": 16.2,
      "S": 25.0
    },
    "capitais_ge_30mm": [],
    "tmax_media": 31.6,
    "tmax_pico": [
      40.1,
      "Teresina"
    ]
  }
]
## Satélite e demais brutos
sat/web/ir_tempos.json: 16/11 08h a 17/11 08h UTC (05h a 05h Brasília), GOES-19 NASA GIBS; base geocolor com bbox [-76,-35,-33,7] e mundo.jpg ao fundo. NOAA METAR e openmeteo_capitais_3d.json preservados, sem uso de seus números no roteiro. Fontes NASA/NOAA: https://gibs.earthdata.nasa.gov/ e https://aviationweather.gov/ .
