# Dados dos brutos — 06/11/2026 (coleta 06/11 08:30 UTC)

Falha da coleta: inmet_estacoes (apitempo sem token, 204) — sem dado de estação do INMET; uso METAR e CEMADEN.

## CEMADEN (cemaden_getJson2_todas_ufs.json, acc24hr até ~06/11 08h UTC)
- DESCARTADO: Salvador/Doron 120,2 mm. Todas as outras ~20 estações de Salvador marcam 0 (ou "-") em 24 h e a Codesal informou tempo firme na quinta: leitura isolada, provável erro. Fica fora do vídeo e da soma.
- MG, Grande BH: Brumadinho/Alberto Flores 78,76 mm ("quase 79"); Santa Luzia/Rio das Velhas 88,2 (estação tipo 3, fica de fora; os pluviômetros comuns de Santa Luzia marcam 52,2 e 40,2); Contagem/Retiro 53,69; BH/Taquaril 41,38.
- MS: Dourados/Centro 79,6 mm ("quase 80").
- PR: Jacarezinho 72,2.
- Soma dos pluviômetros (resumo.json): 12.850,9 mm·estação em 1.510 estações; sem o Doron: 12.730,7 → "mais de 12.700". Rótulo: soma dos pluviômetros, não lâmina de área.
- Soma por UF: MG 7.059,7 (486 estações) → "mais de 7 mil só em Minas"; RJ 1.307,2; PR 1.228,5; SP 1.016,9; ES 630,6.

## NOAA METAR (noaa_metar_brasil_24h.json)
- SBCF Confins (Belo Horizonte/Tancredo Neves) 05/11 15:20Z: SPECI 30031G44KT +TSRA → rajada de 44 kt = 81 km/h, a maior do país.
- SBMG Maringá 05/11 11:00Z: 38 kt = 70 km/h.
- Máxima: Teresina e Juazeiro do Norte 39 °C (05/11). Mínima: Curitiba e Santa Maria 14 °C.

## INPE focos (inpe_focos_diario_br_20261105.csv — dia inteiro de 5/11)
- AQUA_M-T (satélite de referência): 580 focos; Maranhão 100, Ceará 86, Bahia 83, Mato Grosso 66, Piauí 49.
- O CSV de 6/11 é parcial (sem AQUA): não usado.

## INMET avisos (inmet_avisos_ativos.json)
- Hoje 6/11: 56286 Baixa Umidade LARANJA (Perigo) em 341 municípios do NE (PB 106, CE 73, PE 59, PI 45, RN 43, AL 8, BA 7), umidade de 20% a 12%.
- Hoje 6/11: 56293 Tempestade AMARELO (Perigo Potencial) em 1.568 municípios (MG 693, SP 404, PR 243, GO 118, ES 46, RJ 35, MS 26, SC 2, MT 1): até 50 mm/dia, vento 40–60 km/h, granizo.
- Amanhã 7/11: 56295 Tempestade amarelo em 2.595 municípios.
- Domingo 8/11: 56281 Declínio de Temperatura amarelo em 2.060 municípios (PR, SC, RS, SP, MS, MG, RJ), queda de 3 a 5 °C.
- Nenhum vermelho.

## Previsão 7 dias (previsao7d.json, Open-Meteo, 27 capitais, 6/11 a 12/11)
- Somas por dia (mm): sex 22,5 · sáb 87,2 · dom 144,3 · seg 102,9 · ter 106,5 · qua 134,4 · qui 167,0 (dia mais chuvoso = quinta 12/11).
- 7 dias: 764,8 mm somados → "mais de 760". Região: N 200,7 (maior) · CO 191,0 · SE 151,8 · NE 135,7 · S 85,6.
- Pico de máxima: Teresina 39,9 °C hoje.
