# Brasil, últimas 24 h: dados coletados

Janela: **09/10/2026 03:00 → 10/10/2026 03:00 (Brasília)** = 06:00Z → 06:00Z. Coleta feita às 02:58 de 10/10 (05:58Z).
Script: `coleta/ultimas24h.py edicoes/2026-10-10-ultimas-24h/pesquisa/bruto --fim 2026-10-10T06:00`. Brutos e `resumo.json` em `pesquisa/bruto/`.

Legenda: **MEDIDO** = estação ou satélite. **MODELO** = previsão numérica. **AVISO** = alerta oficial (é previsão, não medição).
Horas em Brasília (BRT = UTC−3), salvo quando indicado.

## Números mais fortes

| # | Número | Onde | Fonte · hora | Tipo |
|---|---|---|---|---|
| 1 | **Rajada de 83 km/h** (45 kt), com trovoada forte, chuva e visibilidade de 300 m | Aeroporto de São José dos Campos (SP) | NOAA/aviationweather.gov, METAR SBSJ 091807Z (15h07 de 09/10) | MEDIDO |
| 2 | **86,8 mm em 24 h** | Nazaré Paulista (SP), ETA Sabesp | CEMADEN pluviômetro, último dado 10/10 06:00 | MEDIDO |
| 3 | **16 pluviômetros com ≥ 50 mm em 24 h** (SP, MS, PR, MG) | Sudeste e Centro-Oeste | CEMADEN, 1.354 estações com dado nas últimas 6 h | MEDIDO |
| 4 | **39 °C** | Barra do Garças (MT) | METAR SBBW 091700Z (14h) | MEDIDO |
| 5 | **Umidade de 15 %** (33 °C) | Brasília (DF) | METAR SBBR 091900Z (16h), UR calculada de temp./orvalho | MEDIDO (UR derivada) |
| 6 | **40.857 detecções de fogo**; **2.001** pelo satélite de referência (AQUA tarde) | Pará lidera: 11.638 (1.115 no satélite de referência) | INPE Queimadas, CSV diário, último foco 10/10 04:40Z | MEDIDO |
| 7 | **439 municípios em aviso laranja (Perigo) de tempestade** hoje (PR 177, RS 129, SC 85, MS 47, SP 1) | Sul e MS | INMET avisos ativos, válido 10/10 00:00–23:59 | AVISO |
| 8 | **702 municípios em aviso laranja de baixa umidade** (GO 186, BA 152, PI 139, CE 49, PB 44, TO 43, PE 38, MG 31…) | Centro-Oeste e Nordeste | INMET, 09/10 09:25 → 10/10 21:00 | AVISO |
| 9 | **Brasília 12 % e Goiânia 13 % de umidade mínima** no sábado; **Teresina 39,5 °C** | capitais | Open-Meteo best_match, lido 10/10 05:58Z | MODELO |

**Dado descartado como suspeito:** Aquidabã (SE), pluviômetro CEMADEN 7098 (tipo 5), marca **315,8 mm em 24 h**, sendo 203 mm em 3 h. Nenhuma outra estação CEMADEN de Sergipe passou de 5 mm. Parece falha de sensor. **Não usar sem confirmação.** Excluído dos rankings abaixo.

## Por região

### Sudeste: temporais com rajada e o maior volume de chuva
- **Rajadas (METAR, MEDIDO, 09/10):** São José dos Campos **83 km/h** (15h07, +TSRA, CB); Ribeirão Preto **70 km/h** (14h); Campinas/Viracopos **65 km/h** (15h30, trovoada); Guarulhos **57 km/h** (17h10, trovoada); Vitória **50 km/h** (15h); Uberlândia 46 km/h (11h); Congonhas 39 km/h (17h44, trovoada).
- **Chuva 24 h (CEMADEN, MEDIDO, até 10/10 ~06:00):** Nazaré Paulista/SP **86,8 mm**; Monte Mor/SP 66,2; Valinhos/SP 66,2; Lorena/SP 65,8; Sorocaba/SP 61,0; Tiradentes/MG 54,9. Máximo do RJ: 38,0 mm; ES: 7,8 mm.
- **Calor e ar seco (METAR, MEDIDO):** São José do Rio Preto 37 °C (UR 21 %); Ribeirão Preto 37 °C (UR 25 %); Montes Claros/MG **UR 18 %** (36 °C, 13h); Uberaba UR 23 %; Uberlândia UR 24 %.
- **Trovoada reportada em METAR (MEDIDO):** Guarulhos, Congonhas, Campo de Marte, Campinas, São José dos Campos, Taubaté, Guaratinguetá, Bauru, Ribeirão Preto, Pirassununga, Presidente Prudente, Barbacena.

### Centro-Oeste: o ponto mais quente e o ar mais seco
- **Temperatura máxima (METAR, MEDIDO, 09/10):** Barra do Garças/MT **39 °C** (14h); Goiânia 37 °C; Cuiabá 37 °C; Alta Floresta/MT 37 °C.
- **Umidade mínima (METAR, MEDIDO):** Brasília **15 %** (16h); Anápolis/GO 20 %; Goiânia 21 %; Barra do Garças 23 %.
- **Chuva (CEMADEN, MEDIDO):** Dourados/MS 62,6 mm; Corumbá/MS 60,2; Rochedo/MS 55,0.
- **Rajada (METAR):** Campo Grande **67 km/h** com trovoada (09/10 09h). Trovoada também em Ponta Porã.

### Sul: chuva no oeste do PR e aviso laranja
- **Chuva (CEMADEN, MEDIDO):** Medianeira/PR 57,0 mm; Maria Helena/PR 54,8; máximo do RS 48,0 mm; SC 30,2 mm.
- **Rajada:** Maringá **56 km/h** (09/10 05h). Trovoada em Cascavel, Foz do Iguaçu, Londrina e Maringá.
- **Menor temperatura do país (METAR):** Pelotas/RS 16 °C (10/10 00Z = 21h de 09/10). Bagé, Canoas, Curitiba, Porto Alegre, Passo Fundo, Santa Maria, Chapecó e Santo Ângelo: 17 °C.

### Norte: calor de 38 °C e as queimadas
- **Temperatura máxima (METAR, MEDIDO):** Manaus (Eduardo Gomes e Ponta Pelada) **38 °C**; Itaituba/PA 38 °C; Boa Vista 38 °C; Palmas 37 °C.
- **Fogo (INPE, MEDIDO, todos os satélites):** Pará 11.638, Amazonas 6.563, Tocantins 3.120, Roraima 582. Municípios: **Altamira/PA 1.628**, Uruará/PA 1.125, Autazes/AM 1.079, Itaituba/PA 851, São Félix do Xingu/PA 753.
- Trovoada em METAR: Porto Velho, Rio Branco, Tabatinga.

### Nordeste: calor no PI e ar seco no interior
- **Temperatura máxima (METAR, MEDIDO):** Teresina **38 °C** (16h, UR 26 %).
- **Umidade mínima (METAR):** Juazeiro do Norte/CE 25 %; Petrolina/PE 25 %.
- **Fogo (INPE, todos os satélites):** Bahia 6.130, Piauí 3.156, Maranhão 2.918. Barra/BA 944, Formosa do Rio Preto/BA 843, Muquém do São Francisco/BA 763.
- Chuva: só o suspeito de Aquidabã/SE. Fora ele, o maior acumulado no NE foi 9,5 mm em PE.

### Queimadas: total do país (INPE, MEDIDO, 06:00Z 09/10 → 04:40Z 10/10)
- Todos os satélites: **40.857 detecções**. O mesmo fogo aparece várias vezes (o GOES-19 passa a cada 10 min), então **não é número de incêndios**.
- Satélite de referência AQUA_M-T: **2.001 focos** (série comparável). Pará 1.115, Tocantins 200, Bahia 189, Minas 119, Goiás 87.
- Por bioma: Amazônia 21.409 / Cerrado 15.074 / Caatinga 2.598 / Mata Atlântica 1.776. No satélite de referência: 1.282 / 674 / 10 / 35.

## Avisos INMET ativos (lidos às 02:58 de 10/10)
- **Hoje, 5 avisos:**
  - Tempestade **Perigo** (laranja): 439 municípios em PR, RS, SC, MS e SP, 10/10 00:00–23:59.
  - Baixa Umidade **Perigo** (laranja): 702 municípios em GO, BA, PI, CE, PB, TO, PE, MG, MT, RN, MA e DF, até 21h de 10/10.
  - Tempestade Perigo Potencial (amarelo): 1.937 municípios (09/10 09:40 → 10/10 09:59) e 2.394 municípios (10/10 10:00–23:59), em SP, RS, PR, SC, MG, MT, MS, RO, AM, AC e RJ.
  - Baixa Umidade Perigo Potencial (amarelo): 2.133 municípios em 17 UFs (MG 497, BA 305, GO 239, PI 213…), 10/10 09:00 → 13/10.
- **Futuro, 3 avisos (todos amarelos):** Tempestade 11–12/10 em 2.335 municípios (SP 645, RS 253, PR 399, SC 295, MG 315…); Tempestade 13/10 em 1.776 municípios; Baixa Umidade até 13/10.
- Ao todo, 24 UFs estão sob algum aviso. Ficam de fora: ES, AP e RR.

## Próximas 48 h (Open-Meteo best_match, MODELO, capitais, lido 10/10 05:58Z)

| Capital | Sáb 10/10: máx/mín · chuva · rajada · UR mín | Dom 11/10: máx/mín · chuva · rajada · UR mín |
|---|---|---|
| Teresina | **39,5**/25,4 · 0,1 mm · 49 km/h · 24 % | **38,9**/25,4 · 0 · 48 · 23 % |
| Boa Vista | 37,7/27,2 · 0 · 41 · 34 % | 37,0/27,7 · 1,5 · 45 · 39 % |
| Manaus | 37,1/28,9 · 0 · 36 · 30 % | 36,9/28,8 · 0 · 35 · 34 % |
| Goiânia | 36,7/23,6 · 0 · 53 · **13 %** | 37,4/22,4 · 0 · 42 · **14 %** |
| Porto Velho | 36,8/26,0 · 0,1 · 23 · 42 % | 33,1/25,0 · 7,2 · 32 · 59 % |
| Brasília | 35,5/22,0 · 0 · 32 · **12 %** | 33,4/22,0 · 0 · 42 · **18 %** |
| Rio Branco | 35,7/24,2 · 1,2 · 26 · 43 % | 33,1/23,5 · 9,4 · 41 · 52 % |
| Cuiabá | 34,5/24,8 · 5,8 · 55 · 45 % | 30,1/24,4 · 0,1 · 26 · 66 % |
| Palmas | 33,7/25,8 · 1,8 · 24 · 39 % | 35,5/26,5 · 0,5 · 37 · 34 % |
| Belo Horizonte | 31,6/21,0 · 0 · 33 · 33 % | 31,6/19,8 · 0 · 36 · 31 % |
| São Paulo | 28,9/19,4 · **10,9** · 29 · 56 % | 27,1/19,4 · **15,2** · 30 · 57 % |
| Curitiba | 26,0/16,9 · 5,1 · 46 · 58 % | 23,6/15,2 · **26,2** · 36 · 71 % |
| Florianópolis | 24,8/18,1 · 3,9 · 35 · 80 % | 21,2/17,1 · 0,6 · 43 · 69 % |
| Porto Alegre | 21,3/16,3 · 3,7 · 30 · 78 % | 18,9/14,4 · 1,3 · 28 · 71 % |
| Campo Grande | 27,0/20,3 · 7,9 · 35 · 64 % | 27,9/20,8 · 3,4 · 33 · 61 % |
| Fortaleza | 30,4/25,5 · 0,9 · 54 · 53 % | 30,0/26,1 · 0,1 · 57 · 51 % |
| Vitória | 30,1/22,5 · 0 · 52 · 55 % | 30,3/22,5 · 0 · 55 · 52 % |
| Rio de Janeiro | 27,5/22,2 · 0 · 34 · 76 % | 27,1/22,8 · 3,6 · 29 · 81 % |

As demais capitais têm máximas de 28 a 34 °C, chuva até 6 mm e rajada até 53 km/h. A tabela completa, com 12/10, está em `bruto/openmeteo_capitais_3d.json`.

**Extremos pelos critérios** (calor ≥ 38 °C, chuva ≥ 50 mm, rajada ≥ 70 km/h, UR ≤ 20 %):
- Calor: **Teresina** 39,5 °C (sáb), 38,9 °C (dom) e 38,9 °C (seg).
- UR ≤ 20 %: **Brasília** 12 % (sáb), 18 % (dom) e 17 % (seg); **Goiânia** 13 % (sáb), 14 % (dom) e 20 % (seg).
- Nenhuma capital passa de 50 mm de chuva nem de 70 km/h de rajada no modelo. O modelo pega mal a convecção local: o aviso laranja de tempestade do INMET no Sul e no MS (439 municípios hoje) vale mais que o ponto da capital.

## Falhas de coleta
1. **INMET estações automáticas: sem dados.** `https://apitempo.inmet.gov.br/estacao/dados/2026-10-09/HH00` foi pedido para as 25 horas da janela e devolveu **HTTP 204 (vazio)** em todas. `estacao/2026-10-09/2026-10-10/A001` também deu **204**. `estacao/dados/2026-10-09` (sem hora) deu **404**. A lista de estações (`/estacoes/T`) responde 200, mas sem token não sai dado de estação. **Substituto:** METAR da NOAA (107 aeroportos, 2.192 observações; MEDIDO) para temperatura, umidade e rajada, e CEMADEN para chuva. Os METAR não trazem chuva acumulada.
2. **Raios (GOES GLM): não deu.** O GIBS não tem camada GLM (busca por "GLM/lightning/flash" nas capacidades WMTS epsg4326/best, epsg4326/nrt, epsg4326/all e epsg3857/best). Só existem climatologias LIS/OTD e LIS-ISS (encerrado). **Substituto:** lista de aeroportos com TS (trovoada) no METAR (22 aeroportos).
3. **CEMADEN:** `getJson2.php?uf=XX` funcionou para as 27 UFs, com 5.591 estações. Só 1.354 mandaram dado nas últimas 6 h e entraram no ranking. Aquidabã/SE (315,8 mm) é suspeito (ver acima). O endpoint antigo `sjc.salvar.cemaden.gov.br` não resolve o DNS, e `mapainterativo.cemaden.gov.br/MapaInterativoWS/resources/horario/3/24` dá 404.
4. **NOAA METAR, limite:** o pedido por bbox volta no máximo 400 linhas (cobria só ~8 h). O script passou a pedir por códigos, em lotes de 10 estações. Os nomes da NOAA trazem a UF errada em alguns casos (SBGR "PR", SBAT "SP", SBPJ "TP"): aqui foram corrigidos para SP, MT e TO.
5. **INPE:** o CSV diário vai até 04:40Z de 10/10, então falta ~1h20 da janela. O CSV de 10 min não traz estado nem bioma e não foi usado.

## Arquivos brutos (`pesquisa/bruto/`)
- `resumo.json`: todos os resultados agregados, mais as falhas
- `inmet_avisos_ativos.json`
- `inmet_estacoes_tentativas.json`
- `cemaden_getJson2_todas_ufs.json`
- `inpe_focos_diario_br_20261009.csv` e `inpe_focos_diario_br_20261010.csv`
- `noaa_metar_brasil_24h.json`
- `openmeteo_capitais_3d.json`
