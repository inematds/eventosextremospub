# Dados dos brutos (coleta 12/11/2026 08:30 UTC; janela 11/11 08:30 → 12/11 08:30 UTC)

Falha da coleta: estações do INMET (apitempo sem token, 204) — temperaturas vêm do METAR.

## CEMADEN (cemaden_getJson2_todas_ufs.json; resumo.json → cemaden)
- 5.734 estações, 1.583 com leitura recente; 8 com ≥ 50 mm, 2 com ≥ 100 mm.
- Santa Cruz Cabrália (BA), BR367-km4: 124,14 mm em 24 h (173,8 em 48 h; só 6,32 nas últimas 12 h → chuva de 11/11 de dia).
- Porto Seguro (BA), Areião: 117,19 mm (146,54 em 48 h). Cidades vizinhas confirmam a chuva: Prado 53,0; Alcobaça 41,0; Teixeira de Freitas 33,2 / 37,4 / 34,6.
- Colorado do Oeste (RO): três estações 57,4 / 53,6 / 39,2.
- Fora do vídeo: Aquidabã (SE) 84,4 (estação única, 1 h = 3 h = 6 h = 25,2, leitura estranha); Anapu (PA) 75 (sem 1/3/6 h); Goiatuba (GO) 72,8 (a vizinha 20).
- DESCARTADO: Ituporanga (SC), Centro-Prefeitura 38,04 mm com Gabiroba 0,4 — mesma estação que ontem marcou 99,46 com as vizinhas em ~1 mm; defeito de sensor. Tirada da soma.
- Soma dos pluviômetros (mm·estação, não lâmina): 5.358,7 mm; sem Ituporanga = 5.320,7 (→ "mais de 5 mil milímetros"). Ranking por UF: BA 1.017,5; MG 676,6; ES 418,8; RO 407,9; GO 297,0.

## NOAA METAR (resumo.json → noaa_metar; 108 aeroportos, 2.123 obs.)
- Máximas 11/11: 37 °C Paulo Afonso (BA, 18Z) e Teresina (PI, 18Z); 36 °C Rio Branco, Mossoró, Juazeiro do Norte, Boa Vista.
- Mínimas: 14 °C Curitiba (Afonso Pena e Bacacheri) e Canoas (RS).
- Rajada: 48 km/h Campo Grande (MS, 18:02Z, trovoada na vizinhança); 46 km/h Manaus (19:21Z, trovoada com chuva).
- Trovoada em 20 aeroportos.

## INPE focos (inpe_focos_diario_br_20261111.csv, dia completo 11/11; o de 12/11 é parcial e sem AQUA)
- AQUA_M-T (referência): 1.038 focos em 11/11 (na véspera, 10/11: 333 → mais que triplicou). Maranhão 421, Pará 276, Piauí 89, Bahia 70, Ceará 52, Amapá 52.
- Todos os satélites: 11.208 detecções — não usado (mistura satélites).

## INMET avisos (inmet_avisos_ativos.json) — nenhum laranja ou vermelho
- 56381 Tempestade amarelo, 12/11 00h–23h59: 2.084 cidades (SP 644, MG 553, PR 286, GO 246, MT 136, TO 84, MS 79, RJ 34, PA 10, BA 8, RO 3, DF 1). Até 50 mm/dia, vento 40–60 km/h, granizo.
- 56378 Tempestade amarelo, 11/11 12h → 12/11 12h: 472 (SC 257, PR 183, RS 30, MS 2). União com 56381 = 2.464 cidades.
- 56356 Acumulado de chuva amarelo até 13/11: 71 cidades do litoral da BA.
- 56382 Tempestade amarelo para 13/11: 2.047 cidades.

## Open-Meteo (previsao7d.json, 27 capitais, 12 a 18/11)
- Soma 7 dias: 934,4 mm. Por região: CO 276,1; N 222,2; NE 194,7; SE 187,2; S 54,2.
- Dia mais chuvoso: seg 16/11, 211,7 mm somados (NE 83,4 — Salvador ≥ 30 mm).
- Pico de calor: Teresina 39,3 °C no sábado 14/11 (38,8 hoje).
- Top acumulado: Cuiabá 131,6; Palmas 71,8; Goiânia 66,4.
