# Dados dos brutos (coleta 11/11/2026 08:30 UTC; janela 10/11 08:30 → 11/11 08:30 UTC)

Falha da coleta: estações do INMET (apitempo sem token, 204) — sem dados de estação; temperaturas vêm do METAR.

## CEMADEN (cemaden_getJson2_todas_ufs.json; resumo.json → cemaden)
- 5.725 estações, 1.644 com leitura recente; 9 com ≥ 50 mm, nenhuma ≥ 100 mm.
- Araguaína (TO): Setor Maracanã 71,18 mm; São João 64,97; Pedra Alta 51,74; Aeroporto 42,89 → quatro estações confirmam.
- Uruana (GO), Centro: 71,8 mm (38,8 em 6 h). Aparecida de Goiânia (GO): Jardim Monte Sinai 58,6; Prédio da Prefeitura 41,0; Vale do Sol 34,4 (chuva concentrada nas últimas 6 h).
- Jaraguá (GO) 56,6; Israelândia (GO) 48,0 (45,8 em 3 h).
- Abaetetuba (PA), Mutirão 76,6 (61,4 em 12 h); a outra estação da cidade (Francilândia) 17,2 — sem confirmação, fora do vídeo.
- DESCARTADO: Ituporanga (SC), Centro-Prefeitura 99,46 mm — as outras estações da mesma cidade marcaram 1,39 e 0,99 mm; defeito de sensor. Tirado da soma.
- Soma dos pluviômetros (mm·estação, não lâmina): 7.962,4 mm em 1.644 estações / 26 UFs; sem Ituporanga = 7.862,9 mm (1.643 estações) → "quase 8 mil mm". Ranking: MG 1.860,9; BA 1.526,3; TO 645,8; ES 538,1; SC 539,7 → 440,2 sem Ituporanga; GO 464,2.

## NOAA METAR (resumo.json → noaa_metar; 107 aeroportos, 2.110 observações)
- Belém (SBBE) 10/11 17:28Z: rajada de 37 nós = 68,5 km/h (o coletor arredonda para 69; mantido), trovoada com chuva forte (+TSRA), visibilidade 700 m.
- Máximas: 37 °C Paulo Afonso (BA, 18Z) e Boa Vista (RR, 20Z); 36 °C Petrolina, Juazeiro do Norte, Cuiabá.
- Mínimas: 10 °C Curitiba/Afonso Pena (10/11 09Z = 06h); 11 °C Bacacheri; 13 °C Chapecó, Canoas, Barbacena.
- Trovoada em 12 aeroportos (Goiânia, Anápolis, Brasília, Belém, Macapá, Palmas, Porto Velho…).

## INPE focos (inpe_focos_diario_br_20261110.csv, dia completo 10/11; o de 11/11 é parcial e sem AQUA)
- Satélite de referência AQUA_M-T: 333 focos; Ceará 64, Mato Grosso 52, Roraima 44, Maranhão 33, Pará 22.
- Todos os satélites (11/11 resumo): Pará lidera (2.117) — não usado na fala (mistura satélites).

## INMET avisos (inmet_avisos_ativos.json)
- 56369 Tempestade, LARANJA (Perigo), 11/11: 78 cidades (MS 42, MT 19, GO 17); 30–60 mm/h ou 50–100 mm/dia, vento 60–100 km/h, granizo. Campo Grande na lista.
- 56367 Tempestade, amarelo, 11/11: 618 (GO 182, MT 141, SP 119, MS 79, PR 56, MG 18, RO 12, TO 11) — contém as 78 do laranja.
- 56366 Tempestade, amarelo, 11/11: 224 (RS 184, SC 40). Sem sobreposição com 56367 → 842 cidades com aviso de tempestade hoje.
- 56356 Acumulado de chuva, amarelo, 10 a 13/11: 71 cidades do litoral da BA.
- 56365 Ventos costeiros RS/SC até 11/11 09h. 56370 Tempestade amarela para 12/11: 2.574 cidades.

## Open-Meteo (previsao7d.json, 27 capitais, 11 a 17/11)
- Soma 7 dias: 895,9 mm. Por região: N 262,2; CO 258,7; NE 178,2; S 106,0; SE 90,8.
- Dia mais chuvoso: ter 17/11, 202,8 mm somados. Hoje 127,1.
- Pico de calor: Teresina 40,1 °C no sábado 14/11. Top acumulado: Palmas 86,9; Campo Grande 77,0; Goiânia 76,3.
- Hoje (openmeteo_capitais): Goiânia 27,2 mm previstos; Cuiabá 37,4 °C.
