# Dados da edição de 26/11/2026

Janela da previsão: sexta 27/11 a quinta 03/12. [Open-Meteo, best_match](https://open-meteo.com/en/docs), rodada lida em 26/11. Por data, na ordem 27/11 (sex), 28/11 (sáb), 29/11 (dom), 30/11 (seg), 01/12 (ter), 02/12 (qua), 03/12 (qui):

| Local e medida | Valores diários | Número em destaque |
| --- | --- | --- |
| Sudoeste do Amazonas, ponto −6,0° / −67,5°, chuva (mm) | 13,4 / 8,8 / 18,6 / 29,4 / 29,9 / 30,0 / 25,6 | 155,7 mm no período, maior acumulado da grade nacional. Pico de 30,0 mm na quarta, 02/12. |
| Norte paulista, ponto −21,0° / −48,0°, chuva (mm) | 30,4 / 46,2 / 13,9 / 25,3 / 11,1 / 9,6 / 15,0 | 46,2 mm no sábado, 28/11. Acumulado de 151,5 mm na janela. |
| Cuiabá, chuva (mm) | 22,2 / 13,5 / 14,6 / 5,7 / 3,3 / 13,2 / 9,6 | Chuva prevista todos os dias. Maior volume na sexta, 27/11 (22,2 mm). |
| Teresina, máxima (°C) | 39,4 / 39,2 / 39,7 / 40,2 / 39,6 / 39,0 / 39,6 | Máxima de 40,2 °C na segunda, 30/11. |
| Curitiba, mínima (°C) | 12,8 / 13,9 / 16,4 / 17,1 / 15,9 / 16,0 / 13,7 | Mínima prevista de 12,8 °C na sexta, 27/11. |
| Sul paulista, ponto −24,0° / −48,0°, rajada máxima (km/h) | 41,8 / 31,7 / 37,1 / 42,8 / 32,0 / 44,3 / 67,3 | Rajada de 67,3 km/h na quinta, 03/12, maior valor da grade nacional na janela. |

Arquivos da rodada: `../om/prev15_grade.json` (pontos), `../om/prev15_capitais.json` (capitais) e `../om/prev15_resumo.json` (ranking na chave `semana`). Os valores da grade descrevem pontos, com espaçamento de 1,5°.

**Aviso oficial**. O [INMET](https://apiprevmet3.inmet.gov.br/avisos/ativos) emitiu o aviso 56515 de chuvas intensas, nível Perigo (laranja), para sexta, 27/11, das 09h40 às 23h59. São 233 códigos municipais distintos: 73 no PR, 73 em SC, 87 no RS; a cena usa o polígono oficial. Fonte: `bruto/inmet_avisos_ativos.json`, lista `futuro`, chave `id=56515`. Coleta às 14h de Brasília em 26/11, conforme `bruto/resumo.json`.
