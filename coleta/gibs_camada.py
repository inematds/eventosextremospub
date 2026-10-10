#!/usr/bin/env python3
"""Baixa uma camada qualquer do NASA GIBS (WMS EPSG:3857) recortada numa bbox.
uso: coleta/gibs_camada.py <saida.png|jpg> --camada GHRSST_L4_MUR_Sea_Surface_Temperature_Anomalies
                           --quando 2026-10-07 --bbox -160,-56,-28,22 [--largura 2400]
O formato sai da extensão da saída (png mantém transparência, ex.: terra sem dado na anomalia do mar)."""
import argparse, math, urllib.request
from pathlib import Path

WMS = "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi"
ap = argparse.ArgumentParser()
ap.add_argument("saida")
ap.add_argument("--camada", required=True)
ap.add_argument("--quando", default="")
ap.add_argument("--bbox", required=True, help="lon_min,lat_min,lon_max,lat_max")
ap.add_argument("--largura", type=int, default=2400)
a = ap.parse_args()
b = [float(v) for v in a.bbox.split(",")]


def merc(lon, lat):
    return lon * 20037508.34 / 180, math.log(math.tan((90 + lat) * math.pi / 360)) * 6378137


x0, y0 = merc(b[0], b[1]); x1, y1 = merc(b[2], b[3])
W = a.largura; H = round(W * (y1 - y0) / (x1 - x0))
saida = Path(a.saida)
fmt = "image/png" if saida.suffix == ".png" else "image/jpeg"
url = (f"{WMS}?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&STYLES=&CRS=EPSG:3857&BBOX={x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f}"
       f"&WIDTH={W}&HEIGHT={H}&FORMAT={fmt}&TRANSPARENT=TRUE&LAYERS={a.camada}" + (f"&TIME={a.quando}" if a.quando else ""))
dados = urllib.request.urlopen(url, timeout=180).read()
if dados[:5] == b"<?xml":
    raise SystemExit(dados.decode()[:400])
saida.parent.mkdir(parents=True, exist_ok=True)
saida.write_bytes(dados)
print(f"{a.camada} {a.quando or '(sem data)'} {W}x{H} -> {saida} ({len(dados)//1024} KB)")
