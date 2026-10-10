# eventosextremospub

[![Eventos Extremos](guia/assets/banner-en.jpg)](https://inematds.github.io/eventosextremospub/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

eventosextremospub is a set of scripts that turns a severe-weather alert into a short vertical video (Reels, Shorts, TikTok). It downloads data from public sources: INMET alerts with the list of municipalities, GOES-19 satellite imagery via NASA, and rain and wind forecasts from Open-Meteo. Then it animates everything on a 3D map of Southern Brazil, with narration and word-by-word captions. It is for people who make weather content and want checked numbers, with the source on screen, instead of reposting a website screenshot. It needs a computer with a graphics card, Node with Playwright, Python, ffmpeg and, for the voice, the cardshorts project.

## 📖 User guide

Full guide (landing + step by step): **https://inematds.github.io/eventosextremospub/guia/en/**

## Details

Short 9:16 videos about **extreme weather events** in a "crisis room" style: an animated map with real data (alerts by municipality, satellite, wind, forecast rain), each number appearing the instant it is spoken, narration in Nei's voice and an avatar.

The project has three parts:

1. **News from reliable sources** (`coleta/`, `fontes-clima.md`): INMET (warnings by municipality), NASA GIBS / NOAA GOES-19 (satellite), Open-Meteo (gridded forecast), MetSul, Civil Defense. Every number carries its source and time, and what already happened is kept apart from the forecast.
2. **Animation that holds attention** (`motor/`): deck.gl in headless Chrome, frame by frame, on the GPU (Vulkan, ~0.1 s per frame). Features:
   - municipalities colored by alert level;
   - 3D columns;
   - infrared timelapse of the storms;
   - wind particles;
   - rivers drawn little by little;
   - city pins;
   - counters and word-by-word captions.
3. **Avatar** (to do): HeyGen with the explicavideo data.

## Rules for every video

- Frame 0 already opens full: date **dd/mm/yyyy** and the viral headline with the strongest number that has a source (e.g. "UP TO 300 MM").
- Only numbers with a source, and the source appears on screen.
- The script follows Nei's tone: direct, using the informal "tu", a question to the viewer ("where are you going to go?"), practical preparation and the closing at inema.club.

## Usage (one edition)

```bash
geo/baixar.sh && python3 motor/prep_geo.py                       # geographic base (once)
E=edicoes/2026-10-09-alerta-sul
python3 coleta/inmet_avisos.py $E                                 # alerts by municipality
python3 coleta/satelite_gibs.py $E --base 2026-10-08T18:00 --de 2026-10-08T12:00 --ate 2026-10-09T05:00
python3 coleta/openmeteo.py $E --dia 2026-10-09                   # 7-day rain + wind
# write $E/falas.json (the lines) and $E/base.md (the research)
python3 $E/narrar.py                                              # Nei's voice, checked by transcription
python3 $E/gerar_cena.py                                          # timeline → cena.js
node motor/render.mjs $E --quadros 0,10,30                        # frame preview
motor/montar.sh $E $E/video.mp4                                   # final video
```

The voice uses the [cardshorts](https://github.com/inematds/cardshorts) engine (local Chatterbox + Whisper).

## Editions

| Date | Edition | What it shows |
|---|---|---|
| Oct 9, 2026 | `edicoes/2026-10-09-alerta-sul` | 529 cities in red (INMET), 109 km/h gust, 113 mm in São Borja, weekend map, up to 204 mm in 7 days (Open-Meteo) |
| Oct 9, 2026 | `edicoes/2026-10-09-alerta-norte-nordeste` (dynamic voice; `GEO=geo-nne.js`) | 1,210 cities under dry-air alert (474 orange, down to 12%), up to 41.7 °C in Piauí (Open-Meteo), 1,731 fire hotspots in one day (INPE), Rio Negro −5.21 m, storms in AC/RO/AM, peak through December (El Niño), comment prompt |
| Oct 9, 2026 | `edicoes/2026-10-09-el-nino` (explainer for lay viewers; `GEO=geo-br.js`, states only; NASA warm-sea map) | El Niño "is no joke": 83% chance of the strongest since 1950 (NOAA), sea near Peru +5.3 °C, drought in the North/Northeast and rain in the South (Painel El Niño no. 4), peak by December, what to do (text your ZIP code to 40199) | NOAA/CPC, NASA GIBS (GHRSST MUR), Painel El Niño (INMET, INPE, ANA, Cemaden, SGB, Sedec, Censipam) |

MIT License. Third-party data follows the licenses of the sources (INMET, NASA/NOAA, Open-Meteo, IBGE, Natural Earth).
