# Dados dos brutos — 17/10/2026 (janela 16/10 08h30 UTC → 17/10 08h30 UTC)

Arquivos: `pesquisa/bruto/resumo.json`, `cemaden_getJson2_todas_ufs.json`, `inmet_avisos_ativos.json`, `inpe_focos_diario_br_20261016.csv`, `noaa_metar_brasil_24h.json`, `previsao7d.json`. Falha da coleta: INMET estações (apitempo sem token, 25 pedidos 204) → sem dado de estação do INMET.

## CEMADEN (1.913 pluviômetros com leitura recente, de 5.644)
Sensores **descartados** (valor isolado, 3× ou mais os vizinhos da mesma cidade; fora das somas e do vídeo):
- Mauá (SP) Vila Magini 280,6 mm (acc96 604) — outras 6 estações de Mauá: 12 a 29,6 mm. Descartado também em 16/10.
- Visconde do Rio Branco (MG) Rio Xopoto 220,4 mm (acc96 882,8) — descartado desde 13/10.
- Angra dos Reis (RJ) Colégio Naval (U) 214,8 mm (acc96 405) — as outras 25 estações de Angra: 0,6 a 48,8 mm. Ontem passou (92,8, série coerente); hoje +122 mm sozinho → descartado.
- Deixados de fora por cautela (2,5–3× os vizinhos da mesma cidade, não somados à parte, só não citados): São Vicente Jardim Rio Branco 128,9 (vizinhas 48 / 45 / 8); Sapucaia Secretaria de Transportes 119,7 (vizinhas 45 / 13).

Citado (grupo coerente da Baixada Santista, várias estações concordando):
- Mongaguá Jardim Praia Grande **70,57** (Centro 57,12) · Cubatão Jardim Casqueiro **69,77** · Guarujá Morrinhos 66,96 / Pereque2 61,63 / Enseada 56,27 · Santos Vila Mathias 57,48 · Bertioga 57,82 · Ubatuba 58,68.
- RJ: Rio de Janeiro Alto da Boa Vista 53,0 · Paraty Laranjeiras 53,24 · Teresópolis Serra do Capim 67,78.

Soma dos pluviômetros (mm·estação; NÃO é chuva média):
- SP 7.626,2 (409 estações) − Mauá 280,6 = **7.345,6** → dito "mais de 7.300"
- MG 6.446,4 (511) − Visconde 220,4 = 6.226,0 · RJ 3.544,3 (167) − Colégio Naval 214,8 = 3.329,5 · RS 797,4 · SC 709,8
- Brasil 21.337,1 − 715,8 = **20.621,3** → dito "mais de 20 mil"

## INPE Queimadas — 16/10/2026 (arquivo 20261016, todas as linhas com data 2026-10-16)
- Satélite de referência AQUA_M-T: **1.142 focos** (15/10: 569 → o dobro, 2,0×)
- Por estado (AQUA): Maranhão **336**, Pará **210**, Bahia **204**, Piauí 124, Ceará 74, Tocantins 73
- Pontos do mapa: VIIRS (NPP-375, NOAA-20, NOAA-21) em grade de 0,08°.

## INMET avisos (inmet_avisos_ativos.json)
- **56096** Tempestade · Perigo (laranja) · 17/10 00h01–23h59 · **370 municípios** (MG 245, ES 78, RJ 26, BA 21) · 30–60 mm/h ou 50–100 mm/dia, vento 60–100 km/h, granizo
- **56095** Ventos Costeiros · Perigo (laranja) · 17/10 · **115** (SC 71, RS 43, PR 1)
- 56094 Tempestade · Perigo Potencial (amarelo) · 17/10 · 2.343 (não somar com o laranja)
- 56098 Tempestade amarelo 18/10 (737) · 56089 amarelo 19/10 (87)

## NOAA METAR (107 aeroportos)
- Rajadas: Tabatinga 50 km/h (16/10 19h38Z); Santos Dumont (RJ) 46 km/h (17/10 06h30Z, chuva); Congonhas 43 km/h com chuva forte (+RA) 17/10 04h38Z.
- Máx.: Petrolina 39 °C (16/10 18Z); Teresina 38. Mín.: Chapecó e Santo Ângelo 12 °C (17/10 08Z); Curitiba 13.

## Previsão 7 dias (previsao7d.json, Open-Meteo best_match, 27 capitais; 17 a 23/10)
- Soma 7 dias: **438,0 mm** · por região N **149,3** · SE 123,5 · S 65,6 · NE 58,4 · CO 41,2
- Dia mais chuvoso: **sexta 23/10, 122,1 mm** (Sul 52,5)
- Por dia (mm): sáb 45,2 · dom 35,6 · seg 46,8 · ter 42,8 · qua 67,5 · qui 78,0 · sex 122,1
- Calor: Teresina pico 39,2 (sáb) → **40,5 °C** (sex 23/10); máx. média 29,3–30,7 °C
- Maior acumulado: Vitória 54,4 mm em 7 dias

## Satélite
- GOES-19 infravermelho (NASA GIBS), sat/web/ir00..ir48 + ir_tempos.json; geocolor.jpg; mundo.jpg copiado de 2026-10-16.
