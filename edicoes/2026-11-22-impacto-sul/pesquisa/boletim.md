# Impacto Sul · 22/11/2026

Fonte principal: quatro registros publicados hoje. Foram lidas integralmente as transcrições; todos os quadros, do começo ao fim dos quatro vídeos, foram examinados em pranchas. Inventário e recortes em cenas/inventario.json. Original: 576 × 1024; quadros de inspeção: 720 × 1280. Retângulos documentados nas coordenadas originais. Removidos rosto, ícone, data e inscrições por recorte.

## O que aconteceu
- V1, publicado 08h48, 00:00–00:51: supercélula da noite de 21/11 entrou pela região de Porto Xavier, atingiu Santo Cristo e entorno de Santa Rosa, avançando para Três de Maio e São Martinho. Granizo grande, enxurrada, árvores caídas e prejuízos rurais. Não chamar o evento noturno de ocorrência desta noite.
- V2, 09h55, 00:00–00:47: Sertão, norte gaúcho, granizo grande na noite passada; telhados danificados e raios. Distância citada: aproximadamente 40 km de Erechim, sem medição do tamanho das pedras.
- V3, 11h29, 00:00–00:40: interior de Sarandi com residências destelhadas e árvores de grande porte quebradas nas primeiras horas deste domingo. Calor e umidade favorecem instabilidade (00:40–00:51); núcleos sobre o Paraguai (00:51–01:01).
- V4, 19h50, 00:25–00:43: Altônia, noroeste do Paraná, enxurrada nas ruas, casas e empresas atingidas hoje. A transcrição escreve o topônimo como “outônia”; normalizado para Altônia conforme som e referência geográfica. Não há acumulado medido fornecido para a cidade. Os mais de 300 mm / 24 h citados em 00:47–00:54 pertencem a municípios paraguaios: NÃO transferir ao Paraná.

## Previsão e sistema
A atualização mais recente, V4 00:54–01:00, prevê diminuição da chuva na segunda, 23/11, e retorno forte na terça, 24/11. Essa atualização prevalece sobre as referências genéricas dos registros da manhã. Terça é o próximo dia de atenção, sem afirmar horário ou intensidade exata de pico não informados.

Coleta INMET local, inmet_avisos_ativos.json:
- 56477, laranja, até 22/11 23h59: 371 municípios PR, 114 SC e 1 RS. Faixa prevista 30–60 mm/h ou 50–100 mm/dia; rajadas 60–100 km/h; granizo. O gancho usa o limite DIÁRIO de 100 mm previsto nas áreas paranaenses abrangidas, jamais como chuva já medida ou volume ainda a cair nesta noite.
- 56475, amarelo, até 22/11 23h59: 399 PR, 295 SC, 351 RS; até 50 mm/dia, rajadas 40–60 km/h e granizo. Norte do RS nesta noite: possibilidade de chuva, sem volume observado.
- 56476, segunda 23/11: 399 PR e 52 SC; até 50 mm/dia e rajadas 40–60 km/h. Diminuição regional da chuva não elimina avisos localizados.
- 56480, terça 24/11: 399 PR, 295 SC e 401 RS; até 50 mm/dia e rajadas 40–60 km/h. Sustenta a atenção ao retorno da chuva. Contagens únicas por UF, com asserts em gerar_cena.py.

Sem previsão específica de resfriamento na fonte principal: não inventar. Os números dos avisos são previsão para suas áreas, nunca observação em todas as cidades.

## Conferência de montagem
- Voz local: 11 falas, 210 palavras, alinhamento final de 87,059 s após a pausa de 1 segundo antes da pergunta.
- Portão da versão local: 97% de imagem real; 28 entradas de inventário, 20 fortes, todas usadas. Uma fotografia de granizo é repetida em duas fontes e usa o mesmo clipe limpo.
- Teste preventivo do layout --canto: tempos simulados com redução de 20%, duração de 69,647 s; portão aprovado com todas as cenas fortes e 96% de imagem real. Não usa nem cria avatar. O fluxo automático ainda deve validar os tempos reais do avatar.
- Prévias examinadas: abertura, danos paranaenses, granizo gaúcho, Sarandi, mapa, contadores dos três estados, pergunta e CTA. Ajustada a haste do pino gaúcho para que o ponto catarinense fique visível.
- Sincronia revisada: janelas de Altônia reservadas à enxurrada; granizo grande, árvore derrubada e granizo em Sertão reservados à f3; telhado, telhas e árvore partida de Sarandi reservados à f4. A distribuição global das demais cenas ocorre depois dessas reservas. Prévias de 19, 21, 23, 27, 30 e 33 segundos examinadas.
