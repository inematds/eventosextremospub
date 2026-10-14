# Dados dos brutos — 14/10/2026 (janela 13/10 05h30 → 14/10 05h30, horário de Brasília)

Falha da coleta: INMET estações (apitempo sem token, 25× status 204). Sem dado de estação do INMET; temperatura e vento vêm do METAR (NOAA).

## Chuva 24 h — CEMADEN (`resumo.json` → cemaden.top; `cemaden_getJson2_todas_ufs.json`), leituras até 14/10 08h10 UTC
- Santa Cruz de Monte Castelo (PR), G2-412330303A: **112,4 mm** (outra estação na cidade: 67,0 mm)
- Paranavaí (PR), G2-411840202A: **101,2 mm** (outras: 78,6 e 77,4 mm)
- Querência do Norte (PR): 86,0 mm · Rolândia (PR): 78,8 mm · Londrina (PR), G2-411370003A: **76,8 mm** (outras: 71,4; 69,4; 61,6; 59,2)
- Visconde do Rio Branco (MG), Rio Xopoto: 258,6 mm — **descartado** (sensor isolado, já tinha sido descartado ontem; acc3 7,4 e acc6 50,8 não batem com 258 mm em 24 h)
- Estações ≥ 50 mm: 34; ≥ 100 mm: 3 (inclui Visconde do Rio Branco).

## Volumes somados — CEMADEN soma_por_uf (mm·estação = soma dos pluviômetros, não lâmina de área)
- PR: **4.317,6 mm** em **153** pluviômetros (média 28,2) · MG 3.609,2 (372) · SP 1.922,2 (382) · RJ 558,8 (103) · SC 413,7 (111)
- Brasil: **12.464,1 mm** em **1.518** pluviômetros com leitura recente. Sem Visconde do Rio Branco: 12.205,5 → dito "mais de 12 mil".

## Vento — METAR (NOAA), `noaa_metar_brasil_24h.json`
- Campo Grande (SBCG), 13/10 21h36 UTC (18h36 BRT): SPECI 26024G38KT +TSRA → **38 nós = 70,4 km/h** → dito "70"
- Ribeirão Preto (SBRP), 13/10 21h34 UTC (18h34 BRT): 18022G37KT -TSRA → **37 nós = 68,5 km/h** → dito "68" (resumo arredonda para 69; não arredondamos para cima)
- Maringá (SBMG) 22h UTC: 32 nós (59 km/h) com +TSRA.

## Calor e ar seco — METAR (NOAA)
- Teresina (SBTE): **39 °C** 13/10 20h UTC (17h); umidade mínima **20%** (calculada, 39 °C)
- Itaituba (SBIH): **39 °C** 13/10 18h UTC (15h)

## Fogo — INPE (`inpe_focos_diario_br_20261013.csv`, dia 13/10)
- Satélite de referência AQUA_M-T: **1.050** focos no Brasil; Bahia **283**, Piauí 221, Maranhão 160.
- Todos os satélites: 28.484 registros (contagem repetida entre satélites; não usada como número).
- Pontos no mapa = VIIRS (NPP-375, NOAA-20, NOAA-21) em grade de 0,08°.

## Avisos INMET (`inmet_avisos_ativos.json`)
- 56064 Tempestade **Perigo (laranja)** 14/10 00h01–23h59: **1.342** municípios (SP 590, PR 309, MG 284, RJ 92, MS 54, ES 13); chuva 30–60 mm/h ou 50–100 mm/dia, ventos 60–100 km/h, granizo.
- 56063 Tempestade Perigo Potencial (amarelo) 14/10: 2.701 municípios.
- 56061 Baixa Umidade **Perigo (laranja)** 14/10 10h–22h: **96** municípios (BA 67, MG 29); umidade entre 20% e 12%.
- 56051 Baixa Umidade amarelo até 14/10: 1.012 municípios.
- 56062 Tempestade amarelo **15/10**: **2.074** municípios (MG 722, SP 637, GO 226...).

## Previsão 7 dias — Open-Meteo (`previsao7d.json`, 27 capitais, mm somados)
| dia | soma | N | NE | CO | SE | S | máx. média | pico |
|---|---|---|---|---|---|---|---|---|
| qua 14 | 94,9 | 13,6 | 1,4 | 42,3 | 17,7 | 19,9 | 31,3 | Teresina 39,8 |
| qui 15 | **148,3** | 22,9 | 0,6 | 67,1 | 43,2 | 14,5 | 30,3 | Teresina 39,1 |
| sex 16 | 74,5 | 18,9 | 1,3 | 18,0 | 29,5 | 6,8 | 30,0 | Teresina 39,9 |
| sáb 17 | 60,8 | 12,1 | 3,8 | 10,9 | 32,7 | 1,3 | 29,4 | Teresina 39,8 |
| dom 18 | 51,6 | 31,8 | 3,6 | 3,6 | 6,6 | 6,0 | 29,0 | Teresina 39,2 |
| seg 19 | 63,9 | 22,5 | 10,2 | 4,2 | 24,6 | 2,4 | 28,7 | Teresina 37,4 |
| ter 20 | 45,3 | 18,6 | 6,6 | 1,2 | 17,4 | 1,5 | 29,4 | Teresina 38,7 |
- Total 7 dias: **539,3 mm** (dito "539"). Por região: **SE 171,7** · CO 147,3 · N 140,4 · S 52,4 · NE 27,5.
- Teresina acima de 39 °C em 5 dos 7 dias (qua a dom).
- Capitais hoje (Open-Meteo): Campo Grande 21,9 mm, Goiânia 14,2, Curitiba 12,3, São Paulo 8,7; Teresina 39,8 °C com umidade 17%.

## Satélite
- GOES-19 infravermelho (NASA GIBS), 13/10 08h UTC → 14/10 08h UTC (05h a 05h BRT); geocolor de base.
