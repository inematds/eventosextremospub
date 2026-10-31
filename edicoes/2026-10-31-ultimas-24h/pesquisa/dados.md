# Dados dos brutos — 31/10/2026 (janela 30/10 08:30 UTC a 31/10 08:30 UTC)

Falha da coleta: estações do INMET (apitempo sem token, 204). Resto ok.

## INMET — avisos (inmet_avisos_ativos.json)
- Hoje 31/10: **56218 Chuvas Intensas amarelo, 1.886 municípios** (MG 841, SP 311, GO 244, MT 141, RJ 92, ES 78…). Risco: 20–30 mm/h ou até 50 mm/dia, vento 40–60 km/h. 8 capitais: Goiânia, BH, Rio, Brasília, Cuiabá, Vitória, Rio Branco, Porto Velho.
- 56226 Baixa Umidade amarelo (30/10 9h a 1/11 21h), 665 municípios no NE (PI 187, PB 127, CE 101, PE 96, RN 73…): umidade de 30% a 20%.
- Domingo 1/11: 56223 Tempestade amarelo, 1.854 municípios (MG 586, SP 472, PR 360, RS 150, SC 121…), com granizo.
- **Segunda 2/11: 56227 Tempestade LARANJA (Perigo), 366 municípios (PR 337, SP 16, MS 13)**: 30–60 mm/h ou 50–100 mm/dia, vento 60–100 km/h, granizo. Nenhuma capital. Mais 56225 amarelo de tempestade em 2.396 municípios (com SP, BH, Rio, Curitiba, Florianópolis, Campo Grande, Porto Alegre).
- Terça 3/11: 56229 Tempestade amarelo, 2.089 municípios.

## INPE — focos de 30/10 (inpe_focos_diario_br_20261030.csv)
- O arquivo de 31/10 é parcial (2.000 linhas, 0 AQUA): não usado.
- Satélite de referência (AQUA_M-T): **919 focos**; **Pará 674** (73%, "sete em cada dez"), Amapá 94, Mato Grosso 34, Tocantins 28, Roraima 21. Amazônia 839 no bioma.
- Ontem (29/10) foram 1.078 no mesmo satélite (edição de 30/10): caiu; não comparar na fala.
- Municípios (AQUA): Almeirim 60, Pacajá 47, Óbidos 43 (todos PA).
- Todos os satélites: 19.263 focos, Pará 10.581.

## CEMADEN — 24 h até 31/10 ~5h50 (cemaden_getJson2_todas_ufs.json, resumo.json)
- 5.722 estações, 1.653 com leitura recente; 23 com ≥ 50 mm.
- **Teresópolis (RJ): Três Córregos 87,65 (28,28 em 6 h)** — a maior marca do país sem o sensor isolado; Campo Limpo 60,6; Serra do Capim 47,23.
- **Manaus (AM): Colônia Antônio Aleixo 66,83; Bairro da União 59,76; Santa Luzia 54,6; Mauazinho 50,72** (4 acima de 50); Igarapé do Quarenta 50,0; Igarapé do Mindu 47,2.
- Acre: Tarauacá 84,2 e 81,4 (2 pluviômetros).
- **Zona da Mata (MG)**: Abre Campo 67,4 e 56,6; Caputira 67,4; Canaã 59,0 e 54,2; Cataguases Taquara Preta 52,71 (32,59 em 6 h), Dico Leite 51,7.
- Ituporanga (SC) 67,72 (1 de 3 pluviômetros com leitura alta; os outros 0,4 e 4,57): fora da fala.
- Nova Canaã do Norte (MT) 87,0: sensor único: fica na soma, fora da fala.
- Sensor isolado, FORA da soma e da fala: Visconde do Rio Branco "Rio Xopoto" 134,0 (Centro sem leitura; vizinhos Guiricema 34,6, Ubá até 39,97, Viçosa até 43,8; excluído também em 28, 29 e 30/10).
- Soma dos pluviômetros: 12.967,0 mm·estação em 1.653; sem o isolado 12.833,0 ("mais de 12 mil e 800") em 1.652.
  MG 6.864,9 → sem o isolado 6.730,9 ("mais de 6.700"); RJ 2.020,1; SC 885,5; AM 800,0; SP 580,5.

## NOAA METAR (noaa_metar_brasil_24h.json)
- Manaus: SBMN 301500Z +TSRA visibilidade 500 m, rajada 19 kt (35 km/h); SBEG 301512Z +TSRA visibilidade 500 m (11h12 em Manaus). Temperatura caiu de 27 para 22 °C.
- 18 aeroportos com trovoada (resumo.json → noaa_metar.trovoada).
- Calor 30/10: Teresina (SBTE) 38 °C às 16h (301900Z); Petrolina (SBPL) 36 °C com umidade de 25% às 16h.
- Frio: Pelotas 13 °C às 5h (fora da fala).

## Open-Meteo — previsão 7 dias nas 27 capitais (previsao7d.json, 31/10 a 6/11)
- Soma: 563,5 mm. Por região: SE 157,7 (mais); S 137,1; CO 125,1; N 104,4; NE 39,2.
- Por dia: sáb 62,3 · dom 71,5 · seg 89,8 · ter 57,3 · **qua 125,3 (mais chuvoso; Sul 90,9; Florianópolis e Porto Alegre ≥ 30)** · qui 81,5 · sex 75,8.
- Capitais que mais acumulam: Vitória 54,3; Florianópolis 54,0; BH 51,2; Porto Alegre 48,9.
- Pico de máxima: Teresina 40,0 °C na quinta (5/11).
