# Proposta — "Brasil em 24 horas" (14/10/2026, quarta)

Base: `noticias.md` e `dados.md`. Nenhum balanço de estrago com data confirmada; a edição fica em medição (CEMADEN, METAR/NOAA, INPE), avisos do INMET e previsão Open-Meteo.

Gancho: "112 milímetros no noroeste do Paraná, rajada de 70 km/h em Campo Grande e 39 graus em Teresina."

| cena | fato | número | fonte | tipo |
|---|---|---|---|---|
| f1 abertura | data grande + "O BRASIL EM 24 HORAS" | 112 mm · 70 km/h · 39 °C | CEMADEN, METAR, METAR | medido |
| f2 noroeste/norte do PR | chuva em 24 h | Santa Cruz de Monte Castelo 112; Paranavaí 101; Londrina 76 | CEMADEN | medido |
| f3 MS/SP | tempestade no começo da noite | Campo Grande 70 km/h; Ribeirão Preto 68 | METAR SBCG, SBRP | medido |
| f4 Nordeste | fogo | 1.050 focos no Brasil, 283 na Bahia | INPE (AQUA), 13/10 | medido |
| f5 Norte/NE | calor e ar seco | Teresina 39 °C e 20%; Itaituba 39 °C | METAR | medido |
| f6 hoje | tempestade laranja | 1.342 cidades, MS ao ES; vento até 100 km/h e granizo | INMET 56064 | aviso |
| f7 hoje/amanhã | ar seco laranja + amanhã | 96 cidades BA/MG, umidade até 12%; amanhã amarelo em 2.074 | INMET 56061, 56062 | aviso |
| f8 7 dias | previsão | quinta mais chuvosa (148 mm somados); Sudeste acumula mais (172); Teresina > 39 °C em 5 dias | Open-Meteo | previsão |
| f9 volumes | somados | PR 4.317 mm em 153 pluviômetros; 7 dias: 539 mm nas capitais | CEMADEN, Open-Meteo | medido + previsão |
| f10 | "De que região e de que cidade você é?" | — | — | — |
| f11 | inema.club | — | — | — |

Ordem: Sul (chuva) → Centro-Oeste/SP (vento) → Nordeste (fogo) → Norte/NE (calor) → alertas de hoje e amanhã → previsão → volumes.
Ressalvas: Visconde do Rio Branco (258,6 mm) descartado (sensor isolado, descartado também ontem); rajadas convertidas sem arredondar para cima (70,4 → 70; 68,5 → 68); focos contados pelo AQUA (pontos = VIIRS); a soma dos pluviômetros não é chuva média; 1.342 (laranja) e 2.701 (amarelo) não se somam.
