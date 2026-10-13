# Clima no Brasil: últimas 24 h (12/10 05h30 a 13/10 05h30, Brasília) e próximas 48 h

Pesquisa feita na manhã de terça-feira, 13/10/2026, com WebSearch. Sem API paga.
Marcação: **[oficial]** = órgão público; **[1 fonte]** = um só veículo.

**Limitação:** nenhuma notícia de estragos do feriado (12/10) com data confirmada apareceu nas buscas. Buscas feitas:
"temporal Paraná Foz do Iguaçu chuva 12 outubro 2026 Defesa Civil", "Presidente Prudente temporal vento madrugada 13 outubro 2026",
"Defesa Civil temporal estragos 12/10/2026 chuva granizo desalojados", "Defesa Civil Paraná temporal segunda-feira feriado 12 de outubro estragos municípios",
"chuva São Paulo feriado 12 de outubro 2026 alagamento queda de árvores CGE", "temporal oeste do Paraná Cascavel Medianeira chuva estragos outubro 2026",
"temporal Presidente Prudente Oeste Paulista destelhamento queda de árvores outubro 2026", "previsão do tempo terça-feira 13 de outubro 2026".
Os resultados eram previsões de antes do feriado ou eventos de outras datas (29/09 no oeste do PR, 04/10 em Presidente Prudente, 3 a 5/10 no PR). **Por isso a edição usa só medição (CEMADEN, METAR/NOAA, INPE) e avisos do INMET; nenhum balanço de estrago vai ao ar.**

## Contexto (não vai ao ar como fato das 24 h)

- INMET tinha alerta laranja para 260 cidades do PR no feriado, até 100 mm no dia e granizo (Gazeta do Paraná, véspera) — https://gazetadoparana.com.br/publico/inmet-emite-alerta-laranja-para-260-cidades-do-parana-no-feriado-de-12-de-outubro
- Temporais previstos no Sul e Sudeste no feriado; oeste do PR podia passar de 100 mm em 24 h (Revista Oeste, previsão) — https://revistaoeste.com/brasil/temporais-atingem-sul-e-sudeste-no-feriado-de-12-de-outubro/
- CGE (SP), noite de 12/10: radar sem chuva significativa na Grande SP; para terça (13) pancadas moderadas a fortes no fim da tarde e à noite, com risco de alagamento (via resultado de busca, página https://www.cgesp.org/v3/noticias.jsp) [oficial, não conferido na página].
- Eventos de outras datas, **descartados**: temporal de 29/09 no oeste do PR (souagro.net), 04/10 em Presidente Prudente com rajadas de 80 km/h (ifronteira.com), balanço da Defesa Civil do PR de 3 a 5/10 (bemparana.com.br).

## Últimas 24 h (medido, arquivos em pesquisa/bruto)

- **Foz do Iguaçu (PR): 104,4 mm em 24 h**, pluviômetro CEMADEN "São Miguel", leitura 13/10 08h00 UTC (05h Brasília) — `cemaden_getJson2_todas_ufs.json` / `resumo.json → cemaden.top`.
- **Medianeira (PR): 100,2 mm**; **Cascavel (PR) Centro: 91,2 mm**; São Miguel do Iguaçu 87,7 mm — mesmo arquivo.
- **Presidente Prudente (SP): rajada de 42 nós (77,8 km/h → dito 77 km/h)** com trovoada forte e linha de instabilidade (+TSRA SQ), METAR SBDN 13/10 04h00 UTC (01h Brasília) — `noaa_metar_brasil_24h.json`: `METAR SBDN 130400Z 23027G42KT 3000 +TSRA SQ ...`.
- Foz do Iguaçu, aeroporto: rajada de 36 nós (67 km/h) com trovoada, SPECI SBFI 12/10 21h20 UTC.
- **Calor:** 39 °C em Teresina (SBTE, 12/10 19h UTC) e em Itaituba (SBIH, 12/10 18h UTC) — METAR.
- **Ar seco:** umidade de 16% em Juazeiro do Norte (SBJU, 12/10 20h UTC, 36 °C), calculada do METAR.
- **Fogo:** INPE, 12/10, satélite de referência AQUA (passagem completa, 1.384 focos às 19h UTC): **1.401 focos no Brasil, 1.064 no Pará** (76%); Altamira 124, Itaituba 116, Uruará 113 — `inpe_focos_diario_br_20261012.csv`.

## Hoje e amanhã (avisos e previsão)

- **INMET [oficial, `inmet_avisos_ativos.json`]:**
  - hoje (13/10): **tempestade laranja (Perigo) em 591 municípios** — PR 319, SC 213, RS 44, SP 12, MS 3 — id 56048; chuva de 30 a 60 mm/h ou 50 a 100 mm/dia, vento de 60 a 100 km/h, granizo;
  - hoje: tempestade amarela (Perigo Potencial) em 1.776 municípios — id 56014;
  - amanhã (14/10): **tempestade laranja em 687 municípios** — PR 325, SP 285, MG 41, MS 31, RJ 5 — id 56049;
  - **baixa umidade amarela em 1.012 municípios de 13/10 09h a 14/10** (PI 216, BA 183, CE 143, MG 140, PB 91…; 823 no Nordeste) — id 56051.
- **Open-Meteo (modelo, `openmeteo_capitais_3d.json`):** Curitiba 54,5 mm hoje (13/10); Teresina 39,3 °C hoje e 39,9 °C amanhã; São Paulo 63,3 mm na quinta (15/10).
