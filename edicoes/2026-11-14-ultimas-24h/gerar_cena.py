#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 14/11/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "14/11/2026"
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
CAPA = 2.2  # quadro 0 = capa cheia do Codex (impacto) até aqui (Nei, 15/10/2026)
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05, "selo": "ilustração"}] if (AQUI / "capa-dia/abertura.png").exists() else []
if not telas:
    CAPA = 0
LAR, AMA, VERM, AZC, AZU = [255, 140, 26], [250, 204, 21], [255, 42, 31], [150, 210, 255], [60, 150, 255]



# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
ZM = {"lon": -43.0, "lat": -20.9, "zoom": 7.6}        # Zona da Mata: Viçosa, Guarani
GBH = {"lon": -43.85, "lat": -19.74, "zoom": 9.3}     # Grande BH: Sabará, Santa Luzia, Lagoa Santa
MTZ = {"lon": -59.1, "lat": -9.7, "zoom": 7.2}        # Colniza (noroeste do MT)
EP = {"lon": -45.6, "lat": -19.6, "zoom": 5.0}        # Sooretama (ES) e Londrina (PR)
FOG = {"lon": -42.0, "lat": -5.6, "zoom": 5.3}        # fogo: Maranhão, Ceará, Piauí
CAL = {"lon": -42.8, "lat": -6.0, "zoom": 6.0}        # Teresina (PI)
HOJ = {"lon": -52.0, "lat": -16.0, "zoom": 3.95}      # hoje: amarelo do RS ao AM
PREV = {"lon": -53.0, "lat": -16.0, "zoom": 4.0}      # próximos 7 dias (gráfico em cima)
VOL = {"lon": -43.8, "lat": -19.8, "zoom": 5.6}       # volumes: MG, ES
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, MTZ, 20, -4), K(fim("f2") - .2, {**MTZ, "zoom": 7.35}, 22, 2),
    K(ini("f3") + 1.0, GBH, 20, -4), K(fim("f3") - .2, {**GBH, "zoom": 9.4}, 22, 2),
    K(ini("f4") + 1.0, ZM, 20, -4), K(fim("f4") - .2, {**ZM, "zoom": 8.15}, 22, 2),
    K(ini("f5") + 1.0, EP, 16, -4), K(fim("f5") - .2, {**EP, "zoom": 5.35}, 18, 2),
    K(ini("f6") + 1.0, FOG, 24, -4), K(fim("f6") - .2, {**FOG, "zoom": 5.4}, 26, 2),
    K(ini("f7") + 1.0, CAL, 16, 0), K(fim("f7") - .2, {**CAL, "zoom": 6.1}, 18, 2),
    K(ini("f8") + 1.0, HOJ, 10, 0), K(fim("f8") - .2, {**HOJ, "zoom": 4.05}, 12, 2),
    K(ini("f9") + 1.0, PREV, 0, 0), K(fim("f9") - .2, {**PREV, "zoom": 4.1}, 6, 0),
    K(ini("f10") + 1.0, VOL, 10, 0), K(fim("f10") - .2, {**VOL, "zoom": 5.7}, 10, 2),
    K(ini("f11") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-11-13T21") and TS[-1].startswith("2026-11-14T21"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
assert len(BONS) >= 30, f"IR: só {len(BONS)}/{len(TS)} quadros bons"
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- INPE: focos de 13/11 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
# o CSV de 14/11 é parcial (sem AQUA): não usado.
grade, ref, ref_uf = {}, 0, {}
with open(B / "inpe_focos_diario_br_20261113.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-11-13"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
TRIO = ref_uf["MARANHÃO"] + ref_uf["CEARÁ"] + ref_uf["PIAUÍ"]
assert (ref, ref_uf["MARANHÃO"], ref_uf["CEARÁ"], ref_uf["PIAUÍ"], TRIO) == (767, 247, 220, 123, 590), (ref, TRIO)   # "767 focos"
assert 0.74 < TRIO / ref < 0.79, TRIO / ref                                                                       # "três em cada quatro"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["MARANHÃO", "CEARÁ", "PIAUÍ", "PARÁ", "PERNAMBUCO"], RKF
SIGLA = {"MARANHÃO": "MA", "CEARÁ": "CE", "PIAUÍ": "PI", "PARÁ": "PA", "PERNAMBUCO": "PE"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f6"), "fim": ini("f7") + .3, "dados": fogo, "dur": 2.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
conta = lambda i, ufs: [sum(UF[c[:2]] == u for c in geo(i)) for u in ufs]
assert sorted(aviso) == [56404, 56405, 56406, 56408, 56409, 56410], sorted(aviso)
# hoje 14/11: só amarelo (Perigo Potencial); nenhum laranja ou vermelho
assert all(a["severidade"] == "Perigo Potencial" for a in aviso.values()), "apareceu laranja/vermelho: rever f8"
for i in (56404, 56405):
    assert aviso[i]["descricao"] == "Tempestade" and aviso[i]["inicio"].startswith("2026-11-14") and aviso[i]["fim"].startswith("2026-11-14"), i
TEMP = geo(56404) | geo(56405)
TEMP_N = len(TEMP)
assert TEMP_N == 1330, TEMP_N                                                                   # "1.330 cidades"
TEMP_UF = sorted({UF[c[:2]] for c in TEMP})
assert conta(56404, ["MG", "BA"]) == [341, 183] and conta(56405, ["PR"]) == [149]
for i in (56404, 56405, 56408):
    RL = " ".join(aviso[i]["riscos"])
    assert "40-60 km/h" in RL and "granizo" in RL and "100" not in RL, RL                     # "granizo e vento forte"
assert aviso[56408]["descricao"] == "Tempestade" and aviso[56408]["inicio"].startswith("2026-11-15") and len(geo(56408)) == 2633   # "Amanhã, 2.633"
AMANHA_UF = sorted({UF[c[:2]] for c in geo(56408)})
estados = [
    {"id": "f1mt", "ini": CAPA, "fim": em("f1", "Minas"), "ufs": ["MT"], "cor": AZU, "alfa": .4},
    {"id": "f1mg", "ini": em("f1", "Minas"), "fim": ini("f2") + .3, "ufs": ["MG"], "cor": AZU, "alfa": .4},
    {"id": "mt", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["MT"], "cor": AZU, "alfa": .2},
    {"id": "mg", "ini": ini("f3"), "fim": ini("f5") + .3, "ufs": ["MG"], "cor": AZU, "alfa": .2},
    {"id": "espr", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["ES", "PR"], "cor": AZU, "alfa": .2},
    {"id": "fogo", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["MA", "CE", "PI"], "cor": LAR, "alfa": .3},
    {"id": "calor", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": ["PI"], "cor": VERM, "alfa": .35},
    {"id": "amarelo", "ini": ini("f8"), "fim": em("f8", "Amanhã"), "ufs": TEMP_UF, "cor": AMA, "alfa": .4},
    {"id": "amanha", "ini": em("f8", "Amanhã"), "fim": ini("f9") + .3, "ufs": AMANHA_UF, "cor": AMA, "alfa": .28},
    {"id": "vol", "ini": ini("f10"), "fim": ini("f11") + .3, "ufs": ["MG"], "cor": AZU, "alfa": .4},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros (coleta de 14/11 21:23 UTC)
CRU = json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())
EST = lambda u, c, e: [x for x in CRU if (x["uf"], x["cidade"], x["nomeestacao"]) == (u, c, e)]
acc = lambda u, c, e, k="acc24hr": EST(u, c, e)[0][k]
# Visconde do Rio Branco (Rio Xopoto) 123,6 mm com 58 em 6 h: FORA — a chuva da tarde não aparece nas vizinhas nem no IR (na dúvida, de fora)
assert acc("MG", "GUARANI", "G2-312840202A") == 61.8                                               # "Guarani, 61"
assert acc("MG", "VIÇOSA", "São José do Triunfo") == 70.4                                         # "Viçosa, 70"
assert acc("MT", "COLNIZA", "G2-510325402A") == 112.4                                             # "112 em Colniza"
assert acc("MT", "COLNIZA", "G2-510325401A") == 94.6 and acc("MT", "COLNIZA", "G2-510325403A") == 78.0   # "112, 94 e 78"
assert acc("MG", "SABARÁ", "Borba Gato") == 67.57 and acc("MG", "SANTA LUZIA", "Rio das Velhas") == 67.4  # "passaram de 67"
assert acc("ES", "SOORETAMA", "G2-320501002A") == 72.0                                           # "Sooretama 72"
# leituras suspeitas, fora da soma: Pedro Alexandre (BA) 13.124 mm = sensor com defeito; Maragogi (AL) 134,89 com as vizinhas em ~0
PAX = acc("BA", "PEDRO ALEXANDRE", "PEDRO ALEXANDRE")
MGI = acc("AL", "MARAGOGI", "Centro")
VRB = acc("MG", "VISCONDE DO RIO BRANCO", "Rio Xopoto")   # tarde isolada (vizinhas ~0, IR sem topo frio): fora da soma também
assert (PAX, MGI, VRB) == (13124.2, 134.89, 123.6), (PAX, MGI, VRB)
RES = json.loads((B / "resumo.json").read_text())["cemaden"]
SOMA = {u: dict(d) for u, d in RES["soma_por_uf"].items()}
assert RES["soma_mm_estacoes"] == 24466.3 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 24466.3) < .5
SOMA["BA"]["soma_mm"] = round(SOMA["BA"]["soma_mm"] - PAX, 1); SOMA["BA"]["estacoes"] -= 1
SOMA["AL"]["soma_mm"] = round(SOMA["AL"]["soma_mm"] - MGI, 1); SOMA["AL"]["estacoes"] -= 1
SOMA["MG"]["soma_mm"] = round(SOMA["MG"]["soma_mm"] - VRB, 1); SOMA["MG"]["estacoes"] -= 1
BRASIL = round(RES["soma_mm_estacoes"] - PAX - MGI - VRB, 1)
assert BRASIL == 11083.6 and 11000 < BRASIL < 12000, BRASIL                     # "mais de 11 mil"
NEST, NUF = sum(d["estacoes"] for d in SOMA.values()), len(SOMA)
assert (NEST, NUF) == (1297, 25), (NEST, NUF)
RK = sorted(((u, d["soma_mm"]) for u, d in SOMA.items()), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["MG", "BA", "ES", "SP", "RJ"], RK
assert 0.5 < SOMA["MG"]["soma_mm"] / BRASIL < 0.6                               # "mais da metade em Minas"

# ---------------------------------------------------------------- NOAA METAR: calor e vento
MT = json.loads((B / "resumo.json").read_text())["noaa_metar"]
QUENTE = {x[1]: (x[0], x[3]) for x in MT["tmax_top"]}
assert QUENTE["SBTE"][0] == 38 and QUENTE["SBTE"][1].startswith("14/11") and max(v[0] for v in QUENTE.values()) == 38   # "38 graus em Teresina"
assert QUENTE["SBCY"][0] == 37
UR = MT["ur_min_top"][0]
assert UR[:2] == [29, "SBTE"] and UR[4] == 38, UR                                                        # "umidade de 29 por cento"
RJ = {x[1]: x for x in MT["rajada_kmh_top"]}
RAJ = MT["rajada_kmh_top"][0]
assert RAJ[:2] == [56, "SBLS"] and RAJ[3] == "13/11 22:00Z" and "TSRA" in RAJ[4] and "G30KT" in RAJ[4], RAJ   # "Lagoa Santa, rajada de 56 km/h"
assert RJ["SBLO"][0] == 50 and RJ["SBLO"][3] == "14/11 17:23Z" and "G27KT" in RJ["SBLO"][4] and "TSRA" in RJ["SBLO"][4]   # "Londrina, 50 km/h"
NTROV = len(MT["trovoada"])
assert NTROV == 29, NTROV

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-11-14" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sáb", "dom", "seg", "ter", "qua", "qui", "sex"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 827.6   # "mais de 820 milímetros"
TOP1 = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP1["dia"], TOP1["soma_chuva_mm"]) == ("2026-11-16", 165.7), TOP1                                      # "segunda o mais chuvoso"
R7 = P7["soma_7d_por_regiao_mm"]
assert sorted(R7, key=R7.get, reverse=True)[:2] == ["N", "CO"] and (R7["N"], R7["CO"]) == (223.9, 216.3), R7   # "Norte e Centro-Oeste devem acumular mais"
PICO = max((d["tmax_pico"][0], d["dia"], d["tmax_pico"][1]) for d in P7["por_dia"])
assert PICO == (39.6, "2026-11-20", "Teresina"), PICO                                                            # "Teresina perto de 40 graus"
assert P7["acumulado_7d_top"][0] == ["Palmas", 69.6], P7["acumulado_7d_top"][:2]

pinos = [
    {"nome": "Colniza (MT)", "sub": "112,4 mm em 24 h", "lon": -59.03, "lat": -9.46, "ini": ini("f2") + .3, "fim": ini("f3"), "h": 70},
    {"nome": "Sabará (MG)", "sub": "67,6 mm em 24 h", "lon": -43.81, "lat": -19.89, "ini": em("f3", "Sabará"), "fim": ini("f4"), "h": 8},
    {"nome": "Santa Luzia (MG)", "sub": "67,4 mm em 24 h", "lon": -43.85, "lat": -19.77, "ini": em("f3", "Santa"), "fim": ini("f4"), "h": 8},
    {"nome": "Lagoa Santa (MG)", "sub": "rajada de 56 km/h", "lon": -43.89, "lat": -19.63, "ini": em("f3", "Lagoa"), "fim": ini("f4"), "h": 30},
    {"nome": "Viçosa (MG)", "sub": "70,4 mm em 24 h", "lon": -42.88, "lat": -20.75, "ini": em("f4", "Viçosa"), "fim": ini("f5"), "h": 50},
    {"nome": "Guarani (MG)", "sub": "61,8 mm em 24 h", "lon": -43.05, "lat": -21.36, "ini": em("f4", "Guarani"), "fim": ini("f5"), "h": 50},
    {"nome": "Sooretama (ES)", "sub": "72 mm em 24 h", "lon": -40.10, "lat": -19.19, "ini": em("f5", "Sooretama"), "fim": ini("f6"), "h": 25},
    {"nome": "Londrina (PR)", "sub": "rajada de 50 km/h", "lon": -51.16, "lat": -23.31, "ini": em("f5", "Londrina"), "fim": ini("f6"), "h": 50},
    {"nome": "Teresina (PI)", "sub": "38 °C · umidade 29%", "lon": -42.80, "lat": -5.09, "ini": em("f7", "Teresina"), "fim": ini("f8"), "h": 40},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 f'<div class="t4" style="font-size:44px;line-height:1.35">🌧️ 112 mm em Colniza (MT) · ⛈️ temporal em Minas Gerais · 🟡 amarelo em {TEMP_N:,} cidades</div>'.replace(",", ".")}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "CHUVA EM 24 H · NOROESTE DO MT",
     "contador": {"de": 0, "ate": 112, "dec": 0, "ini": em("f2", "112") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM COLNIZA (MT)"},
     "itens": [{"t": em("f2", "94"), "txt": "🌧️ 3 pluviômetros de Colniza: 112,4 · 94,6 · 78 mm"}],
     "l": "CEMADEN, leituras até 14/11 18h10", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "GRANDE BH · 24 H",
     "contador": {"de": 0, "ate": 67, "dec": 0, "ini": em("f3", "67") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM SABARÁ E SANTA LUZIA"},
     "itens": [{"t": em("f3", "Lagoa"), "txt": "💨 Lagoa Santa: rajada de 56 km/h com trovoada (13/11, 19h)"},
               {"t": em("f3", "56") + .6, "txt": "🌧️ Brumadinho 54,6 mm · BH (Taquaril) 48,9 mm"}],
     "l": "CEMADEN · estações dos aeroportos (METAR, NOAA)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "CHUVA EM 24 H · ZONA DA MATA (MG)",
     "contador": {"de": 0, "ate": 70, "dec": 0, "ini": em("f4", "70") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM VIÇOSA (MG)"},
     "itens": [{"t": em("f4", "Guarani"), "txt": "🌧️ Guarani 61,8 · Divino 55 · Pedra Bonita 51,8 mm"}],
     "l": "CEMADEN, leituras até 14/11 18h10", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "ESPÍRITO SANTO E PARANÁ",
     "contador": {"de": 0, "ate": 72, "dec": 0, "ini": em("f5", "72") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM SOORETAMA (ES)"},
     "itens": [{"t": em("f5", "72") + .5, "txt": "🌧️ Jaguaré 60,4 · Colatina 56,2 mm (ES)"},
               {"t": em("f5", "Londrina"), "txt": "💨 Londrina (PR): rajada de 50 km/h com trovoada (14/11, 14h23)"}],
     "l": "CEMADEN · estações dos aeroportos (METAR, NOAA)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "FOGO · SEXTA, 13/11",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f6", "767") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": "FOCOS NO BRASIL"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f6", "três") - .3, "dur": 1.0},
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência AQUA (INPE)", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "CALOR · SÁBADO (14/11)",
     "contador": {"de": 25, "ate": 38, "dec": 0, "ini": em("f7", "38") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "°C EM TERESINA (PI)"},
     "itens": [{"t": em("f7", "umidade"), "txt": "💧 umidade do ar em 29% · 37 °C em Cuiabá (MT)"}],
     "l": "estações dos aeroportos (METAR, NOAA)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "HOJE · AVISO AMARELO DE TEMPESTADE",
     "contador": {"de": 0, "ate": TEMP_N, "dec": 0, "ini": em("f8", "1.330") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES · MG 341 · BA 183 · PR 149"},
     "itens": [{"t": em("f8", "granizo"), "txt": "até 50 mm no dia, vento de 40 a 60 km/h e granizo · nenhum laranja"},
               {"t": em("f8", "Amanhã"), "txt": "⏭️ Amanhã (15/11): amarelo de tempestade em 2.633 cidades"}],
     "l": "avisos do INMET · é aviso, pode mudar", "borda": "rgba(250,204,21,.85)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f9") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "itens": [{"t": em("f9", "segunda"), "txt": "🌧️ Segunda (16/11): 165,7 mm somados nas capitais"},
               {"t": em("f9", "Teresina"), "txt": "🔥 Teresina: 39,6 °C previstos na sexta (20/11)"}],
     "l": "previsão Open-Meteo · Norte 223,9 e Centro-Oeste 216,3 mm na semana · Palmas 69,6 mm", "borda": "rgba(251,146,60,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f10", "mil") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM · {NEST:,} PLUVIÔMETROS EM {NUF} UFS".replace(",", ".")},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f10", "metade") - .3, "dur": 1.2},
     "itens": [{"t": em("f10", "820"), "txt": "7 dias nas capitais: 827,6 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · sem 3 leituras suspeitas (Pedro Alexandre-BA, Maragogi-AL, Visconde do Rio Branco-MG)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f11", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 13/11 18h a 14/11 18h · <b>CEMADEN</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>CEMADEN</b>: pluviômetros, chuva em 24 h até 14/11 18h"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>CEMADEN</b>: pluviômetros, chuva até 14/11 18h · vento: METAR da <b>NOAA</b>"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>CEMADEN</b>: pluviômetros, chuva em 24 h até 14/11 18h"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>CEMADEN</b> · vento e trovoada nos aeroportos: METAR da <b>NOAA</b>"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INPE</b>: focos de 13/11 no AQUA tarde, satélite de referência"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Temperatura e umidade medidas nos aeroportos: METAR da <b>NOAA</b> (14/11)"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>INMET</b>: amarelo de tempestade hoje ({TEMP_N:,} municípios) e amanhã (2.633) · é aviso, pode mudar".replace(",", ".")},
    {"ini": ini("f9"), "fim": ini("f10"), "html": "Previsão <b>Open-Meteo</b> (14/11 a 20/11) nas 27 capitais · é previsão, pode mudar"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST:,} pluviômetros)".replace(",", ".") + " · previsão <b>Open-Meteo</b>: 827,6 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"enxurrada": "#5ec8ff", "desalojados": "#ff2a1f", "severo": "#ff2a1f", "forte": "#ff8c1a", "chuvosa": "#5ec8ff", "temporal": "#ff8c1a", "ventania": "#ff8c1a", "arvores": "#ff8c1a", "umidade": "#ff2a1f", "chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff", "acumular": "#5ec8ff",
         "acumulada": "#5ec8ff", "alagamento": "#5ec8ff", "deslizamento": "#ff8c1a", "rajada": "#ff8c1a", "trovoada": "#ff8c1a",
         "tempestade": "#ff8c1a", "granizo": "#ff8c1a", "aviso": AM, "amarelo": AM, "alerta": "#ff2a1f", "vento": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "triplicou": "#ff2a1f", "calor": "#ff2a1f",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"guarani", "mata", "sabara", "lagoa", "sooretama", "londrina", "gerais", "goiania", "colniza", "mato", "grosso", "campo", "uberlandia", "noroeste", "estado", "minas", "vicosa", "luzia", "bh", "belo", "horizonte",
         "congonhas", "maranhao", "ceara", "piaui", "sexta", "sabado", "centrooeste", "grande", "sao", "paulo", "mogi", "cruzes", "zona", "leste", "capital", "tiradentes", "maua", "defesa", "civil", "porto",
         "velho", "aeroporto", "norte", "espirito", "santo", "pedro", "canario", "para", "teresina", "centrooeste", "quinta",
         "domingo", "segunda", "hoje", "amanha", "capitais", "cidades", "inemaclub", "cidade", "regiao", "pais"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        if bloco and sum(len(x["w"]) + 1 for x in bloco) + len(w) > 19:   # bloco largo corta na borda ("derrubar a temperatura")
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["t"] + .12, "palavras": bloco})
            bloco = []
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:;" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · CLIMA 24 H", "selo": "CEMADEN · INMET · INPE · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · "
      f"amarelo {TEMP_N} · fogo {len(fogo)} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
