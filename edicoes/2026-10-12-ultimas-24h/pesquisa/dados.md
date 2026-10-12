# Dados dos brutos (coleta de 12/10/2026 05h30; janela 11/10 05h30 → 12/10 05h30, Brasília)

Arquivos em `pesquisa/bruto/`. Falha da coleta: estações do INMET (apitempo sem token: 25 pedidos com 204) → sem dado de estação INMET.

## CEMADEN (pluviômetros, `cemaden_getJson2_todas_ufs.json`)
- 5.607 estações, 1.451 com dado recente; 12 com ≥ 50 mm em 24 h.
- **Estiva Gerbi (SP), estação Centro: 71,6 mm em 24 h** (12/10 08h30 UTC); vizinha Mogi Guaçu (Jd Novo II) 25 mm em 24 h e 52,4 mm em 48 h → chuva forte no interior de SP, coerente com os alertas da Defesa Civil.
- Outras de SP ≥ 45 mm: Taubaté 51,4; Paulínia 50,8; Engenheiro Coelho 49,8; Joanópolis 47,8; Artur Nogueira 47,0; Jaguariúna 45,8; Leme 44,8.
- Oeste do PR: Foz do Iguaçu (São Miguel) 55,6 mm; São Miguel do Iguaçu (Centro) 43,3 mm, 24,2 em 3 h.
- **Descartados (sensor isolado):**
  - Visconde do Rio Branco (MG), estação hidrológica Rio Xopoto (tipo 3): 148,6 mm em 24 h, mas só 26,8 em 12 h e nada parecido em volta (Guidoval Rio Xopoto 17,2; Guidoval Centro 24,4; Ubá 2,8 a 11). Nenhuma notícia confirma.
  - Matias Barbosa (MG), Cedofeita: 60 mm, enquanto Matias Barbosa Centro marcou 0,6 e N. S. da Penha 0,2.

## NOAA METAR (aeroportos, `noaa_metar_brasil_24h.json`)
- **Teresina (SBTE): 38 °C** às 19Z e 20Z de 11/10 (`METAR SBTE 112000Z 09004KT 9999 FEW040 38/15 Q1007`).
- **Itaituba (SBIH, PA): 38 °C** às 19Z (`METAR SBIH 111900Z 05005KT 9999 FEW020 38/22 Q1007`).
- **Juazeiro do Norte (SBJU, CE): umidade 15%** às 19Z (16h Brasília) — calculada de 37 °C e orvalho 6 °C (`METAR SBJU 111900Z 11006KT 9999 FEW022 37/06 Q1011`; Magnus: 9,35/62,7 hPa = 14,9%).
- **Ribeirão Preto (SBRP): rajada de 59 km/h com trovoada** às 20h24Z (17h24 Brasília) (`SPECI SBRP 112024Z 35020G32KT ... TS VCSH ... FEW040CB`; 32 kt × 1,852 = 59,3 km/h).
- Vitória (SBVT): rajada 57 km/h às 19Z.
- Mínimas: Curitiba e Pelotas 13 °C.

## INPE Queimadas (`inpe_focos_diario_br_20261011.csv`)
- Satélite de referência (AQUA_M-T) em 11/10: só **150 focos** (Acre 98, Amazonas 46, Rondônia 6), contra 1.155 em 10/10. Quase certamente passagem incompleta do AQUA (nada no Pará, que lidera nos outros satélites). **Não usar** número de fogo hoje.

## INMET avisos (`inmet_avisos_ativos.json`)
- 56036 tempestade laranja 12/10: 449 (PR 260, SC 137, RS 29, MS 23).
- 56044 tempestade laranja 11/10 12h → 12/10 23h59: 547 (MG 255, SP 243, RJ 49).
- 56036 ∩ 56044 = 0 → 996 municípios em laranja hoje.
- 56037 tempestade laranja 13/10: 601 (PR 399 = estado inteiro, SP 161, MS 24, SC 17).
- 56041 baixa umidade amarela até 13/10: 1.364.
- 56011 tempestade amarela até 12/10: 2.335.

## Open-Meteo (`openmeteo_capitais_3d.json`, modelo best_match)
- Teresina: máx 38,3 °C (12/10), 39,5 °C (13/10), 40,3 °C (14/10).
- Curitiba: 44,8 mm em 13/10; Porto Alegre 30,4 mm; São Paulo 17,7 mm.
- Boa Vista 37,4 °C hoje.
