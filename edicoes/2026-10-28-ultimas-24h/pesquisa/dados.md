# Dados dos brutos — 28/10/2026 (janela 27/10 08:30 UTC a 28/10 08:30 UTC)

Falha da coleta: estações do INMET (apitempo sem token, 204). Resto ok.

## INPE — focos de 27/10 (inpe_focos_diario_br_20261027.csv)
- Satélite de referência (AQUA_M-T): 1.331 focos no Brasil; Pará 902, Maranhão 214, Tocantins 88, Amapá 53, Bahia 21.
- Municípios (referência): Uruará 65, Portel 63, Moju 46, Pacajá 37, Santarém 37 (todos PA).
- Todos os satélites no CSV de 27/10: 20.798 registros (inclui GOES de 10 em 10 min; não usado como contagem).

## CEMADEN — 24 h até 28/10 ~5h20 (cemaden_getJson2_todas_ufs.json, resumo.json)
- 5.713 estações, 1.215 com leitura recente; 17 com ≥ 50 mm, 2 com ≥ 100 mm.
- Vitória da Conquista (BA): Barcelar 54,39; Recreio 54,3; Patagônia 45,8; Centro 45,68 mm (4 pluviômetros concordam).
- Camacan (BA): Centro 54,81; São João do Panelinha 52,12 mm.
- Formosa (GO): Av. Maestro Joaquim de Abreu 69,0 mm (69 nas últimas 3 h); Parque da Colina 50,2 (50,2 em 3 h). Dois concordam.
- Soma dos pluviômetros: 6.971,5 mm·estação no Brasil; BA 3.686,0 (246 estações), MG 1.303,8 (273), GO 326,6, SP 287,9, RJ 229,7.
- Sensores isolados (vizinhos da cidade bem abaixo ou sem leitura), FORA das somas e da fala:
  Visconde do Rio Branco "Rio Xopoto" 146,2 (Centro sem leitura; ontem 338,0); Arinos G2-310450202A 95,0 (vizinho 8,6);
  Jacobina "JACOBINA" 86,6 (vizinhos 16,0 e 16,8); Salvador "Doron" 48,2 (demais de Salvador ≤ 19,3). Total fora: 376,0.
- Capim Grosso (BA) 117,2: único pluviômetro da cidade, sem leitura horária; não citado na fala (fica na soma).
- Soma sem os 4: Brasil 6.595,5 ("mais de 6.500"); Bahia 3.551,2 ("mais de 3.500", 54% do total).

## NOAA METAR (noaa_metar_brasil_24h.json)
- Teresina (SBTE) 39 °C às 15h de 27/10; Boa Vista (SBBV) 38 °C às 17h; Santarém (SBSN) 37 °C às 17h.
- Santarém: FU (fumaça) e visibilidade 3.000 m de 4h a 7h de 27/10 (SBSN 270700Z…271000Z). Marabá: HZ/FU, 5 km.
- Mínimas 27/10 6h: Canoas (SBCO), Santa Maria (SBSM) e Santo Ângelo (SBNM) 9 °C.
- Rajada: São José dos Campos (SBSJ) 29 kt = 54 km/h às 17h de 27/10 (13017G29KT).

## INMET — avisos (inmet_avisos_ativos.json)
- Hoje 28/10: 56201 Tempestade amarelo, 1.861 municípios (SP 409, GO 246, PR 188, PI 186, MG 156…): 20–30 mm/h ou até 50 mm/dia, vento 40–60 km/h, granizo.
- 56196 Acumulado de chuva amarelo, 116 municípios da BA (28 e 29/10).
- Quinta 29/10: 56195 Tempestade amarelo, 2.777 municípios (SP 645, MG 536, PR 399, SC 295).
- Sexta 30/10: 56202 Tempestade amarelo, 2.430 municípios.
- Nenhum laranja/vermelho vigente.

## Open-Meteo — previsão 7 dias nas 27 capitais (previsao7d.json, 28/10 a 3/11)
- Soma: 686,0 mm. Por região: CO 227,5; SE 191,0; N 128,8; NE 83,8; S 54,9.
- Por dia: qua 110,2 · qui 117,0 · sex 139,4 (mais chuvoso) · sáb 96,7 · dom 57,7 · seg 111,6 · ter 53,4.
- Pico de máxima: Boa Vista 39,3 °C na quinta (29/10). Teresina 38,1–38,8 °C.
- Capitais que mais acumulam: Goiânia 78,7; Belo Horizonte 62,0; Campo Grande 52,0.
