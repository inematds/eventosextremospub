# Dados dos brutos — 30/10/2026 (janela 29/10 08:30 UTC a 30/10 08:30 UTC)

Falha da coleta: estações do INMET (apitempo sem token, 204). Resto ok.

## INMET — avisos (inmet_avisos_ativos.json)
- Só amarelo (Perigo Potencial); nenhum laranja ou vermelho.
- Hoje 30/10: **56215 Chuvas Intensas amarelo, 3.226 municípios** (MG 853, SP 645, PR 399, SC 283, GO 246, MT 141, TO 135, RJ 92…). Risco: 20–30 mm/h ou até 50 mm/dia, vento 40–60 km/h. Inclui 10 capitais: Goiânia, São Paulo, BH, Rio, Brasília, Curitiba, Florianópolis, Campo Grande, Cuiabá, Vitória.
- Sábado 31/10: 56218 Chuvas Intensas amarelo, 1.886 municípios (MG 841, SP 311, GO 244…).
- Domingo 1/11: 56219 Tempestade amarelo, 1.277 municípios (MG 656, SP 229, PR 167, GO 114, MS 77, SC 34), com queda de granizo.

## INPE — focos de 29/10 (inpe_focos_diario_br_20261029.csv)
- O arquivo de 30/10 é parcial (0 focos AQUA): não usado.
- Satélite de referência (AQUA_M-T): **1.078 focos** no Brasil; Maranhão 278, Pará 223, Bahia 189, Piauí 156, Ceará 75.
- Em 28/10 foram 502 no mesmo satélite (../2026-10-29-ultimas-24h/pesquisa/bruto/inpe_focos_diario_br_20261028.csv, conferido: 502) → "mais que o dobro".
- Em todos os satélites o Pará lidera de longe (7.916): no vídeo, dizer "no satélite de referência".
- Biomas (ref.): Amazônia 426, Cerrado 335, Caatinga 311.

## CEMADEN — 24 h até 30/10 ~5h30 (cemaden_getJson2_todas_ufs.json, resumo.json)
- 5.722 estações, 1.847 com leitura recente; 16 com ≥ 50 mm.
- Belford Roxo (RJ): Vila Pauline 51,0 (40 em 6 h); Nova Aurora 49,93; Parque Fluminense 47,4; Santa Emília 46,8; Vila Santa Rita 42,4.
- Niterói (RJ): Capela Sto Expedito (Fonseca) 49,8; Jurujuba 48,17; Praia João Caetano 46,77. Duque de Caxias: Jardim Olavo Bilac 48,93; Sarapuí 48,93.
- Cachoeira da Prata (MG): 55,0 (53,2 em 3 h) e 51,2 (48,6 em 3 h) — os 2 pluviômetros.
- Araxá (MG): os 4 pluviômetros 55,6; 54,2; 53,8; 51,6.
- Sensor isolado, FORA da soma e da fala: Visconde do Rio Branco "Rio Xopoto" 179,0 (Centro sem leitura; vizinhos Senador Firmino 5,6/6,2, Guiricema 2,4, Viçosa 4,8–7,6, Ubá 0,2–1,2; excluído também em 28 e 29/10).
- Xambioá (TO) 68,02: sensor único, sem horária: fica na soma, não vai à fala.
- Soma dos pluviômetros: 21.585,1 mm·estação; sem o isolado 21.406,1 ("mais de 21 mil") em 1.846 pluviômetros.
  SP 7.117,7 ("mais de 7 mil"), MG 5.826,1 (sem o isolado), RJ 3.306,3, SC 1.274,4, PR 1.017,0.
- Não comparar com a soma de ontem (1.847 estações recentes hoje × 1.192 ontem).

## NOAA METAR (noaa_metar_brasil_24h.json)
- Guarulhos (SBGR): SPECI 292115Z +RA BR, visibilidade 1.500 m (18h15 de quinta).
- Confins/BH (SBCF): 300606Z +TSRA (3h06 de sexta).
- 11 aeroportos com trovoada (lista em resumo.json → noaa_metar.trovoada).
- Calor 29/10: Itaituba (SBIH) 39 °C às 15h e 16h, com fumaça (FU) 3.000 m de manhã; Boa Vista (SBBV) 38 °C às 18h.
- Frio: Pelotas (SBPK) 12 °C às 7h (291000Z).

## Open-Meteo — previsão 7 dias nas 27 capitais (previsao7d.json, 30/10 a 5/11)
- Soma: 523,8 mm. Por região: CO 167,0 (mais); SE 157,7; N 98,3; S 58,0; NE 42,8.
- Por dia: sex 105,2 (mais chuvoso) · sáb 55,1 · dom 83,0 · seg 88,9 · ter 80,6 · qua 43,4 · qui 67,6.
- Capitais que mais acumulam: Belo Horizonte 83,0; Brasília 63,2; Goiânia 53,8; São Paulo 37,6.
- Pico de máxima: Teresina 40,2 °C na quinta (5/11).
