#!/usr/bin/env python3
"""Gera geo.js (window.GEO) com municípios de PR/SC/RS, estados, países vizinhos e rios,
simplificados para caber leve no navegador."""
import csv, json, pathlib

G = pathlib.Path(__file__).resolve().parent.parent / "geo"
OUT = pathlib.Path(__file__).resolve().parent / "geo.js"
BBOX = (-62.0, -36.5, -44.0, -19.5)  # lon_min, lat_min, lon_max, lat_max


def arred(c, nd=3):
    if isinstance(c[0], (int, float)):
        return [round(c[0], nd), round(c[1], nd)]
    out = [arred(x, nd) for x in c]
    if out and isinstance(out[0][0], (int, float)):  # anel: tira pontos repetidos
        lim = [out[0]]
        for p in out[1:]:
            if p != lim[-1]:
                lim.append(p)
        out = lim
    return out


def dentro(geom):
    def pts(c):
        if not c:
            return
        if isinstance(c[0], (int, float)):
            yield c
        else:
            for x in c:
                yield from pts(x)
    for x, y in pts(geom["coordinates"]):
        if BBOX[0] <= x <= BBOX[2] and BBOX[1] <= y <= BBOX[3]:
            return True
    return False


cent = {}
with open(G / "municipios.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        cent[r["codigo_ibge"]] = (float(r["longitude"]), float(r["latitude"]))

mun = []
for uf, cod in (("PR", "41"), ("SC", "42"), ("RS", "43")):
    for ft in json.load(open(G / f"mun{cod}.json"))["features"]:
        i = ft["properties"]["id"]
        mun.append({"type": "Feature", "properties": {"id": i, "nome": ft["properties"]["name"], "uf": uf,
                                                      "c": cent.get(i)},
                    "geometry": {"type": ft["geometry"]["type"], "coordinates": arred(ft["geometry"]["coordinates"])}})

ufs = []
for ft in json.load(open(G / "uf.json"))["features"]:
    if dentro(ft["geometry"]):
        ufs.append({"type": "Feature", "properties": {"uf": ft["properties"]["SIGLA"]},
                    "geometry": {"type": ft["geometry"]["type"], "coordinates": arred(ft["geometry"]["coordinates"], 3)}})

paises = []
for ft in json.load(open(G / "paises.geojson"))["features"]:
    if dentro(ft["geometry"]):
        paises.append({"type": "Feature", "properties": {"nome": ft["properties"]["NAME"]},
                       "geometry": {"type": ft["geometry"]["type"], "coordinates": arred(ft["geometry"]["coordinates"], 3)}})

rios = []
for ft in json.load(open(G / "rios.geojson"))["features"]:
    if ft["geometry"] and dentro(ft["geometry"]):
        rios.append({"type": "Feature", "properties": {"nome": ft["properties"].get("name") or ""},
                     "geometry": {"type": ft["geometry"]["type"], "coordinates": arred(ft["geometry"]["coordinates"], 3)}})

geo = {"mun": {"type": "FeatureCollection", "features": mun},
       "uf": {"type": "FeatureCollection", "features": ufs},
       "paises": {"type": "FeatureCollection", "features": paises},
       "rios": {"type": "FeatureCollection", "features": rios}}
OUT.write_text("window.GEO=" + json.dumps(geo, separators=(",", ":")) + ";")
print(f"mun {len(mun)} uf {len(ufs)} paises {len(paises)} rios {len(rios)} -> {OUT} {OUT.stat().st_size//1024} KB")
print("rios:", sorted({r['properties']['nome'] for r in rios})[:40])
