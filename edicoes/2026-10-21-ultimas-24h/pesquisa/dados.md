# Dados dos brutos — 21/10/2026 (janela 20/10 08h30 UTC → 21/10 08h30 UTC)

Arquivos: `pesquisa/bruto/resumo.json`, `cemaden_getJson2_todas_ufs.json`, `inmet_avisos_ativos.json`, `inpe_focos_diario_br_20261020.csv` (20/10 inteiro, 00:00–23:50 GMT; o de 20261021 tem só até 06h GMT e 0 AQUA), `noaa_metar_brasil_24h.json`, `previsao7d.json`, `geocoding_openmeteo.txt` (coordenadas dos pinos). Falha da coleta: INMET estações (apitempo sem token, 25 pedidos 204). `sat/web/mundo.jpg` copiado de 2026-10-20. IR GOES-19: 20/10 08Z → 21/10 08Z.

## CEMADEN (774 pluviômetros com leitura recente, de 5.668)
Sensores descartados das somas: Mauá (SP) Vila Magini 154,4 mm (vizinhos ≤ 5,6 mm; descartado em 16 e 17/10); Visconde do Rio Branco (MG) Rio Xopoto 46,4 mm; Angra dos Reis (RJ) Colégio Naval (U) 26,0 mm (descartados desde 13 e 17/10).

Citados:
- **Santana do Araguaia (PA) Balneário 69,4 mm** em 24 h → "sessenta e nove".
- **Santa Maria da Vitória (BA) G2-292810901A 56,0 mm** (as outras 2 estações da cidade: 51,0 e 38,2) → "cinquenta e seis".
- Não citado: Aquidabã (SE) 59,8 mm (estação única em SE, sem vizinho para conferir).

Soma dos pluviômetros (mm·estação; NÃO é chuva média):
- BA **576,3** (92 estações) → "mais de 570" (maior UF)
- TO 294,4 · SP 255,2 − 154,4 = 100,8 · MG 238,8 − 46,4 = 192,4 · AM 230,5 · RJ 219,6 − 26,0 = 193,6
- Brasil 2.533,7 − 226,8 = **2.306,9** (771) → "mais de dois mil e trezentos"

## INPE Queimadas — 20/10/2026 (arquivo 20261020)
- AQUA_M-T (referência): **399 focos**. Pará **106** (26,6%), Mato Grosso 62, Santa Catarina 41, Rio Grande do Sul 29, Paraná 26.
- Municípios (AQUA): Óbidos 11, Paranatinga 10, Juruti 9.
- Todos os satélites: 13.757 detecções (PA 4.292). Sem comparação com 19/10 (1.011 no AQUA): a variação diária do AQUA depende da passagem do satélite.

## INMET avisos (coleta 21/10 08h30 UTC)
- **56127 Tempestade, amarelo**, hoje 21/10 15:00 → 23:59, **623 municípios** (PR 323, RS 147, SC 121, MS 28, SP 4), granizo, 40–60 km/h, até 50 mm/dia.
- **56124 Chuvas Intensas, amarelo**, hoje 21/10, **179 municípios** (RO 52, AM 53, MT 42, AC 22, PA 7, RR 3).
- **56129 Tempestade, amarelo**, quinta 22/10, **2.853 municípios em 15 UFs** (SP 643, MG 592, RS 496, PR 399, SC 293…), granizo.
- 56131 Baixa Umidade, quinta 22/10 12h–20h, 684 municípios (PI 218, CE 106, PB 104…), umidade 30% a 20%.
- Outros: 56132 tempestade 23/10 (2.812), 56134 tempestade 24/10 (2.168), 56120 chuvas intensas 23/10 (43).

## NOAA METAR (107 aeroportos)
- Máxima: Teresina (SBTE) 38 °C em 20/10 20Z; Petrolina, Juazeiro do Norte e Cuiabá 37 °C. Mínima: 8 °C em Canoas, Santo Ângelo, Passo Fundo e Santa Maria (RS). Rajada: Natal 52 km/h. Não citados (fala ficou longa).

## Previsão 7 dias (previsao7d.json, Open-Meteo, 27 capitais, 21 a 27/10)
- Soma 7 dias: **671,8 mm** → "mais de seiscentos e setenta" (S 189,8 · SE 156,4 · N 141,0 · CO 101,4 · NE 83,2) → Sul acumula mais.
- Dia mais chuvoso: **domingo 25/10, 187,5 mm somados** (S 99,9 · SE 53,1).
- Curitiba **141,6 mm** em 7 dias (maior) → "mais de cento e quarenta".
- Calor: Teresina pico 40,9 °C (sáb 24), 40,2 (qui 22), 40,3 (dom 25) → "Teresina deve passar dos quarenta graus".

## Satélite
- GOES-19 infravermelho, NASA GIBS, 20/10 08Z → 21/10 08Z (sat/web/ir*.jpg); geocolor.
