# Dados dos brutos — 07/11/2026 (coleta 07/11 08:30 UTC)

Falha da coleta: inmet_estacoes (apitempo sem token, 204) — sem dado de estação do INMET; uso METAR e CEMADEN.

## CEMADEN (cemaden_getJson2_todas_ufs.json, acc24hr até ~07/11 08h30 UTC)
- DESCARTADO: Salvador/Doron 119,4 mm (tipo 10). As outras estações de Salvador estão sem leitura ("-"), e ontem a mesma estação já tinha dado 120,2 mm isolado: leitura suspeita, fora do vídeo e da soma.
- SC: Abdon Batista G2-420005101A 105,8 mm ("quase 106"; 2ª estação da cidade 93,4); Anita Garibaldi 80,6; Lages/Morro do Pandolfo 69,24; Pouso Redondo 65,4.
- RS: Paim Filho G2-431360701A 94,0 mm; Passo Fundo/Parque Farroupilha 71,2; Lagoa Vermelha 62,0.
- n ≥ 50 mm: 25 estações; n ≥ 100: 2 (uma é o Doron descartado).
- Soma dos pluviômetros (resumo.json): 8.096,5 mm·estação em 1.231 estações recentes; sem o Doron: 7.977,1 → "quase 8 mil". Rótulo: soma dos pluviômetros, não lâmina de área.
- Soma por UF: SC 3.689,6 (185 estações) → "mais de 3.600 só em Santa Catarina"; RS 2.088,6 (254); MG 658,4; PR 468,3; RJ 251,5.

## NOAA METAR (noaa_metar_brasil_24h.json)
- Máxima: 38 °C em Teresina, Petrolina, Paulo Afonso, Juazeiro do Norte, Cuiabá e Boa Vista (06/11 tarde).
- Mínima: Santa Maria 12 °C, Passo Fundo 13 °C (06/11 madrugada).
- Rajada máxima: Cuiabá 50 km/h (27 kt) — fraco, não usado.

## INPE focos (inpe_focos_diario_br_20261106.csv — dia inteiro de 6/11)
- AQUA_M-T (satélite de referência): 2.139 focos; Maranhão 729, Pará 628, Bahia 257, Amapá 138, Piauí 129. (Ontem, 5/11: 580.)
- O CSV de 7/11 é parcial (sem AQUA): não usado.

## INMET avisos (inmet_avisos_ativos.json)
- Hoje 7/11: 56310 Tempestade VERMELHO (Grande Perigo) em 325 municípios (RS 124, SC 112, PR 89): mais de 60 mm/h ou 100 mm/dia, vento acima de 100 km/h, granizo.
- Hoje 7/11: 56309 Tempestade LARANJA (Perigo) em 1.098 municípios (PR 399, SC 295, RS 269, SP 116, MS 19).
- Hoje 7/11: 56308 Tempestade amarelo em 3.170 municípios; 56296 Baixa Umidade amarelo 608 (NE); 56280 declínio de temperatura amarelo 105 (RS); 56311 ventos costeiros 10 (RS).
- Domingo 8/11: 56281 Declínio de Temperatura amarelo em 2.060 municípios (PR, SC, RS, SP, MS, MG, RJ), queda de 3 a 5 °C.
- Segunda 9/11: 56316 Declínio de Temperatura amarelo em 1.063 (MG 764…).

## Previsão 7 dias (previsao7d.json, Open-Meteo, 27 capitais, 7/11 a 13/11)
- Somas por dia (mm): sáb 94,1 · dom 132,5 · seg 120,7 · ter 152,0 · qua 108,3 · qui 155,1 · sex 127,6 (dia mais chuvoso = quinta 12/11).
- 7 dias: 890,3 mm somados → "mais de 890". Região: SE 291,2 (maior) · N 232,6 · CO 193,3 · NE 103,7 · S 69,5.
- Capital com mais chuva em 7 dias: Belo Horizonte 131,2 mm.
- Pico de máxima: Teresina 40,0 °C na segunda (9/11).
