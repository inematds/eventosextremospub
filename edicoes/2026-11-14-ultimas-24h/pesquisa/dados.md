# Dados dos brutos (coleta 14/11/2026 21:23 UTC; janela 13/11 21:23 → 14/11 21:23 UTC = 13/11 18h23 → 14/11 18h23 de Brasília)

Falha da coleta: estações do INMET (apitempo sem token, 204) — temperaturas vêm do METAR.

## CEMADEN (cemaden_getJson2_todas_ufs.json; resumo.json → cemaden)
- 5.750 estações, 1.300 com leitura recente; 19 com ≥ 50 mm.
- DESCARTADO: Pedro Alexandre (BA), 13.124,2 mm em 24 h (2.025,8 em 6 h) — o mesmo sensor com defeito dos dias anteriores.
- DESCARTADO: Maragogi (AL), Centro, 134,89 mm — estação isolada (todas as vizinhas de AL com 0 a 1 mm em 24 h; última leitura 16:00) → suspeita.
- DESCARTADO: Visconde do Rio Branco (MG), Rio Xopoto, 123,6 mm em 24 h (79,2 em 12 h; 58 em 6 h). As vizinhas confirmam só a chuva da noite: na tarde, Viçosa S. J. Triunfo 0,2 mm em 6 h, Ubá 2–4, Ervália 4,6, Guiricema 0,2 em 12 h; o IR do GOES-19 não mostra topo frio sobre a cidade das 15Z às 21Z; nenhuma notícia. Na dúvida, de fora (mesmo critério de Maragogi).
- Zona da Mata (chuva da noite de 13→14, vizinhas concordam): **Viçosa São José do Triunfo 70,4**; **Guarani 61,8**; Divino 55,0; Pedra Bonita 51,8; Coimbra 46,8; Viçosa Centro 40,4.
- **Colniza (MT, noroeste): G2-510325402A 112,4; 510325401A 94,6; 510325403A 78,0** (três concordam).
- Grande BH: Sabará Borba Gato 67,57; Santa Luzia Rio das Velhas 67,4 (ambas > 67); Brumadinho 54,62; BH Taquaril 48,94.
- ES: Sooretama G2-320501002A 72,0 (as outras duas de Sooretama 48,8 e 45,4); Jaguaré 60,4; Colatina 56,22; Muniz Freire 53,0.
- Fora: Mangaratiba (RJ) 67,42 (sem leitura de 1 h); Colorado do Oeste (RO) 49.
- Soma dos pluviômetros (mm·estação, não lâmina): 24.466,3 bruto; sem Pedro Alexandre, Maragogi e Visconde do Rio Branco = 11.083,6 mm em 1.297 estações (→ "mais de 11 mil milímetros"). MG sem VRB 5.558,7 = 50,2% (→ "mais da metade em Minas"); ES 1.048,1; BA sem PA 1.157,9; SP 894,2; RJ 667,5.

## NOAA METAR (resumo.json → noaa_metar; 98 aeroportos, 1.995 obs.)
- Rajada: **56 km/h em Lagoa Santa (MG)** (METAR SBLS 132200Z 17019G30KT -TSRA = 13/11 19h, trovoada com chuva); **50 km/h em Londrina (PR)** (SPECI SBLO 141723Z G27KT TSRA = 14/11 14h23, trovoada); Pelotas 48; Brasília 46.
- Máximas: **38 °C Teresina** (14/11 20Z), umidade mínima 29% (mesmo horário); 37 °C Cuiabá; 36 °C Mossoró, Corumbá, Boa Vista.
- Trovoada em 29 aeroportos.

## INPE focos (inpe_focos_diario_br_20261113.csv, dia completo 13/11; o de 14/11 é parcial, AQUA = 0)
- AQUA_M-T (referência): 767 focos em 13/11. Maranhão 247, Ceará 220, Piauí 123 (= 590, 77% → "três em cada quatro").

## INMET avisos (inmet_avisos_ativos.json) — só amarelo (Perigo Potencial), nenhum laranja ou vermelho
- Hoje 14/11 (até 23:59), tempestade: 56404 (988 cidades: MG 341, BA 183, TO 139...) + 56405 (342 cidades: PR 149, RS 94, SC 87, MS 12, das 20h às 23h59) → união 1.330 cidades. + 56406 chuvas intensas AP (3).
- Amanhã 15/11: 56408 tempestade 2.633 cidades (MG 844, SP 645, PR 399, SC 270...); 56409 chuvas intensas 533 (PI 189, TO 122, MA 98). Riscos: 20–30 mm/h ou até 50 mm/dia, vento 40–60 km/h, granizo.

## Previsão Open-Meteo (previsao7d.json, 27 capitais, 14 a 20/11)
- Soma 7 dias: 827,6 mm (→ "mais de 820"). Por região: N 223,9; CO 216,3; SE 198,1; S 101,3; NE 88,0 (→ "Norte e Centro-Oeste devem acumular mais").
- Dia mais chuvoso: segunda 16/11, 165,7 mm somados.
- Acumulado top: Palmas 69,6; BH 62,9; Cuiabá 62,0; São Paulo 60,5.
- Pico de calor: Teresina 39,6 °C na sexta 20/11 (39,3 na quinta) → "perto de 40 graus".
