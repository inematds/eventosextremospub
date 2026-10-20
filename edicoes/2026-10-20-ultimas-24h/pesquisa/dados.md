# Dados dos brutos — 20/10/2026 (janela 19/10 08h30 UTC → 20/10 08h30 UTC)

Arquivos: `pesquisa/bruto/resumo.json`, `cemaden_getJson2_todas_ufs.json`, `inmet_avisos_ativos.json`, `inpe_focos_diario_br_20261019.csv` (19/10 inteiro; o de 20261020 tem só até 05h40 GMT e 0 AQUA), `noaa_metar_brasil_24h.json`, `previsao7d.json`, `geocoding_openmeteo.txt` (coordenadas dos pinos, Open-Meteo geocoding). Falha da coleta: INMET estações (apitempo sem token, 25 pedidos 204). `sat/web/mundo.jpg` copiado de 2026-10-19. IR GOES-19: 49 quadros, 19/10 08Z → 20/10 08Z.

## CEMADEN (784 pluviômetros com leitura recente, de 5.659 — bem menos que os 1.054 de ontem: não comparar somas com a véspera)
Sensores descartados das somas (já fora em edições anteriores): Visconde do Rio Branco (MG) Rio Xopoto 49,6 mm; Angra dos Reis (RJ) Colégio Naval (U) 54,4 mm.

Citados:
- **Tapauá (AM) Manoel Costa 72,42 mm** em 24 h → "setenta e dois".
- **Canutama (AM) Centro 67,28 mm** → "sessenta e sete".
- **Macarani (BA) G2-291970201A 66,0 mm** → "sessenta e seis" (área do aviso laranja de hoje).

Soma dos pluviômetros (mm·estação; NÃO é chuva média):
- MG 898,0 (198) − Rio Xopoto 49,6 = **848,4** (197) → "mais de 840"
- RJ 562,3 − 54,4 = 507,9 · BA 400,9 · AM 393,4 · ES 300,9
- Brasil 3.704,7 − 104,0 = **3.600,7** (782) → "mais de três mil e seiscentos"

## INPE Queimadas — 19/10/2026 (arquivo 20261019, todo de 19/10)
- AQUA_M-T (referência): **1.011 focos**. Pará **465** (46% → "quase metade"), Maranhão 134, Minas 113, Bahia 77, Amapá 56.
- Municípios (AQUA): Portel 68, Uruará 45, Anapu 24, Bagre 23, Moju 22 (todos PA).
- Todos os satélites: 9.678 detecções (PA 3.124). Sem comparação com 18/10 (222 no AQUA, queda sem explicação segura na edição de ontem).

## INMET avisos (coleta 20/10 08h30 UTC)
- **56114 Acumulado de Chuva, Perigo (laranja)**, 20/10 00:01 → 23:59, **38 municípios** (BA 23, MG 15), 50 a 100 mm/dia.
- **56112 Chuvas Intensas, amarelo**, 19/10 08:51 → 20/10 23:59, **1.144 municípios em 14 UFs** (BA 382, TO 139, PI 127, MG 114, AM 62, MA 60, MT 59, PA 56, RO 43, GO 40, AC 22, ES 21, RR 10, PE 9).
- **56117 Tempestade, amarelo**, quarta 21/10 15h → 23:59, **407 municípios** (PR 178, RS 131, SC 87, MS 11), granizo.
- **56118 Tempestade, amarelo**, quinta 22/10, **2.745 municípios em 14 UFs** (SP 645, MG 545, RS 497, PR 399, SC 295, RJ 92, MS 59, AM 54, ES 53, RO 52, MT 25, AC 22, GO 5, RR 2), granizo.
- Outros (não citados): 56115 acumulado amarelo 21/10 (39, BA/MG/ES), 56116 chuvas intensas 21/10 (153, Norte), 56119 tempestade 23/10 (983, Sul), 56120 chuvas intensas 23/10 (43).

## NOAA METAR (107 aeroportos)
- Máxima: **Teresina (SBTE) 38 °C** em 19/10 19Z (segunda, 16h); Juazeiro do Norte 37 °C (19/10 18Z).
- Mínima: Passo Fundo 5 °C (19/10 09Z) — não citada (MetSul tem estações mais frias).

## Previsão 7 dias (previsao7d.json, Open-Meteo, 27 capitais, 20 a 26/10)
- Soma 7 dias: **593,4 mm** (S 195,0 · N 131,1 · SE 123,9 · NE 72,6 · CO 70,8) → Sul acumula mais.
- Dia mais chuvoso: **domingo 25/10, 142,1 mm somados** (S 72,9 · CO 38,7).
- Curitiba **113,5 mm** em 7 dias (maior) → "mais de cento e dez milímetros".
- Calor: pico Cuiabá 40,4 °C (dom 25), Teresina 40,2 (qua 21), 40,3 (qui 22) → "Teresina e Cuiabá devem passar dos quarenta graus".

## Satélite
- GOES-19 infravermelho, NASA GIBS, 19/10 08Z → 20/10 08Z (sat/web/ir*.jpg); geocolor.
