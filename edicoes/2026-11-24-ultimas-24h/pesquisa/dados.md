# Dados auditados · 24/11/2026
Coleta: 08h30 UTC (05h30 BRT). Janela nominal 23/11 08h30–24/11 08h30 UTC. Arquivos íntegros em bruto/. As chuvas são acumulados móveis de cada sensor, encerrados no horário de sua atualização, e não um único intervalo idêntico de todas as estações.

## CEMADEN
Arquivo cemaden_getJson2_todas_ufs.json. Usados apenas tipoestacao=1, valor acc24hr numérico não negativo e atualização nas 6 h anteriores ao fechamento, nunca posterior. Soma recalculada em soma-validada.json: **14.823,77 mm·estação, 1.447 sensores**. SP 5.738,29; MG 4.809,41; RJ 1.525,96 mm·estação. Não é chuva média territorial nem volume em litros. A fala trunca o total para 14.823 e a tela identifica mm·estação.

O resumo bruto geral tem 17.525,6: inclui tipo 5 (Aquidabã, 662) e registros posteriores ao fechamento; não vai ao ar. Maragogi (216,07) está desatualizado desde 23/11 16h50 UTC: excluído. Nenhum desses valores é manchete.

Sensores usados: 7092 Jardim Amazonas/Suzano 89,2 mm, 24/11 07h40 UTC; 19306 Cana Verde 84,6 mm, 08h10 UTC; 18207 Israelândia 58,8 mm, 08h20 UTC; 17359 Rolim de Moura 69 mm, 08h10 UTC. Todos acc24hr; não juntar acc48/72/96.

## INMET
inmet_avisos_ativos.json: 56492 Tempestade/Grande Perigo, 642 códigos únicos, 24/11 00h00–23h59 (horário conforme arquivo). RS 214, SC 139, PR 287, MS 2. Riscos previstos: acima de 100 mm/dia ou 60 mm/h, vento acima de 100 km/h, granizo. 56494 laranja 1.468 e 56490 amarelo 3.476: sobreposição, não somar. Amanhã 56496 amarelo: 2.978 códigos únicos. Baixa Umidade 56481: 589 municípios, até 26/11 00h00, umidade prevista 20–30%. Fontes públicas: https://avisos.inmet.gov.br/ e API apiprevmet.inmet.gov.br, já coletada.

## INPE e NOAA
Somente inpe_focos_diario_br_20261123.csv, dia UTC completo. AQUA_M-T de referência: Brasil 620, PA 233, AM 77, MA 74. Mapa usa pontos NOAA-20/21 agrupados espacialmente; esses pontos não são a contagem do contador AQUA. O arquivo parcial de 24/11 fica fora. Fonte: https://terrabrasilis.dpi.inpe.br/queimadas/portal/
NOAA noaa_metar_brasil_24h.json: SBTE, 40 °C em 23/11 20h UTC (17h BRT), temperatura aeroportuária, sem afirmar recorde ou máxima absoluta da cidade. Fonte: https://aviationweather.gov/

## Open-Meteo
previsao7d.json: 24–30/11, sete dias nas 27 capitais, não estimativa territorial. Soma 1.186,8 mm; fala/tela inteira 1.186, truncada. SE 519,1; N 260,6; CO 222,1; S 142,7; NE 42,3. Quinta 26 maior soma diária: 404,7 mm; hoje 95,9 e amanhã 134,1. Teresina pico previsto 40,7 °C na quinta. Máximas médias diárias: 31,7/31,8/30,5/29,6/29,6/30,3/30,6 °C. Rótulos ter/qua/qui/sex/sáb/dom/seg. As séries regionais e totais são conferidos com tolerância 0,2 mm para arredondamento dos dados. Fonte: https://open-meteo.com/ (best_match, coleta gratuita).

## Satélite e falhas
GOES-19 via NASA GIBS, 23/11 08h UTC a 24/11 08h UTC: ir_tempos.json. Fundo mundial do modelo é textura estática, não imagem meteorológica de ontem; base e IR atuais. Somente transparência nas bordas para não exibir corte do bbox. As estações INMET retornaram HTTP 204 nos 25 pedidos: sem dado observado INMET, substituído por CEMADEN e NOAA. Limite registrado no hub.
