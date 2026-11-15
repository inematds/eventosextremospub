# Dados dos brutos (coleta 15/11/2026 08:30 UTC; janela 14/11 08:30 → 15/11 08:30 UTC = 14/11 05h30 → 15/11 05h30 de Brasília)

Falha da coleta: estações do INMET (apitempo sem token, 204) — temperaturas vêm do METAR.

## CEMADEN (cemaden_getJson2_todas_ufs.json; resumo.json → cemaden)
- 5.750 estações, 1.349 com leitura recente; 7 com ≥ 50 mm.
- DESCARTADO: Pedro Alexandre (BA), 9.535,6 mm em 24 h (637,2 em 1 h) — o mesmo sensor com defeito dos dias anteriores.
- DESCARTADO: Visconde do Rio Branco (MG), Rio Xopoto, 87,4 mm — carrega a chuva da tarde de 14/11 que já foi julgada isolada na edição de 14/11 (vizinhas ~0, IR sem topo frio); acc6 = 8,2. Fora da soma e do vídeo.
- **Nova Olinda (PB, sertão): G2-251020402A 69,8; 251020403A 67,6; 251020401A 66,0** — acc6 = acc24 nas três: toda a chuva em menos de 6 h (14/11 23h30 → 15/11 05h30). Três concordam.
- **Brejo Santo (CE, Cariri): G2-230250302A 42,8 (40,4 em 1 h)**; 230250301A 31,0 (31 em 1 h); 230250303A 29,6 (29,6 em 1 h) — temporal na última hora (≈ 04h30–05h30 de 15/11). Três concordam.
- **Mundo Novo (BA): G2-292210201A 68,0 e 292210202A 66,0** (acc12 = 68/66, acc6 ≈ 1,5 → choveu entre ~17h e 23h de 14/11). BA: Ubaíra 49,6; Itagibá 46,4; Wenceslau Guimarães 43,4; Jequié 42,6.
- Fora (isoladas/menores): Santa Rosa do Piauí 47,6 (42,8 em 1 h; vizinhas 3–13 mm) — fica na soma, não vai à fala; Cubatão (SP) 45,0; Planaltina (GO) 43,2; Iretama (PR) 42,6; Apucarana (PR) 32,2.
- Soma dos pluviômetros (mm·estação, não lâmina): 17.010,4 bruto; sem Pedro Alexandre e Visconde do Rio Branco = **7.387,4 mm em 1.347 estações de 26 UFs** (→ "mais de 7 mil milímetros"). BA sem PA 2.211,7 = 29,9% (→ "quase um terço na Bahia"; BA na frente); MG 1.089,4; PR 896,2; SP 465,4; ES 379,8.

## NOAA METAR (resumo.json → noaa_metar; 106 aeroportos, 2.127 obs.)
- **Rajada de 70 km/h em Maringá (PR)**: METAR SBMG 142200Z COR 25017G38KT -TSRA (= 14/11 19h, trovoada com chuva); a temperatura caiu de 29 °C (21Z) para 21 °C (22Z). Londrina 50 km/h (14/11 14h23, TSRA); Pelotas 48; Brasília 46; Goiânia 44.
- Máximas: **38 °C Teresina** (14/11 18Z–20Z), umidade mínima 29% (20Z); 37 °C Cuiabá; 36 °C Mossoró, Corumbá, Boa Vista.
- Trovoada em 27 aeroportos.

## INPE focos (inpe_focos_diario_br_20261114.csv, dia completo 14/11; o de 15/11 é parcial, AQUA = 0)
- AQUA_M-T (referência): **1.577 focos em 14/11** (13/11: 767 → 2,06× → "mais que dobrou"). **Pará 749 (47,5% → "quase metade")**, Maranhão 482, Amapá 111, Tocantins 81, Bahia 58. Municípios (AQUA): Pacajá 67, Portel 65, Novo Repartimento 62.

## INMET avisos (inmet_avisos_ativos.json) — só amarelo (Perigo Potencial), nenhum laranja ou vermelho
- Hoje 15/11: 56408 tempestade 2.633 cidades (MG 844, SP 645, PR 399, SC 270…), até 50 mm/dia, vento 40–60 km/h, granizo; 56409 chuvas intensas 533 cidades (PI 189, TO 122, MA 98); 56406 chuvas intensas AP (3).
- Amanhã 16/11: 56410 tempestade 2.819 cidades (MG 853, SP 600, BA 326…).

## Previsão Open-Meteo (previsao7d.json, 27 capitais, 15 a 21/11)
- Soma 7 dias: 880,2 mm (→ "mais de 880"). Por região: CO 264,3; N 195,8; SE 170,9; S 141,2; NE 108,0 (→ "Centro-Oeste deve acumular mais").
- Dia mais chuvoso: segunda 16/11, 218,1 mm somados (CO 86,2).
- Acumulado top: Cuiabá 86,3; Palmas 72,4; Goiânia 69,2.
- Pico de calor: Teresina 39,7 °C na sexta 20/11 e no sábado 21/11 (→ "perto de 40 graus").
