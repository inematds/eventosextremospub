# Dados — 18/11/2026

Corte editorial: 17/11 05h30 a 18/11 05h30 Brasília (08h30 UTC). Todos os números do roteiro têm os arquivos abaixo como fonte. Horários do feed CEMADEN interpretados em UTC, como na edição modelo.

## Chuva observada — CEMADEN

Fonte: bruto/cemaden_getJson2_todas_ufs.json. Acumulado móvel de 24 h de cada estação; não se trata de lâmina de área.
- Riachão do Jacuípe/BA, G2-292630101A: 116,8 mm, leitura 18/11 08h10 UTC.
- Antônio Dias/MG, G2-310300901A: 87,6 mm, leitura 18/11 08h10 UTC. Outro sensor da cidade tem valor distinto: não generalizar medição para toda cidade.
- Rio Verde/GO, Céu Azul: 51,4 mm, leitura 18/11 08h00 UTC.
- Excluída idestacao 8327, Pedro Alexandre/BA, 17.280,2 mm: anomalia incompatível; não vai ao ar nem entra nas somas revisadas. Excluídos também relógios posteriores ao corte, registros mais antigos que 6 horas e valores não numéricos/negativos. Brutos preservados.

Soma revisada: 16656.9 mm·estação, 1686 sensores, 25 UFs. Reprodução e valores por UF: soma-validada.json e gerar_cena.py. Soma bruta 34355.1 contaminada pela anomalia e relógios adiantados: não usar.

- BA: 7245.07 mm·estação (269 sensores)
- RS: 2063.20 mm·estação (247 sensores)
- MG: 2009.00 mm·estação (312 sensores)
- PR: 1597.23 mm·estação (108 sensores)
- SC: 600.48 mm·estação (125 sensores)
- SP: 584.80 mm·estação (145 sensores)
- GO: 539.40 mm·estação (42 sensores)
- SE: 435.80 mm·estação (47 sensores)
- TO: 242.50 mm·estação (30 sensores)
- PE: 192.46 mm·estação (64 sensores)
- PI: 191.20 mm·estação (25 sensores)
- MA: 152.80 mm·estação (24 sensores)
- RJ: 140.98 mm·estação (88 sensores)
- ES: 123.69 mm·estação (22 sensores)
- AL: 113.80 mm·estação (27 sensores)
- MS: 106.00 mm·estação (12 sensores)
- PA: 76.60 mm·estação (19 sensores)
- MT: 75.20 mm·estação (9 sensores)
- AM: 59.49 mm·estação (10 sensores)
- AP: 35.80 mm·estação (11 sensores)
- RO: 22.20 mm·estação (15 sensores)
- AC: 21.60 mm·estação (7 sensores)
- DF: 17.20 mm·estação (4 sensores)
- PB: 5.40 mm·estação (7 sensores)
- CE: 5.00 mm·estação (17 sensores)

## INPE — dia fechado

bruto/inpe_focos_diario_br_20261117.csv: 17/11 UTC completo; satélite de referência AQUA_M-T: 1.245 focos no Brasil, 1.054 no Pará, 78 Amapá, 51 Maranhão. Pontos VIIRS são apenas camada visual, não outra contagem. O CSV de 18/11 é parcial e não sustenta a fala de ontem.

## Vento e calor — NOAA

bruto/noaa_metar_brasil_24h.json e resumo.json → noaa_metar:
- SBCA 171900Z 35025G41KT 1000 +TSGRRA: aeroporto de Cascavel, 17/11 16h BRT, rajada de 41 nós × 1,852 = 75,932 km/h. No ar 75,9 km/h (truncado a uma decimal, sem arredondar para cima); código GR indica granizo.
- SBRB, 17/11 20h UTC = 17h BRT, 38 °C no aeroporto de Rio Branco.

## INMET — avisos vigentes

bruto/inmet_avisos_ativos.json: selecionar por tempestade e severidade. Hoje: 56432 (387 municípios) e 56442 (1.066), união sem duplicatas 1.453 cidades em laranja; risco previsto de vento 60–100 km/h e granizo. Amanhã: 56440, 3.830 cidades em amarelo. Não são impactos já observados. Vigência até 23h59 de cada dia. https://avisos.inmet.gov.br/56432 https://avisos.inmet.gov.br/56442 https://avisos.inmet.gov.br/56440

## Open-Meteo — previsão

bruto/previsao7d.json: 18–24/11, 27 capitais; soma de pontos, não volume físico nem média regional. Total 685,2 mm somados; Sul 175,5 mm (maior soma regional nas capitais). Domingo, 22/11: 122,7 mm, maior soma diária. Teresina: pico previsto de 40,5 °C na terça 24/11. Porto Alegre: 84,8 mm previstos acumulados. Gráfico usa todos os sete dias, cinco regiões e máxima média das capitais, 31,0–31,5 °C, distinta do pico individual.

## Satélite e falhas

GOES-19 NASA/NOAA, sat/web/ir_tempos.json: 17/11 08h UTC–18/11 08h UTC; quadros com brilho inválido filtrados. Base geocolor atual e Blue Marble de fundo local reutilizado do modelo, sem tratar o fundo como observação de hoje.
INMET estações retornou 204 em 25 pedidos: sem medições de estações INMET nesta edição; falha anotada em LIMITES.md. Não foram usadas APIs adicionais.
