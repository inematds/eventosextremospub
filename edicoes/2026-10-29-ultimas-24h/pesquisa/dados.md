# Dados dos brutos — 29/10/2026 (janela 28/10 08:30 UTC a 29/10 08:30 UTC)

Falha da coleta: estações do INMET (apitempo sem token, 204). Resto ok.

## INMET — avisos (inmet_avisos_ativos.json)
- Hoje 29/10: **56207 Chuvas Intensas LARANJA (Perigo), 918 municípios** (MG 352, SP 342, GO 160, RJ 43, MT 15, MS 6); inclui Goiânia e São Paulo (capital). Risco: 30–60 mm/h ou 50–100 mm/dia, vento 60–100 km/h.
- Hoje 29/10: 56206 Chuvas Intensas amarelo, 2.338 municípios (SP 645, MG 519, PR 399, GO 243…), inclui BH, Rio, Brasília, Campo Grande, Cuiabá, Curitiba.
- 56196 Acumulado de Chuva amarelo, 116 municípios da BA (28 e 29/10), inclui Salvador.
- Sexta 30/10: 56209 amarelo 1.670 (MG 853, SP 410, GO 209…) e 56210 amarelo 945 (PR 399, SC 295, RS 206…). Dois avisos com sobreposição em SP/MS: NÃO somar.

## INPE — focos de 28/10 (inpe_focos_diario_br_20261028.csv)
- O arquivo de 29/10 é parcial (0 focos AQUA): não usado.
- Satélite de referência (AQUA_M-T): 502 focos no Brasil; Pará 257, Roraima 61, Amazonas 55, Ceará 43, Pernambuco 23.
- Municípios PA (ref.): Placas 33, Juruti 30, Uruará 30, Santarém 29, Aveiro 26.
- Conferido: os 502 do AQUA de 28/10 não coincidem com os 502 do TERRA_M-M de 29/10 (0 coordenadas em comum; coincidência de contagem).

## CEMADEN — 24 h até 29/10 ~5h20 (cemaden_getJson2_todas_ufs.json, resumo.json)
- 5.716 estações, 1.192 com leitura recente; 14 com ≥ 50 mm.
- Salvador (BA): Matatu 58,89; Federação 58,35; Engenho Velho de Brotas 58,2; Centro 45,27; Fazenda Coutos 44,0 (vários bairros concordam).
- Colorado do Oeste (RO): 81,6; 70,4; 68,2 mm (3 pluviômetros, todos os da cidade).
- Buriti Bravo (MA): 59,0 (31,2 em 3 h); 49,2; 36,0. Parnarama (MA): 50,0 mm, 50 em 3 h (único).
- Goiânia (GO): Jardim Curitiba 53,6; Vila Jardim Pompeia 42,2.
- Bonito (MS): 50,8; 49,8; 45,2.
- Sensores isolados, FORA das somas e da fala:
  Visconde do Rio Branco "Rio Xopoto" 121,6 (Centro sem leitura desde jul.; vizinhos Senador Firmino 0,2, Guiricema 0,2, Viçosa 1,6; excluído também em 28/10);
  Sertãozinho G2-355170202A 83,2 (4 vizinhos da cidade: 0,4; 0,6; sem leitura).
- Anapu (PA) 71,4 e Comodoro (MT) 65,4: sensor único, sem horária; ficam na soma, não vão à fala.
- Soma dos pluviômetros: 6.180,0 mm·estação; sem os 2 isolados 5.975,4 ("quase 6 mil") em 1.190 pluviômetros.
  BA 1.659,3 ("mais de 1.600"), MA 802,7, GO 676,2, SP 557,8, RO 464,4.

## NOAA METAR (noaa_metar_brasil_24h.json)
- Salvador (SBSV): SPECI 281206Z +RA BR, visibilidade 1.000 m (9h06); 281300Z +RA 2.000 m.
- Calor 28/10: Teresina (SBTE) 38 °C às 16h; Santarém (SBSN) 38 °C às 14h; Itaituba (SBIH) 38 °C às 17h; Boa Vista 37.
- Fumaça: Santarém 3.000 m FU às 9h (281200Z); Manaus (SBEG) 4.000 m FU às 7h local; Itaituba 4.000 m FU.
- Frio: Curitiba (SBCT) 12 °C às 5h (280800Z); Bacacheri 12 °C às 7h.
- Teresina: TSRA com 3.000 m e rajada de 25 kt (46 km/h) às 19h.

## Open-Meteo — previsão 7 dias nas 27 capitais (previsao7d.json, 29/10 a 4/11)
- Soma: 750,7 mm. Por região: SE 236,9 (mais); CO 190,3; S 151,8; N 125,7; NE 46,0.
- Por dia: qui 130,0 · sex 143,3 (mais chuvoso) · sáb 119,8 · dom 72,6 · seg 126,0 · ter 46,8 · qua 112,2.
- Capitais que mais acumulam: Belo Horizonte 107,6; Curitiba 68,1; Brasília 63,8; Goiânia 62,8; São Paulo 60,7.
- Pico de máxima: Teresina 39,9 °C na quarta (4/11); hoje Boa Vista 39,0.
