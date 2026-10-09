#!/usr/bin/env python3
"""Previsão do Open-Meteo (API gratuita) para o Sul:
  prev7.json  — chuva somada e rajada máxima por dia, grade de 0,5° dentro de RS/SC/PR (colunas 3D)
  vento.json  — vento a 10 m hora a hora num dia, grade de 1° (partículas animadas)
uso: coleta/openmeteo.py <pasta-da-edicao> --dia 2026-10-09
O plano grátis limita chamadas por minuto: vai em lotes de 40 pontos com pausa e espera no 429."""
import argparse, json, time, urllib.error, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
API = "https://api.open-meteo.com/v1/forecast"
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


geo = json.loads((REPO / "motor/geo.js").read_text()[len("window.GEO="):-1])
aneis = []
for f in geo["uf"]["features"]:
    if f["properties"]["uf"] in ("RS", "SC", "PR"):
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


grade = [(x / 2, y / 2) for y in range(-67, -44) for x in range(-115, -95) if dentro(x / 2, y / 2)]
res = [{"p": list(p), "dias": r["daily"]["time"], "chuva": r["daily"]["precipitation_sum"], "raj": r["daily"]["wind_gusts_10m_max"]}
       for p, r in lotes(grade, "&daily=precipitation_sum,wind_gusts_10m_max&forecast_days=7")]
(dst / "prev7.json").write_text(json.dumps({"fonte": f"Open-Meteo forecast (best_match), lido {a.dia}", "pts": res}))
soma = sorted(((round(sum(c or 0 for c in r["chuva"])), r["p"]) for r in res), reverse=True)
print(f"prev7: {len(res)} pontos · máx {soma[0]} · >100 mm em {sum(s > 100 for s, _ in soma)}")

vg = [(x, y) for y in range(-35, -20) for x in range(-61, -44)]
vento = [{"p": list(p), "v": r["hourly"]["wind_speed_10m"], "dir": r["hourly"]["wind_direction_10m"]}
         for p, r in lotes(vg, f"&hourly=wind_speed_10m,wind_direction_10m&start_date={a.dia}&end_date={a.dia}&wind_speed_unit=kmh")]
(dst / "vento.json").write_text(json.dumps({"fonte": f"Open-Meteo, vento 10 m horário, {a.dia}", "pts": vento}))
print(f"vento: {len(vento)} pontos · máx {max(max(q['v']) for q in vento)} km/h")
