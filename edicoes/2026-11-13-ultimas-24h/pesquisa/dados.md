# Dados dos brutos (coleta 13/11/2026 08:30 UTC; janela 12/11 08:30 → 13/11 08:30 UTC)

Falha da coleta: estações do INMET (apitempo sem token, 204) — temperaturas vêm do METAR.

## CEMADEN (cemaden_getJson2_todas_ufs.json; resumo.json → cemaden)
- 5.739 estações, 1.568 com leitura recente.
- DESCARTADO: Pedro Alexandre (BA), 13.184,4 mm em 24 h com 720,2 mm em 1 h — sensor com defeito (a vizinha Jeremoabo 0,2). Tirada da soma e do ranking.
- Grande SP (chuva da tarde de 12/11: 12 h quase zero): Mogi das Cruzes, Jd Santos Dummond 75,0 (Jundiapeba 48,0; Vila São Paulo 45,4); São Paulo, Cidade Tiradentes 69,44; Mauá, Jardim Paranavai 63,44 (+ Jardim Anchieta 57,62, Vila Carlina 54,88, Feital 54,84, Parque das Américas 53,04); Santo André 59,97; Suzano 57,4; Poá 54,0; Itaquaquecetuba 52,8. 12 estações de SP com ≥ 50 mm.
- Norte do ES: Pedro Canário, Novo Horizonte 61,4; Conceição da Barra 60,0 / 40,8; Sooretama 52,6 / 51,2.
- Fora do vídeo: Guaxupé (MG) 78,6 (estação única); Patrocínio (MG) 72; Aquidabã (SE) 62 (a mesma estação estranha de ontem).
- Soma dos pluviômetros (mm·estação, não lâmina): 25.527,3 bruto; sem Pedro Alexandre = 12.342,9 mm em 1.567 estações (→ "mais de 12 mil milímetros"). Ranking por UF: SP 3.824,4 (31% → "quase um terço"); MG 3.063,1; RJ 847,7; ES 793,4; PR 702,4.

## NOAA METAR (resumo.json → noaa_metar; 108 aeroportos, 2.138 obs.)
- Rajada: 74 km/h em Porto Velho (SPECI SBPV 121745Z 13016G40KT ... +TSRA ... FEW035CB = trovoada com chuva forte); 54 km/h São Luís; 48 km/h Cruzeiro do Sul.
- Máximas 12/11: 38 °C Teresina (20Z, umidade 26%); 37 °C Paulo Afonso e Boa Vista.
- Trovoada em 33 aeroportos.

## INPE focos (inpe_focos_diario_br_20261112.csv, dia completo 12/11; o de 13/11 é parcial e sem AQUA)
- AQUA_M-T (referência): 614 focos em 12/11 (11/11 tinha 1.038). Pará 408 (66% → "dois em cada três"), Amapá 95, Amazonas 47.
- Todos os satélites: 13.022 detecções — não usado (mistura satélites).

## INMET avisos (inmet_avisos_ativos.json) — só amarelo, nenhum laranja ou vermelho
- 56389 Tempestade amarelo, 13/11 00h–23h59: 2.343 cidades em 16 UFs (MG 794, SP 645, GO 246, MT 141, TO 103, RJ 92, MS 79, ES 74, RO 52, AM 46, PA 24, AC 22, PR 14, BA 9, MA 1, DF 1). Até 50 mm/dia, vento 40–60 km/h, granizo.
- 56390 Tempestade amarelo, 14/11: 1.803 cidades (MG 691, BA 279, GO 246, TO 139, MT 130...).

## Previsão Open-Meteo (previsao7d.json, 27 capitais, 13 a 19/11)
- Soma 7 dias: 793,6 mm (→ "mais de 790"). Por região: CO 270,9; N 197,8; SE 137,7; NE 113,0; S 74,2.
- Dias mais chuvosos: domingo 15/11 153,6 mm e segunda 16/11 153,5 mm (empate prático → "domingo e segunda").
- Acumulado top: Goiânia 91,7; Brasília 81,2; Cuiabá 73,2. Porto Alegre ≥ 30 mm no domingo.
- Pico de calor: Teresina 39,5 °C hoje (13/11), 39,1 sábado.
