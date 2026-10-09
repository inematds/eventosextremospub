#!/usr/bin/env python3
"""Previsão do Open-Meteo (API gratuita) para seca e calor no Norte e Nordeste:
  calor7.json — máxima, umidade mínima e chuva por dia, grade de 1° dentro dos estados de N/NE (colunas 3D)
uso: coleta/openmeteo_calor.py <pasta-da-edicao> --dia 2026-10-09
Precisa de motor/geo-nne.js (motor/prep_geo.py --regiao nne). Lotes de 40 pontos com pausa e espera no 429."""
import argparse, json, time, urllib.error, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
API = "https://api.open-meteo.com/v1/forecast"
UFS = ("RO", "AC", "AM", "RR", "PA", "AP", "TO", "MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA")
ap = argparse.ArgumentParser()
ap.add_argument("pasta")
ap.add_argument("--dia", required=True)
a = ap.parse_args()
dst = Path(a.pasta) / "om"; dst.mkdir(parents=True, exist_ok=True)


def lotes(pts, extra):
    out = []
    for i in range(0, len(pts), 40):
        lote = pts[i:i + 40]
        url = (f"{API}?latitude=" + ",".join(str(p[1]) for p in lote) + "&longitude=" + ",".join(str(p[0]) for p in lote) +
               "&timezone=America%2FSao_Paulo" + extra)
        for tent in range(5):
            try:
                d = json.loads(urllib.request.urlopen(url, timeout=120).read()); break
            except urllib.error.HTTPError as e:
                if e.code != 429:
                    raise
                time.sleep(20 * (tent + 1))
        else:
            raise SystemExit("Open-Meteo recusou 5 vezes (429)")
        out += list(zip(lote, d if isinstance(d, list) else [d]))
        time.sleep(8)
    return out


geo = json.loads((REPO / "motor/geo-nne.js").read_text()[len("window.GEO="):-1])
aneis = []
for f in geo["uf"]["features"]:
    if f["properties"]["uf"] in UFS:
        g = f["geometry"]
        for p in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]):
            aneis.append(p[0])


def dentro(x, y):
    for r in aneis:
        c, j = False, len(r) - 1
        for i in range(len(r)):
            (xi, yi), (xj, yj) = r[i], r[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                c = not c
            j = i
        if c:
            return True
    return False


grade = [(x + .5, y + .5) for y in range(-19, 6) for x in range(-74, -34) if dentro(x + .5, y + .5)]
res = [{"p": list(p), "dias": r["daily"]["time"], "tmax": r["daily"]["temperature_2m_max"],
        "urmin": r["daily"]["relative_humidity_2m_min"], "chuva": r["daily"]["precipitation_sum"]}
       for p, r in lotes(grade, "&daily=temperature_2m_max,relative_humidity_2m_min,precipitation_sum&forecast_days=7")]
(dst / "calor7.json").write_text(json.dumps({"fonte": f"Open-Meteo forecast (best_match), lido {a.dia}", "pts": res}))
tm = max(res, key=lambda r: max(t or 0 for t in r["tmax"]))
print(f"calor7: {len(res)} pontos · máx {max(tm['tmax'])} °C em {tm['p']} · "
      f"≥40 °C em {sum(max(t or 0 for t in r['tmax']) >= 40 for r in res)} · UR ≤15% em {sum(min(u or 100 for u in r['urmin']) <= 15 for r in res)}")
