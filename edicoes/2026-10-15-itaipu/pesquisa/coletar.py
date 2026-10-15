#!/usr/bin/env python3
"""Itaipu (15/10/2026): chuva e vazão na bacia do Paraná acima de Itaipu e do Iguaçu, só Open-Meteo (API gratuita liberada).
  bruto/grade.json    — grade 0,5°: chuva diária de 01/09 a 30/10/2026 (observado até 14/10 + previsão 16 dias) e 01/09–14/10/2024
  bruto/vazao.json    — GloFAS (Open-Meteo Flood): vazão diária do rio Paraná/Iguaçu em pontos-chave, 2024, 2026 + previsão, e máximas da série
uso: python3 coletar.py   (grava em ./bruto)"""
import http.client, json, time, urllib.error, urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
OUT = AQUI / "bruto"; OUT.mkdir(exist_ok=True)


def get(url):
    for tent in range(5):
        try:
            return json.loads(urllib.request.urlopen(url, timeout=180).read())
        except urllib.error.HTTPError as e:
            if e.code not in (429, 502, 503, 504):
                raise SystemExit(f"{e.code} {e.read()[:300]}")
            time.sleep(20 * (tent + 1))
        except (json.JSONDecodeError, http.client.IncompleteRead, TimeoutError):
            time.sleep(20 * (tent + 1))
    raise SystemExit("Open-Meteo recusou 5 vezes")


def lotes(api, pts, extra):
    out = []
    for i in range(0, len(pts), 40):
        lote = pts[i:i + 40]
        d = get(f"{api}?latitude=" + ",".join(f"{p[1]}" for p in lote) + "&longitude=" + ",".join(f"{p[0]}" for p in lote) +
                "&timezone=America%2FSao_Paulo" + extra)
        out += list(zip(lote, d if isinstance(d, list) else [d]))
        time.sleep(8)
    return out


# bacia: oeste/norte do PR, sul de MS, oeste de SP, Paraguai oriental, bacia do Iguaçu (PR/SC)
grade = [(round(-56 + i * .5, 2), round(-27 + j * .5, 2)) for i in range(18) for j in range(17)]
# observado de 2026 do MESMO produto do 2024 (archive), previsão do forecast; junta numa série só (15/10/2026)
o26 = lotes("https://archive-api.open-meteo.com/v1/archive", grade,
            "&daily=precipitation_sum&start_date=2026-09-01&end_date=2026-10-14")
f26 = lotes("https://api.open-meteo.com/v1/forecast", grade,
            "&daily=precipitation_sum&start_date=2026-10-15&end_date=2026-10-30")
g26 = [(p, {"daily": {"time": a["daily"]["time"] + b["daily"]["time"],
                      "precipitation_sum": a["daily"]["precipitation_sum"] + b["daily"]["precipitation_sum"]}})
       for (p, a), (_, b) in zip(o26, f26)]
g24 = lotes("https://archive-api.open-meteo.com/v1/archive", grade,
            "&daily=precipitation_sum&start_date=2024-09-01&end_date=2024-10-14")
pts = []
for ((p, a), (_, b)) in zip(g26, g24):
    pts.append({"p": list(p), "dias": a["daily"]["time"], "chuva": a["daily"]["precipitation_sum"],
                "chuva24": b["daily"]["precipitation_sum"]})
(OUT / "grade.json").write_text(json.dumps({"fonte": "Open-Meteo forecast (best_match; até 14/10 = análise) e archive (ERA5) 2024, lido em 15/10/2026", "pts": pts}))
print("grade", len(pts))

# vazão (GloFAS v4 via Open-Meteo Flood API)
import sys
if "--sem-vazao" in sys.argv: raise SystemExit
PONTOS = {"guaira": ("Rio Paraná em Guaíra (entra no lago)", -54.25, -24.07),
          "jusante": ("Rio Paraná abaixo de Itaipu", -54.60, -25.43),
          "cataratas": ("Rio Iguaçu nas Cataratas", -54.44, -25.69),
          "foz_iguacu": ("Paraná após o Iguaçu (Tríplice Fronteira)", -54.60, -25.62),
          "uniao": ("Rio Iguaçu em União da Vitória", -51.09, -26.23)}
vaz = {}
for k, (nome, x, y) in PONTOS.items():
    base = f"https://flood-api.open-meteo.com/v1/flood?latitude={y}&longitude={x}&daily=river_discharge"
    agora = get(base + "&start_date=2026-08-01&end_date=2026-11-13")
    hist = get(base + "&start_date=1984-01-01&end_date=2026-07-31")
    t, q = hist["daily"]["time"], hist["daily"]["river_discharge"]
    serie = [(a, b) for a, b in zip(t, q) if b is not None]
    top = sorted(serie, key=lambda r: -r[1])
    maxano = {}
    for a, b in serie:
        maxano[a[:4]] = max(maxano.get(a[:4], 0), b)
    vaz[k] = {"nome": nome, "lon": x, "lat": y, "dias": agora["daily"]["time"], "q": agora["daily"]["river_discharge"],
              "q2024": [b for a, b in serie if "2024-08-01" <= a <= "2024-11-13"],
              "max_serie": top[0], "max_ano": maxano,
              "media_out": round(sum(b for a, b in serie if a[5:7] == "10") / max(1, sum(1 for a, b in serie if a[5:7] == "10")))}
    time.sleep(5)
    print(k, "max", top[0], "out média", vaz[k]["media_out"])
(OUT / "vazao.json").write_text(json.dumps({"fonte": "GloFAS v4 (Copernicus) via Open-Meteo Flood API, lido em 15/10/2026 · modelo hidrológico, não é medição da Itaipu", "pontos": vaz}))
