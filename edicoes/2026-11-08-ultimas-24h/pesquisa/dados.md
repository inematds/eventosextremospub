# Dados dos brutos — coleta 08/11/2026 08:30 UTC (janela 07/11 05h30 → 08/11 05h30, horário de Brasília)

Falha: INMET estações (apitempo sem token, 25 pedidos 204). Resto ok.

## CEMADEN (cemaden_getJson2_todas_ufs.json; resumo.json → cemaden)
- Maiores acumulados de 24 h:
  - Serra (ES) Cantinho do Céu 102,38 mm — SUSPEITO: acc24 = acc96 = 102,38, última leitura 02h40, vizinhas de Serra com 0 a 15 mm → fora do vídeo e fora da soma.
  - Abdon Batista (SC) G2-420005101A 100,8 mm em 24 h; 206,4 em 48 h; 307,2 em 96 h (leitura 08/11 08h10). Segunda estação da cidade: 95,2 / 188,6 / 266,8.
  - Guaxupé (MG) Centro 97,2 mm (95,6 em 12 h).
  - Vargem (SC) 97,2; Canas (SP) 89,4; Sertãozinho (SP) 86,8; São Carlos (SC) 86,0.
- Soma dos pluviômetros (soma_mm_estacoes): 36.901,7 mm; sem Serra/Cantinho do Céu: 36.799,3 ("mais de 36 mil"). É SOMA de leituras, não chuva média.
- Por UF: MG 10.138,6 (516 estações) · SP 8.427,3 · SC 6.959,1 · RJ 4.588,1 · PR 3.153,1 · RS 2.199,6.

## INPE focos
- CSV de 07/11 (dia completo): AQUA_M-T (satélite de referência) 1.034 focos; Pará 729, Amazonas 109, Roraima 73. Todos os satélites: 28.913.
- CSV de 08/11 parcial (sem AQUA): não usado.

## NOAA METAR
- Rajada máxima: Brasília (SBBR) 96 km/h (52 kt) às 17h10Z de 7/11; Bauru 91; Campinas/Viracopos 83.
- Máximas: 39 °C em Teresina, Juazeiro do Norte e Cuiabá (7/11). Mínima: 13 °C em Curitiba (8/11 05h).

## INMET avisos (inmet_avisos_ativos.json)
- Hoje 8/11: 56329 Tempestade LARANJA (Perigo) em 480 municípios — MG 352, GO 76, ES 33, SP 17, MS 2; 60–100 km/h, 50–100 mm/dia, granizo.
- 56331 Ventos Costeiros laranja em 47 (RJ 21, SP 26).
- 56327 Tempestade amarelo em 2.042; 56281 Declínio de Temperatura amarelo em 2.060 (PR, SC, RS, SP, MS, MG, RJ; 3 a 5 °C); 56330 Baixa Umidade amarelo em 353 (NE).
- Amanhã 9/11: 56333 declínio de temperatura em 1.011 (MG 748); 56332 tempestade amarelo em 885. 10–11/11: 56335 acumulado de chuva em 80 (BA).

## Open-Meteo 7 dias (previsao7d.json, 27 capitais)
- Soma 7 dias: 937,0 mm. Por região: N 289,4 · SE 264,8 · CO 237,0 · NE 107,3 · S 38,5.
- Dia mais chuvoso: segunda 9/11, 187,6 mm somados (SE 93,0).
- Pico de máxima: Teresina 39,6 °C na segunda (9/11).
- Top acumulado: Belo Horizonte 125,8; Brasília 91,5; Vitória 86,2.

## Satélite
- sat/web/ir00..: GOES-19 infravermelho das últimas 24 h (GIBS); geocolor.jpg.
