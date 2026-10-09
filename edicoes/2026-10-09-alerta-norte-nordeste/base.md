# Base de dados conferida: seca, calor e fogo no Norte e Nordeste, 09/10/2026

Gerada em 09/10/2026 (tarde). Fontes públicas liberadas (INMET, INPE/CPTEC, Open-Meteo, NASA GIBS/NOAA) + imprensa citada.
Legenda: OCORRIDO = medido/relatado · PREVISÃO = modelo/aviso para o futuro · ANÁLISE = boletim/especialista.

## Números usados no vídeo

| Número | Tipo | Fonte |
|---|---|---|
| 1.210 municípios de N/NE em alerta de baixa umidade hoje (aviso 56030 amarelo; 474 deles também no laranja 56017) | PREVISÃO (aviso vigente 09/10) | INMET, JSON público `apiprevmet3.inmet.gov.br/avisos/ativos`, lido 09/10 ~16h; `fonte/alertas_nne.json` |
| 474 municípios em laranja, umidade entre 20% e 12% (BA 152, PI 139, CE 49, PB 44, TO 43, PE 38, RN 8, MA 1) | PREVISÃO | INMET aviso 56017, 09/10 09h25 → 10/10 21h |
| 1.316 municípios em amarelo de baixa umidade de 10 a 13/10 | PREVISÃO | INMET aviso 56019 |
| Tempestade (20–30 mm/h, vento 40–60 km/h, granizo) em ~119 municípios de RO (52), AC (22), AM (44), PA (1), todos os dias até 13/10 | PREVISÃO | INMET avisos 56021, 56027, 56011, 56014 |
| 1.731 focos de calor em N/NE no dia 08/10 (satélite de referência AQUA_M-T); BA 524, MA 464, PI 311, AM 138 | OCORRIDO | INPE Programa Queimadas, CSV diário `dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/diario/Brasil/focos_diario_br_20261008.csv`; `fonte/focos/` |
| Pontos de fogo no mapa: detecções VIIRS (NPP/NOAA-20/NOAA-21) de 08/10 agrupadas em grade de 0,08° | OCORRIDO | INPE, mesmo CSV |
| Máxima de 41,7 °C no centro do PI (ponto -41,5/-7,5; 7 dias ≥38 °C, umidade mín. 11%, chuva 0) e 40,6 °C no oeste da BA (-43,5/-13,5, umidade 10%); 16 pontos da grade ≥40 °C; chuva zero em 7 dias | PREVISÃO | Open-Meteo (best_match), lido 09/10, 09 a 15/10; `om/calor7.json` |
| Rio Negro perdeu 5,21 m em setembro em Manaus (24,09 → 18,88 m) | OCORRIDO | Portal do Amazonas, 10/2026, dados do Porto de Manaus/SGB — https://portaldoamazonas.com.br/2026/10/rio-negro-perde-521-metros-em-setembro-durante-a-vazante-de-2026/ |
| SGB: cota de Manaus pode terminar outubro entre 12,31 e 16,50 m; pior cenário 12,92 m, perto do recorde de 12,66 m (04/10/2024) | PREVISÃO | Serviço Geológico do Brasil — https://www.sgb.gov.br/w/seca-se-intensifica-na-regiao-amazonica-e-rio-negro-pode-ficar-abaixo-dos-12-m-em-manaus-am- |
| Amazonas: 6.901 focos em 2026 até 08/10, quase o dobro de 2025; Manaus com IQA 181 em 08/10 (fumaça) | OCORRIDO | Vocativo, 08/10/2026 — https://vocativo.com/2026/10/08/amazonas-dobra-focos-de-queimadas-em-2026-e-manaus-lidera-poluicao-entre-capitais/ |
| El Niño muito forte: NOAA dá ~98% para OND; pico de outubro a dezembro; atraso da estação chuvosa no Norte; Cemaden: seca pode se estender até o fim do ano | ANÁLISE/PREVISÃO | CPTEC/INPE https://clima.cptec.inpe.br/enos · NOAA CPC https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/ensodisc.shtml · Canal Rural https://www.canalrural.com.br/diversos/el-nino-deve-intensificar-calor-seca-e-temporais-na-primavera-de-2026/ · nota técnica Cemaden |
| Salas de monitoramento do NE: OND com temperatura acima e chuva abaixo da média | PREVISÃO | Portal R10/Semarh-PI — https://www.portalr10.com/blogs-e-colunas/179970/primavera-de-2026-deve-ser-marcada-por-calor-intenso-baixa-umidade-e-chuvas-irregulares-no-piaui/ |

## "Pico até dezembro" — como foi dito

Não é aviso do INMET. É leitura dos boletins: El Niño com pico de outubro a dezembro (NOAA), estação chuvosa do Norte atrasada (INMET/Cemaden) e OND quente e seco no Nordeste (salas do NE). Na tela: "PICO ATÉ DEZEMBRO" com essas fontes.

## Ressalvas

- Foco de calor ≠ incêndio: vários focos podem ser o mesmo fogo. A contagem oficial usa só o satélite de referência (AQUA_M-T); os pontos do mapa usam todos os VIIRS só para desenhar.
- Cotas de rio vêm da imprensa e da página do SGB (sem API do SGB/ANA).
- Open-Meteo é modelo, não medição.
