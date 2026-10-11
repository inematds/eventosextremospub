# Brasil, últimas 24 h: dados coletados (11/10/2026)

Janela: **10/10/2026 05:30 → 11/10/2026 05:30 (Brasília)** = 08:30Z → 08:30Z. Coleta automática às 05:30 de 11/10.
Script: `coleta/ultimas24h.py` → `pesquisa/bruto/` (resumo.json e brutos). Falha: `inmet_estacoes` (apitempo sem token, 25 pedidos com 204) — sem dado de estação do INMET; usei METAR e CEMADEN.

Legenda: **MEDIDO** = estação ou satélite. **MODELO** = previsão numérica. **AVISO** = alerta oficial (previsão, não medição). Horas em Brasília (UTC−3).

## Números mais fortes

| # | Número | Onde | Fonte · hora | Tipo |
|---|---|---|---|---|
| 1 | **124,69 mm em 24 h** (152,45 mm em 48 h); a 2ª estação da mesma cidade (Bom Jesus) marcou **110,13 mm** | Capitão Leônidas Marques (PR), estação Centro | CEMADEN `cemaden_getJson2_todas_ufs.json`, último dado 11/10 08:30Z | MEDIDO |
| 2 | **82,04 mm em 24 h**, 42,84 mm em 3 h | São Miguel do Iguaçu (PR), estação Centro | CEMADEN, idem | MEDIDO |
| 3 | 26 pluviômetros ≥ 50 mm e 2 ≥ 100 mm em 24 h (1.376 estações com dado recente) | PR lidera (máx. 124,69); MS 79,0; SP 73,8; MG 70,2; RS 68,6 | CEMADEN, resumo.json | MEDIDO |
| 4 | **Umidade de 14 %** (34 °C, orvalho 3 °C) | Brasília (DF) | METAR SBBR 101900Z (16h de 10/10): `SBBR 101900Z 09006KT 060V140 9999 FEW045 34/03 Q1016`; UR calculada (Magnus) = 14,3 % | MEDIDO (UR derivada) |
| 5 | **38 °C** | Manaus (Ponta Pelada, SBMN 101900Z, 16h) e Teresina (SBTE 102000Z, 17h); também Juazeiro do Norte e Boa Vista | NOAA/aviationweather.gov, METAR | MEDIDO |
| 6 | **1.155 focos** pelo satélite de referência (AQUA tarde) em 10/10; **494 no Amazonas** (1º lugar), Bahia 180, Pará 98. Município líder: Autazes (AM) 109 | Brasil | INPE Queimadas, `inpe_focos_diario_br_20261010.csv` (só 10/10; 45.285 linhas de todos os satélites — não somar satélites) | MEDIDO |
| 7 | **1.373 municípios em aviso laranja (Perigo) de tempestade hoje** (SP 645, PR 304, MG 297, RJ 68, MS 54, GO 5); chuva de 30 a 60 mm/h ou 50 a 100 mm/dia, vento de 60 a 100 km/h, granizo | Sudeste, PR, MS, GO | INMET avisos ativos id 56035, 11/10 00:01–23:59 | AVISO |
| 8 | **291 municípios em aviso laranja de baixa umidade hoje** (PI 166, BA 50, GO 21, TO 18, MA 10, MG 10, PE 8, CE 8); umidade entre 20 % e 12 % | Nordeste e Centro | INMET id 56034, 11/10 10:00–22:00 | AVISO |
| 9 | **449 municípios em aviso laranja de tempestade amanhã (feriado 12/10)** (PR 260, SC 137, RS 29, MS 23) | Sul e MS | INMET id 56036, 12/10 00:01–23:59 | AVISO |
| 10 | Teresina **39,1 °C** de máxima hoje (39,4 °C na terça); Goiânia umidade mínima 18 %, Brasília 18 % hoje | capitais | Open-Meteo best_match (`openmeteo_capitais_3d.json`), lido 11/10 08:30Z | MODELO |

## Por região

### Sul
- Chuva (CEMADEN, 24 h): oeste/sudoeste do PR concentra os maiores volumes: Capitão Leônidas Marques 124,69 e 110,13; São Miguel do Iguaçu 82,04; Medianeira 77,2; Santo Antônio do Sudoeste 67,0; Foz do Iguaçu 65,0. RS máx. 68,6 (Porto Mauá); SC máx. 38,6.
- Trovoada em METAR: Curitiba (Afonso Pena e Bacacheri), Cascavel, Foz do Iguaçu, Chapecó, Caxias do Sul. Rajadas modestas: Florianópolis e Curitiba 50 km/h, Chapecó 48 km/h.
- Mínima mais baixa: Pelotas 14 °C (11/10 00Z).

### Sudeste
- Rajada máxima do país: Pirassununga (SP) 57 km/h (10/10 14h). Chuva: Cruzeiro/SP 73,8 mm; Desterro do Melo/MG 70,2; Amparo/SP 63,2; Resende/RJ 59,8.
- Trovoada em METAR: Guarulhos, Congonhas, Campo de Marte, Campinas, Taubaté, Galeão, Santos Dumont, Jacarepaguá.

### Centro-Oeste
- Umidade mínima (METAR): Brasília 14 %; Anápolis 20 %; Goiânia 24 %.
- Itaquiraí (MS) 79,0 mm.

### Norte e Nordeste
- 38 °C em Manaus, Teresina, Juazeiro do Norte (UR 19 %) e Boa Vista; 37 °C em Itaituba e Manaus/Eduardo Gomes.
- Focos (AQUA): Amazonas 494 de 1.155 (Autazes 109, Itacoatiara 42, Manaquiri 35, Manacapuru 32).
- Jupi (PE) 74,23 mm (APAC via CEMADEN). Aquidabã (SE) tipo 5 = mesma estação suspeita de ontem: **não usar**.

## Satélite
- `sat/web/geocolor.jpg` (bbox −76,−35,−33,7) e infravermelho GOES-19 de 10/10 08:00Z a 11/10 (ir_tempos.json), NASA GIBS.
