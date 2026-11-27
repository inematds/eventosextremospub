# Dados de 27/11/2026

O instantâneo de `bruto/resumo.json` cobre 26/11 às 08h30 UTC até 27/11 às 08h30 UTC, ou 05h30 em Brasília. Cada pluviômetro totaliza as 24 h até o horário de sua leitura.

| Fonte e arquivo bruto | Medição ou previsão | Janela |
|---|---|---|
| CEMADEN · `bruto/cemaden_getJson2_todas_ufs.json` | Iconha (ES) 131,4 mm, G2-320260301A, sensor 17331 | 24 h até 27/11 às 05h10 BRT |
| CEMADEN · mesmo bruto | Petrópolis (RJ) 120,61 mm, Morin, sensor 3321 | 24 h até 27/11 às 05h10 BRT |
| CEMADEN · mesmo bruto | Rolim de Moura (RO) 87,4 mm, G2-110028802A, sensor 17360 | 24 h até 27/11 às 05h10 BRT |
| CEMADEN · mesmo bruto | Coxim (MS) 43,8 mm, Prefeitura Municipal, sensor 7917 | 24 h até 27/11 às 05h10 BRT |
| CEMADEN · mesmo bruto | Ituporanga (SC) 54,33 mm, Centro – Prefeitura, sensor 3992 | 24 h até 27/11 às 05h30 BRT |
| CEMADEN · mesmo bruto | 11.742,59 mm·estação em 1.293 pluviômetros. MG 4.238,63, RJ 2.339,41 e ES 1.697,62 mm·estação | Soma de `acc24hr` dos sensores de tipo 1, valores não negativos e leitura nas seis horas anteriores à coleta. Tela e voz truncam o total para 11.742. |
| INPE · `bruto/inpe_focos_diario_br_20261126.csv` | 425 detecções no Maranhão e 1.167 no Brasil, satélite de referência AQUA_M-T | Dia 26/11 UTC. Deteções próximas no mapa compartilham o ponto. Cada detecção é um foco de calor. |
| NOAA · `bruto/noaa_metar_brasil_24h.json` | 39 °C no aeroporto de Teresina, SBTE | 26/11, boletins de 17h a 20h UTC. Contexto de pesquisa, sem uso no vídeo. |
| INMET · `bruto/inmet_avisos_ativos.json` | 56515: 233 municípios (PR, SC, RS); 56513: 2.154; 56512: 589; 56516: 1.142 | Códigos IBGE distintos por aviso. Vigências em `noticias.md`, geometria do campo `poligono`. |
| Open-Meteo · `bruto/openmeteo_capitais_3d.json` | Vitória 35,4 mm na sexta e Florianópolis 30,6 mm no sábado | Previsão pontual de chuva diária em 27 e 28/11, respectivamente |
| Open-Meteo · `bruto/previsao7d.json` | 937,4 mm somados; 03/12 tem a maior soma diária (162,6 mm); Norte tem a maior soma regional (322,3 mm); Teresina tem o maior pico de máxima, 39,9 °C em 30/11 | Previsão de 27/11 a 03/12 nas 27 capitais. O total em tela e na voz fica em 937 mm. A linha do gráfico representa a média diária das máximas das capitais. |
| NASA GIBS / NOAA GOES-19 · `../sat/web/ir_tempos.json` | Janela IR de 26/11 às 05h a 27/11 às 05h BRT | 49 horários na coleta. O quadro das 08h BRT de 26/11 veio preto e foi omitido da animação, que usa 48 imagens com os horários preservados. Blue Marble é fundo estático reaproveitado do modelo. |

A soma original do resumo é 28.584,5 mm·estação. Ela mistura tipos de estação e inclui registros anômalos de tipo 5 (Pedro Alexandre, 14.848,6 mm; Aquidabã, 886,6 mm). A edição usa o recorte dos pluviômetros de tipo 1 e calcula o total diretamente do bruto. Somar pluviômetros ou previsões pontuais não produz lâmina média sobre o território.

As 25 consultas de estações INMET retornaram HTTP 204. As leituras locais vêm do CEMADEN; foram preservados os avisos disponibilizados pelo INMET. [CEMADEN](https://resources.cemaden.gov.br/graficos/interativo/getJson2.php?uf=ES) · [INPE](https://terrabrasilis.dpi.inpe.br/queimadas/portal/) · [NOAA](https://aviationweather.gov/data/metar/) · [Open-Meteo](https://open-meteo.com/) · [NASA GIBS](https://www.earthdata.nasa.gov/eosdis/science-system-description/eosdis-components/gibs)
