# Dados conferidos — 23/11/2026
Coleta: 23/11/2026 08h30 UTC (05h30 BRT). Janela: 22/11 08h30 a 23/11 08h30 UTC.

## Pluviômetros CEMADEN
Fonte bruta: `bruto/cemaden_getJson2_todas_ufs.json`; resumo de coleta em `bruto/resumo.json`. Endpoint e parâmetros originais estão no coletor `../../../coleta/ultimas24h.py`; origem https://resources.cemaden.gov.br/ . Cada valor é o campo acc24hr de um sensor e sua própria janela móvel de 24 h.

Aplicado o mesmo filtro do modelo: tipoestacao = 1 (pluviômetro), valor não negativo e última atualização nas 6 h anteriores ao fechamento, inclusive fechamento, excluindo horários futuros. O resumo automático contém outras estações e horários posteriores: soma original 23.644,4 não vai ao ar. Aquidabã (181 mm) excluída por tipo 5. Não interpretar soma dos sensores como lâmina ou média territorial.

Amostra válida: **1.697 sensores**, soma **21.688,25 mm·estação**. Voz/contador: **21.688**, inteiro truncado. Detalhe reproduzível: `soma-validada.json` e asserts no gerar_cena.py.

| UF | soma dos pluviômetros (mm·estação) | sensores |
|---|---:|---:|
| SP | 5473.75 | 297 |
| MG | 5354.94 | 423 |
| SC | 3091.82 | 163 |
| PR | 1934.82 | 137 |
| RJ | 1801.84 | 147 |
| RS | 1672.60 | 289 |
| ES | 723.69 | 53 |
| MS | 445.20 | 9 |
| TO | 293.07 | 20 |
| AM | 251.42 | 24 |
| BA | 239.50 | 53 |
| GO | 140.00 | 32 |
| PA | 116.00 | 9 |
| MT | 95.20 | 4 |
| MA | 28.00 | 11 |
| DF | 12.60 | 3 |
| RN | 6.40 | 8 |
| RO | 3.20 | 3 |
| AC | 2.80 | 8 |
| PE | 1.20 | 3 |
| AP | 0.20 | 1 |

Medições locais usadas (nenhuma soma entre bairros):
- Ubatuba/SP, Centro 2, id 3521: **144,45 mm/24 h**, última atualização 23/11 08h10 UTC = 05h10 BRT.
- Água Boa/MT, Prefeitura Municipal, id 7883: **91,6 mm/24 h**, 23/11 08h10 UTC.
- Eldorado dos Carajás/PA, Prefeitura Municipal, id 6789: **84 mm/24 h**, 23/11 08h00 UTC.

## Focos INPE
`bruto/inpe_focos_diario_br_20261122.csv`, domingo 22/11 UTC completo; **1.487** focos do satélite de referência AQUA_M-T, **1.018 PA**, **238 MA**, **197 AP**. Não confundir com soma de satélites (duplicações); pontos do mapa usam NOAA-20/21 agregados em grade de 0,08 grau como localização visual. O arquivo de 23/11 é parcial e não sustenta a contagem. Origem https://terrabrasilis.dpi.inpe.br/queimadas/portal/ .

## Calor NOAA
`bruto/noaa_metar_brasil_24h.json` e resumo: METAR SBTE, Teresina, **39 °C** em 22/11 19h UTC = 16h BRT. É aeroporto, não máxima de toda a cidade/estado. Origem https://aviationweather.gov/ . Não usar mínimo 0 °C de Chapecó, associado a relatório sem temperatura no campo bruto.

## Avisos INMET
`bruto/inmet_avisos_ativos.json`: selecionar descrição Tempestade e severidade Perigo Potencial. Hoje **56476**, 3.059 códigos únicos, 23/11 00h00–23h59. Amanhã **56480**, 3.206, 24/11 00h00–23h59. Vento 40–60 km/h é risco previsto. Baixa umidade **56479**, 589 códigos, hoje 10h–22h; não somar os conjuntos. URLs: https://avisos.inmet.gov.br/56476 ; https://avisos.inmet.gov.br/56480 ; https://avisos.inmet.gov.br/56479 .

Falha de coleta: estações INMET retornaram 204 em 25 pedidos. Sem novo pedido/chave; usamos CEMADEN e NOAA. Registrado em LIMITES do hub.

## Previsão Open-Meteo
`bruto/previsao7d.json` e `resumo.json.openmeteo_capitais`: best_match, **27 capitais**, 23–29/11. Origem https://open-meteo.com/ . Soma de chuva em pontos de capitais agrupados por região; não lâmina média do Brasil, nem previsão de cada município das regiões. Temperatura da linha é média das máximas nas 27 capitais; calor de Teresina é pico individual previsto.

| data | soma capitais mm | N | NE | CO | SE | S | máx. média °C | pico °C/cidade |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2026-11-23 | 75.2 | 8.7 | 1.9 | 24.8 | 16.3 | 23.5 | 31.6 | [40.3, 'Teresina'] |
| 2026-11-24 | 139.7 | 19.3 | 11.2 | 26.7 | 45.5 | 37.0 | 31.7 | [40.6, 'Teresina'] |
| 2026-11-25 | 157.4 | 34.0 | 8.4 | 27.9 | 53.2 | 33.9 | 31.7 | [40.3, 'Teresina'] |
| 2026-11-26 | 170.9 | 40.7 | 5.0 | 40.5 | 76.5 | 8.2 | 30.6 | [40.7, 'Teresina'] |
| 2026-11-27 | 232.5 | 36.0 | 2.4 | 93.6 | 98.4 | 2.1 | 29.6 | [39.1, 'Teresina'] |
| 2026-11-28 | 145.8 | 51.4 | 6.4 | 54.9 | 14.7 | 18.4 | 29.9 | [39.6, 'Teresina'] |
| 2026-11-29 | 155.4 | 71.6 | 4.6 | 31.0 | 30.0 | 18.2 | 30.4 | [39.7, 'Teresina'] |

Total previsto: **1.076,9 mm somados** (voz/contador 1.076, inteiro truncado). Região líder: capitais do SE, 334,6 mm. Dia de maior soma: sexta 27/11, 232,5 mm. Pico de calor: Teresina, quinta 26/11, 40,7 °C previstos. Totais e dias validados por asserts; diferenças decimais toleradas só até 0,2 mm pelo arredondamento do bruto.

## Satélite
NASA GIBS / NOAA GOES-19: https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi . Bbox [-76,-35,-33,7]. Geocolor e IR preservados em `sat/web/`; 49 horários em `ir_tempos.json`, 22/11 08h a 23/11 08h UTC (05h a 05h BRT). Último quadro meia hora antes do fechamento dos sensores. Seleção por luminosidade exclui quadros incompletos; texturas alfa derivadas por `preparar_texturas.py`, sem alterar JPG original. `mundo.jpg` Blue Marble estático do modelo serve só como fundo de continuidade, sem dado meteorológico atual.
