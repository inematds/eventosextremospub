#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 14/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos pluviômetros do CEMADEN, do METAR (NOAA), dos focos do INPE, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "14/10/2026"
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
NPR = {"lon": -52.4, "lat": -23.35, "zoom": 7.0}    # noroeste/norte do PR: Santa Cruz de Monte Castelo, Paranavaí, Londrina
CGR = {"lon": -51.2, "lat": -21.2, "zoom": 5.6}     # Campo Grande (MS) e Ribeirão Preto (SP)
NE = {"lon": -42.5, "lat": -10.0, "zoom": 4.9}      # fogo: Bahia, Piauí, Maranhão
NOR = {"lon": -48.5, "lat": -5.5, "zoom": 5.0}      # Itaituba e Teresina
SE = {"lon": -48.8, "lat": -21.0, "zoom": 4.9}      # hoje: tempestade laranja MS → ES
BAM = {"lon": -46.0, "lat": -15.5, "zoom": 4.6}     # ar seco BA/MG e amarelo de amanhã
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}    # próximos 7 dias (gráfico em cima)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, NPR, 40, -10), K(fim("f2") - .2, {**NPR, "lon": -52.35}, 45, 8),
    K(ini("f3") + 1.0, CGR, 35, -6), K(fim("f3") - .2, {**CGR, "lon": -51.0}, 40, 4),
    K(ini("f4") + 1.0, NE, 6, -2), K(fim("f4") - .2, {**NE, "lon": -42.3}, 8, 2),
    K(ini("f5") + 1.0, NOR, 15, -3), K(fim("f5") - .2, {**NOR, "lon": -48.3}, 18, 3),
    K(ini("f6") + 1.0, SE, 25, 0), K(fim("f6") - .2, {**SE, "zoom": 4.85}, 25, 2),
    K(ini("f7") + 1.0, BAM, 6, -2), K(fim("f7") - .2, {**BAM, "zoom": 4.55}, 6, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f9") + 1.0, {"lon": -51.5, "lat": -24.0, "zoom": 5.2}, 10, 0), K(fim("f9") - .2, {"lon": -51.5, "lat": -24.0, "zoom": 5.3}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-13T08") and TS[-1].startswith("2026-10-14T08"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# fundo: Blue Marble do mundo (copiado de 2026-10-13-clima-do-dia) por baixo, senão a borda leste do geocolor aparece preta no Nordeste
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- focos de 13/10 (INPE: pontos VIIRS em grade de 0,08°; conta pelo AQUA)
grade, ref, ref_ba = {}, 0, 0
with open(B / "inpe_focos_diario_br_20261013.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-13"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            ref_ba += r["estado"].strip().upper() == "BAHIA"
assert (ref, ref_ba) == (1050, 283), (ref, ref_ba)
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
HOJE = ufs_av(56064)     # tempestade laranja 14/10: 1.342 (SP 590, PR 309, MG 284, RJ 92, MS 54, ES 13)
SECO = ufs_av(56061)     # baixa umidade laranja 14/10 10h–22h: 96 (BA 67, MG 29)
AMANHA = ufs_av(56062)   # tempestade amarela 15/10: 2.074 (MG 722, SP 637, GO 226...)
assert (len(geo(56064)), len(geo(56061)), len(geo(56062))) == (1342, 96, 2074), (len(geo(56064)), len(geo(56061)), len(geo(56062)))
assert (sum(c[:2] == "29" for c in geo(56061)), sum(c[:2] == "31" for c in geo(56061))) == (67, 29)
assert aviso[56064]["severidade"] == "Perigo" and aviso[56064]["descricao"] == "Tempestade" and aviso[56064]["inicio"].startswith("2026-10-14")
assert aviso[56061]["severidade"] == "Perigo" and aviso[56061]["descricao"] == "Baixa Umidade" and aviso[56061]["inicio"].startswith("2026-10-14")
assert aviso[56062]["severidade"] == "Perigo Potencial" and aviso[56062]["descricao"] == "Tempestade" and aviso[56062]["inicio"].startswith("2026-10-15")
estados = [
    {"id": "hoje", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": HOJE, "cor": LAR, "alfa": .55},
    {"id": "seco", "ini": ini("f7"), "fim": em("f7", "Amanhã") + .3, "ufs": SECO, "cor": LAR, "alfa": .55},
    {"id": "amanha", "ini": em("f7", "Amanhã"), "fim": ini("f8") + .3, "ufs": AMANHA, "cor": AMA, "alfa": .45},
    {"id": "volpr", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["PR"], "cor": [60, 150, 255], "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
top = {(r["cidade"], r["estacao"]): r["acc24"] for r in CM["top"]}
assert top[("Santa Cruz De Monte Castelo", "G2-412330303A")] == 112.4 and top[("Paranavaí", "G2-411840202A")] == 101.2
assert top[("Londrina", "G2-411370003A")] == 76.8
SOMA = CM["soma_por_uf"]
assert SOMA["PR"]["soma_mm"] == 4317.6 and SOMA["PR"]["estacoes"] == 153 and CM["soma_mm_estacoes"] == 12464.1
assert sum(d["estacoes"] for d in SOMA.values()) == 1518
RK = sorted(SOMA.items(), key=lambda x: -x[1]["soma_mm"])[:5]
assert [u for u, _ in RK] == ["PR", "MG", "SP", "RJ", "SC"], RK

# ---------------------------------------------------------------- METAR: rajadas e calor citados
MT = json.loads((B / "resumo.json").read_text())["noaa_metar"]
raj = {r[1]: r[4] for r in MT["rajada_kmh_top"]}
assert "G38KT" in raj["SBCG"] and "G37KT" in raj["SBRP"]        # 38 kt = 70,4 km/h; 37 kt = 68,5 km/h
assert int(38 * 1.852) == 70 and int(37 * 1.852) == 68
assert [39, "SBTE"] == MT["tmax_top"][0][:2] and [39, "SBIH"] == MT["tmax_top"][1][:2] and MT["ur_min_top"][0][:2] == [20, "SBTE"]

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-14" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qua", "qui", "sex", "sáb", "dom", "seg", "ter"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 539.3
assert max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])["dia"] == "2026-10-15"          # quinta, o mais chuvoso (148 mm)
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "SE"        # Sudeste acumula mais (172 mm)
assert sum(d["tmax_pico"][1] == "Teresina" and d["tmax_pico"][0] > 39 for d in P7["por_dia"]) == 5   # Teresina > 39 °C em 5 dias

pinos = [
    {"nome": "Santa Cruz de Monte Castelo", "sub": "112 mm em 24 h", "lon": -53.30, "lat": -22.96, "ini": em("f2", "Castelo"), "fim": ini("f3"), "h": 200},
    {"nome": "Paranavaí", "sub": "101 mm", "lon": -52.47, "lat": -23.07, "ini": em("f2", "Paranavaí"), "fim": ini("f3"), "h": 120},
    {"nome": "Londrina", "sub": "76 mm", "lon": -51.16, "lat": -23.31, "ini": em("f2", "Londrina"), "fim": ini("f3"), "h": 160},
    {"nome": "Campo Grande", "sub": "rajada de 70 km/h", "lon": -54.65, "lat": -20.47, "ini": em("f3", "Campo"), "fim": ini("f4"), "h": 180},
    {"nome": "Ribeirão Preto", "sub": "rajada de 68 km/h", "lon": -47.81, "lat": -21.18, "ini": em("f3", "Ribeirão"), "fim": ini("f4"), "h": 150},
    {"nome": "Bahia", "sub": "283 focos em 1 dia", "lon": -42.0, "lat": -12.0, "ini": em("f4", "Bahia"), "fim": ini("f5"), "h": 160},
    {"nome": "Teresina", "sub": "39 °C · umidade 20%", "lon": -42.8, "lat": -5.09, "ini": em("f5", "Teresina"), "fim": ini("f6"), "h": 170},
    {"nome": "Itaituba", "sub": "39 °C", "lon": -55.98, "lat": -4.28, "ini": em("f5", "Itaituba"), "fim": ini("f6"), "h": 170},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌧️ 112 mm · 💨 70 km/h · 🌡️ 39 °C</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "NOROESTE DO PARANÁ · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 112, "dec": 0, "ini": em("f2", "112") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "em Santa Cruz de Monte Castelo · Paranavaí 101 mm · Londrina 76 mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "CAMPO GRANDE (MS) · COMEÇO DA NOITE",
     "contador": {"de": 0, "ate": 70, "dec": 0, "ini": em("f3", "70") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "KM/H"},
     "l": "rajada com tempestade forte · Ribeirão Preto (SP) 68 km/h", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "FOGO · TERÇA, 13/10",
     "contador": {"de": 0, "ate": 1050, "dec": 0, "ini": em("f4", "1.050") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": "FOCOS"},
     "l": "no Brasil · 283 na Bahia · 221 no Piauí", "borda": "rgba(255,90,20,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "CALOR E AR SECO · ONTEM",
     "contador": {"de": 30, "ate": 39, "dec": 0, "ini": em("f5", "39") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "°C"},
     "l": "Teresina (PI), umidade 20% · Itaituba (PA)", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "HOJE · ALERTA LARANJA DE TEMPESTADE",
     "contador": {"de": 0, "ate": 1342, "dec": 0, "ini": em("f6", "1.342") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES"},
     "l": "SP 590 · PR 309 · MG 284 · RJ 92 · MS 54 · ES 13 — vento de 60 a 100 km/h e granizo", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE E AMANHÃ",
     "itens": [{"t": em("f7", "96"), "txt": "🏜️ ar seco laranja em 96 cidades: BA 67 · MG 29 (umidade de 20% a 12%)"},
               {"t": em("f7", "2.074"), "txt": "⛈️ amanhã, 15/10: amarelo de tempestade em 2.074 cidades"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · quinta 148 mm somados · Teresina acima de 39 °C até domingo", "borda": "rgba(244,114,182,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": 4317, "dec": 0, "ini": em("f9", "4.300") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM NO PR · 153 PLUVIÔMETROS"},
     "ranking": {"itens": [{"nome": u, "v": int(d["soma_mm"])} for u, d in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "4.300") + .3, "dur": 1.2},
     "l": "soma dos pluviômetros, não chuva média · Brasil mais de 12 mil mm · 7 dias nas capitais: 539 mm previstos", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": .5, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 13/10 05h a 14/10 05h · chuva: <b>CEMADEN</b> · vento e calor: METAR (<b>NOAA</b>)"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "Pluviômetros do <b>CEMADEN</b>, 24 h até 14/10 05h: Santa Cruz de Monte Castelo 112,4 mm · Paranavaí 101,2 mm · Londrina 76,8 mm"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "METAR dos aeroportos (<b>NOAA</b>), 13/10 ~18h30: Campo Grande rajada de 38 nós (70,4 km/h) com trovoada forte · Ribeirão Preto 37 nós (68,5 km/h)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INPE</b> Programa Queimadas, 13/10 · contagem pelo satélite de referência (AQUA) · pontos = VIIRS · foco não é igual a incêndio"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "METAR dos aeroportos de Teresina (17h, umidade calculada) e Itaituba (15h) (<b>NOAA</b>), 13/10"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INMET</b>, aviso laranja de tempestade para 14/10 (1.342 municípios) · Defesa Civil de SP: alerta de chuva forte até 15/10"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: aviso laranja de baixa umidade 14/10, 10h às 22h (96 municípios) · aviso amarelo de tempestade para 15/10 (2.074 municípios)"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (14 a 20/10) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": "<b>CEMADEN</b>: soma das leituras de 24 h (1.518 pluviômetros, 12.464 mm) · previsão <b>Open-Meteo</b>: 539 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "previsao": "#f472b6", "fogo": "#ff5a14", "focos": "#ff5a14", "chuva": "#5ec8ff",
         "milimetros": "#5ec8ff", "tempestade": "#ff8c1a", "rajada": "#5ec8ff", "vento": "#5ec8ff", "granizo": "#5ec8ff", "umidade": "#ff8c1a",
         "seco": "#ff8c1a", "graus": "#ff2a1f", "alerta": "#ff8c1a", "laranja": "#ff8c1a", "amarelo": AM, "comenta": AM, "inteligencia": AM,
         "artificial": AM}
LUGAR = {"parana", "santa", "cruz", "monte", "castelo", "paranavai", "londrina", "campo", "grande", "ribeirao", "preto", "brasil", "bahia",
         "minas", "teresina", "itaituba", "para", "sudeste", "capitais", "quinta", "inemaclub", "cidade", "regiao"}
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
      f"tempestade hoje {HOJE} · seco {SECO} · amanhã {AMANHA} · 7 dias {ROTD}")
