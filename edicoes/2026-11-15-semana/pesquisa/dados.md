# Dados auditáveis — lidos em 15/11/2026

Fonte: Open-Meteo forecast best_match, API gratuita https://api.open-meteo.com/v1/forecast . Brutos: om/prev15_grade.json e om/prev15_capitais.json; síntese om/prev15_resumo.json. Coletor: ../../coleta/previsao15d.py. Variáveis precipitation_sum (mm), temperature_2m_max/min (°C), wind_gusts_10m_max (km/h); timezone America/Sao_Paulo. Semana índices [0:7] = 16–22/11; tendência [7:15] = 23–30/11. Não arredondar para cima.

| Trecho | Local / coordenadas lon,lat | Valor exato | Janela / campo |
|---|---|---|---|
| f2 | PR [-54, -25.5] | 156.5 | chuva, 16–22/11 |
| f3 | MG [-43.5, -15] | 154.2 | chuva, 16–22/11 |
| f4 | GO [-48, -13.5] | 62.2 | chuva, 2026-11-17 |
| f5 | PI [-42, -4.5] | 40.5 | tmax, 2026-11-19 |
| f6 | TO [-46.5, -12] | 138.8 | chuva, 16–22/11 |
| f7 | SP [-49.5, -21] | 65.2 | raj, 2026-11-20 |
| f7 | RS [-51, -28.5] | 12.8 | tmin, 2026-11-22 |
| f9 | Vitória, ES | 254.1 mm | chuva 23–30/11, tendência |

Complementos na tela: PR 77,7 mm em 18/11 (quarta); GO 149,5 mm em 16–22/11; MT 141,1 mm em 16–22/11 (ponto -51,-13.5). Tendência AM: 212,7 mm na grade (-60,-3); PI 41,8 °C na grade (-42,-6). Esses dois valores sustentam a direção qualitativa da f10, sem prometer certeza.

INMET: pesquisa/bruto/inmet_avisos_ativos.json → futuro → id 56415; geocodes separados por vírgula = 2.938 e conjunto = 2.938; descrição Tempestade; severidade Perigo Potencial; validade 16/11/2026 00:00–23:59. Aviso emitido/disponível na coleta de domingo para segunda. f1/f8 e hero. https://alertas2.inmet.gov.br/ .

A síntese por_uf usa chuva_max com arredondamento inteiro do coletor. Apenas classes de cor no mapa; contadores usam soma decimal exata da grade. Nenhum volume é média de UF nem total nacional de chuva.
