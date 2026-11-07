#!/usr/bin/env python3
"""Monta cena.js do "Impacto Sul" de 06/11/2026 a partir de tempos.json (palavras da narração),
da meteorologia do dia no Sul (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da chuva/rajada prevista de 07 a 08/11 na grade do Brasil (Open-Meteo, om/prev15_grade.json, lida em 06/11,
copiada da edição 2026-11-06-clima-do-dia).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png descida 130 px, original em abertura-orig.png; "GRANIZO DESTRÓI LAVOURAS / 3 ESTADOS DO SUL / NESTA SEXTA · 06/11"),
Alpestre (RS) com gelo no chão (foto do Codex, ilustração), oeste catarinense e Paraná com tabaco destruído (foto do Codex,
ilustração), choque do ar frio com a umidade da Amazônia (câmera inclinada, IR do GOES-19), chuva forte no sábado de manhã,
INMET tempestade no sábado em 1.107 cidades do Sul, colunas 3D da chuva prevista de 07 a 08/11 (84 mm), rajada de 72 km/h
perto de Curitiba, sábado = maior risco, domingo com queda de temperatura em todo o Sul.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "06/11/2026"
MET = "Meteorologia · " + DATA
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / (os.environ.get("TEMPOS") or ("avatar/tempos.json" if AVATAR else "tempos.json"))).read_text())
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
LAR, AMA, VERM, AZUL, FRIO, GELO = [255, 140, 26], [250, 204, 21], [255, 42, 31], [60, 150, 255], [150, 210, 255], [235, 245, 255]

# ---------------------------------------------------------------- câmera (sempre fechada no Sul)
SUL = {"lon": -51.4, "lat": -27.4, "zoom": 5.35}       # f1: RS, SC e PR
ALP = {"lon": -53.03, "lat": -27.25, "zoom": 7.6}      # f2: Alpestre (RS)
OESTE = {"lon": -52.9, "lat": -26.5, "zoom": 6.5}      # f3: oeste catarinense e sudoeste do Paraná
AMZ = {"lon": -54.0, "lat": -21.0, "zoom": 4.6}       # f4: corredor de umidade da Amazônia até o Sul (câmera inclinada)
NORTE = {"lon": -51.8, "lat": -26.8, "zoom": 5.7}      # f5: norte gaúcho, oeste catarinense e Paraná
COL = {"lon": -51.4, "lat": -28.0, "zoom": 5.8}        # f7: colunas 3D da chuva prevista de 07 a 08/11
CWB = {"lon": -49.4, "lat": -25.45, "zoom": 7.2}       # f8: Curitiba
RISCO = {"lon": -52.6, "lat": -27.5, "zoom": 6.3}      # f9: oeste catarinense e norte gaúcho
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.0  # quadro 0 = capa cheia do Codex até aqui
camera = [
    K(0, SUL), K(CAPA, SUL), K(fim("f1") - .2, {**SUL, "zoom": 5.5}, 0, 0),
    K(ini("f2") + 1.0, ALP, 38, -8), K(fim("f2") - .2, {**ALP, "zoom": 7.8}, 44, 6),
    K(ini("f3") + 1.0, OESTE, 20, 0), K(fim("f3") - .2, {**OESTE, "zoom": 6.65}, 24, 6),
    K(ini("f4") + 1.2, AMZ, 0, 0), K(fim("f4") - .2, {**AMZ, "zoom": 4.7}, 0, 0),
    K(ini("f5") + 1.0, NORTE, 0, 0), K(fim("f5") - .2, {**NORTE, "zoom": 5.8}, 4, 0),
    K(ini("f6") + 1.0, SUL, 0, 0), K(fim("f6") - .2, {**SUL, "zoom": 5.45}, 0, 0),
    K(ini("f7") + 1.2, COL, 55, -20), K(fim("f7") - .2, {**COL, "zoom": 5.9}, 56, 14),
    K(ini("f8") + 1.0, CWB, 30, 0), K(fim("f8") - .2, {**CWB, "zoom": 7.35}, 34, 6),
    K(ini("f9") + 1.0, RISCO, 0, 0), K(fim("f9") - .2, {**RISCO, "zoom": 6.4}, 4, 0),
    K(ini("f10") + 1.0, SUL, 0, 0), K(fim("f10") - .2, {**SUL, "zoom": 5.45}, 0, 0),
    K(ini("f11") + 1.4, {**SUL, "zoom": 5.2}, 0, 0), K(DUR, {**SUL, "zoom": 5.3}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) no choque de massas (f4)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 130]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# IR com borda esmaecida (irfNN.png, alfa nas bordas, feito desta edição a partir de irNN.jpg) e o Blue Marble do mundo por baixo do geocolor (sem borda preta)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/irf{i:02d}.png" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": ini("f4") - .3, "fim": ini("f5") + .3, "dur": ini("f5") - ini("f4") + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])
assert len(BONS) >= 36, f"poucos quadros bons de infravermelho: {len(BONS)}"
imagens = []

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de 07 a 08/11 (Open-Meteo, grade de 1,5°)
G15 = json.loads((AQUI / "om/prev15_grade.json").read_text())
CS = {"RS", "SC", "PR"}
dias = G15["pts"][0]["dias"]
ND = 2
assert dias[0] == "2026-11-07" and dias[ND - 1] == "2026-11-08", (dias[0], dias[ND - 1])
SUL_PTS = [p for p in G15["pts"] if p["uf"] in CS]
SOMA = [(p, round(sum(x or 0 for x in p["chuva"][:ND]))) for p in SUL_PTS]
col = [{"id": i, "p": p["p"], "v": v, "cor": [60, 150, 255] if v >= 50 else [120, 190, 255]} for i, (p, v) in enumerate(SOMA) if v >= 15]
ordem = {c["id"]: (-c["p"][1] - 25) * .12 for c in col}   # sobe do RS para SC e o PR
colunas = [{"id": "chuva3d", "ini": ini("f7") + .3, "fim": ini("f8") + .3, "dados": col, "raio": 60000, "escala": 4200, "ordem": ordem, "varredura": 1}]
TOPO = max(SOMA, key=lambda x: x[1])
assert TOPO[1] == 84 and TOPO[0]["uf"] == "RS" and len(col) >= 6, (TOPO[0]["uf"], TOPO[1], len(col))   # a fala f7 diz "84 milímetros"
RAJ = max(SUL_PTS, key=lambda p: p["raj"][0])
assert round(RAJ["raj"][0]) == 72 and RAJ["uf"] == "PR", (RAJ["uf"], RAJ["raj"][0])                      # a fala f8 diz "72 quilômetros por hora"

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, gelo e tabaco
GELO_T = em("f2", "gelo")
TAB = em("f3", "tabaco")
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/gelo.png", "ini": GELO_T - .1, "fim": em("f2", "tarde") - .1, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/tabaco.png", "ini": TAB - .1, "fim": fim("f3") - .1, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET (sábado 07/11 e domingo 08/11) no Sul
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
UFCOD = {"41": "PR", "42": "SC", "43": "RS"}
from collections import Counter
sul = lambda i: Counter(UFCOD[c[:2]] for c in geo(i) if c[:2] in UFCOD)
assert aviso[56308]["descricao"] == "Tempestade" and aviso[56308]["inicio"].startswith("2026-11-07"), aviso[56308]["descricao"]
TEMP_SUL = sul(56308)                                  # tempestade no sábado (todas as severidades: 56308 contém 56309 e 56310)
assert (TEMP_SUL["PR"], TEMP_SUL["SC"], TEMP_SUL["RS"]) == (399, 295, 413), TEMP_SUL
assert sum(TEMP_SUL.values()) == 1107, TEMP_SUL       # a fala f6 diz "1.107 cidades do Sul"
assert aviso[56281]["descricao"] == "Declínio de Temperatura" and aviso[56281]["inicio"].startswith("2026-11-08"), aviso[56281]["descricao"]
FRIO_SUL = sul(56281)                                  # declínio de temperatura no domingo: todo o Sul
assert (FRIO_SUL["PR"], FRIO_SUL["SC"], FRIO_SUL["RS"]) == (399, 295, 497), FRIO_SUL   # a fala f10 diz "todo o Sul"
NFRIO = sum(FRIO_SUL.values())

# ---------------------------------------------------------------- estados
estados = [
    {"id": "gr1", "ini": em("f1", "estados"), "fim": ini("f2") + .3, "ufs": ["RS", "SC", "PR"], "cor": GELO, "alfa": .32},
    {"id": "rs2", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["RS"], "cor": GELO, "alfa": .28},
    {"id": "sc3", "ini": em("f3", "catarinense"), "fim": ini("f4") + .3, "ufs": ["SC"], "cor": GELO, "alfa": .3},
    {"id": "pr3", "ini": em("f3", "Paraná"), "fim": ini("f4") + .3, "ufs": ["PR"], "cor": GELO, "alfa": .3},
    {"id": "chuva5", "ini": em("f5", "chover"), "fim": ini("f6") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .32},
    {"id": "temp6", "ini": em("f6", "tempestade"), "fim": ini("f7") + .3, "ufs": ["RS", "SC", "PR"], "cor": LAR, "alfa": .42},
    {"id": "chuva7", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": ["RS", "SC"], "cor": AZUL, "alfa": .3},
    {"id": "pr8", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["PR"], "cor": FRIO, "alfa": .3},
    {"id": "risco9", "ini": em("f9", "atenção"), "fim": ini("f10") + .3, "ufs": ["RS", "SC"], "cor": VERM, "alfa": .4},
    {"id": "frio10", "ini": em("f10", "despenca"), "fim": ini("f11") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .4},
]

H = em("f1", "impacto") - .1   # o hero (data grande) fica até "impacto"
pinos = [
    {"nome": "Rio Grande do Sul", "sub": "granizo hoje", "lon": -53.0, "lat": -28.9, "ini": H, "fim": ini("f2"), "h": 100},
    {"nome": "Santa Catarina", "sub": "granizo hoje", "lon": -50.4, "lat": -27.2, "ini": H + .3, "fim": ini("f2"), "h": 230},
    {"nome": "Paraná", "sub": "granizo hoje", "lon": -52.6, "lat": -24.8, "ini": H + .6, "fim": ini("f2"), "h": 140},
    {"nome": "Alpestre (RS)", "sub": "gelo cobriu o chão", "lon": -53.03, "lat": -27.25, "ini": em("f2", "Alpestre"), "fim": GELO_T - .1, "h": 260},
    {"nome": "Alpestre (RS)", "sub": "granizo na tarde de hoje", "lon": -53.03, "lat": -27.25, "ini": em("f2", "tarde") - .1, "fim": ini("f3"), "h": 260},
    {"nome": "oeste catarinense", "sub": "granizo nas lavouras", "lon": -52.9, "lat": -26.95, "ini": em("f3", "catarinense"), "fim": TAB - .1, "h": 200},
    {"nome": "Paraná", "sub": "granizo em áreas isoladas", "lon": -53.05, "lat": -26.0, "ini": em("f3", "Paraná"), "fim": TAB - .1, "h": 150},
    {"nome": "Amazônia", "sub": "corredor de umidade", "lon": -58.0, "lat": -14.5, "ini": em("f4", "Amazônia"), "fim": ini("f5"), "h": 70},
    {"nome": "Sul", "sub": "ar frio da manhã", "lon": -52.0, "lat": -28.5, "ini": em("f4", "frio"), "fim": ini("f5"), "h": 160},
    {"nome": "norte gaúcho", "sub": "chuva forte sábado de manhã", "lon": -52.4, "lat": -28.3, "ini": em("f5", "gaúcho"), "fim": ini("f6"), "h": 160},
    {"nome": "oeste catarinense", "sub": "chuva forte sábado", "lon": -52.6, "lat": -26.9, "ini": em("f5", "catarinense"), "fim": ini("f6"), "h": 260},
    {"nome": "Paraná", "sub": "chuva forte sábado", "lon": -51.6, "lat": -25.0, "ini": em("f5", "Paraná"), "fim": ini("f6"), "h": 400},
    {"nome": f"{TOPO[1]} mm até 08/11", "sub": "nordeste gaúcho · soma prevista · Open-Meteo", "lon": TOPO[0]["p"][0], "lat": TOPO[0]["p"][1],
     "ini": em("f7", "84"), "fim": ini("f8"), "h": 220},
    {"nome": "Curitiba", "sub": "rajadas de até 72 km/h no sábado", "lon": -49.27, "lat": -25.43, "ini": em("f8", "Curitiba"), "fim": ini("f9"), "h": 240},
    {"nome": "oeste catarinense", "sub": "maior risco no sábado", "lon": -52.6, "lat": -26.9, "ini": em("f9", "catarinense"), "fim": ini("f10"), "h": 260},
    {"nome": "norte gaúcho", "sub": "maior risco no sábado", "lon": -52.4, "lat": -28.3, "ini": em("f9", "gaúcho"), "fim": ini("f10"), "h": 160},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)   # número dito logo no começo da fala: o contador começa com a fala
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">IMPACTO SUL</div>'
                 '<div class="t1" style="font-size:104px">GRANIZO</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">lavouras destruídas em 3 estados</div>'}]
paineis = [
    {"ini": H, "fim": ini("f2"), "k": "GRANIZO · SEXTA 06/11",
     "itens": [{"t": H, "txt": "🧊 RS · SC · PR"}],
     "l": "lavouras atingidas", "borda": "rgba(235,245,255,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "ALPESTRE (RS) · HOJE À TARDE",
     "itens": [{"t": em("f2", "Alpestre"), "txt": "📍 norte gaúcho"},
               {"t": GELO_T, "txt": "🧊 gelo cobriu o chão"}],
     "borda": "rgba(235,245,255,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "GRANIZO · HOJE À TARDE",
     "itens": [{"t": em("f3", "catarinense"), "txt": "🧊 oeste catarinense"},
               {"t": em("f3", "Paraná"), "txt": "🧊 áreas do Paraná"},
               {"t": TAB, "txt": "🌿 tabaco destruído"}],
     "borda": "rgba(235,245,255,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "A CAUSA",
     "itens": [{"t": em("f4", "frio"), "txt": "❄️ ar frio da manhã"},
               {"t": em("f4", "umidade"), "txt": "💧 umidade da Amazônia"},
               {"t": em("f4", "Niño"), "txt": "🌡️ ano de El Niño"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "SÁBADO DE MANHÃ · PREVISÃO",
     "itens": [{"t": em("f5", "gaúcho"), "txt": "🌧️ norte gaúcho"},
               {"t": em("f5", "catarinense"), "txt": "🌧️ oeste catarinense"},
               {"t": em("f5", "Paraná"), "txt": "🌧️ Paraná"}],
     "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "INMET · TEMPESTADE · SÁBADO 07/11",
     "contador": conta(1107, "f6", "1.107", "#ff8c1a", "CIDADES NO SUL"),
     "l": f"PR {TEMP_SUL['PR']} (todas), SC {TEMP_SUL['SC']} (todas), RS {TEMP_SUL['RS']}", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SÁBADO E DOMINGO · CHUVA",
     "contador": conta(84, "f7", "84", "#5ec8ff", "MM PREVISTOS"),
     "l": "colunas: chuva prevista somada de 07 a 08/11 · Open-Meteo", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CURITIBA · SÁBADO 07/11",
     "contador": conta(72, "f8", "72", "#96d2ff", "KM/H EM RAJADAS"),
     "l": "previsão · Open-Meteo", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "ATENÇÃO",
     "itens": [{"t": em("f9", "catarinense"), "txt": "⚠️ oeste catarinense"},
               {"t": em("f9", "gaúcho"), "txt": "⚠️ norte gaúcho"},
               {"t": em("f9", "sábado"), "txt": "🔴 sábado: maior risco"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "DOMINGO 08/11 · PREVISÃO",
     "itens": [{"t": em("f10", "despenca"), "txt": "🥶 temperatura despenca"},
               {"t": em("f10", "INMET"), "txt": f"⚠️ INMET: {NFRIO:,} cidades".replace(",", ".")}],
     "l": "declínio de temperatura no RS, SC e PR", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "cidade"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f11", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
     "borda": "rgba(250,204,21,.8)"},
]
for a, b in zip(paineis, paineis[1:]):
    assert a["fim"] <= b["ini"] + 1e-6, (a["k"], b["k"])
for a in paineis:
    if a.get("contador"):
        c = a["contador"]
        assert a["ini"] - .01 <= c["ini"] and c["ini"] + c["dur"] <= a["fim"], ("contador fora do painel", a["k"])

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f4"), "html": f"<b>{MET}</b> · fotos do granizo e do tabaco: ilustração"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INMET</b>, aviso de tempestade de 07/11"},
    {"ini": ini("f7"), "fim": ini("f9"), "html": "<b>Open-Meteo</b>, previsão lida em 06/11 · chuva somada de 07 a 08/11 e rajada de 07/11"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f10"), "fim": DUR, "html": "<b>INMET</b>, aviso de declínio de temperatura de 08/11"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chover": "#5ec8ff", "milimetros": "#5ec8ff", "umidade": "#5ec8ff", "frio": "#96d2ff",
         "despenca": "#96d2ff", "granizo": "#e6f3ff", "gelo": "#e6f3ff", "destroi": "#ff2a1f", "destruidas": "#ff2a1f",
         "tempestade": "#ff8c1a", "aviso": "#ff8c1a", "atencao": "#ff2a1f", "risco": "#ff2a1f", "dispara": "#ff2a1f",
         "rajadas": "#96d2ff", "quilometros": "#96d2ff", "abafada": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "parana", "santa", "catarina", "catarinense", "gaucho", "alpestre", "amazonia", "curitiba", "oeste",
         "inemaclub", "cidade"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        if bloco and len(" ".join(b["w"] for b in bloco) + " " + w) > 19:   # teto de 19 caracteres: bloco longo corta na borda do 9:16
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": t["palavras"][i - 1]["f"] + .12, "palavras": bloco})
            bloco = []
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · IMPACTO SUL", "selo": DATA[:5] + " · INMET · Open-Meteo · NOAA",
     "camera": camera, "sat": SAT, "imagens": imagens, "colunas": colunas, "telas": telas, "estados": estados, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"INMET tempestade sábado no Sul {sum(TEMP_SUL.values())} · declínio domingo {NFRIO} · colunas {len(col)} "
      f"(máx {TOPO[0]['uf']} {TOPO[1]} mm) · rajada {RAJ['uf']} {RAJ['raj'][0]} km/h")
