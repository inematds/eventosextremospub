# Dados de 26/11/2026

A coleta de `bruto/resumo.json` cobre de 25/11 às 08h30 UTC a 26/11 às 08h30 UTC (05h30 em Brasília). O quadro de avisos corresponde ao instantâneo de coleta.

| Origem e bruto | Número usado no vídeo | Recorte |
|---|---|---|
| CEMADEN · `bruto/cemaden_getJson2_todas_ufs.json` | Angra dos Reis/RJ: 168,84 mm | Vila Histórica, sensor 3428, leitura de 26/11 às 05h20 BRT. A abertura usa “passou de 168”. |
| CEMADEN · mesmo bruto | Aparecida/SP: 96,2 mm | São Francisco, sensor 4337, 26/11 às 05h20 BRT. |
| CEMADEN · mesmo bruto | Corumbá/MS: 93,4 mm | Cravo Vermelho, sensor 7916, 26/11 às 05h20 BRT. |
| CEMADEN · mesmo bruto | Timbó/SC: 28,06 mm | Tiroleses, sensor 4043, 26/11 às 05h10 BRT. A fala usa “passou de 28”. |
| CEMADEN · mesmo bruto | 17.120,50 mm·estação em 1.470 sensores. SP 6.091,54, RJ 4.263,02 e MG 4.210,47 mm·estação. | Soma de acc24hr por UF para registros de tipoestacao 1, não negativos e com última leitura no intervalo (02h30, 08h30] UTC. Cada acumulado de 24 h termina na leitura do próprio sensor. Tela e voz truncam o total para 17.120. |
| INPE · `bruto/inpe_focos_diario_br_20261125.csv` | 1.488 focos no Pará, 1.811 no Brasil | Apenas AQUA_M-T, dia completo UTC. O mapa mostra as mesmas detecções filtradas, agrupadas visualmente por célula. Foco de calor não equivale a incêndio individual. |
| NOAA · `bruto/noaa_metar_brasil_24h.json` | 40 °C em Teresina | Aeroporto SBTE em 25/11 às 19h UTC (16h BRT). |
| INMET · `bruto/inmet_avisos_ativos.json` | 56503: 1.278 municípios (ES, GO, MG, MS, RJ e SP). 56502: 2.768. 56507: 589. 56505: 1.225. | Contagem de códigos IBGE distintos por aviso. As áreas em cor dão destaque às UFs que têm municípios no aviso. Ver vigências em noticias.md. |
| Open-Meteo · `bruto/openmeteo_capitais_3d.json` | Vitória: 65,9 mm na quinta e 58,7 mm na sexta | Previsões diárias pontuais na capital. |
| Open-Meteo · `bruto/previsao7d.json` | 1.030,3 mm somados em 7 dias. Sábado 28/11: maior soma diária, 201,1 mm. Sudeste: maior soma regional, 381,5 mm. Teresina: pico de 40,4 °C previsto em 30/11. | Janela 26/11–02/12, soma das previsões nas 27 capitais e máxima média diária no gráfico. O total mostrado e falado fica em 1.030 mm. |
| NASA GIBS / GOES-19 · `../sat/web/ir_tempos.json` e imagens | IR de 25/11 05h a 26/11 05h BRT | 49 quadros a cada 30 min. Blue Marble de fundo é estático e foi reaproveitado da edição de 24/11. |

A soma bruta do CEMADEN em `resumo.json` inclui tipos de estação distintos e horários fora do filtro aplicado na última edição completa. As leituras de 16.141,8 mm de Pedro Alexandre e 578 mm de Aquidabã são de tipo 5 e ficaram fora. Não se infere lâmina de chuva sobre o território somando leituras de estações ou previsões pontuais de capitais.

Falha reportada pelo coletor: 25 consultas de estações INMET retornaram HTTP 204, detalhadas em `bruto/inmet_estacoes_tentativas.json`. A edição usa observações CEMADEN/NOAA e avisos INMET. Fontes de dados públicos: [CEMADEN](https://resources.cemaden.gov.br/graficos/interativo/getJson2.php?uf=RJ), [INPE](https://terrabrasilis.dpi.inpe.br/queimadas/portal/), [NOAA](https://aviationweather.gov/data/metar/), [Open-Meteo](https://open-meteo.com/), [NASA GIBS](https://www.earthdata.nasa.gov/eosdis/science-system-description/eosdis-components/gibs).
