# Dados dos brutos — 22/10/2026 (janela 21/10 08h30 UTC → 22/10 08h30 UTC)

Arquivos: `pesquisa/bruto/resumo.json`, `cemaden_getJson2_todas_ufs.json`, `inmet_avisos_ativos.json`, `inpe_focos_diario_br_20261021.csv` (21/10 inteiro, 00:00–23:50 GMT; o de 20261022 tem só até 06h10 GMT e 0 AQUA), `previsao7d.json`. Falhas da coleta: INMET estações (apitempo sem token, 25 pedidos 204) e NOAA METAR (HTTP 504) — sem máximas/mínimas de aeroporto hoje. `sat/web/mundo.jpg` copiado de 2026-10-21. IR GOES-19: 21/10 08Z → 22/10 08Z.

## CEMADEN (1.484 pluviômetros com leitura recente, de 5.679)
Sensores descartados (isolados, vizinhos secos):
- Mauá (SP) Vila Magini 125,8 mm (vizinhos 1,2–1,4; descartado desde 16/10)
- Videira (SC) Rio das Pedras 105,4 mm (Aeroporto, na mesma cidade, 0,4)
- Salvador (BA) Doron 97,8 mm (Tancredo Neves 0,2; demais sem leitura de chuva)
- Manoel Urbano (AC) G2-120034401A 88,2 mm (vizinha 1,8)
- Visconde do Rio Branco (MG) Rio Xopoto 86,0 mm (descartado desde 13/10)
- Angra dos Reis (RJ) Vila do Abraão 65,28 mm (outras de Angra ≤ 1,6)

Citados:
- **Manfrinópolis (PR) G2-411435101A 38,4 mm** em 24 h, 20,2 na última hora (a 2ª estação: 38,0 / 20,6) → "trinta e oito", "vinte deles em uma hora". Barracão (PR) 33,2.
- **Jaru (RO) G2-110011402A 66,6 mm** (a 2ª estação: 32,8) → "sessenta e seis".
- **Humaitá (AM) São Domingos Sávio 57,22 mm** (São Pedro 45,19) → "cinquenta e sete".
- Não citado: Sena Madureira (AC) 52,8 / 38,6.

Soma dos pluviômetros (mm·estação; NÃO é chuva média):
- PR **1.793,1** (149 estações) → "mais de mil setecentos e noventa" (maior UF)
- SP 1.382,1 − 125,8 = 1.256,3 · AM 679,0 · AC 489,8 − 88,2 = 401,6 · MG 384,0 − 86,0 = 298,0 · SC 372,0 − 105,4 = 266,6
- Brasil 6.692,4 − 568,48 = **6.123,9** (1.478 pluviômetros) → "mais de seis mil e cem"

## INPE Queimadas — 21/10/2026 (arquivo 20261021)
- AQUA_M-T (referência): **1.237 focos**. Maranhão **559**, Bahia 203, Pará 109, Piauí 105, Ceará 100.
- Municípios (AQUA): Lábrea (AM) 23; Barra do Corda, Coroatá, Santa Luzia (MA) 22.
- Todos os satélites: 20.386 detecções. Sem comparação com 20/10 (399 no AQUA): a variação diária do AQUA depende da passagem.

## INMET avisos (coleta 22/10 08h30 UTC)
- **56137 Tempestade, amarelo (Perigo Potencial)**, hoje 22/10 00:00 → 23:59, **2.883 municípios em 15 UFs** (MG 646, SP 645, RS 497, PR 399, SC 295…), granizo, 40–60 km/h, até 50 mm/dia.
- **56131 Baixa Umidade, amarelo**, hoje 22/10 12h–20h, **684 municípios** (PI 218, CE 106, PB 104…), umidade 30% a 20%.
- **56139 Tempestade, laranja (Perigo)**, sexta 23/10, **678 municípios** (PR 342, RS 189, SC 132, MS 14, SP 1): 30–60 mm/h ou 50–100 mm/dia, vento 60–100 km/h, granizo.
- 56132 tempestade amarelo 23/10 (2.812), 56134 24/10 (2.168), 56138 25/10 (1.845), 56120 chuvas intensas 23/10 (43, AC/AM/RO).

## Previsão 7 dias (previsao7d.json, Open-Meteo, 27 capitais, 22 a 28/10)
- Soma 7 dias: **792,0 mm** → "mais de setecentos e noventa" (SE 258,4 · S 169,6 · CO 146,7 · N 144,5 · NE 72,8) → Sudeste acumula mais.
- Dia mais chuvoso: **domingo 25/10, 191,4 mm somados** (SE 85,6 · S 65,8).
- Curitiba **122,7 mm** em 7 dias (maior), Rio de Janeiro 107,1, São Paulo 81,5 → "Curitiba, mais de cento e vinte".
- Calor: Cuiabá pico 40,1 °C (sáb 24) e 40,0 (dom 25); Teresina 39,4–39,9 → "Cuiabá deve chegar aos quarenta graus".

## Satélite
- GOES-19 infravermelho, NASA GIBS, 21/10 08Z → 22/10 08Z (sat/web/ir*.jpg); geocolor.
