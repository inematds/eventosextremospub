# Dados auditados — 21/11/2026

Fechamento 08h30 UTC / 05h30 BRT. Todos os arquivos citados estão em pesquisa/bruto/.

CEMADEN: cemaden_getJson2_todas_ufs.json, critérios e sensores em soma-validada.json. Soma recalculada 33092.3 mm·estação em 1866 pluviômetros tipo 1. Universo difere do resumo (37211,9, vários tipos de instrumento). Excluída leitura de Aquidabã tipo 5. Não inferir lâmina de área.

Por UF (soma dos pluviômetros em mm·estação / número de sensores):
- RS: 8968.2 / 355
- MG: 8818.78 / 470
- SC: 4981.97 / 161
- SP: 3478.42 / 348
- PR: 3127.71 / 137
- ES: 754.41 / 52
- BA: 600.8 / 61
- RJ: 500.62 / 88
- GO: 436.4 / 33
- AM: 405.65 / 47
- TO: 355.6 / 19
- RO: 227.55 / 19
- MT: 167.6 / 7
- RR: 86.4 / 3
- MS: 60.6 / 3
- PA: 40.6 / 15
- PI: 28.6 / 6
- MA: 24.2 / 19
- AC: 12.8 / 7
- DF: 9.4 / 2
- PB: 1.6 / 4
- AP: 1.4 / 2
- PE: 1.39 / 2
- CE: 1.0 / 3
- RN: 0.4 / 2
- SE: 0.2 / 1

Sensores usados individualmente:
[
  {
    "idestacao": 7154,
    "uf": "ES",
    "codibge": 3202900,
    "cidade": "ITARANA",
    "nomeestacao": "Morro do Cafezal",
    "ultimovalor": 0.2,
    "datahoraUltimovalor": "21/11/26 08:30",
    "acc1hr": 3.8,
    "acc3hr": 9.2,
    "acc6hr": 23.6,
    "acc12hr": 138.6,
    "acc24hr": 139.6,
    "acc48hr": 155,
    "acc72hr": 155,
    "acc96hr": 156.6,
    "tipoestacao": 1,
    "status": 0
  },
  {
    "idestacao": 18217,
    "uf": "GO",
    "codibge": 5219803,
    "cidade": "SÃO DOMINGOS",
    "nomeestacao": "G2-521980301A",
    "ultimovalor": 0,
    "datahoraUltimovalor": "21/11/26 08:10",
    "acc1hr": "-",
    "acc3hr": 0.2,
    "acc6hr": 22.6,
    "acc12hr": 45.8,
    "acc24hr": 56,
    "acc48hr": 56,
    "acc72hr": 57.8,
    "acc96hr": 62.6,
    "tipoestacao": 1,
    "status": 0
  },
  {
    "idestacao": 18432,
    "uf": "TO",
    "codibge": 1716208,
    "cidade": "PARANÃ",
    "nomeestacao": "G2-171620801A",
    "ultimovalor": 0,
    "datahoraUltimovalor": "21/11/26 08:10",
    "acc1hr": "-",
    "acc3hr": "-",
    "acc6hr": 0.2,
    "acc12hr": 92,
    "acc24hr": 104.2,
    "acc48hr": 104.6,
    "acc72hr": 104.8,
    "acc96hr": 106,
    "tipoestacao": 1,
    "status": 0
  }
]

INMET: inmet_avisos_ativos.json, selecionados por tipo Tempestade e severidade Perigo Potencial, hoje 56462: 3715 geocodes únicos; futuro 56466: 3591. Até 50 mm/dia e 40–60 km/h são previsão, não observação.

INPE: inpe_focos_diario_br_20261120.csv (dia UTC completo), AQUA_M-T: 707, Pará 463, Ceará 87, Roraima 38. O resumo mistura janela móvel e parcial de hoje: não usar para substituir a contagem do CSV diário. Pontos do mapa NOAA-20/21 agregados espacialmente, contador somente AQUA.

NOAA: noaa_metar_brasil_24h.json, METAR SBTE 20/11 19h UTC (16h BRT), 39 °C. Não é máxima absoluta municipal nem recorde.

Open-Meteo: previsao7d.json, gráfico fiel ao bruto, somas de chuva nas capitais, não previsão de toda a área regional.
{
  "dias": [
    "2026-11-21",
    "2026-11-22",
    "2026-11-23",
    "2026-11-24",
    "2026-11-25",
    "2026-11-26",
    "2026-11-27"
  ],
  "por_dia": [
    {
      "dia": "2026-11-21",
      "soma_chuva_mm": 113.8,
      "por_regiao_mm": {
        "N": 48.2,
        "NE": 3.1,
        "CO": 28.9,
        "SE": 29.4,
        "S": 4.2
      },
      "capitais_ge_30mm": [],
      "tmax_media": 31.5,
      "tmax_pico": [
        38.7,
        "Teresina"
      ]
    },
    {
      "dia": "2026-11-22",
      "soma_chuva_mm": 117.7,
      "por_regiao_mm": {
        "N": 30.7,
        "NE": 6.5,
        "CO": 20.5,
        "SE": 12.7,
        "S": 47.3
      },
      "capitais_ge_30mm": [
        "Florianópolis"
      ],
      "tmax_media": 31.3,
      "tmax_pico": [
        39.3,
        "Teresina"
      ]
    },
    {
      "dia": "2026-11-23",
      "soma_chuva_mm": 115.7,
      "por_regiao_mm": {
        "N": 28.9,
        "NE": 7.0,
        "CO": 17.5,
        "SE": 28.8,
        "S": 33.5
      },
      "capitais_ge_30mm": [
        "Curitiba"
      ],
      "tmax_media": 31.5,
      "tmax_pico": [
        40.0,
        "Teresina"
      ]
    },
    {
      "dia": "2026-11-24",
      "soma_chuva_mm": 128.3,
      "por_regiao_mm": {
        "N": 12.9,
        "NE": 16.5,
        "CO": 37.6,
        "SE": 35.6,
        "S": 25.7
      },
      "capitais_ge_30mm": [],
      "tmax_media": 31.5,
      "tmax_pico": [
        40.6,
        "Teresina"
      ]
    },
    {
      "dia": "2026-11-25",
      "soma_chuva_mm": 170.5,
      "por_regiao_mm": {
        "N": 18.5,
        "NE": 9.7,
        "CO": 27.1,
        "SE": 42.2,
        "S": 73.0
      },
      "capitais_ge_30mm": [
        "Florianópolis"
      ],
      "tmax_media": 31.7,
      "tmax_pico": [
        40.8,
        "Teresina"
      ]
    },
    {
      "dia": "2026-11-26",
      "soma_chuva_mm": 172.5,
      "por_regiao_mm": {
        "N": 38.8,
        "NE": 5.1,
        "CO": 51.3,
        "SE": 66.6,
        "S": 10.7
      },
      "capitais_ge_30mm": [],
      "tmax_media": 30.5,
      "tmax_pico": [
        40.1,
        "Teresina"
      ]
    },
    {
      "dia": "2026-11-27",
      "soma_chuva_mm": 238.6,
      "por_regiao_mm": {
        "N": 64.8,
        "NE": 3.0,
        "CO": 47.2,
        "SE": 122.6,
        "S": 1.0
      },
      "capitais_ge_30mm": [
        "Vitória"
      ],
      "tmax_media": 29.4,
      "tmax_pico": [
        39.0,
        "Teresina"
      ]
    }
  ],
  "soma_7d_mm": 1057.1,
  "soma_7d_por_regiao_mm": {
    "N": 242.8,
    "NE": 50.9,
    "CO": 230.1,
    "SE": 337.9,
    "S": 195.4
  },
  "acumulado_7d_top": [
    [
      "Belo Horizonte",
      124.3
    ],
    [
      "Florianópolis",
      113.8
    ],
    [
      "Vitória",
      112.9
    ],
    [
      "São Paulo",
      69.9
    ],
    [
      "Curitiba",
      69.9
    ],
    [
      "Porto Velho",
      68.9
    ],
    [
      "Palmas",
      67.0
    ],
    [
      "Campo Grande",
      63.0
    ]
  ],
  "rotulo": "soma da chuva prevista nas 27 capitais (mm somados), Open-Meteo best_match; não é lâmina média do país"
}

NASA GIBS: sat/web/ir_tempos.json, 20/11 08h UTC a 21/11 08h UTC, rótulos convertidos para BRT. Blue Marble de fundo reaproveitado da edição anterior, base estática.

Falha da coleta: INMET estações retornou 204 em 25 pedidos. Não usamos dado INMET de estação; chuva vem do CEMADEN e calor do NOAA. Nenhuma chave/API adicional.
