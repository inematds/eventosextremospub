# Dados dos brutos — janela 23/10 08h30 UTC → 24/10 08h30 UTC

Falhas da coleta (resumo.json → falhas): só INMET estações (204, sem token). NOAA METAR voltou hoje (107 aeroportos, 2.147 observações).

## INMET avisos (inmet_avisos_ativos.json)
- 56168 Tempestade, GRANDE PERIGO (vermelho), 24/10 06:00 → 21:00: 325 municípios (SC 146, PR 99, RS 80). Chuva > 60 mm/h ou > 100 mm/dia, vento > 100 km/h, granizo; grande risco de danos em edificações, corte de energia, queda de árvores, alagamentos e transtornos nas rodovias.
- 56164 Tempestade, Perigo (laranja), 24/10: 934 municípios (PR 351, SC 273, SP 187, RS 123); 30–60 mm/h ou 50–100 mm/dia, vento 60–100 km/h, granizo.
- 56153 Tempestade, Perigo Potencial (amarelo), 24/10: 2.627 municípios em 9 UFs (SP 645, MG 638, RS 497, PR 399, SC 295, RJ 78, MS 57, GO 11, ES 7).
- 56162 Baixa Umidade amarelo, 24/10 10h–18h: 600 municípios (PI 184, PB 108, BA 102, CE 77, PE 64, RN 49…), 20% a 30%.
- 56166 Tempestade amarelo 25/10 (domingo): 2.383 municípios (MG 769, SP 645, PR 251, SC 169, GO 152, RJ 92, RS 90, ES 78, MS 73, MT 48, BA 16).
- 56167 Tempestade amarelo 26/10: 1.441 municípios (MG 561, BA 259, GO 205…).

## CEMADEN (cemaden_getJson2_todas_ufs.json; resumo.json → cemaden)
- 5.700 estações, 1.816 com dado recente. Soma bruta 15.338,7 mm·estação; 19 estações ≥ 50 mm, 5 ≥ 100 mm (3 delas suspeitas, abaixo).
- Barracão (PR), sudoeste: os 3 pluviômetros coerentes — G2-410260402A 103,6 mm (25,6 na última hora), G2-410260403A 102,6 (32,8 na última hora), G2-410260401A 96,4.
- Santo Antônio do Sudoeste (PR) 94,6 e 70,0; Santa Izabel do Oeste 70,0; Manfrinópolis 67,0 e 60,4; Francisco Beltrão Pinheirinho 64,4 (22,2 na última hora); Coronel Vivida 55,4.
- RS: Sant'Ana do Livramento 65,0 e 55,6 (vizinho 33,6); São Francisco de Assis 51,0 e 48,8; Alegrete 47,4.
- Sensores isolados FORA das somas: Aquidabã (SE) 357,2 (sem leitura de 1/3/6 h, sem vizinho; SE inteiro tem 9 estações e soma 363,2); Visconde do Rio Branco (MG) Rio Xopoto 275,4 (isolado de novo, descartado em 22 e 23/10); Angra dos Reis (RJ) Colégio Naval 129,0 (vizinhos 0,2 a 0,4; descartado também em 23/10); Caeté (MG) Cidade Jardim 70,79 (vizinhos 3,73 / 1,8 / 0,2; descartado em 23/10). Total descartado 832,39.
- Brasil sem os 4 sensores: 15.338,7 − 832,39 = 14.506,31 mm·estação → "mais de 14.500".
- Por UF (sem os sensores): MG 4.200,7 (497 estações), SP 3.343,1 (376), PR 2.709,9 (143, maior média: 19,0 mm), RS 2.156,2 (207), SC 1.159,3 (161). PR → "mais de 2.700".
- Rótulo: soma dos pluviômetros, não chuva média.

## NOAA METAR (noaa_metar_brasil_24h.json; resumo.json → noaa_metar)
- Máxima: Teresina (SBTE) 39 °C às 23/10 20:00Z; Itaituba, Cuiabá, Corumbá e Boa Vista 38 °C.
- Umidade mínima: Teresina 23% (23/10 19:00Z); Juazeiro do Norte 25%.
- Rajada: Foz do Iguaçu (SBFI) 67 km/h às 23/10 12:23Z (SPECI 10025G36KT; 36 nós = 66,7 km/h).
- Trovoada observada em vários aeroportos do Centro-Sul (Chapecó, Foz do Iguaçu, BH, Brasília, Campinas…).

## INPE Queimadas (inpe_focos_diario_br_20261023.csv)
- AQUA (satélite de referência) em 23/10: só 487 focos (Ceará 102, Bahia 67, Roraima 52, Pará 35), contra 1.933 em 22/10 — Pará 35 no AQUA mas 11.609 detecções em todos os satélites: queda parece falha de cobertura da passagem, não queda real. Fogo FORA da pauta de hoje (na dúvida, de fora).

## Open-Meteo — previsão 7 dias (previsao7d.json, 27 capitais, 24 a 30/10)
- Soma 7 dias: 959,8 mm somados nas capitais ("mais de 950").
- Por região em 7 dias: SE 318,0; CO 244,9; S 168,4; N 155,3; NE 73,2 → Sudeste acumula mais.
- Dia mais chuvoso: sexta 30/10, 209,2 mm (SE 108,4); domingo 25/10 quase igual, 207,5 (SE 113,4) → "domingo e a próxima sexta".
- Hoje 24/10: 72,2 mm, 56,9 no Sul (Florianópolis ≥ 30 mm).
- Top acumulado: Rio de Janeiro 133,6; Goiânia 87,8; Curitiba 81,0; Belo Horizonte 78,1; São Paulo 69,4.
- Calor: pico Cuiabá 40,2 °C no domingo 25/10; Teresina 39,3 a 39,8 todos os dias.
