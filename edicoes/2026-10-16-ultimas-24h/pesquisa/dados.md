# Dados dos brutos — 16/10/2026 (janela 15/10 16h58 → 16/10 16h58, horário de Brasília)

Falha da coleta: INMET estações (apitempo sem token, 25× status 204). Temperatura e vento vêm do METAR (NOAA).

## Chuva 24 h — CEMADEN (`resumo.json` → cemaden.top), leituras até 16/10 ~19h50 UTC
- Mauá (SP), Vila Magini: 391,8 mm — **descartado**: as outras duas estações de Mauá marcam 37,5 e 37,7 mm; diz 121,6 mm em 6 h quando os vizinhos marcam ≤ 0,2; acc96 503; nenhuma notícia.
- Visconde do Rio Branco (MG), Rio Xopoto: 275,8 mm (acc96 803,6) — **descartado** (sensor descartado em 13, 14 e 15/10).
- Sem os dois, não há estação ≥ 100 mm. Estações ≥ 50 mm: 28 no resumo (26 sem os dois).
- Angra dos Reis (RJ), Colégio Naval: **92,8 mm** (acc3 29,6 · acc6 55 · acc12 85,4: série coerente; área do aviso laranja do INMET "Baía da Ilha Grande") → dito "92"
- Caeté (MG) 74,2 · Trombudo Central (SC) 66,2 · **Diadema (SP), Centro2: 65,05 mm** → dito "65" (bate com a enxurrada da madrugada no limite SP–Diadema) · Rio de Janeiro, Usina 58,2 · Butantã (SP) 52,55 (CGE na USP: 51)

## Volumes somados — CEMADEN (`soma_por_uf`, mm·estação, NÃO é chuva média)
- Brasil: 21.305,6 mm em 2.011 pluviômetros. Sem os 2 descartados: **20.638,0** → dito "mais de 20.600"
- SP: 7.827,6 (415) → sem Mauá **7.435,8** → dito "mais de 7.400" · MG 5.241,0 → sem Visconde 4.965,2 · RJ 2.330,1 (180) · SC 2.241,0 (194) · PR 1.140,7 (137)
- Ranking sem os descartados: SP, MG, RJ, SC, PR

## Vento e calor — METAR (NOAA)
- Rajada: Campinas/Viracopos (SBKP) 16/10 06Z (03h) G33KT = 61,1 km/h com TSRA → dito "61". Guarulhos (SBGR, a NOAA marca "PR" por erro) 52 · Congonhas 41.
- Máxima: Petrolina (SBPL) 39 °C (16/10 18Z) · Teresina e Imperatriz 38.
- Umidade mínima: Juazeiro do Norte (SBJU) 22% (15/10 20Z) · Petrolina e Rio Branco 24%.
- Mínima: Santo Ângelo (RS) 12 °C.
- Campo Grande (SBCG): TSRA de 15/10 18Z a 21Z, VCTS até 16/10 02Z → temporal de quinta à tarde/noite.

## Fogo — INPE (`inpe_focos_diario_br_20261015.csv`, 15/10 completo)
- Satélite de referência AQUA_M-T: **569 focos** no Brasil; Amazonas **188**, Pará 163, Bahia 63, Roraima 38.
- Pontos no mapa: VIIRS (NPP-375, NPP-375D, NOAA-20, NOAA-21) em grade de 0,08°.

## Avisos INMET (`inmet_avisos_ativos.json`)
- 56091 Tempestade **Perigo (laranja)** 16/10 09h35–23h59: **563** municípios (MG 364, RJ 92, SP 55, ES 52). Riscos: 30–60 mm/h ou 50–100 mm/dia, vento 60–100 km/h, granizo.
- 56090 Tempestade Perigo Potencial (amarelo) 16/10: 2.590 · 56084 Baixa Umidade amarelo 16/10: 830 (NE) · 56083 Ventos Costeiros amarelo 16/10: 64 (SC, RS).
- Amanhã 17/10: 56096 Tempestade **laranja** 370 (MG 245, ES 78, RJ 26, BA 21) · 56095 Ventos Costeiros **laranja** 115 (SC 71, RS 43, PR 1) · 56094 Tempestade amarela 2.343.

## Previsão 7 dias — Open-Meteo (`previsao7d.json`, 27 capitais, 16 a 22/10)
- Soma 7 dias: **788,2 mm** (N 163,5 · NE 48,8 · CO 84,2 · **SE 348,7** · S 143,0)
- Por dia: sex 175,7 · sáb 62,8 · dom 72,8 · seg 62,9 · ter 51,6 · qua 68,7 · **qui 22/10 293,7** (o mais chuvoso; SP, RJ e Curitiba ≥ 30 mm)
- Teresina: pico de cada dia, 38,3 a **40,7 °C** (qui 22/10).
- Capital com mais chuva em 7 dias: São Paulo 129,9 mm · Rio 96,0.

## Satélite
- GOES-19 IR via NASA GIBS: 48 quadros de 15/10 20Z a 16/10 19h30Z (15/10 17h a 16/10 16h30 Brasília). Geocolor de fundo; `mundo.jpg` copiado de 15/10.
