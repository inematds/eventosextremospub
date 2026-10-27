# Dados dos brutos — janela 26/10 08h30 UTC → 27/10 08h30 UTC

Falha da coleta: estações do INMET (apitempo sem token, 204 em todos os pedidos). Contorno: METAR da NOAA.

## CEMADEN (cemaden_getJson2_todas_ufs.json; horário UTC, última leitura 27/10 ~08h20 UTC = 5h20 de Brasília)
- Ibicuí (BA): G2-291230101A 141,2 mm em 24 h, 138,6 mm em 3 h, 31,6 mm na última hora; G2-291230102A 131,0 mm (127,2 em 3 h). Dois sensores concordam → chuva da madrugada de terça.
- Camacan (BA), São João do Panelinha: 78,23 mm em 24 h, 68,25 mm em 1 h. Itororó (BA) 50,6 mm.
- Petrópolis (RJ): LNCC - Geo 2 67,2 mm; LNCC - Geo 54,2; Independência2 49,58; São Sebastião 46,0.
- Leste de MG: Coroaci 81,2; Águas Formosas 74,8 e 69,0; Governador Valadares (Chonim de Baixo) 67,0.
- DESCARTADOS (sensor isolado, vizinhos sem leitura): Visconde do Rio Branco (MG) "Rio Xopoto" 338,0 (acc6 só 27,2; vizinho Centro "-"; já descartado em 26/10) e Salvador "Doron" 63,4 (vizinhos "-" ou 0,2; descartado em 26/10).
- Soma dos pluviômetros (resumo.json): 9.158,8 mm·estação em 1.393 estações recentes. Sem os 2 descartados: 8.757,4 → "mais de 8.700". MG 3.511,7 − 338 = 3.173,7 → "mais de 3 mil". RJ 1.400,2; BA 1.223,7 − 63,4 = 1.160,3; SP 949,6.

## NOAA METAR (noaa_metar_brasil_24h.json)
- Teresina (SBTE) 38 °C em 26/10 19Z (16h); Boa Vista (SBBV) 38 °C em 26/10 19Z (15h local).
- Santo Ângelo (SBNM) 9 °C em 27/10 08Z (5h); Curitiba (SBCT) 10 °C em 27/10 08Z (5h).
- Campos dos Goytacazes (SBCP) rajada 32 kt = 59,3 km/h em 26/10 18Z (15h): "METAR SBCP 261800Z 20019G32KT".

## INPE focos (inpe_focos_diario_br_20261026.csv, todos de 26/10)
- Satélite de referência (AQUA_M-T): 468 no Brasil; Maranhão 142, Bahia 72, Piauí 39, Amazonas 36, Ceará 33.
- O arquivo de 27/10 só tem passagens da madrugada (sem AQUA): não usado.

## INMET avisos (inmet_avisos_ativos.json) — só amarelo (Perigo Potencial)
- Hoje 27/10: tempestade 56190 (1.022 municípios: BA 349, MG 308, GO 145, TO 105, ES 47 …) + 56191 (36: AC 22, AM 13, RO 1) = 1.058.
- Quarta 28/10: tempestade 56194 (1.246); acumulado de chuva 56196 na BA (116 municípios, 28–29/10).
- Quinta 29/10: tempestade 56195 (2.777: SP 645, MG 536, PR 399, SC 295, GO 246).

## Open-Meteo, 7 dias nas 27 capitais (previsao7d.json)
- Somas por dia (mm): ter 83,8 · qua 87,8 · qui 168,9 · sex 207,8 · sáb 101,3 · dom 71,0 · seg 55,2. Total 775,8 → "mais de 770".
- Sexta 30/10 o dia mais chuvoso (207,8; BH, Florianópolis e Rio com ≥ 30 mm). Região: Sudeste 235,5 (N 210,3; CO 193,8).
- Top 7 dias: Porto Velho 91,8; Rio de Janeiro 86,6; Brasília 70,0.
- Pico de máxima: Teresina 39,5 °C no domingo 1º/11.
