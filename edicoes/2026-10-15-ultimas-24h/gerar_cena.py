#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 15/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos pluviômetros do CEMADEN, do METAR (NOAA), dos focos do INPE, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "15/10/2026"
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
SPC = {"lon": -46.66, "lat": -23.53, "zoom": 8.4}    # capital paulista: Brasilândia, Congonhas, Vila Clementino
GOM = {"lon": -48.3, "lat": -17.6, "zoom": 6.2}      # Novo Gama (GO) e Uberlândia (MG)
NOR = {"lon": -51.5, "lat": -6.0, "zoom": 4.7}       # fogo: Pará, Maranhão, Tocantins
CAL = {"lon": -46.0, "lat": -10.5, "zoom": 4.4}      # Teresina, Barra do Garças, Juazeiro do Norte
SE = {"lon": -48.0, "lat": -19.5, "zoom": 4.8}       # hoje: tempestade laranja MG/SP/GO...
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
SPE = {"lon": -48.6, "lat": -22.4, "zoom": 5.7}      # estado de SP (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, SPC, 35, -8), K(fim("f2") - .2, {**SPC, "lon": -46.64}, 40, 4),
    K(ini("f3") + .8, {**SPC, "lat": -23.58, "zoom": 8.6}, 40, 6), K(fim("f3") - .2, {**SPC, "lat": -23.58, "zoom": 8.7}, 42, 10),
    K(ini("f4") + 1.0, GOM, 35, -6), K(fim("f4") - .2, {**GOM, "lon": -48.15}, 40, 4),
    K(ini("f5") + 1.0, NOR, 8, -2), K(fim("f5") - .2, {**NOR, "lon": -51.3}, 10, 2),
    K(ini("f6") + 1.0, CAL, 12, -3), K(fim("f6") - .2, {**CAL, "lon": -45.8}, 15, 3),
    K(ini("f7") + 1.0, SE, 25, 0), K(fim("f7") - .2, {**SE, "zoom": 4.85}, 25, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f9") + 1.0, SPE, 10, 0), K(fim("f9") - .2, {**SPE, "zoom": 5.8}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-14T08") and TS[-1].startswith("2026-10-15T08"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# fundo: Blue Marble do mundo (copiado de 2026-10-14-ultimas-24h) por baixo, senão a borda do geocolor aparece preta com a câmera inclinada
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- focos de 14/10 (INPE: pontos VIIRS em grade de 0,08°; conta pelo AQUA)
grade, ref, ref_pa = {}, 0, 0
with open(B / "inpe_focos_diario_br_20261014.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-14"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            ref_pa += r["estado"].strip().upper() == "PARÁ"
assert (ref, ref_pa) == (2177, 1125), (ref, ref_pa)
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f5"), "fim": ini("f6") + .3, "dados": fogo, "dur": 3.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
HOJE = ufs_av(56071, 30)     # tempestade laranja 15/10: 2.163 (MG 815, SP 645, GO 246, PR 104, MT 103, RJ 92, ES 78, MS 41, TO 30, BA 8)
SECO = ufs_av(56074, 30)     # baixa umidade amarela 15/10 09h–23h59: 501 (BA 249, PI 140, MG 39, CE 34, PE 31)
assert (len(geo(56071)), len(geo(56074)), len(geo(56072))) == (2163, 501, 2188), (len(geo(56071)), len(geo(56074)), len(geo(56072)))
assert [sum(c[:2] == u for c in geo(56071)) for u in ("31", "35", "52")] == [815, 645, 246]
assert aviso[56071]["severidade"] == "Perigo" and aviso[56071]["descricao"] == "Tempestade" and aviso[56071]["inicio"].startswith("2026-10-15")
assert aviso[56074]["severidade"] == "Perigo Potencial" and aviso[56074]["descricao"] == "Baixa Umidade" and aviso[56074]["inicio"].startswith("2026-10-15")
assert aviso[56072]["severidade"] == "Perigo Potencial" and aviso[56072]["descricao"] == "Tempestade" and aviso[56072]["inicio"].startswith("2026-10-16")
estados = [
    {"id": "sp", "ini": ini("f2"), "fim": ini("f4") + .3, "ufs": ["SP"], "cor": VERM, "alfa": .35},
    {"id": "seco", "ini": em("f6", "Juazeiro"), "fim": ini("f7") + .3, "ufs": SECO, "cor": AMA, "alfa": .4},
    {"id": "hoje", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": HOJE, "cor": LAR, "alfa": .55},
    {"id": "volsp", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["SP"], "cor": [60, 150, 255], "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
top = {(r["cidade"], r["estacao"]): r["acc24"] for r in CM["top"]}
assert top[("Novo Gama", "Lago azul")] == 104.8 and top[("São Paulo", "Vila Clementino")] == 73.04
VRB = top[("Visconde Do Rio Branco", "Rio Xopoto")]          # 127,6 mm: sensor descartado (acc6 11,2), fora das somas ditas
SOMA = CM["soma_por_uf"]
assert SOMA["SP"]["soma_mm"] == 2111.7 and SOMA["SP"]["estacoes"] == 370 and CM["soma_mm_estacoes"] == 7978.4
assert sum(d["estacoes"] for d in SOMA.values()) == 1482
assert CM["soma_mm_estacoes"] - VRB > 7800                   # "mais de 7.800" sem Visconde do Rio Branco (7.850,8)
SEMV = {u: d["soma_mm"] - (VRB if u == "MG" else 0) for u, d in SOMA.items()}
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["SP", "PR", "MG", "GO", "RS"], RK

# ---------------------------------------------------------------- METAR: rajadas e calor citados
MT = json.loads((B / "resumo.json").read_text())["noaa_metar"]
raj = {r[1]: r[4] for r in MT["rajada_kmh_top"]}
assert "G48KT" in raj["SBSP"] and "G38KT" in raj["SBUL"]        # 48 kt = 88,9 km/h; 38 kt = 70,4 km/h
assert int(48 * 1.852) == 88 and int(38 * 1.852) == 70
assert [39, "SBTE"] == MT["tmax_top"][0][:2] and [39, "SBBW"] == MT["tmax_top"][1][:2] and MT["ur_min_top"][0][:2] == [16, "SBJU"]

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-15" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qui", "sex", "sáb", "dom", "seg", "ter", "qua"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 614.4
assert max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])["dia"] == "2026-10-15"          # hoje, quinta, o mais chuvoso (133,7 mm)
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "SE"        # Sudeste acumula mais (199,5 mm)
assert sum(d["tmax_pico"][1] == "Teresina" and d["tmax_pico"][0] > 39 for d in P7["por_dia"]) == 3   # Teresina > 39 °C em 3 dias (até 39,6)

pinos = [
    {"nome": "Brasilândia", "sub": "1 morte em deslizamento", "lon": -46.69, "lat": -23.46, "ini": em("f2", "Brasilândia"), "fim": ini("f3"), "h": 180},
    {"nome": "Congonhas", "sub": "rajada de 88 km/h", "lon": -46.656, "lat": -23.627, "ini": em("f3", "Congonhas"), "fim": ini("f4"), "h": 210},
    {"nome": "Vila Clementino", "sub": "73 mm em 24 h", "lon": -46.645, "lat": -23.598, "ini": em("f3", "Clementino"), "fim": ini("f4"), "h": 110},
    {"nome": "Novo Gama (GO)", "sub": "104 mm em 24 h", "lon": -48.04, "lat": -16.06, "ini": em("f4", "Novo"), "fim": ini("f5"), "h": 200},
    {"nome": "Uberlândia (MG)", "sub": "rajada de 70 km/h", "lon": -48.28, "lat": -18.92, "ini": em("f4", "Uberlândia"), "fim": ini("f5"), "h": 150},
    {"nome": "Pará", "sub": "1.125 focos em 1 dia", "lon": -52.5, "lat": -4.5, "ini": em("f5", "Pará"), "fim": ini("f6"), "h": 160},
    {"nome": "Teresina", "sub": "39 °C", "lon": -42.8, "lat": -5.09, "ini": em("f6", "Teresina"), "fim": ini("f7"), "h": 170},
    {"nome": "Barra do Garças", "sub": "39 °C", "lon": -52.26, "lat": -15.89, "ini": em("f6", "Garças"), "fim": ini("f7"), "h": 150},
    {"nome": "Juazeiro do Norte", "sub": "umidade 16%", "lon": -39.31, "lat": -7.21, "ini": em("f6", "Juazeiro"), "fim": ini("f7"), "h": 130},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">⚠️ 1 morte · 💨 88 km/h · 🌧️ 104 mm</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "SÃO PAULO · TEMPORAL DE QUARTA, 14/10",
     "itens": [{"t": em("f2", "morreu"), "txt": "uma mulher morreu em deslizamento na Brasilândia (zona norte)"},
               {"t": em("f2", "17"), "txt": "17 chamados de enchente das 15h às 18h"}],
     "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "CONGONHAS · RAJADA COM TROVOADA",
     "contador": {"de": 0, "ate": 88, "dec": 0, "ini": em("f3", "88") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "KM/H"},
     "l": "quarta 16h35 · Vila Clementino 73 mm em 24 h", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "NOVO GAMA (GO) · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 104, "dec": 0, "ini": em("f4", "104") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "perto de Brasília · Uberlândia (MG) rajada de 70 km/h", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "FOGO · QUARTA, 14/10",
     "contador": {"de": 0, "ate": 2177, "dec": 0, "ini": em("f5", "2.177") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": "FOCOS NO BRASIL"},
     "itens": [{"t": em("f5", "1.125"), "txt": "1.125 no Pará · 210 no Maranhão · 201 no Tocantins"}],
     "borda": "rgba(255,90,20,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "CALOR E AR SECO · ONTEM",
     "contador": {"de": 30, "ate": 39, "dec": 0, "ini": em("f6", "39") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "°C"},
     "l": "Teresina (PI) e Barra do Garças (MT) · Juazeiro do Norte (CE) umidade 16%", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA LARANJA DE TEMPESTADE",
     "contador": {"de": 0, "ate": 2163, "dec": 0, "ini": em("f7", "2.163") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES"},
     "itens": [{"t": em("f7", "80"), "txt": "Grande São Paulo: chuva pode chegar a 80 mm hoje"}],
     "l": "MG 815 · SP 645 · GO 246 · PR 104 · MT 103 · RJ 92 · ES 78 — vento de 60 a 100 km/h e granizo", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · hoje 134 mm somados · Sudeste 199 mm na semana · Teresina até 39,6 °C", "borda": "rgba(244,114,182,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": 2111, "dec": 0, "ini": em("f9", "2.100") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM SP · 370 PLUVIÔMETROS"},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "2.100") + .3, "dur": 1.2},
     "itens": [{"t": em("f9", "7.800"), "txt": "Brasil: mais de 7.800 mm somados em 24 h"},
               {"t": em("f9", "614"), "txt": "7 dias nas capitais: 614 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": .5, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 14/10 05h a 15/10 05h · morte: <b>Governo de SP</b> · vento: METAR (<b>NOAA</b>) · chuva: <b>CEMADEN</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>Agência SP</b> (Governo do Estado) e <b>CNN Brasil</b>, 14/10: deslizamento na Brasilândia; Corpo de Bombeiros, chamados entre 15h e 18h"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "METAR de Congonhas (<b>NOAA</b>), 14/10 16h35: rajada de 48 nós (88,9 km/h) com trovoada · <b>CEMADEN</b> Vila Clementino 73,0 mm em 24 h até 15/10 05h"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Pluviômetro do <b>CEMADEN</b> em Novo Gama (Lago Azul), 104,8 mm em 24 h até 15/10 05h · METAR de Uberlândia (<b>NOAA</b>), 14/10 22h: 38 nós (70,4 km/h)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INPE</b> Programa Queimadas, 14/10 · contagem pelo satélite de referência (AQUA) · pontos = VIIRS · foco não é igual a incêndio"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "METAR dos aeroportos (<b>NOAA</b>), 14/10 à tarde (umidade calculada) · <b>INMET</b>: aviso amarelo de baixa umidade hoje em 501 cidades"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>, aviso laranja de tempestade para 15/10 (2.163 municípios) · <b>Defesa Civil de SP</b>: até 80 mm na Grande SP hoje (previsão)"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (15 a 21/10) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": "<b>CEMADEN</b>: soma das leituras de 24 h (1.482 pluviômetros; sem 1 sensor descartado em MG) · previsão <b>Open-Meteo</b>: 614 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "previsao": "#f472b6", "fogo": "#ff5a14", "focos": "#ff5a14", "chuva": "#5ec8ff",
         "milimetros": "#5ec8ff", "tempestade": "#ff8c1a", "rajada": "#5ec8ff", "vento": "#5ec8ff", "granizo": "#5ec8ff", "umidade": "#ff8c1a",
         "graus": "#ff2a1f", "alerta": "#ff8c1a", "laranja": "#ff8c1a", "morte": "#ff2a1f", "morreu": "#ff2a1f", "deslizamento": "#ff2a1f",
         "enchente": "#5ec8ff", "temporal": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sao", "paulo", "goias", "brasilandia", "congonhas", "vila", "clementino", "novo", "gama", "brasilia", "uberlandia", "brasil",
         "para", "teresina", "barra", "garcas", "juazeiro", "norte", "grande", "sudeste", "capitais", "hoje", "inemaclub", "cidade", "regiao"}
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
      f"tempestade hoje {HOJE} · seco {SECO} · 7 dias {ROTD}")
