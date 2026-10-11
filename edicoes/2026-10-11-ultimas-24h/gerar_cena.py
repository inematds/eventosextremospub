#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 11/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE e dos avisos do INMET (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "11/10/2026"
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
LAR, AZUL, VERM = [255, 140, 26], [60, 150, 255], [255, 42, 31]

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
PR = {"lon": -53.9, "lat": -25.5, "zoom": 6.6}
AM = {"lon": -60.0, "lat": -4.0, "zoom": 4.9}
CO = {"lon": -47.9, "lat": -15.0, "zoom": 5.0}
BEL = {"lon": -48.5, "lat": -3.6, "zoom": 5.6}
SE = {"lon": -49.8, "lat": -21.5, "zoom": 4.8}
SUL = {"lon": -52.0, "lat": -26.5, "zoom": 4.9}
NE = {"lon": -45.5, "lat": -9.5, "zoom": 4.9}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, PR, 40, -10), K(fim("f2") - .2, {**PR, "lon": -53.7}, 45, 8),
    K(ini("f3") + 1.0, AM, 35, -8), K(fim("f3") - .2, {**AM, "lon": -59.3}, 40, 4),
    K(ini("f4") + 1.0, CO, 35, -6), K(fim("f4") - .2, {**CO, "lon": -47.6}, 40, 6),
    K(ini("f5") + 1.0, BEL, 15, -6), K(fim("f5") - .2, {**BEL, "lon": -48.3}, 20, 6),
    K(ini("f6") + 1.0, SE, 20, 0), K(fim("f6") - .2, {**SE, "zoom": 4.7}, 20, 4),
    K(ini("f7") + 1.0, SUL, 25, -4), K(max(em("f7", "Teresina") - .2, ini("f7") + 1.4), {**SUL, "zoom": 4.8}, 25, 0),
    K(min(em("f7", "Teresina") + 1.2, fim("f7") - .6), NE, 15, -4), K(fim("f7") - .2, {**NE, "lon": -45.0}, 20, 4),
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

# ---------------------------------------------------------------- focos de 10/10 (INPE: pontos VIIRS em grade de 0,08°; conta pelo AQUA)
grade, ref, ref_am = {}, 0, 0
with open(B / "inpe_focos_diario_br_20261010.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            ref_am += r["estado"].strip() == "AMAZONAS"
assert (ref, ref_am) == (1155, 494), (ref, ref_am)
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f3"), "fim": ini("f4") + .3, "dados": fogo, "dur": 3.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET (estados com aviso laranja)
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in aviso[i]["geocodes"].split(",")
                                    if sum(x[:2] == c[:2] for x in aviso[i]["geocodes"].split(",")) >= minimo})
TEMP = ufs_av(56035)       # tempestade, laranja, hoje 11/10 (1.373 municípios: SP, PR, MG, RJ, MS, GO)
AMANHA = ufs_av(56036)     # tempestade, laranja, 12/10 (449 municípios: PR, SC, RS, MS)
SECO = ufs_av(56034)       # baixa umidade, laranja, hoje (291 municípios, 166 no PI)
nmun = lambda i: len(aviso[i]["geocodes"].split(","))
assert (nmun(56035), nmun(56036), nmun(56034)) == (1373, 449, 291), (nmun(56035), nmun(56036), nmun(56034))
assert all(aviso[i]["severidade"] == "Perigo" for i in (56035, 56036, 56034))
estados = [
    {"id": "temp", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": TEMP, "cor": VERM, "alfa": .5},
    {"id": "amanha", "ini": ini("f7"), "fim": em("f7", "Teresina") + .3, "ufs": AMANHA, "cor": VERM, "alfa": .5},
    {"id": "seco", "ini": em("f7", "Teresina"), "fim": ini("f8") + .3, "ufs": SECO, "cor": LAR, "alfa": .5},
]

pinos = [
    {"nome": "Capitão Leônidas Marques", "sub": "124,7 mm em 24 h", "lon": -53.61, "lat": -25.48, "ini": em("f2", "Leônidas"), "fim": ini("f3"), "h": 200},
    {"nome": "São Miguel do Iguaçu", "sub": "42,8 mm em 3 h", "lon": -54.24, "lat": -25.35, "ini": em("f2", "Miguel"), "fim": ini("f3"), "h": 110},
    {"nome": "Manaus", "sub": "38 °C ontem", "lon": -60.02, "lat": -3.1, "ini": em("f3", "Amazonas"), "fim": ini("f4"), "h": 170},
    {"nome": "Autazes", "sub": "109 focos: 1º do país", "lon": -59.13, "lat": -3.58, "ini": em("f3", "494"), "fim": ini("f4"), "h": 110},
    {"nome": "Brasília", "sub": "umidade 14%", "lon": -47.93, "lat": -15.78, "ini": em("f4", "Brasília"), "fim": ini("f5"), "h": 170},
    {"nome": "Belém", "sub": "Círio: sensação de até 40 °C", "lon": -48.5, "lat": -1.45, "ini": em("f5", "Belém"), "fim": ini("f6"), "h": 170},
    {"nome": "Teresina", "sub": "até 39 °C hoje (previsão)", "lon": -42.8, "lat": -5.09, "ini": em("f7", "Teresina"), "fim": ini("f8"), "h": 170},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌧️ 124 mm · 🌡️ 38 °C · 🏜️ umidade 14%</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "OESTE DO PARANÁ · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 124, "dec": 0, "ini": em("f2", "124"), "dur": 1.4, "cor": "#5ec8ff", "unid": "MM"},
     "l": "em Capitão Leônidas Marques · São Miguel do Iguaçu: 42,8 mm em 3 h", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "FOCOS DE FOGO · 10/10",
     "contador": {"de": 0, "ate": 1155, "dec": 0, "ini": em("f3", "1.155"), "dur": 1.4, "cor": "#ff5a14", "unid": "NO BRASIL"},
     "l": "494 só no Amazonas · satélite de referência do INPE", "borda": "rgba(255,90,20,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "BRASÍLIA · UMIDADE DO AR",
     "contador": {"de": 60, "ate": 14, "dec": 0, "ini": em("f4", "umidade"), "dur": 1.4, "cor": "#ff8c1a", "unid": "%"},
     "l": "💧 beba água · ☀️ fuja do sol do meio-dia", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "BELÉM · CÍRIO DE NAZARÉ",
     "itens": [{"t": em("f5", "Círio"), "txt": "🙏 Círio hoje"}, {"t": em("f5", "sensação"), "txt": "🌡️ sensação de até 40 °C"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "HOJE · ALERTA LARANJA DE TEMPESTADE",
     "contador": {"de": 0, "ate": 1373, "dec": 0, "ini": em("f6", "1.373"), "dur": 1.2, "cor": "#ff2a1f", "unid": "CIDADES"},
     "l": "SP · PR · MG · RJ · MS · GO — vento de 60 a 100 km/h e granizo", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "AMANHÃ, 12/10 · E HOJE NO NORDESTE",
     "itens": [{"t": em("f7", "Sul"), "txt": "⛈️ 449 cidades em alerta laranja (PR · SC · RS · MS)"},
               {"t": em("f7", "Teresina"), "txt": "🌡️ Teresina até 39 °C hoje"}],
     "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f8", "Chuva"), "txt": "🌧️ Chuva?"}, {"t": em("f8", "calor"), "txt": "🌡️ Calor?"},
               {"t": em("f8", "fumaça"), "txt": "😷 Fumaça?"}, {"t": em("f8", "cidade"), "txt": "📍 Sua cidade"}],
     "borda": "rgba(255,210,63,.8)"},
]

cta = {"ini": ini("f9"), "fim": DUR, "a": "CURSO GRATUITO PRA VOCÊ", "b": "Tecnologia e IA no inema.club."}
club = {"ini": em("f9", "inema"), "fim": DUR, "a": "inema.club", "b": "cursos gratuitos de tecnologia e IA"}

fontes = [
    {"ini": .5, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 10/10 05h a 11/10 05h · chuva: <b>CEMADEN</b> · 38 °C e umidade: METAR (<b>NOAA</b>), 10/10"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "Pluviômetros do <b>CEMADEN</b>: Capitão Leônidas Marques (estação Centro) 124,7 mm em 24 h · São Miguel do Iguaçu 42,8 mm em 3 h · até 11/10 05h30"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INPE</b> Programa Queimadas, 10/10 · contagem pelo satélite de referência (AQUA) · pontos = VIIRS · Manaus 38 °C: METAR (<b>NOAA</b>), 10/10 16h"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Umidade de Brasília calculada do METAR do aeroporto (<b>NOAA</b>), 10/10 16h: 34 °C, orvalho 3 °C"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Previsão do meteorologista José Raimundo de Sousa, <b>INMET</b> (entrevista ao IPAM, Portal Amazônia, 06/10)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INMET</b>, aviso laranja de tempestade para 11/10 (1.373 municípios)"},
    {"ini": ini("f7"), "fim": DUR, "html": "<b>INMET</b>, aviso laranja de tempestade para 12/10 (449 municípios) · em laranja: baixa umidade hoje (291) · Teresina: previsão <b>Open-Meteo</b> para 11/10"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"fumaca": "#ff8c1a", "fogo": "#ff5a14", "focos": "#ff5a14", "temporal": "#5ec8ff", "chuva": "#5ec8ff", "deserto": "#ff8c1a",
         "umidade": "#ff8c1a", "calor": "#ff2a1f", "alerta": "#ff2a1f", "tempestade": "#ff2a1f", "inundacao": "#3c96ff",
         "desalojados": "#3c96ff", "rajada": "#5ec8ff", "pior": "#ff2a1f", "comenta": "#ffd23f", "gratuito": "#ffd23f", "laranja": "#ff8c1a", "cirio": "#ffd23f", "sensacao": "#ff2a1f", "feriado": "#ffd23f", "milimetros": "#5ec8ff"}
LUGAR = {"manaus", "parana", "brasilia", "capitao", "leonidas", "marques", "sao", "miguel", "iguacu", "amazonas", "pais", "sul",
         "sudeste", "teresina", "belem", "brasil", "inemaclub", "cidade"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or ("#ffd23f" if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · CLIMA 24 H", "selo": "INMET · INPE · NOAA · " + DATA[:5],
     "camera": camera, "sat": SAT, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · {len(fogo)} pontos de fogo · tempestade hoje {TEMP} · amanhã {AMANHA} · seco {SECO}")
