# Dados · 28/11/2026

O instantâneo de `bruto/resumo.json` cobre 27/11 às 08h30 UTC até 28/11 às 08h30 UTC (05h30 BRT). Cada sensor informa as 24 horas anteriores ao horário de sua última leitura. A contagem de focos usa o dia civil em UTC.

| Fonte e bruto | Dado usado | Janela |
|---|---|---|
| CEMADEN · `bruto/cemaden_getJson2_todas_ufs.json` | Porto Vera Cruz (RS), **96,2 mm**, sensor 17072, G2-431507302A | 24 h até 28/11 às 05h10 BRT |
| CEMADEN · mesmo bruto | Ipuã (SP), **82,8 mm**, sensor 19808, G2-352130901A. Outro sensor da cidade registrou 74,0 mm | 24 h até 28/11 às 05h10 BRT |
| CEMADEN · mesmo bruto | Manoel Urbano (AC), **66,4 mm**, sensor 17606, G2-120034401A | 24 h até 28/11 às 05h10 BRT |
| CEMADEN · mesmo bruto | Aparecida de Goiânia (GO), **47,8 mm**, sensor 6763, Vila Brasília | 24 h até 28/11 às 05h30 BRT |
| CEMADEN · mesmo bruto | **7.727,71 mm·estação** somados em **1.318 pluviômetros**. MG 1.577,65, RS 1.305,20 e PR 1.109,42 mm·estação | Soma de `acc24hr` em estações de tipo 1 com valor não negativo e leitura nas seis horas anteriores ao corte. Exibição e narração truncam a soma para 7.727 |
| INPE Queimadas · `bruto/inpe_focos_diario_br_20261127.csv` | **603 focos** no Maranhão, **775** no Pará, **1.908** no Brasil, somente AQUA_M-T | 27/11 UTC. Focos são detecções, e detecções próximas compartilham marcador no mapa |
| INMET · `bruto/inmet_avisos_arquivo_20261127.json` | Aviso **56516**, 1.142 municípios distintos, Chuvas Intensas · Perigo Potencial, polígono do campo `poligono` | Emitido antes da coleta de 27/11 para 28/11 das 00h às 23h59 BRT. Sem instantâneo novo por timeout |
| Open-Meteo · `bruto/openmeteo_capitais_3d.json` | **43,7 mm** em São Paulo no sábado e **23,6 mm** no Rio de Janeiro no domingo | Chuva diária prevista nos pontos das capitais para 28 e 29/11 |
| Open-Meteo · `bruto/previsao7d.json` | **983 mm** somados nas 27 capitais. Maior soma diária na sexta, 04/12 (**232,6 mm**), maior soma regional no Norte (**346,2 mm**) e máxima de **40 °C** em Teresina na segunda, 30/11 | Previsão de 28/11 a 04/12, modelo best_match. A linha do gráfico mostra a média diária das máximas previstas nas capitais |
| NASA GIBS / NOAA GOES-19 · `../sat/web/ir_tempos.json` | 49 horários no bruto, 46 quadros válidos para animação | 27/11 às 05h a 28/11 às 05h BRT. Quadros 23, 39 e 44 vieram integralmente pretos e foram omitidos. Blue Marble é fundo estático reutilizado |
| NOAA · `bruto/noaa_metar_brasil_24h.json` | SPECI SBAN reportou trovoada com chuva forte em Anápolis, GO (`+TSRA`) | 28/11 às 08h07 UTC (05h07 BRT). Contexto instrumental, sem uso no vídeo |

A soma automática CEMADEN de 26.891,1 mm·estação inclui múltiplos tipos de estação, leituras posteriores ao corte e registros anômalos de tipo 5 (14.976,0 mm em Pedro Alexandre e 1.965,8 mm em Aquidabã). A edição recalcula o total e o ranking no recorte de pluviômetros descrito acima. A soma observada é por estação e a previsão soma os pontos das capitais. Nenhuma das duas representa a lâmina de chuva do Brasil.

Falhas da coleta em `bruto/resumo.json`: os avisos ativos do INMET expiraram na coleta e na nova tentativa por IPv4. As 25 requisições horárias de estações do INMET também expiraram. Dados de superfície do CEMADEN e METAR da NOAA foram usados conforme cobertura.
