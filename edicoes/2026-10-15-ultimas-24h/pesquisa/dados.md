# Dados dos brutos — 15/10/2026 (janela 14/10 05h30 → 15/10 05h30, horário de Brasília)

Falha da coleta: INMET estações (apitempo sem token, 25× status 204). Temperatura e vento vêm do METAR (NOAA).

## Chuva 24 h — CEMADEN (`resumo.json` → cemaden.top), leituras até 15/10 ~08h UTC
- Novo Gama (GO), Lago Azul: **104,8 mm** (acc6 89,8) — outra estação na cidade, Parque Estrela Dalva VI: 70,0 mm → dito "104"
- Israelândia (GO): 86,2 mm · Catalão (GO): 63,2 mm
- São Paulo (SP), Vila Clementino: **73,04 mm** (Defesa Civil SP também cita 73 mm em 24 h, o maior do estado) → dito "73"
- Altamira do Paraná (PR): 71,2 mm
- Visconde do Rio Branco (MG), Rio Xopoto: 127,6 mm — **descartado** (acc3 8,2 e acc6 11,2 não batem; sensor já descartado em 13 e 14/10).
- Estações ≥ 50 mm: 8; ≥ 100 mm: 2 (1 sem Visconde do Rio Branco).

## Volumes somados — CEMADEN soma_por_uf (mm·estação = soma dos pluviômetros, não lâmina de área)
- SP: **2.111,7 mm** em **370** pluviômetros (média 5,7) · PR 1.838,4 (152) · MG 1.230,2 (330; sem Visconde 1.102,6) · GO 942,8 (43) · RS 506,4 (249)
- Brasil: **7.978,4 mm** em **1.482** pluviômetros com leitura recente. Sem Visconde do Rio Branco: 7.850,8 → dito "mais de 7.800".

## Vento — METAR (NOAA), `noaa_metar_brasil_24h.json`
- São Paulo/Congonhas (SBSP), 14/10 19h35 UTC (16h35 BRT): SPECI 03024G48KT TSRA → **48 nós = 88,9 km/h** → dito "88"
- Uberlândia (SBUL), 15/10 01h05 UTC (14/10 22h05 BRT): 27025G38KT TSRA → **38 nós = 70,4 km/h** → dito "70"
- Araxá (SBAX) 37 nós (68,5) · Campinas (SBKP) 36 nós (66,7)

## Calor e ar seco — METAR (NOAA)
- Teresina (SBTE): **39 °C** 14/10 19h UTC (16h)
- Barra do Garças (SBBW, MT): **39 °C** 14/10 19h UTC
- Juazeiro do Norte (SBJU, CE): umidade mínima **16%** (calculada, 36 °C, 14/10 20h UTC)

## Fogo — INPE (`inpe_focos_diario_br_20261014.csv`, dia 14/10; o arquivo 20261015 é parcial e não tem AQUA)
- Satélite de referência AQUA_M-T: **2.177** focos no Brasil; Pará **1.125**, Maranhão 210, Tocantins 201, Bahia 175.
- Todos os satélites: 41.874 registros (repetidos entre satélites; não usado como número).
- Pontos no mapa = VIIRS (NPP-375, NOAA-20, NOAA-21) em grade de 0,08°.

## Avisos INMET (`inmet_avisos_ativos.json`)
- 56071 Tempestade **Perigo (laranja)** 15/10 00h01–23h59: **2.163** municípios (MG 815, SP 645, GO 246, PR 104, MT 103, RJ 92, ES 78, MS 41, TO 30, BA 8, DF 1); chuva 30–60 mm/h ou 50–100 mm/dia, ventos 60–100 km/h, granizo.
- 56070 Tempestade Perigo Potencial (amarelo) 15/10: 3.600 municípios (inclui os do laranja em parte; não somar).
- 56074 Baixa Umidade Perigo Potencial (amarelo) 15/10 09h–23h59: **501** municípios (BA 249, PI 140, MG 39, CE 34, PE 31); umidade 30% a 20%.
- 56072 Tempestade amarelo 16/10: **2.188** municípios (MG 853, SP 421, GO 246...).
- 56073 Chuvas Intensas amarelo 17 e 18/10: 813 municípios (MG 258, BA 196...).

## Previsão 7 dias — Open-Meteo (`previsao7d.json`, 27 capitais, 15 a 21/10)
- Soma por dia (mm): qui 133,7 · sex 122,8 · sáb 79,2 · dom 52,5 · seg 85,1 · ter 55,5 · qua 85,6 → **614,4 mm** em 7 dias
- Dia mais chuvoso: **hoje, quinta (133,7)**. Região que mais acumula: **Sudeste 199,5** (N 171,9 · CO 112,2 · S 84,9 · NE 45,9)
- Calor: Teresina é o pico em todos os dias; passa de 39 °C em 3 dias (39,6 sex · 39,1 sáb · 39,6 qua).
- Capital que mais acumula: Belo Horizonte 65,0 mm.

## Satélite
- `sat/web/ir00..ir48.jpg`, GOES-19 infravermelho 14/10 08h UTC → 15/10 08h UTC; geocolor de base; `mundo.jpg` copiado da edição de 14/10 (fundo para câmera inclinada).
