# Dados dos brutos — 19/10/2026 (janela 18/10 15h20 UTC → 19/10 15h20 UTC)

Arquivos: `pesquisa/bruto/resumo.json`, `cemaden_getJson2_todas_ufs.json`, `inmet_avisos_ativos.json`, `inpe_focos_diario_br_20261018.csv`, `noaa_metar_brasil_24h.json`, `previsao7d.json`. Falha da coleta: INMET estações (apitempo sem token, 25 pedidos 204). Na rodada das 05:30 o GIBS deu timeout; a coleta das 12:20 baixou o IR (sat/web, 18/10 15Z → 19/10 15Z). `sat/web/mundo.jpg` copiado de 2026-10-18.

## CEMADEN (1.054 pluviômetros com leitura recente, de 5.657)
Sensores descartados das somas (já fora em edições anteriores): Visconde do Rio Branco (MG) Rio Xopoto 14,0 mm; Angra dos Reis (RJ) Colégio Naval (U) 8,6 mm.

Citados:
- **Caparaó (MG) G2-311210902A 96,8 mm** em 24 h (outra estação de Caparaó 50,0; Espera Feliz/Pq. Nac. Caparaó 50,2) → dito "noventa e seis".
- **Divino (MG) G2-312200901A 92,2 mm** → dito "noventa e dois".
- Outros (não citados): Serrinha (BA) 92,2; Saúde (BA) 83,6; Tabatinga (AM) 79,0; Coari (AM) 76,6; Nova Friburgo (RJ) Vila Nova 65,5.

Soma dos pluviômetros (mm·estação; NÃO é chuva média):
- MG 2.467,7 (224) − Rio Xopoto 14,0 = **2.453,7** → "mais de 2.400"
- BA 1.719,9 (183) · RJ 1.700,3 − 8,6 = 1.691,7 · AM 757,1 · ES 648,7
- Brasil 9.008,3 − 22,6 = **8.985,7** → "quase 9.000"

## INPE Queimadas — 18/10/2026 (arquivo 20261018, todo de 18/10)
- AQUA_M-T: 222 focos (17/10: 1.226). Maranhão 42, Ceará 38, Pernambuco 31; Pará só 4 no AQUA (6.044 detecções de todos os satélites no PA). Queda grande no satélite de referência sem explicação segura → fogo FORA da fala.

## INMET avisos (coleta 19/10 15h20 UTC)
- **56112 Chuvas Intensas, Perigo Potencial (amarelo)**, 19/10 08:51 → 20/10 23:59, **1.144 municípios em 14 UFs** (BA 382, TO 139, PI 127, MG 114, AM 62, MA 60, MT 59, PA 56, RO 43, GO 40, AC 22, ES 21, RR 10, PE 9). 20–30 mm/h ou até 50 mm/dia, vento 40–60 km/h.
- **56111 Baixa Umidade, amarelo**, 19/10 até 23:59, **296 municípios** (PB 101, CE 68, PE 56, RN 41, AL 16, BA 7, PI 6, SE 1). UR 30–20%.
- **56114 Acumulado de Chuva, Perigo (laranja)**, 20/10, **38 municípios** (BA 23, MG 15). 50–100 mm/dia.
- Futuro: 56118 Tempestade amarelo 22/10 em 2.745 municípios (SP 645, MG 545, RS 497, PR 399, SC 295…) — não citado (fala longa).

## NOAA METAR (107 aeroportos)
- Máxima: **Teresina (SBTE) 38 °C** em 18/10 19Z (16h).
- Mínimas: Passo Fundo 5 °C (19/10 09Z), Santo Ângelo 6, Chapecó 8 — não citados (MetSul tem estações mais frias).
- Rajada máx.: Navegantes e Maringá 54 km/h — fraco, fora.

## Previsão 7 dias (previsao7d.json, Open-Meteo, 27 capitais, 19 a 25/10)
- Soma 7 dias: **674,8 mm** (S 313,1 · SE 118,3 · N 112,3 · NE 87,6 · CO 43,5) → Sul acumula mais.
- Dia mais chuvoso: **domingo 25/10, 229,2 mm somados** (Sul 175,5; Curitiba, Florianópolis e Porto Alegre ≥ 30 mm).
- Curitiba 150,9 mm em 7 dias (maior) → "mais de 150 milímetros".
- Teresina: pico 40,2 °C na quinta 22 e no domingo 25 → "deve passar dos 40 graus".

## Satélite
- GOES-19 infravermelho, NASA GIBS, 18/10 15Z → 19/10 15Z (sat/web/ir*.jpg); geocolor.
