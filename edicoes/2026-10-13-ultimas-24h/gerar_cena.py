#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 13/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos pluviômetros do CEMADEN, do METAR (NOAA), dos focos do INPE e dos avisos do INMET (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "13/10/2026"
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())
B = AQUI / "pesquisa/bruto"


def n(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


def roteiro(t, texto):
    """troca as palavras ouvidas pelo Whisper pelas do roteiro (campo legenda ou fala), mantendo os tempos."""
    tok, W = texto.split(), t["palavras"]
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [n(x) for x in tok], [n(p["w"]) for p in W], autojunk=False).get_opcodes():
        if op == "equal":
            out += [{"w": tok[i1 + k], "t": W[j1 + k]["t"], "f": W[j1 + k]["f"]} for k in range(i2 - i1)]
        elif i2 > i1:
            a = W[j1]["t"] if j2 > j1 else (W[j1 - 1]["f"] if j1 else t["ini"])
            b = W[j2 - 1]["f"] if j2 > j1 else (W[j1]["t"] if j1 < len(W) else a + .3)
            d = (b - a) / (i2 - i1)
            out += [{"w": tok[i1 + k], "t": round(a + k * d, 3), "f": round(a + (k + 1) * d, 3)} for k in range(i2 - i1)]
    return out


ROT = {f["id"]: f.get("legenda") or f["fala"] for f in json.loads((AQUI / "falas.json").read_text())}
for t in T:
    t["palavras"] = roteiro(t, ROT[t["id"]])
FALA = {t["id"]: t for t in T}


def em(fid, palavra, k=1):
    achou = 0
    for p in FALA[fid]["palavras"]:
        if n(palavra) in n(p["w"]):
            achou += 1
            if achou == k:
                return p["t"]
    raise KeyError(f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in FALA[fid]["palavras"]))


ini = lambda fid: FALA[fid]["ini"]
fim = lambda fid: FALA[fid]["fim"]
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
LAR, AMA, VERM = [255, 140, 26], [250, 204, 21], [255, 42, 31]

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
OPR = {"lon": -54.0, "lat": -25.25, "zoom": 7.5}     # oeste do PR: Foz, Medianeira, Cascavel
PRU = {"lon": -51.4, "lat": -22.3, "zoom": 6.6}     # Presidente Prudente
PA = {"lon": -53.5, "lat": -6.5, "zoom": 5.0}       # Pará (fogo)
NOR = {"lon": -47.5, "lat": -6.0, "zoom": 4.75}     # Itaituba, Teresina, Juazeiro do Norte
SUL = {"lon": -51.2, "lat": -26.4, "zoom": 5.3}     # alerta laranja de hoje (PR, SC)
BRL = {"lon": -49.5, "lat": -16.0, "zoom": 4.65}     # amanhã: PR ao RJ + ar seco no Nordeste
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, OPR, 40, -10), K(fim("f2") - .2, {**OPR, "lon": -53.95}, 45, 8),
    K(ini("f3") + 1.0, PRU, 40, -8), K(fim("f3") - .2, {**PRU, "lon": -51.2}, 45, 4),
    K(ini("f4") + 1.0, PA, 6, -2), K(fim("f4") - .2, {**PA, "lon": -53.2}, 8, 2),
    K(ini("f5") + 1.0, NOR, 15, -3), K(fim("f5") - .2, {**NOR, "lon": -47.3}, 18, 3),
    K(ini("f6") + 1.0, SUL, 25, 0), K(fim("f6") - .2, {**SUL, "zoom": 5.2}, 25, 2),
    K(ini("f7") + 1.0, BRL, 6, -2), K(fim("f7") - .2, {**BRL, "zoom": 4.6}, 6, 2),
    K(ini("f8") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


SAT = {"base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- focos de 12/10 (INPE: pontos VIIRS em grade de 0,08°; conta pelo AQUA)
grade, ref, ref_pa = {}, 0, 0
with open(B / "inpe_focos_diario_br_20261012.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            ref_pa += r["estado"].strip().upper() == "PARÁ"
assert (ref, ref_pa) == (1401, 1064), (ref, ref_pa)
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f4"), "fim": ini("f5") + .3, "dados": fogo, "dur": 3.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
HOJE = ufs_av(56048)     # tempestade laranja 13/10: 591 (PR 319, SC 213, RS 44, SP 12, MS 3)
AMANHA = ufs_av(56049)   # tempestade laranja 14/10: 687 (PR 325, SP 285, MG 41, MS 31, RJ 5)
SECO = ufs_av(56051)     # baixa umidade amarela 13/10 09h → 14/10: 1.012 (PI 216, BA 183, CE 143, MG 140...)
assert (len(geo(56048)), len(geo(56049)), len(geo(56051))) == (591, 687, 1012), (len(geo(56048)), len(geo(56049)), len(geo(56051)))
assert (sum(c[:2] == "41" for c in geo(56048)), sum(c[:2] == "42" for c in geo(56048))) == (319, 213)
assert all(aviso[i]["severidade"] == "Perigo" and aviso[i]["descricao"] == "Tempestade" for i in (56048, 56049))
assert aviso[56051]["descricao"] == "Baixa Umidade" and aviso[56051]["severidade"] == "Perigo Potencial"
estados = [
    {"id": "hoje", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": HOJE, "cor": LAR, "alfa": .55},
    {"id": "amanha", "ini": ini("f7"), "fim": em("f7", "1.012") + .3, "ufs": AMANHA, "cor": LAR, "alfa": .55},
    {"id": "seco", "ini": em("f7", "1.012"), "fim": ini("f8") + .3, "ufs": SECO, "cor": AMA, "alfa": .45},
]

pinos = [
    {"nome": "Foz do Iguaçu", "sub": "104 mm em 24 h", "lon": -54.58, "lat": -25.52, "ini": em("f2", "Foz"), "fim": ini("f3"), "h": 200},
    {"nome": "Cascavel", "sub": "91 mm", "lon": -53.46, "lat": -24.96, "ini": em("f2", "Cascavel"), "fim": ini("f3"), "h": 120},
    {"nome": "Presidente Prudente", "sub": "rajada de 77 km/h", "lon": -51.39, "lat": -22.12, "ini": em("f3", "Prudente"), "fim": ini("f4"), "h": 180},
    {"nome": "Pará", "sub": "1.064 focos em 1 dia", "lon": -52.2, "lat": -3.8, "ini": em("f4", "Brasil"), "fim": ini("f5"), "h": 160},
    {"nome": "Itaituba", "sub": "39 °C", "lon": -55.98, "lat": -4.28, "ini": em("f5", "Itaituba"), "fim": ini("f6"), "h": 170},
    {"nome": "Teresina", "sub": "39 °C", "lon": -42.8, "lat": -5.09, "ini": em("f5", "Teresina"), "fim": ini("f6"), "h": 170},
    {"nome": "Juazeiro do Norte", "sub": "umidade 16%", "lon": -39.32, "lat": -7.21, "ini": em("f5", "Juazeiro"), "fim": ini("f6"), "h": 140},
    {"nome": "Curitiba", "sub": "até 54 mm hoje (previsão)", "lon": -49.27, "lat": -25.43, "ini": em("f6", "Curitiba"), "fim": ini("f7"), "h": 170},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌧️ 104 mm · 💨 77 km/h · 🔥 1.064 focos</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "OESTE DO PARANÁ · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 104, "dec": 0, "ini": em("f2", "104"), "dur": 1.4, "cor": "#5ec8ff", "unid": "MM"},
     "l": "em Foz do Iguaçu · Cascavel 91 mm · Medianeira 100 mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "PRESIDENTE PRUDENTE (SP) · MADRUGADA",
     "contador": {"de": 0, "ate": 77, "dec": 0, "ini": em("f3", "77"), "dur": 1.2, "cor": "#5ec8ff", "unid": "KM/H"},
     "l": "rajada com tempestade forte, 1h desta terça", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "FOGO · SEGUNDA, 12/10",
     "contador": {"de": 0, "ate": 1401, "dec": 0, "ini": em("f4", "1.401"), "dur": 1.4, "cor": "#ff5a14", "unid": "FOCOS"},
     "l": "no Brasil · 1.064 só no Pará", "borda": "rgba(255,90,20,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "CALOR E AR SECO · ONTEM",
     "contador": {"de": 30, "ate": 39, "dec": 0, "ini": em("f5", "39"), "dur": 1.2, "cor": "#ff2a1f", "unid": "°C"},
     "l": "Teresina (PI) · Itaituba (PA) · umidade 16% em Juazeiro do Norte (CE)", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "HOJE · ALERTA LARANJA DE TEMPESTADE",
     "contador": {"de": 0, "ate": 591, "dec": 0, "ini": em("f6", "591"), "dur": 1.2, "cor": "#ff8c1a", "unid": "CIDADES"},
     "l": "PR 319 · SC 213 · RS 44 · SP 12 · MS 3 — vento de 60 a 100 km/h e granizo", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "AMANHÃ, 14/10",
     "itens": [{"t": em("f7", "687"), "txt": "⛈️ laranja em 687 cidades: PR · SP · MG · MS · RJ"},
               {"t": em("f7", "1.012"), "txt": "🏜️ ar seco em 1.012 cidades, a maioria no Nordeste"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f8", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f8", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f9"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f9", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": .5, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 12/10 05h a 13/10 05h · chuva: <b>CEMADEN</b> · vento: METAR (<b>NOAA</b>) · focos: <b>INPE</b>, 12/10"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "Pluviômetros do <b>CEMADEN</b>, 24 h até 13/10 05h: Foz do Iguaçu (São Miguel) 104,4 mm · Medianeira 100,2 mm · Cascavel (Centro) 91,2 mm"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "METAR do aeroporto de Presidente Prudente (<b>NOAA</b>), 13/10 01h: rajada de 42 nós (77,8 km/h), trovoada forte"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INPE</b> Programa Queimadas, 12/10 · contagem pelo satélite de referência (AQUA) · pontos = VIIRS · foco não é igual a incêndio"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "METAR dos aeroportos de Teresina, Itaituba e Juazeiro do Norte (<b>NOAA</b>), 12/10 · umidade calculada (36 °C, orvalho 6 °C)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INMET</b>, aviso laranja de tempestade para 13/10 (591 municípios) · Curitiba: previsão <b>Open-Meteo</b> para 13/10"},
    {"ini": ini("f7"), "fim": DUR, "html": "<b>INMET</b>: aviso laranja de tempestade para 14/10 (687 municípios) · aviso amarelo de baixa umidade até 14/10 (1.012 municípios)"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"fogo": "#ff5a14", "focos": "#ff5a14", "chuva": "#5ec8ff", "milimetros": "#5ec8ff", "tempestade": "#ff8c1a", "rajada": "#5ec8ff",
         "vento": "#5ec8ff", "madrugada": "#5ec8ff", "umidade": "#ff8c1a", "seco": "#ff8c1a", "graus": "#ff2a1f", "alerta": "#ff8c1a",
         "laranja": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM, "agua": "#5ec8ff"}
LUGAR = {"foz", "iguacu", "parana", "medianeira", "cascavel", "presidente", "prudente", "oeste", "paulista", "para", "brasil", "teresina",
         "itaituba", "juazeiro", "norte", "santa", "catarina", "curitiba", "rio", "inemaclub", "cidade", "regiao"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · CLIMA 24 H", "selo": "CEMADEN · INPE · INMET · NOAA · " + DATA[:5],
     "camera": camera, "sat": SAT, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · {len(fogo)} pontos de fogo · "
      f"tempestade hoje {HOJE} · amanhã {AMANHA} · seco {SECO}")
