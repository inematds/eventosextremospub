# Dados dos brutos — 18/10/2026 (janela 17/10 08h30 UTC → 18/10 08h30 UTC)

Arquivos: `pesquisa/bruto/resumo.json`, `cemaden_getJson2_todas_ufs.json`, `inmet_avisos_ativos.json`, `inpe_focos_diario_br_20261017.csv`, `noaa_metar_brasil_24h.json`, `previsao7d.json`. Falha da coleta: INMET estações (apitempo sem token, 25 pedidos 204) → sem dado de estação do INMET.

## CEMADEN (1.591 pluviômetros com leitura recente, de 5.649)
Sensores **descartados** (fora das somas e do vídeo):
- Angra dos Reis (RJ) Colégio Naval (U) 88,4 mm — as outras 25 estações de Angra: 0,2 a 21,1 mm; já descartado em 17/10 (214,8).
- Visconde do Rio Branco (MG) Rio Xopoto 81,2 mm (acc1/acc3 sem leitura) — descartado desde 13/10.

Citados:
- Linhares (ES) Centro **75,8 mm** (única estação de Linhares com leitura; bate com o temporal com granizo noticiado) → dito "75".
- Varre-Sai (RJ) G2-330615603A **46,8 mm** (vizinhas 30,8 e 25,6; bate com a notícia) → dito "46".
- Outros (não citados): Aquidabã (SE) 58,0; Conceição de Macabu (RJ) 51,2; Guaraciaba (MG) 49,2; Santa Cruz Cabrália (BA) 48,4.

Soma dos pluviômetros (mm·estação; NÃO é chuva média):
- MG 3.837,9 (468 estações) − Rio Xopoto 81,2 = **3.756,7** (467) → dito "mais de 3.700"
- RJ 1.520,5 (171) − Colégio Naval 88,4 = 1.432,1 · BA 1.366,7 · SP 887,0 · ES 835,1
- Brasil 9.981,8 − 169,6 = **9.812,2** (1.589 pluviômetros) → dito "mais de 9.800"

## INPE Queimadas — 17/10/2026 (arquivo 20261017, todo de 17/10)
- Satélite de referência AQUA_M-T: **1.226 focos** no Brasil (16/10: 1.142, edição de ontem).
- Pará **918** (74,9% → "quase três de cada quatro"); Tocantins 81; Amazonas 78; Mato Grosso 52.
- Municípios (AQUA): São Félix do Xingu 114, Uruará 114, Altamira 74, Aveiro 72 (todos PA).
- Todos os satélites: 21.020 detecções (não usar como "focos").

## INMET avisos ativos (coleta 18/10 08h30 UTC)
- Só 1 aviso: id 56102, **Chuvas Intensas, Perigo Potencial (amarelo)**, 18/10 00:00 → 19/10 23:59, **1.345 municípios em 15 UFs** (BA 376, MG 219, PI 149, TO 139, MT 72, PA 66, MA 65, AM 62, ES 53, RO 52, GO 48, AC 22, PE 11, RR 10, CE 1). Riscos: 20–30 mm/h ou até 50 mm/dia, vento 40–60 km/h.

## NOAA METAR (104 aeroportos)
- Rajada máxima: **Pelotas (SBPK) 33 kt = 61 km/h**, 17/10 15Z, com chuva fraca (ciclone extratropical).
- Mínimas: **Chapecó (SBCH) 8 °C** às 18/10 08Z (05h); Santo Ângelo 9 °C; Curitiba 10 °C.
- Máximas 17/10: Teresina e Itaituba 39 °C.

## Previsão 7 dias (previsao7d.json, Open-Meteo, 27 capitais, 18 a 24/10)
- Soma 7 dias: **546,0 mm** (N 158,9 · SE 122,7 · S 108,2 · NE 87,6 · CO 68,6) → Norte acumula mais.
- Dia mais chuvoso: **sexta 23/10, 160,8 mm somados** (Sul 88,2 nesse dia; Curitiba e Porto Alegre ≥ 30 mm).
- Teresina: pico 40,2 °C na quarta 21 e quinta 22 → "deve passar dos 40 graus".
- Acumulado por capital: Manaus 46,1; Curitiba 42,0; Vitória 41,5; São Paulo 39,6; Porto Alegre 39,3.

## Satélite
- GOES-19 infravermelho, NASA GIBS, 17/10 08Z → 18/10 08Z (sat/web/ir*.jpg); geocolor.
