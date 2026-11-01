# Dados dos brutos — 01/11/2026

Janela da coleta: 31/10 08:30 UTC → 01/11 08:30 UTC (05:30 de Brasília).

## CEMADEN (pluviômetros, acumulado de 24 h)
- A coleta das 05:30 falhou em 26 UFs (connection refused; só AC respondeu: 12 estações, 56,8 mm somados — resumo.json).
- **Recoleta às 08:41 UTC** com `pesquisa/recoleta_cemaden.py` (mesma regra: estação com leitura nas últimas 6 h): `bruto/cemaden_recoleta.json` e `bruto/cemaden_getJson2_todas_ufs.json` (sobrescrito). 5.419 estações, 987 vivas, 22 UFs (AC, AL, AM e AP recusaram nessa hora). Janela do acumulado ~3 h depois da coleta (o acc24hr é das 24 h até a última leitura).
- Maiores: Padre Paraíso (MG, Centro) 107,6 mm, 52,6 em 6 h; Visconde do Rio Branco (MG, Rio Xopoto) 102,8 mm com 0,2 em 6 h — **sensor isolado** (Ubá ao lado 17,4; Guiricema 0,2; o mesmo sensor já ficou fora em 28–31/10): fora da fala e da soma; Palmeiras de Goiás (GO) 88,8 (sensor único, sem leitura de 1/3/6 h): só na soma; Jaíba (MG) 68,2, todos em 6 h (acc6 68,2); Antônio Dias 61,8; Jaguaraçu 59,8; Santa Cruz de Salinas 59,6.
- ≥ 50 mm: 17 pluviômetros (MG 15, GO 1, RO 1); sem o sensor isolado: **16, 14 em Minas**.
- Soma das leituras de 24 h (mm·estação, não é lâmina): 7.230,1 em 22 UFs; sem o sensor isolado **7.127,3** ("mais de 7.100"); Minas 4.440,8 → **4.338,0** sem o isolado ("mais de 4.300"); depois GO 750,6, SC 400,0, RJ 287,9, ES 281,5.

## NOAA METAR (aeroportos)
- Goiânia (SBGO) 31/10 16:05Z (13h05): `SPECI SBGO 311605Z 33021G33KT 2500 +TSRA` → rajada de 33 nós = **61 km/h**, trovoada forte, 2.500 m de visibilidade.
- Cuiabá (SBCY) 18:00Z rajada 61 km/h com chuva.
- Brasília (SBBR) 01/11 01:35Z (31/10 22h35): `SPECI SBBR 010135Z ... 1000 ... +TSRA` → **1.000 m** de visibilidade em trovoada forte.
- Teresina (SBTE) **39 °C** de 18Z a 20Z (15h a 17h). Juazeiro do Norte (SBJU) 37/12 às 20Z → ~22% de umidade (ur_min_top do resumo: 22%).
- Trovoada em 25 aeroportos (Manaus, Goiânia, Brasília, BH, Cuiabá, Campo Grande, Porto Velho, Rio Branco…).

## INPE (focos)
- Arquivo de 31/10 completo (00:00 a 23:50 GMT). Satélite de referência AQUA_M-T: **699 focos**; Ceará **184**, Maranhão 166, Piauí 81, Bahia 75, Pernambuco 50. Caatinga 402 dos 699.

## INMET (avisos ativos)
- Hoje 01/11: 56236 Tempestade amarelo (Perigo Potencial) em **1.092** municípios (SP 379, MG 271, PR 212, GO 148, MS 79, MT 2, DF 1); capitais Goiânia, Belo Horizonte, Campo Grande, Brasília. 20–30 mm/h ou até 50 mm/dia, vento 40–60 km/h, granizo.
- 56226 Baixa umidade amarelo em **665** municípios do Nordeste, até 01/11 21h; umidade 30% a 20%.
- Segunda 02/11: 56227 Tempestade **laranja** (Perigo) em **366** (PR 337, SP 16, MS 13): 30–60 mm/h ou 50–100 mm/dia, vento 60–100 km/h, granizo. Também 56234 amarelo em 2.474 municípios.
- Terça e quarta: amarelos de tempestade no Sul e Sudeste (56229, 56237).

## Open-Meteo (previsão 7 dias, 27 capitais, previsao7d.json)
- Dias: dom 01/11 a sáb 07/11. Mais chuvoso: **quinta 05/11, 135,1 mm somados** (Sul 60,3). Região que mais acumula: **Sul 202,4 mm**; Sudeste 180,7. Soma 7 dias: **652,4 mm** ("mais de 650"). Pico de calor: **Teresina 40,5 °C no sábado 07/11** ("passar dos 40 graus").
