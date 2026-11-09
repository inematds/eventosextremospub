# Dados dos brutos — coleta 09/11/2026 08:30 UTC (janela 08/11 05h30 → 09/11 05h30, horário de Brasília)

Falha: INMET estações (apitempo sem token, 25 pedidos 204). Resto ok.

## CEMADEN (cemaden_getJson2_todas_ufs.json; resumo.json → cemaden)
- Maiores acumulados de 24 h (leituras 09/11 08h10 UTC):
  - Governador Valadares (MG) Morro do Querosene **110,0 mm** (134,8 em 96 h); Sir 90,4 (vizinha confirma).
  - Tumiritinga (MG) G2-316950503A **106,6 mm** (129,8 em 96 h).
  - Petrópolis (RJ): Morin **92,76**, São Sebastião 89,6, Independência2 85,74, LNCC-Geo 2 81,8 (várias estações coerentes).
  - Guajará-Mirim (RO) 80,6; São Pedro do Suaçuí (MG) 73,4; Cananéia (SP) 71,78.
  - Pinhais (PR) 59,58 com acc24 = acc72 = acc96: não citado (fica na soma, valor pequeno).
- 24 estações ≥ 50 mm, 2 ≥ 100 mm.
- Soma dos pluviômetros (soma_mm_estacoes): **11.711,9 mm** em 1.642 estações com leitura recente, 23 UFs ("mais de 11 mil"). É SOMA de leituras, não chuva média.
- Por UF: MG 3.130,1 · SP 2.756,8 · RJ 2.522,0 · ES 667,8 · AC 446,8.

## INPE focos
- CSV de 08/11 (dia completo): AQUA_M-T (satélite de referência) **652** focos; **Maranhão 268**, Pará 87, Ceará 64, Piauí 48, Bahia 44. Todos os satélites: 18.019 (Pará 10.778).
- CSV de 09/11 parcial (sem AQUA): não usado.

## NOAA METAR (107 aeroportos, 2.162 observações)
- Mínima: **10 °C em Curitiba** (SBCT, 09/11 08h UTC = 05h); 12 °C em Porto Alegre/Canoas, Foz do Iguaçu, Florianópolis; 13 °C em Congonhas (SP).
- Máximas: **39 °C** em Paulo Afonso (BA), Petrolina (PE) e Boa Vista (RR) (8/11); 38 em Teresina e Juazeiro do Norte.
- Rajada máx.: 57 km/h Brasília (09/11 06Z); 56 em Santa Cruz e Afonsos (RJ).
- Umidade mínima 17% em Juazeiro do Norte (CE).

## INMET avisos (inmet_avisos_ativos.json) — nenhum laranja nem vermelho
- Hoje 9/11: 56352 Tempestade amarelo (Perigo Potencial) em **1.176** municípios — MG 514, BA 267, GO 241, ES 78, TO 45, MT 23, RJ 7, DF 1; 20–30 mm/h ou até 50 mm/dia, 40–60 km/h, granizo.
- Hoje 9/11: 56333 Declínio de Temperatura amarelo em **1.011** (MG 748, RJ 92, ES 78, GO 52, SP 24, BA 14, MS 3); 3 a 5 °C.
- 10 a 12/11: 56354 Acumulado de Chuva amarelo em 71 (BA).

## Open-Meteo 7 dias (previsao7d.json, 27 capitais, 9 a 15/11)
- Soma 7 dias: **772,7 mm**. Por região: N 249,3 · CO 197,8 · NE 143,1 · SE 140,6 · S 41,9.
- Dia mais chuvoso: **quarta 11/11, 143,9 mm** somados.
- Pico de máxima: **Teresina 39,6 °C na sexta 13/11**.
- Capitais que mais acumulam: Palmas 92,2 · Goiânia 72,3 · Brasília 70,8 · Vitória 67,0.
- Hoje 9/11 (openmeteo_capitais_3d): mínimas Curitiba 10,3 · Porto Alegre 12,6 · Florianópolis 12,9 · São Paulo 13,1.

## Satélite
- GOES-19 IR via NASA GIBS, 08/11 08:00Z → 09/11 (ir_tempos.json); geocolor; mundo.jpg copiado da edição de 08/11 (Blue Marble, estático).
