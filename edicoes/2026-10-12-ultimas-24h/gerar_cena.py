#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 12/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET, da Defesa Civil de SP, do CEMADEN e do METAR (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "12/10/2026"
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
SP = {"lon": -47.7, "lat": -22.9, "zoom": 6.5}
SP2 = {"lon": -47.4, "lat": -21.8, "zoom": 6.7}
NOR = {"lon": -49.5, "lat": -7.0, "zoom": 5.0}
CE = {"lon": -40.0, "lat": -7.8, "zoom": 6.0}
SSE = {"lon": -50.5, "lat": -23.8, "zoom": 4.85}
PR = {"lon": -51.2, "lat": -24.9, "zoom": 5.8}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, SP, 40, -10), K(fim("f2") - .2, {**SP, "lon": -47.5}, 45, 8),
    K(ini("f3") + 1.0, SP2, 40, -8), K(fim("f3") - .2, {**SP2, "lon": -47.2}, 45, 4),
    K(ini("f4") + 1.0, NOR, 15, -3), K(fim("f4") - .2, {**NOR, "lon": -49.2}, 18, 3),
    K(ini("f5") + 1.0, CE, 15, -3), K(fim("f5") - .2, {**CE, "lon": -39.8}, 18, 3),
    K(ini("f6") + 1.0, SSE, 20, 0), K(fim("f6") - .2, {**SSE, "zoom": 4.75}, 20, 2),
    K(ini("f7") + 1.0, PR, 30, -4), K(fim("f7") - .2, {**PR, "lon": -50.9}, 35, 4),
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

# ---------------------------------------------------------------- focos: fora hoje (AQUA de 11/10 só com 150 focos, passagem incompleta)
pontos = []

# ---------------------------------------------------------------- avisos do INMET (estados com aviso laranja)
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
HOJE = sorted(set(ufs_av(56036)) | set(ufs_av(56044)))  # tempestade laranja hoje: 449 (PR, SC, RS, MS) + 547 (MG, SP, RJ)
AMANHA = ufs_av(56037)                                   # tempestade laranja 13/10: 601 (PR 399, SP, MS, SC)
assert (len(geo(56036)), len(geo(56044)), len(geo(56037))) == (449, 547, 601), (len(geo(56036)), len(geo(56044)), len(geo(56037)))
assert not geo(56036) & geo(56044) and len(geo(56036) | geo(56044)) == 996
assert sum(c[:2] == "41" for c in geo(56037)) == 399
assert all(aviso[i]["severidade"] == "Perigo" for i in (56036, 56044, 56037))
estados = [
    {"id": "hoje", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": HOJE, "cor": VERM, "alfa": .5},
    {"id": "amanha", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": AMANHA, "cor": VERM, "alfa": .5},
]

pinos = [
    {"nome": "Cesário Lange", "sub": "71 árvores derrubadas", "lon": -47.95, "lat": -23.23, "ini": em("f2", "Cesário"), "fim": ini("f3"), "h": 200},
    {"nome": "Estiva Gerbi", "sub": "71,6 mm em 24 h", "lon": -46.95, "lat": -22.27, "ini": em("f3", "Estiva"), "fim": ini("f4"), "h": 170},
    {"nome": "Ribeirão Preto", "sub": "rajada de 59 km/h", "lon": -47.81, "lat": -21.18, "ini": em("f3", "Ribeirão"), "fim": ini("f4"), "h": 120},
    {"nome": "Teresina", "sub": "38 °C ontem", "lon": -42.8, "lat": -5.09, "ini": em("f4", "Teresina"), "fim": ini("f5"), "h": 170},
    {"nome": "Itaituba", "sub": "38 °C ontem", "lon": -55.98, "lat": -4.28, "ini": em("f4", "Itaituba"), "fim": ini("f5"), "h": 170},
    {"nome": "Juazeiro do Norte", "sub": "umidade 15%", "lon": -39.32, "lat": -7.21, "ini": em("f5", "Juazeiro"), "fim": ini("f6"), "h": 170},
    {"nome": "Curitiba", "sub": "até 44 mm amanhã (previsão)", "lon": -49.27, "lat": -25.43, "ini": em("f7", "Curitiba"), "fim": ini("f8"), "h": 170},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌳 71 árvores · 🌡️ 38 °C · 🏜️ 15%</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "SÃO PAULO · TEMPORAL DE DOMINGO",
     "contador": {"de": 0, "ate": 71, "dec": 0, "ini": em("f2", "71"), "dur": 1.4, "cor": "#3fdc6a", "unid": "ÁRVORES"},
     "l": "no chão em Cesário Lange · 29 alertas da Defesa Civil", "borda": "rgba(63,220,106,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "INTERIOR DE SP · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 71, "dec": 0, "ini": em("f3", "71"), "dur": 1.4, "cor": "#5ec8ff", "unid": "MM"},
     "l": "em Estiva Gerbi · rajada de 59 km/h em Ribeirão Preto", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "CALOR MEDIDO ONTEM",
     "contador": {"de": 30, "ate": 38, "dec": 0, "ini": em("f4", "38"), "dur": 1.2, "cor": "#ff2a1f", "unid": "°C"},
     "l": "Teresina (PI) · Itaituba (PA)", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "JUAZEIRO DO NORTE (CE) · UMIDADE",
     "contador": {"de": 60, "ate": 15, "dec": 0, "ini": em("f5", "umidade"), "dur": 1.4, "cor": "#ff8c1a", "unid": "%"},
     "l": "💧 beba água · ☀️ fuja do sol do meio-dia", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "HOJE · ALERTA LARANJA DE TEMPESTADE",
     "contador": {"de": 0, "ate": 996, "dec": 0, "ini": em("f6", "996"), "dur": 1.2, "cor": "#ff2a1f", "unid": "CIDADES"},
     "l": "PR · SC · RS · MS · MG · SP · RJ — vento de 60 a 100 km/h e granizo", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "AMANHÃ, 13/10 · ALERTA LARANJA",
     "itens": [{"t": em("f7", "Paraná"), "txt": "⛈️ 601 cidades: o Paraná inteiro + SP · MS · SC"},
               {"t": em("f7", "Curitiba"), "txt": "🌧️ Curitiba: até 44 mm (previsão)"}],
     "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f8", "Chuva"), "txt": "🌧️ Chuva?"}, {"t": em("f8", "vento"), "txt": "💨 Vento?"},
               {"t": em("f8", "calor"), "txt": "🌡️ Calor?"}, {"t": em("f8", "cidade"), "txt": "📍 Sua cidade"}],
     "borda": "rgba(255,210,63,.8)"},
]

cta = {"ini": ini("f9"), "fim": DUR, "a": "CURSO GRATUITO PRA VOCÊ", "b": "Tecnologia e IA no inema.club."}
club = {"ini": em("f9", "inema"), "fim": DUR, "a": "inema.club", "b": "cursos gratuitos de tecnologia e IA"}

fontes = [
    {"ini": .5, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 11/10 05h a 12/10 05h · árvores: <b>Defesa Civil de SP</b> · 38 °C e umidade: METAR (<b>NOAA</b>), 11/10"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>Defesa Civil do Estado de SP</b> (Agência SP, 11/10): 29 alertas até 18h35 · Cesário Lange: 71 quedas de árvores, família de 4 pessoas desalojada"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Pluviômetro do <b>CEMADEN</b> em Estiva Gerbi (Centro): 71,6 mm em 24 h até 12/10 05h30 · rajada: METAR do aeroporto de Ribeirão Preto (<b>NOAA</b>), 11/10 17h24"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "METAR dos aeroportos de Teresina e Itaituba (<b>NOAA</b>), 11/10 entre 16h e 17h"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Umidade calculada do METAR do aeroporto de Juazeiro do Norte (<b>NOAA</b>), 11/10 16h: 37 °C, orvalho 6 °C"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INMET</b>, avisos laranja de tempestade para 12/10: 449 municípios (PR, SC, RS, MS) + 547 (MG, SP, RJ)"},
    {"ini": ini("f7"), "fim": DUR, "html": "<b>INMET</b>, aviso laranja de tempestade para 13/10 (601 municípios, 399 no PR) · Curitiba: previsão <b>Open-Meteo</b> para 13/10"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"fumaca": "#ff8c1a", "fogo": "#ff5a14", "focos": "#ff5a14", "temporal": "#5ec8ff", "chuva": "#5ec8ff", "deserto": "#ff8c1a",
         "umidade": "#ff8c1a", "calor": "#ff2a1f", "alerta": "#ff2a1f", "tempestade": "#ff2a1f", "inundacao": "#3c96ff",
         "desalojados": "#3c96ff", "rajada": "#5ec8ff", "pior": "#ff2a1f", "comenta": "#ffd23f", "gratuito": "#ffd23f", "laranja": "#ff8c1a", "cirio": "#ffd23f", "sensacao": "#ff2a1f", "feriado": "#ffd23f", "milimetros": "#5ec8ff", "arvores": "#3fdc6a", "granizo": "#5ec8ff", "vento": "#5ec8ff", "calorao": "#ff2a1f"}
LUGAR = {"sao", "paulo", "paulista", "cesario", "lange", "estiva", "gerbi", "ribeirao", "preto", "teresina", "itaituba", "para", "juazeiro",
         "norte", "ceara", "sul", "rio", "janeiro", "parana", "curitiba", "brasil", "inemaclub", "cidade"}
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
     "marca": "INEMA · CLIMA 24 H", "selo": "DEFESA CIVIL · INMET · NOAA · " + DATA[:5],
     "camera": camera, "sat": SAT, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · tempestade hoje {HOJE} · amanhã {AMANHA}")
