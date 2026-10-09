#!/usr/bin/env python3
"""Satélite GOES-19 (NOAA) via NASA GIBS, já em Web Mercator (casa com o mapa do motor).
Baixa a base em cor real (GeoColor) e a sequência do infravermelho colorido (topo das nuvens) para o timelapse.
uso: coleta/satelite_gibs.py <pasta-da-edicao> --base 2026-10-08T18:00 --de 2026-10-08T12:00 --ate 2026-10-09T05:00 [--passo 20]
     [--bbox -74.5,-18.6,-34,5.6]   (sem --de/--ate baixa só a base GeoColor)
(horas em UTC; o motor mostra em horário de Brasília)"""
import argparse, concurrent.futures as cf, hashlib, json, math, subprocess, urllib.request
from datetime import datetime, timedelta
from pathlib import Path

WMS = "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi"
BBOX = (-62.0, -36.5, -44.0, -19.5)  # lon/lat padrão (Sul); tem que ser o mesmo sat.bbox da cena

ap = argparse.ArgumentParser()
ap.add_argument("pasta")
ap.add_argument("--base", required=True)
ap.add_argument("--de")
ap.add_argument("--ate")
ap.add_argument("--passo", type=int, default=20, help="minutos")
ap.add_argument("--bbox", help="lon_min,lat_min,lon_max,lat_max")
a = ap.parse_args()
if a.bbox:
    BBOX = tuple(float(v) for v in a.bbox.split(","))


def merc(lon, lat):
    return lon * 20037508.34 / 180, math.log(math.tan((90 + lat) * math.pi / 360)) * 6378137


x0, y0 = merc(BBOX[0], BBOX[1]); x1, y1 = merc(BBOX[2], BBOX[3])
W = 2000; H = round(W * (y1 - y0) / (x1 - x0))


def url(camada, quando):
    return (f"{WMS}?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&STYLES=&CRS=EPSG:3857&BBOX={x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f}"
            f"&WIDTH={W}&HEIGHT={H}&FORMAT=image/jpeg&LAYERS={camada}&TIME={quando}")


sat = Path(a.pasta) / "sat"; bruto = sat / "ir"; web = sat / "web"
for p in (bruto, web):
    p.mkdir(parents=True, exist_ok=True)


def baixa(camada, quando, dst):
    if not dst.exists():
        dst.write_bytes(urllib.request.urlopen(url(camada, quando), timeout=120).read())
    return dst


z = lambda s: datetime.fromisoformat(s).strftime("%Y-%m-%dT%H:%M:00Z")
baixa("GOES-East_ABI_GeoColor", z(a.base), sat / "geocolor.jpg")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", sat / "geocolor.jpg", "-vf", "scale=1800:-1", "-q:v", "3", web / "geocolor.jpg"], check=True)
if not a.de:
    print(f"base GeoColor {a.base} em {web}"); raise SystemExit(0)
tempos = []; t = datetime.fromisoformat(a.de)
while t <= datetime.fromisoformat(a.ate):
    tempos.append(t.strftime("%Y-%m-%dT%H:%M:00Z")); t += timedelta(minutes=a.passo)
with cf.ThreadPoolExecutor(6) as ex:
    arqs = list(ex.map(lambda q: baixa("GOES-East_ABI_Band13_Clean_Infrared", q, bruto / f"{q}.jpg"), tempos))

# o GIBS repete o último quadro quando a hora ainda não existe: tira repetidos seguidos
manter, ult = [], None
for q, f in zip(tempos, arqs):
    h = hashlib.md5(f.read_bytes()).hexdigest()
    if h != ult:
        manter.append(q); ult = h
for i, q in enumerate(manter):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", bruto / f"{q}.jpg", "-vf", "scale=1500:-1", "-q:v", "4", web / f"ir{i:02d}.jpg"], check=True)
(web / "ir_tempos.json").write_text(json.dumps(manter))
print(f"base + {len(manter)} quadros IR ({manter[0]} → {manter[-1]}) em {web}")
