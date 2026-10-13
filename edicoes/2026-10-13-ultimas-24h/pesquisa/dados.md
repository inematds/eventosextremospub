# Dados dos brutos (coleta de 13/10/2026 08h30 UTC, janela 12/10 08h30 → 13/10 08h30 UTC)

Arquivos em `pesquisa/bruto/`. Falha da coleta: estações do INMET (apitempo sem token, 25 pedidos com 204) — sem dado de estação; usamos METAR e CEMADEN.

## CEMADEN (pluviômetros, `cemaden_getJson2_todas_ufs.json`)
- 5.615 estações, 1.350 com leitura recente; 50 com ≥ 50 mm em 24 h, 3 com ≥ 100 mm.
- Máximo por UF: MG 152,2 · PR 104,4 · RJ 61,4 · RS 51,8 · MS 40,4.
- **Descartado:** Visconde do Rio Branco (MG) "Rio Xopoto" 152,2 mm — mesmo sensor isolado descartado ontem (148,6 mm), sem vizinho que confirme.
- Oeste do PR, coerente entre vários sensores: Foz do Iguaçu 104,4 (São Miguel) e 77,0 (Vila Boa Esperança); Medianeira 100,2 / 88,2 / 85,0 / 81,8; Cascavel 91,2; São Miguel do Iguaçu 87,7; Capitão Leônidas Marques 78,7. Leituras de 13/10 ~08h UTC.

## METAR (NOAA, `noaa_metar_brasil_24h.json`, 105 aeroportos, 2.130 obs.)
- Rajadas: Presidente Prudente SBDN 42 kt = 77,8 km/h (13/10 04h UTC, +TSRA SQ); Foz SBFI 36 kt = 67 km/h (12/10 21h20 UTC, TSRA); Campinas 30 kt = 56 km/h; Congonhas 29 kt = 54 km/h.
- Máximas: Teresina 39 °C (19h UTC), Itaituba 39 °C (18h UTC), Juazeiro do Norte 37, Altamira 37, Boa Vista 37.
- Umidade mínima (calculada): Juazeiro do Norte 16% (20h UTC), Petrolina 20%, Teresina 21%, Montes Claros 22%.
- Trovoada em 22 aeroportos (Foz, Cascavel, Curitiba, Londrina, Maringá, Presidente Prudente, Campinas, BH, Manaus…).

## INPE Queimadas (`inpe_focos_diario_br_20261012.csv`)
- 27.117 linhas, todos os satélites; satélite de referência AQUA_M-T: **1.401** (17 às 17h UTC + 1.384 às 19h UTC — passagem completa).
- AQUA por estado: Pará 1.064, Amazonas 186, Mato Grosso 59, Roraima 33, Tocantins 16.
- AQUA por município: Altamira 124, Itaituba 116, Uruará 113, Aveiro 93, Santarém 69.
- Arquivo de 13/10 só até 07h15 UTC (sem AQUA): não usado.

## INMET avisos (`inmet_avisos_ativos.json`)
| id | tipo | severidade | validade | municípios |
|---|---|---|---|---|
| 56048 | Tempestade | Perigo (laranja) | 13/10 | 591 (PR 319, SC 213, RS 44, SP 12, MS 3) |
| 56014 | Tempestade | Perigo Potencial (amarelo) | 13/10 | 1.776 |
| 56051 | Baixa Umidade | Perigo Potencial (amarelo) | 13/10 09h → 14/10 | 1.012 |
| 56049 | Tempestade | Perigo (laranja) | 14/10 | 687 (PR 325, SP 285, MG 41, MS 31, RJ 5) |
| 56046 | Tempestade | Perigo Potencial | 14/10 | 1.824 |
| 56038 | Chuvas Intensas | Perigo Potencial | 14/10 | 77 (AM, RO, MT, RR) |
- 56048 e 56049 se sobrepõem em 260 municípios (não somar).

## Open-Meteo capitais (`openmeteo_capitais_3d.json`, best_match)
- Curitiba 13/10: 54,5 mm, rajada 57 km/h. Teresina 39,3 °C (13/10), 39,9 °C (14/10), umidade mín. 17% em 14/10. São Paulo 15/10: 63,3 mm.

## Satélite
- `sat/web/ir00..ir48` (GOES-19 IR, 12/10 08h → 13/10 08h UTC); ir16 e ir23 vazios (13,9 kB) — o filtro de brilho do gerar_cena.py tira.
