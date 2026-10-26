# Dados dos brutos (coleta 26/10/2026 08h30 UTC; janela 25/10 05h30 → 26/10 05h30 de Brasília)

## NOAA METAR (noaa_metar_brasil_24h.json)
- Rajada: SBCF Confins (BH) 47 kt = 87,0 km/h, SPECI 25/10 16h11Z (13h11), "-TSRA" (trovoada com chuva). SBBH Pampulha 35 kt = 65 km/h 16h00Z. Maringá 63, Brasília 61, Uberlândia 59 km/h.
- Calor: SBIH Itaituba (PA) 40 °C em 25/10 18h00Z (15h), com "FU" (fumaça) no METAR. Teresina e Cuiabá 39 °C.
- Frio: SBNM Santo Ângelo (RS) 9 °C em 26/10 07h00Z (04h). Chapecó 11, Foz 12, Curitiba 13 °C.
- Trovoada em 20 aeroportos (BH, Brasília, Goiânia, Manaus, Campo Grande, Vitória, Porto Alegre…).

## CEMADEN (cemaden_getJson2_todas_ufs.json, resumo.json)
- Carinhanha (BA): 91,0 mm em 24 h (G2-290710303A; 84 mm em 6 h), vizinhos 68,0 e 38,4; Malhada (BA) 71,4.
- Serra Negra (SP) 86,8 mm; Mairiporã 77,0; Ribeirão Preto (Bonfim) 70,4; Águas da Prata 65,6; Caseara (TO) 84,6 e 83,2 (dois sensores).
- Descartados por isolados: Visconde do Rio Branco (MG) "Rio Xopoto" 137,4 (o outro sensor da cidade sem dado; já descartado em 24/10) e Salvador "Doron" 94,6 (os demais ~40 sensores de Salvador sem leitura; METAR de Salvador CAVOK).
- Soma dos pluviômetros (24 h): Brasil 22.732,8 mm em 1.981 estações recentes; sem os 2 isolados = 22.500,8 → "mais de 22.500". MG 8.351,3 (549) − 137,4 = 8.213,9 → "mais de 8.200"; SP 6.253,8 (390); RJ 2.521,8; RS 2.410,8; SC 814,4.

## INMET avisos (inmet_avisos_ativos.json)
- 56174 Tempestade amarelo (perigo potencial) 26/10 00h–23h59: 2.818 municípios (MG 853, SP 645, GO 246, BA 242, PR 219, MT 136, TO 124, RJ 92…), 20–30 mm/h ou até 50 mm/dia, vento 40–60 km/h, granizo.
- 56176 Baixa umidade amarelo 26/10 10h–17h: 355 municípios do Nordeste (PB 109, CE 69, PE 67, RN 44, PI 30, AL 20, BA 13, SE 3), 20–30%.
- 56177 Tempestade amarelo 27/10: 652 municípios (BA 276, GO 149, MG 148…).
- Nenhum laranja ou vermelho vigente.

## INPE focos (inpe_focos_diario_br_20261025.csv, dia 25/10 completo)
- Satélite de referência (AQUA tarde): 1.177 no Brasil; Pará 908; Uruará 164, Santarém 96, Aveiro 80. Todos os satélites: 30.403 linhas no arquivo (com repetição entre satélites; não usado).

## Open-Meteo previsão 7 dias (previsao7d.json, 27 capitais)
- Dias: seg 26 73,2 · ter 27 52,5 · qua 28 149,4 · qui 29 152,2 · sex 30 142,6 · sáb 31 86,8 · dom 01 100,8 mm somados. Total 757,5 → "mais de 750".
- Região: SE 233,2 (maior), N 208,8, CO 193,7, NE 80,6, S 41,2. Top capital: Goiânia 80,2 mm.
- Pico de máxima: Teresina 39,6 °C (qua 28 e dom 01).
