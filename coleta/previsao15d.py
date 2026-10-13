#!/usr/bin/env python3
"""Previsão de 16 dias do Open-Meteo (API gratuita liberada) para a edição de domingo "Clima da semana + 15 dias".
  om/prev15_grade.json  — grade de 1,5° dentro do Brasil: chuva, máxima, mínima e rajada por dia (mapa / colunas)
  om/prev15_capitais.json — as 27 capitais, dia a dia
  om/prev15_resumo.json — o que vira manchete: semana 1 (dias 1–7) e tendência (dias 8–15), por ponto e por UF
uso: coleta/previsao15d.py <pasta-da-edicao> --dia 2026-10-11
Dias 8–15 são TENDÊNCIA (o modelo erra mais longe): o roteiro tem de dizer isso."""
import argparse, ast, http.client, json, re, time, urllib.error, urllib.request
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
API = "https://api.open-meteo.com/v1/forecast"
VARS = "precipitation_sum,temperature_2m_max,temperature_2m_min,wind_gusts_10m_max"
ap = argparse.ArgumentParser()
ap.add_argument("pasta")
ap.add_argument("--dia", required=True)
a = ap.parse_args()
dst = Path(a.pasta) / "om"; dst.mkdir(parents=True, exist_ok=True)
d0 = date.fromisoformat(a.dia) + timedelta(days=1)  # a semana começa na segunda (o vídeo sai no domingo)
d1 = d0 + timedelta(days=14)


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
                if e.code not in (429, 502, 503, 504):
                    raise
                time.sleep(20 * (tent + 1))
            except (json.JSONDecodeError, http.client.IncompleteRead, TimeoutError):  # resposta cortada (13/10/2026)
                time.sleep(20 * (tent + 1))
        else:
            raise SystemExit("Open-Meteo recusou ou cortou a resposta 5 vezes")
        out += list(zip(lote, d if isinstance(d, list) else [d]))
        time.sleep(8)
    return out


# UF de cada ponto da grade pelos polígonos do geo-br.js
geo = json.loads((REPO / "motor/geo-br.js").read_text().strip()[len("window.GEO="):].rstrip(";"))
aneis = []
for f in geo["uf"]["features"]:
    g = f["geometry"]
    for p in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]):
        aneis.append((f["properties"]["uf"], p[0]))


def uf_de(x, y):
    for uf, r in aneis:
        c, j = False, len(r) - 1
        for i in range(len(r)):
            (xi, yi), (xj, yj) = r[i], r[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                c = not c
            j = i
        if c:
            return uf
    return None


extra = f"&daily={VARS}&start_date={d0}&end_date={d1}"
grade = [(x * 1.5, y * 1.5, uf) for y in range(-23, 4) for x in range(-49, -23) if (uf := uf_de(x * 1.5, y * 1.5))]
pts = []
UF = {(x, y): uf for x, y, uf in grade}
for (x, y), r in lotes(list(UF), extra):
    dd = r["daily"]
    pts.append({"p": [x, y], "uf": UF[(x, y)], "dias": dd["time"],
                "chuva": dd["precipitation_sum"], "tmax": dd["temperature_2m_max"], "tmin": dd["temperature_2m_min"],
                "raj": dd["wind_gusts_10m_max"]})
fonte = f"Open-Meteo forecast (best_match), 16 dias, lido em {a.dia}"
(dst / "prev15_grade.json").write_text(json.dumps({"fonte": fonte, "pts": pts}))

src = (REPO / "coleta/ultimas24h.py").read_text()
CAP = ast.literal_eval(re.search(r"^CAP = (\{.*?\})\n", src, re.S | re.M).group(1))
caps = []
for (lon, lat), r in lotes([(v[2], v[1]) for v in CAP.values()], extra):
    n = next(k for k, v in CAP.items() if (v[2], v[1]) == (lon, lat))
    dd = r["daily"]
    caps.append({"cap": n, "uf": CAP[n][0], "dias": dd["time"], "chuva": dd["precipitation_sum"], "tmax": dd["temperature_2m_max"],
                 "tmin": dd["temperature_2m_min"], "raj": dd["wind_gusts_10m_max"]})
(dst / "prev15_capitais.json").write_text(json.dumps({"fonte": fonte, "capitais": caps}, ensure_ascii=False))


def janela(serie, a_, b_):
    v = [s for s in serie[a_:b_] if s is not None]
    return v


def resumo(rows, nome):
    out = {}
    for rot, (a_, b_) in {"semana": (0, 7), "tendencia_8a15": (7, 15)}.items():
        top = lambda k, f: sorted(((round(f(janela(r[k], a_, b_)), 1), r[nome], r["uf"], r.get("p")) for r in rows
                                   if janela(r[k], a_, b_)), key=lambda t: t[0], reverse=k != "tmin")[:8]
        uf = defaultdict(lambda: {"chuva_max": 0, "tmax": -99, "tmin": 99, "raj": 0})
        for r in rows:
            c, tx, tn, rj = (janela(r[k], a_, b_) for k in ("chuva", "tmax", "tmin", "raj"))
            u = uf[r["uf"]]
            if c: u["chuva_max"] = max(u["chuva_max"], round(sum(c)))
            if tx: u["tmax"] = max(u["tmax"], max(tx))
            if tn: u["tmin"] = min(u["tmin"], min(tn))
            if rj: u["raj"] = max(u["raj"], max(rj))
        out[rot] = {"dias": f"{rows[0]['dias'][a_]} a {rows[0]['dias'][b_ - 1]}",
                    "chuva_acumulada_top": top("chuva", sum), "calor_top": top("tmax", max),
                    "frio_top": top("tmin", min), "rajada_top": top("raj", max), "por_uf": dict(sorted(uf.items()))}
    return out


pts_n = [{**p, "lugar": f"{p['p'][1]:.1f},{p['p'][0]:.1f}"} for p in pts]
R = {"fonte": fonte, "inicio": str(d0), "fim": str(d1), "aviso": "dias 8 a 15 = tendência, incerteza maior",
     "grade": resumo(pts_n, "lugar"), "capitais": resumo(caps, "cap")}
(dst / "prev15_resumo.json").write_text(json.dumps(R, ensure_ascii=False, indent=1))
s = R["grade"]["semana"]
print(f"grade {len(pts)} pts · capitais {len(caps)} · semana {s['dias']}: chuva máx {s['chuva_acumulada_top'][0][:3]} · "
      f"calor {s['calor_top'][0][:3]} · rajada {s['rajada_top'][0][:3]}")
