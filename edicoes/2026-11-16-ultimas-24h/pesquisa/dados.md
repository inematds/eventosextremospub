# Dados auditados — 16/11/2026

Janela: 15/11 08h30 UTC a 16/11 08h30 UTC (05h30 BRT). Coleta: 16/11 08h30 UTC.

## Chuva observada

Fonte de todos os números desta seção: bruto/cemaden_getJson2_todas_ufs.json; horários do feed UTC, tela em BRT. Acumulados móveis: cada sensor tem seu próprio término, próximo do corte.

| Fala | UF / cidade | Estação | Acumulado e janela | Leitura BRT |
|---|---|---|---|---|
| f2 | TO / Paranã | G2-170320803A | 197,6 mm / 24 h | 16/11 05h30 |
| f2 | TO / Paranã | G2-170320801A | 192,2 mm / 24 h (voz: 192, truncado) | 16/11 05h20 |
| f3 | BA / Candiba | CANDIBA | 133 mm / 6 h; 123,6 mm / 3 h | 16/11 05h30 |
| f4 | MG / Matias Cardoso | Alto Bonito | 122 mm / 6 h | 16/11 05h20 |
| f5 | PR / Mallet | G2-411390803A | 101 mm / 24 h | 16/11 05h10 |
| painel | PR / Mallet | G2-411390802A | 79,2 mm / 24 h | 16/11 05h10 |
| f7 | GO / Niquelândia | Belo Horizonte | 68 mm / 12 h | 16/11 05h20 |

## Soma dos pluviômetros

Resumo automático inclui 36.945,2 mm·estação / 2.294 sensores. Uma leitura anômala, Pedro Alexandre-BA, idestacao 8327, informa 5.071,4 mm / 24 h e 43.538 mm / 96 h; é excluída, como na edição anterior. Há também 112 leituras com horário posterior ao corte (somam 1.831,57 mm·estação). Não entram. Recomputação estrita do bruto: leitura > corte−6 h e ≤ corte, acc24hr numérico, sem estação 8327. Total calculado antes de arredondar os subtotais: 30.042,18 mm·estação, em 2.181 sensores de 26 UFs. Tela 30.042 (truncado); voz “mais de 30 mil”. Não é lâmina, média ou total volumétrico sobre o território. Receita e resultado: soma-validada.json e gerar_cena.py.

| UF | Soma mm·estação | Sensores |
|---|---:|---:|
| MG | 7606.09 | 521 |
| SP | 7520.9 | 372 |
| SC | 2728.35 | 160 |
| BA | 2290.89 | 212 |
| TO | 1852.75 | 32 |
| PR | 1348.91 | 97 |
| PE | 1157.89 | 106 |
| MA | 936.58 | 59 |
| RS | 839.4 | 149 |
| GO | 663.8 | 47 |
| RJ | 581.67 | 134 |
| SE | 541.4 | 39 |
| PI | 505.8 | 33 |
| PA | 303.8 | 19 |
| ES | 245.9 | 43 |
| MS | 207.6 | 17 |
| CE | 206.15 | 33 |
| AM | 193.32 | 27 |
| MT | 109.6 | 12 |
| AL | 79.2 | 19 |
| AP | 70.6 | 13 |
| PB | 24.6 | 12 |
| RO | 14.38 | 16 |
| AC | 5.2 | 7 |
| DF | 4.2 | 1 |
| RN | 3.2 | 1 |

## INPE

Arquivo bruto/inpe_focos_diario_br_20261115.csv: 10.914 detecções de todos os satélites. No AQUA_M-T, referência para contagem nacional: 261 focos; PA 196, AM 23, RR 18. Dia 15/11 UTC completo, não o CSV parcial de 16/11. Não somar detecções de todos os satélites como incêndios únicos. Mapa: grade de pontos VIIRS, explicitada na fonte. Sem comparação com o total da edição anterior.

## INMET

bruto/inmet_avisos_ativos.json, selecionado por descrição, severidade e início: 56415 tempestade / perigo potencial, 16/11 00h–23h59, 2.938 geocodes únicos. MG 853, SP 586, BA 417. Risco de chuva 20–30 mm/h ou até 50 mm/dia, vento 40–60 km/h e granizo. Amanhã 17/11: 56418 (1.416 municípios) e 56419 (300), união = 1.703 (13 municípios aparecem nos dois avisos). Aviso costeiro 56420: 32 municípios (RS 22 / SC 10), inicia hoje 09h e termina amanhã 23h59; não vigente às 05h30, por isso a tela diz “a partir de 09h”. Não misturar esse total com tempestade. Horários conforme aviso do INMET.

## Previsão — Open-Meteo

bruto/previsao7d.json (best_match), 27 capitais / 16 a 22/11. Soma semanal 857,1 mm; tela/fala 857 (truncado). Somas das capitais por região: N 220,7; NE 141,3; CO 221,9; SE 141,7; S 131,5 mm. São somas de pontos de previsão; não chuva média da região. Palmas lidera acumulado individual com 91,1 mm. Segunda 16/11 soma 214,8 mm nas capitais, maior valor diário. Teresina: pico de 40,5 °C sábado, 40,4 sexta e 40,1 domingo. Todos os sete dias são previstos, inclusive hoje (previsto_a_partir = 0). Linha do gráfico = média das máximas das 27 capitais, não pico nacional.

| Dia | Soma mm | Máxima média °C | Pico °C / cidade |
|---|---:|---:|---|
| 2026-11-16 | 214.8 | 29.7 | [34.9, 'Boa Vista'] |
| 2026-11-17 | 139.1 | 30.4 | [37.6, 'Teresina'] |
| 2026-11-18 | 106.9 | 30.6 | [38.6, 'Teresina'] |
| 2026-11-19 | 74.0 | 31.1 | [39.0, 'Teresina'] |
| 2026-11-20 | 112.2 | 30.9 | [40.4, 'Teresina'] |
| 2026-11-21 | 110.1 | 31.2 | [40.5, 'Teresina'] |
| 2026-11-22 | 100.0 | 31.2 | [40.1, 'Teresina'] |

## Satélite e falhas

NASA GIBS / NOAA GOES-19: sat/web/ir_tempos.json, 49 instantes entre 15/11 08h e 16/11 08h UTC; 48 quadros válidos; excluído o ir23 (vazio, brilho 0). Filtro ajustado ao dia: brilho médio entre 90 e 145 (os quatro primeiros quadros válidos tinham brilho 128–130). Documentado em gerar_cena.py. Geocolor no bbox [−76,−35,−33,7]. Fundo global mundo.jpg reutilizado do modelo (mesma base geográfica estática).

INMET estações: 25 respostas 204, sem observações. NOAA METAR existe no bruto, mas não sustenta números nesta pauta. Sem novos pedidos de chave ou API. Limitações registradas no hub LIMITES.md.
