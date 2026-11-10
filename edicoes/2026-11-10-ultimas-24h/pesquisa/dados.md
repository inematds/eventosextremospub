# Dados dos brutos — coleta 10/11/2026 08:30 UTC (janela 09/11 05h30 → 10/11 05h30, horário de Brasília)

Falha: INMET estações (apitempo sem token, 25 pedidos 204). Resto ok.

## CEMADEN (cemaden_getJson2_todas_ufs.json; resumo.json → cemaden)
- Maiores acumulados de 24 h (leituras 10/11 ~08h10 UTC):
  - **Bom Jesus da Lapa (BA)** G2-290390401A **119,4 mm** (102,8 em 12 h); vizinha G2-290390403A 107,2 (confirma).
  - **Simolândia (GO)** G2-522068601A **107,6 mm**; vizinha 96,2 (confirma).
  - Cristino Castro (PI) 93,8; São Pedro da Água Branca (MA) 93,72; Brejo Santo (CE) 83,8 (3 estações, acc24 = acc96).
  - Goiânia: Jardim Curitiba 31,6 mm (o temporal de ~70 mm em 2 h é do g1, não do CEMADEN).
  - **Aquidabã (SE) 954,6 mm: DEFEITO** (34 mm em 6 h, 1,2 em 3 h). Fora do vídeo e tirado da soma.
- 34 estações ≥ 50 mm, 4 ≥ 100 mm (contando Aquidabã).
- Soma dos pluviômetros: soma_mm_estacoes 16.430,7 mm em 1.740 estações; **sem Aquidabã: 15.476,1 mm em 1.739 estações, 27 UFs** ("mais de 15 mil"). É SOMA de leituras, não chuva média.
- Por UF (sem Aquidabã): MG 6.251,0 · BA 2.091,9 · MA 862,8 · ES 849,4 · RJ 811,0.

## INPE focos
- CSV de 9/11 (dia completo): AQUA_M-T (referência) **1.219** focos; **Pará 829**, Amapá 203, Maranhão 86, Tocantins 50, Goiás 15.
- CSV de 10/11 parcial (sem AQUA): não usado.

## NOAA METAR (108 aeroportos, 2.155 observações)
- Máximas 9/11: **41 °C Paulo Afonso (BA)** (18Z = 15h), **39 °C Teresina** (19Z), 38 °C Petrolina.
- Mínima: **9 °C Curitiba** (SBCT, 10/11 03Z = 00h de terça, "na virada da noite"); 10 °C Santa Maria (RS).
- Umidade mínima 16% em Paulo Afonso.
- Rajada máx.: 63 km/h Maringá (PR) 10/11 03Z.

## INMET avisos (inmet_avisos_ativos.json) — só amarelos (Perigo Potencial), nenhum laranja/vermelho
- Hoje 10/11: 56361 Tempestade em **654** municípios — GO 171, PI 165, TO 139, MA 94, PA 37, MT 29, BA 17, CE 1, PE 1; Goiânia (5208707) incluída; 20–30 mm/h ou até 50 mm/dia, 40–60 km/h, granizo.
- 10 a 13/11: 56356 Acumulado de Chuva em **71** municípios da BA (litoral, de Salvador a Teixeira de Freitas: Ilhéus, Itabuna, Porto Seguro...).
- Hoje: 56360 Chuvas Intensas em 29 (AM 24, RR 5).
- Amanhã 11/11: 56362 Tempestade em 252 (GO 178, MT 44, MS 27, TO 3), Goiânia incluída.

## Open-Meteo 7 dias (previsao7d.json, 27 capitais, ter 10/11 a seg 16/11)
- Soma 7 dias: **873,0 mm**. Por região: **CO 283,6** · N 209,9 · NE 187,4 · SE 131,1 · S 61,0.
- Dia mais chuvoso: **segunda 16/11, 160,8 mm** somados (depois qui 12/11, 145,1).
- Pico de máxima: **Teresina 39,8 °C na sexta 13/11**.
- Capitais que mais acumulam: Brasília 90,0 · Campo Grande 77,9 · Palmas 67,4 · Goiânia 57,9.

## Satélite
- GOES-19 IR via NASA GIBS, 09/11 08:00Z → 10/11 08:00Z (ir_tempos.json, 49 quadros); geocolor; mundo.jpg copiado da edição de 09/11 (Blue Marble, estático).
