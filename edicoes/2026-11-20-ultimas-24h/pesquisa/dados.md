# Dados conferidos · 20/11/2026
Fechamento: 20/11 08h30 UTC = 05h30 Brasília; início 19/11 08h30 UTC. Captura em pesquisa/bruto/resumo.json. Estações INMET: 25 respostas 204, substituídas pelos brutos CEMADEN/NOAA, sem credenciais.

## CEMADEN
Fonte: https://resources.cemaden.gov.br/graficos/interativo/getJson2.php?uf=BA (e demais UFs). Arquivo cemaden_getJson2_todas_ufs.json. Horário do bruto tratado como UTC, conforme coletor. Só atualização > fechamento − 6 h e <= fechamento, acc24hr não negativo. Nenhuma leitura futura; acumulados móveis de 24 h por sensor, finais não simultâneos.
- CAETANOS (BA), CAETANOS, id 8234: 138.8 mm; atualização 20/11/26 08:00 UTC.
- PLANALTINA (GO), G2-521760904A, id 18213: 33.8 mm; atualização 20/11/26 08:10 UTC.
- VOLTA REDONDA (RJ), Retiro, id 7629: 87.6 mm; atualização 20/11/26 08:00 UTC.
- FONTOURA XAVIER (RS), Centro, id 7340: 47.2 mm; atualização 20/11/26 08:30 UTC.

Soma validada: 11128.69 mm·estação; 1431 sensores; inteiro truncado 11128. Não é lâmina de área. Reprodução: python3 pesquisa/preparar.py. Detalhe por UF em soma-validada.json:
- MG: 4289.73 mm·estação, 461 sensores.
- BA: 2315.8 mm·estação, 118 sensores.
- RS: 1516.8 mm·estação, 226 sensores.
- RJ: 691.0 mm·estação, 86 sensores.
- SC: 578.4 mm·estação, 111 sensores.
- AM: 378.57 mm·estação, 39 sensores.
- ES: 374.56 mm·estação, 51 sensores.
- SP: 301.14 mm·estação, 146 sensores.
- GO: 235.2 mm·estação, 36 sensores.
- PI: 81.6 mm·estação, 13 sensores.
- PR: 76.39 mm·estação, 36 sensores.
- MA: 63.58 mm·estação, 21 sensores.
- MS: 55.6 mm·estação, 11 sensores.
- AC: 33.2 mm·estação, 11 sensores.
- DF: 24.4 mm·estação, 1 sensores.
- MT: 21.6 mm·estação, 5 sensores.
- RO: 16.8 mm·estação, 13 sensores.
- SE: 16.6 mm·estação, 2 sensores.
- TO: 14.8 mm·estação, 8 sensores.
- PA: 14.4 mm·estação, 12 sensores.
- AP: 11.8 mm·estação, 3 sensores.
- PE: 8.32 mm·estação, 9 sensores.
- RN: 5.0 mm·estação, 5 sensores.
- CE: 1.2 mm·estação, 3 sensores.
- PB: 1.2 mm·estação, 3 sensores.
- AL: 1.0 mm·estação, 1 sensores.

## INPE
Arquivo inpe_focos_diario_br_20261119.csv; dia UTC completo 19/11, satélite de referência AQUA_M-T: Brasil 1.681; PA 855, MA 532, PI 87. Não somar satélites como eventos únicos. Pontos visuais NOAA-20/21 são apenas localização. Fonte: https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/diario/Brasil/focos_diario_br_20261119.csv

## NOAA
Arquivo noaa_metar_brasil_24h.json, https://aviationweather.gov/api/data/metar . Aeroporto SBTE: 38 °C em 19/11 20h UTC = 17h Brasília. Não generalizar a máxima nacional nem cidade inteira.

## INMET
inmet_avisos_ativos.json; https://avisos.inmet.gov.br/56456 e /56457: tempestade, Perigo, 470 + 1.230 municípios, união 1.700. Inícios hoje 09h10 e 09h16, término 23h59. Previsão de 50–100 mm/dia e vento 60–100 km/h, granizo. São avisos para hoje a partir da manhã, não ativos no instante 05h30. /56460 amarelo 62 cidades até 08h, /56455 amarelo 3.946 a partir de 09h06. /56458: amanhã 21/11, amarelo, 3.332 cidades de 09h25 a 23h59. /56459: domingo, fora da contagem de amanhã.

## Open-Meteo
Arquivo previsao7d.json e openmeteo_capitais_3d.json; https://api.open-meteo.com/v1/forecast ; best_match, timezone America/Sao_Paulo, 27 capitais. Soma em sete dias 961 mm; soma por região SE 263,7, S 253,2, N 216,5, CO 181,2, NE 46,4. Maior soma diária quinta 26/11: 200,4 mm. Pico previsto Teresina 40,7 °C em 26/11. Hoje Florianópolis 48 mm e amanhã 8,2 mm; previsão, não observado. Gráfico inclui todos os dias e médias das máximas das capitais. Soma não é lâmina média nacional.

## NASA GIBS / NOAA GOES-19
sat/web/ir_tempos.json e ir00..ir48.jpg: 19/11 08h UTC a 20/11 08h UTC, janela de 24 h, 05h–05h Brasília. Geocolor: bbox -76,-35,-33,7. Fundo global para evitar borda de textura em movimento. Fonte: https://gibs.earthdata.nasa.gov/ .
