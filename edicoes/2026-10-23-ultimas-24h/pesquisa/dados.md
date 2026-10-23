# Dados dos brutos — janela 22/10 08h30 UTC → 23/10 08h30 UTC

Falhas da coleta (resumo.json → falhas): INMET estações (204, sem token) e NOAA METAR (504). Sem temperatura medida de estação hoje.

## CEMADEN (cemaden_getJson2_todas_ufs.json; resumo.json → cemaden)
- 5.690 estações, 1.975 com dado nas últimas 6 h. Soma bruta 12.930,5 mm·estação.
- Paraná: 3.480,8 mm somados em 155 pluviômetros (média 22,5 mm). Maior soma por UF.
- Guarapuava (PR) Centro 59,6 mm (última leitura 23/10 06:20 UTC); Coronel Vivida (PR) Prefeitura 54,4 mm, 16,8 mm na última hora; Ipiranga (PR) 50,8 mm (17 na última hora); Cascavel Centro 50,2; Prudentópolis 49,8; Chopinzinho 49,0 e 45,4 (duas estações, coerentes).
- Senador Canedo (GO) G2-522045402A 49,2 mm; as outras três da cidade 37,2 / 39,8 / 33,2 (coerente). Aparecida de Goiânia Jardim Monte Sinai 45,8.
- Sensores isolados (vizinhos da mesma cidade quase secos) FORA das somas: Angra dos Reis (RJ) Colégio Naval 92,2 (17 vizinhos de 0,2 a 16,7); Visconde do Rio Branco (MG) Rio Xopoto 89,8 (sem vizinho; isolado de novo, descartado também em 22/10); Salvador (BA) Doron 47,8 (vizinhos ≤3); Caeté (MG) Cidade Jardim 50,73 (vizinhos 0,6 e 0,4); Japurá (AM) G2-130210801A 34,2 (vizinho 0,6). Total descartado 314,73.
- Brasil sem os 5 sensores: 12.930,5 − 314,73 = 12.615,77 mm·estação → "mais de 12.600" (1.970 pluviômetros). PR não muda: "mais de 3.400".
- Rótulo: soma dos pluviômetros, não chuva média.

## INPE Queimadas (inpe_focos_diario_br_20261022.csv, todos os focos com data 22/10)
- Satélite de referência AQUA_M-T: 1.933 focos no Brasil em 22/10 (quinta). Pará 1.260; Tocantins 334; Goiás 73; Amapá 72; Maranhão 69.
- Municípios (AQUA): Portel (PA) 149; Pacajá 70; Uruará 67; Almeirim 61; São Félix do Xingu 52.
- Todos os satélites: 28.869 detecções no arquivo (não usado na fala).
- Ontem (edição 22/10, arquivo de 21/10): 1.237 AQUA — só citado no painel como comparação de dias separados ("na quarta, 1.237").

## INMET avisos (inmet_avisos_ativos.json)
- 56144 Tempestade, Perigo (laranja), 23/10: 590 municípios (PR 277, RS 184, SC 109, MS 19, SP 1); 30–60 mm/h ou 50–100 mm/dia, vento 60–100 km/h, granizo.
- 56143 Tempestade, Perigo Potencial (amarelo), 23/10: 2.746 municípios em 10 UFs (MG 633, SP 645, RS 497, PR 399, SC 295, RJ 92, MS 79, ES 54, GO 46, MT 6).
- 56120 Chuvas Intensas amarelo 23/10: 43 municípios (AC 22, AM 20, RO 1).
- 56156 Baixa Umidade amarelo até 23/10 20h: 684 municípios (PI 218, CE 106, PB 104…), 20% a 30%.
- 56154 Tempestade, Perigo (laranja), 24/10: 835 municípios (PR 323, SP 196, SC 192, RS 109, RJ 8, MG 7).
- 56153 amarelo 24/10: 2.627; 56155 amarelo 25/10: 2.472.

## Open-Meteo — previsão 7 dias (previsao7d.json, 27 capitais, 23 a 29/10)
- Soma 7 dias: 757,8 mm somados nas capitais ("mais de 750").
- Por região em 7 dias: SE 189,0; CO 171,4; S 168,8; N 149,3; NE 79,3 → Sudeste acumula mais.
- Dia mais chuvoso: domingo 25/10, 176,7 mm somados (SE 65,2; S 55,1; CO 47,1).
- Top acumulado: Florianópolis 81,7; São Paulo 77,2; Curitiba 71,5.
- Pico de máxima: Teresina 39,9 °C no sábado 24/10 ("perto dos 40").

## Satélite
- sat/web/ir00..ir24 + ir_tempos.json (GOES-19 infravermelho via NASA GIBS), geocolor.jpg.
