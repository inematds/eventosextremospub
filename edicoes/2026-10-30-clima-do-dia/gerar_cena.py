#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 30/10/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da chuva prevista de 30/10 a 13/11 na grade do Brasil (Open-Meteo, om/prev15_grade.json, gravado por
coleta/previsao15d.py --dia 2026-10-29).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "a chuva de um mês em 15 dias", Minas e Rio), faixa de nuvens
do sul do Pará ao Sudeste no infravermelho do GOES-19, chuva forte hoje em Juiz de Fora, serra do Rio, Grande Rio e sul do ES,
pancadas em Goiás e garoa em SP (mínima 13 °C), granizo de madrugada no oeste de SC (foto do Codex, ilustração),
aviso de chuvas intensas do INMET hoje (Minas 795 → Brasil 2.166), Piauí quente (Teresina 37, interior 40 °C),
frio no sábado na serra de SC (5 a 7 °C), colunas 3D da chuva prevista até 13/11 (Open-Meteo), queda brusca da
temperatura de 4 a 12/11 com geada na serra (foto do Codex, ilustração).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "30/10/2026"
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
LAR, AMA, VERM, AZUL, FRIO = [255, 140, 26], [250, 204, 21], [255, 42, 31], [60, 150, 255], [150, 210, 255]

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
SE = {"lon": -44.0, "lat": -20.5, "zoom": 5.0}         # f1: Minas e Rio
FAIXA = {"lon": -47.5, "lat": -14.5, "zoom": 4.25}     # f2: faixa de nuvens do sul do Pará ao Sudeste (IR)
SERRA = {"lon": -42.9, "lat": -22.0, "zoom": 6.3}      # f3: Juiz de Fora, serra do Rio, Grande Rio, sul do ES
CO = {"lon": -48.0, "lat": -19.5, "zoom": 5.0}         # f4: Goiânia, Brasília, São Paulo
OSC = {"lon": -52.3, "lat": -27.2, "zoom": 6.6}        # f5: Xanxerê e Chapecó
INM = {"lon": -48.5, "lat": -20.0, "zoom": 4.1}        # f6: Minas e depois o Brasil (aviso do INMET)
PI = {"lon": -42.5, "lat": -7.0, "zoom": 5.4}          # f7: Piauí
SSC = {"lon": -50.0, "lat": -28.0, "zoom": 6.3}        # f8: serra de SC
COL = {"lon": -48.0, "lat": -21.5, "zoom": 4.75}       # f9: colunas 3D da chuva prevista até 13/11
FRIA = {"lon": -50.5, "lat": -25.5, "zoom": 4.9}       # f10: Sul e Sudeste esfriando
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.0  # quadro 0 = capa cheia do Codex até aqui
GRANIZO = em("f5", "granizo")
GEADA = em("f10", "geada")
BR6 = em("f6", "2.166")
camera = [
    K(0, BR), K(CAPA, BR), K(ini("f1") + 3.2, SE), K(fim("f1") - .2, {**SE, "zoom": 5.15}, 0, 0),
    K(ini("f2") + 1.2, FAIXA, 0, 0), K(fim("f2") - .2, {**FAIXA, "zoom": 4.35}, 0, 0),
    K(ini("f3") + 1.2, SERRA, 40, -10), K(fim("f3") - .2, {**SERRA, "zoom": 6.4}, 45, 6),
    K(ini("f4") + 1.0, CO, 0, 0), K(fim("f4") - .2, {**CO, "zoom": 5.1}, 4, 0),
    K(ini("f5") + 1.0, OSC, 35, -8), K(fim("f5") - .2, {**OSC, "zoom": 6.7}, 40, 4),
    K(ini("f6") + 1.0, {"lon": -44.5, "lat": -18.5, "zoom": 5.1}, 0, 0), K(BR6 - .6, {"lon": -44.5, "lat": -18.5, "zoom": 5.15}, 0, 0),
    K(BR6 + .6, INM, 0, 0), K(fim("f6") - .2, {**INM, "zoom": 4.15}, 0, 0),
    K(ini("f7") + 1.0, PI, 0, 0), K(fim("f7") - .2, {**PI, "zoom": 5.5}, 4, 0),
    K(ini("f8") + 1.0, SSC, 35, -8), K(fim("f8") - .2, {**SSC, "zoom": 6.4}, 40, 4),
    K(ini("f9") + 1.0, COL, 55, -20), K(em("f9", "Espírito"), {**COL, "zoom": 4.85}, 56, 0), K(fim("f9") - .2, {**COL, "zoom": 4.9}, 56, 18),
    K(ini("f10") + 1.0, FRIA, 0, 0), K(fim("f10") - .2, {**FRIA, "zoom": 5.0}, 4, 0),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na faixa de nuvens (f2)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 130]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# câmera inclinada: o Blue Marble do mundo por baixo do geocolor (sem borda preta)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": ini("f2") - .3, "fim": ini("f3") + .3, "dur": ini("f3") - ini("f2") + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])
assert len(BONS) >= 36, f"poucos quadros bons de infravermelho: {len(BONS)}"
imagens = []

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de 30/10 a 13/11 (Open-Meteo, grade de 1,5°)
G15 = json.loads((AQUI / "om/prev15_grade.json").read_text())
CS = {"MG", "GO", "DF", "RJ", "ES", "PR"}   # onde o boletim diz que chove muito até 13/11
dias = G15["pts"][0]["dias"]
assert dias[0] == "2026-10-30" and dias[14] == "2026-11-13", (dias[0], dias[14])
SOMA = [(p, round(sum(x or 0 for x in p["chuva"][:15]))) for p in G15["pts"] if p["uf"] in CS]
C100 = sum(v >= 100 for p, v in SOMA)
col = [{"id": i, "p": p["p"], "v": v, "cor": [60, 150, 255] if v >= 100 else [120, 190, 255]} for i, (p, v) in enumerate(SOMA) if v >= 40]
ordem = {c["id"]: (c["p"][1] + 26) * .05 for c in col}   # sobe do Paraná para Minas e Goiás
colunas = [{"id": "chuva3d", "ini": ini("f9") + .2, "fim": ini("f10") + .2, "dados": col, "raio": 70000, "escala": 2600, "ordem": ordem, "varredura": 1}]
TOPO_MG = max((x for x in SOMA if x[0]["uf"] == "MG"), key=lambda x: x[1])
TOPO_PR = max((x for x in SOMA if x[0]["uf"] == "PR"), key=lambda x: x[1])
assert TOPO_MG[1] == 170 and TOPO_PR[1] == 175, (TOPO_MG[1], TOPO_PR[1])

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, granizo e geada
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": GRANIZO - .1, "fim": ini("f6") + .3, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/geada.png", "ini": GEADA - .1, "fim": ini("f11") + .3, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
for i in (56221, 56222):
    assert aviso[i]["descricao"] == "Chuvas Intensas" and aviso[i]["inicio"].startswith("2026-10-30"), i
HOJE_CI = geo(56221) | geo(56222)   # chuvas intensas hoje 30/10: Sudeste/Centro-Oeste 1.500 (MG 795) + Sul 666
assert len(HOJE_CI) == 2166, len(HOJE_CI)
SECO = geo(56226)                   # baixa umidade 30/10 a 01/11: 665 (PI 187)
assert aviso[56226]["descricao"] == "Baixa Umidade", aviso[56226]["descricao"]
UFCOD = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN",
         "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC",
         "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
from collections import Counter
POR_UF = Counter(UFCOD[c[:2]] for c in HOJE_CI)
assert POR_UF["MG"] == 795, POR_UF["MG"]
HOJE_UF = [u for u, k in POR_UF.items() if k >= 40]   # estados com 40+ municípios no aviso
SECO_UF = [u for u, k in Counter(UFCOD[c[:2]] for c in SECO).items() if k >= 40]

# ---------------------------------------------------------------- estados
estados = [
    {"id": "a_mg", "ini": em("f1", "Minas"), "fim": ini("f2") + .3, "ufs": ["MG"], "cor": LAR, "alfa": .4},
    {"id": "a_rj", "ini": em("f1", "Rio"), "fim": ini("f2") + .3, "ufs": ["RJ"], "cor": LAR, "alfa": .45},
    {"id": "faixa", "ini": em("f2", "faixa"), "fim": ini("f3") + .3, "ufs": ["PA", "TO", "MT", "GO", "DF", "MG", "RJ", "ES"], "cor": AZUL, "alfa": .25},
    {"id": "s_mg", "ini": em("f3", "Juiz"), "fim": ini("f4") + .3, "ufs": ["MG"], "cor": LAR, "alfa": .3},
    {"id": "s_rj", "ini": em("f3", "serra"), "fim": ini("f4") + .3, "ufs": ["RJ"], "cor": LAR, "alfa": .4},
    {"id": "s_es", "ini": em("f3", "Espírito"), "fim": ini("f4") + .3, "ufs": ["ES"], "cor": LAR, "alfa": .4},
    {"id": "c_go", "ini": em("f4", "Goiás"), "fim": ini("f5") + .3, "ufs": ["GO", "DF"], "cor": AZUL, "alfa": .35},
    {"id": "c_sp", "ini": em("f4", "Paulo"), "fim": ini("f5") + .3, "ufs": ["SP"], "cor": FRIO, "alfa": .35},
    {"id": "g_sc", "ini": em("f5", "Santa"), "fim": GRANIZO, "ufs": ["SC"], "cor": AZUL, "alfa": .4},
    {"id": "i_mg", "ini": em("f6", "795") - 1.0, "fim": BR6 - .1, "ufs": ["MG"], "cor": LAR, "alfa": .45},
    {"id": "i_br", "ini": BR6 - .1, "fim": ini("f7") + .3, "ufs": HOJE_UF, "cor": LAR, "alfa": .35},
    {"id": "calor", "ini": em("f7", "Piauí"), "fim": ini("f8") + .3, "ufs": ["PI"], "cor": VERM, "alfa": .45},
    {"id": "seco", "ini": em("f7", "interior"), "fim": ini("f8") + .3, "ufs": [u for u in SECO_UF if u != "PI"], "cor": VERM, "alfa": .3},
    {"id": "frio_sc", "ini": em("f8", "frio"), "fim": ini("f9") + .3, "ufs": ["SC", "RS", "PR"], "cor": FRIO, "alfa": .4},
    {"id": "frio2", "ini": em("f10", "temperatura"), "fim": GEADA, "ufs": ["RS", "SC", "PR", "SP", "MG", "RJ", "ES", "MS"], "cor": FRIO, "alfa": .35},
]

pinos = [
    {"nome": "Minas e Rio", "sub": "chuva forte hoje (previsão)", "lon": -43.4, "lat": -21.6, "ini": em("f1", "forte"), "fim": ini("f2"), "h": 200},
    {"nome": "Sul do Pará", "sub": "início da faixa de nuvens", "lon": -51.0, "lat": -8.0, "ini": em("f2", "Pará"), "fim": ini("f3"), "h": 200},
    {"nome": "Juiz de Fora", "sub": "chuva forte hoje", "lon": -43.35, "lat": -21.76, "ini": em("f3", "Juiz"), "fim": ini("f4"), "h": 260},
    {"nome": "Serra do Rio", "sub": "Petrópolis · chuva forte", "lon": -43.18, "lat": -22.51, "ini": em("f3", "serra"), "fim": ini("f4"), "h": 200},
    {"nome": "Grande Rio", "sub": "chuva forte hoje", "lon": -43.2, "lat": -22.9, "ini": em("f3", "Grande"), "fim": ini("f4"), "h": 120},
    {"nome": "Sul do ES", "sub": "Cachoeiro · chuva forte", "lon": -41.11, "lat": -20.85, "ini": em("f3", "Espírito"), "fim": ini("f4"), "h": 180},
    {"nome": "Goiânia", "sub": "pancadas hoje", "lon": -49.25, "lat": -16.68, "ini": em("f4", "Goiânia"), "fim": ini("f5"), "h": 200},
    {"nome": "Brasília", "sub": "pancadas hoje", "lon": -47.88, "lat": -15.79, "ini": em("f4", "Brasília"), "fim": ini("f5"), "h": 280},
    {"nome": "São Paulo", "sub": "garoa · mínima de 13 °C", "lon": -46.63, "lat": -23.55, "ini": em("f4", "Paulo"), "fim": ini("f5"), "h": 160},
    {"nome": "Chapecó", "sub": "trovoada de madrugada", "lon": -52.62, "lat": -27.10, "ini": em("f5", "trovoada"), "fim": GRANIZO - .1, "h": 160},
    {"nome": "Xanxerê", "sub": "trovoada de madrugada", "lon": -52.40, "lat": -26.87, "ini": em("f5", "madrugada"), "fim": GRANIZO - .1, "h": 260},
    {"nome": "Teresina", "sub": "37 °C hoje (previsão)", "lon": -42.80, "lat": -5.09, "ini": em("f7", "Teresina"), "fim": ini("f8"), "h": 200},
    {"nome": "Interior do Piauí", "sub": "até 40 °C (previsão)", "lon": -42.5, "lat": -8.5, "ini": em("f7", "interior"), "fim": ini("f8"), "h": 160},
    {"nome": "São Joaquim", "sub": "5 a 7 °C no sábado (previsão)", "lon": -49.93, "lat": -28.29, "ini": em("f8", "serra"), "fim": ini("f9"), "h": 220},
    {"nome": f"{TOPO_MG[1]} mm até 13/11", "sub": "Minas · soma prevista · Open-Meteo", "lon": TOPO_MG[0]["p"][0], "lat": TOPO_MG[0]["p"][1],
     "ini": em("f9", "Minas"), "fim": ini("f10"), "h": 120},
    {"nome": f"{TOPO_PR[1]} mm até 13/11", "sub": "Paraná · soma prevista · Open-Meteo", "lon": TOPO_PR[0]["p"][0], "lat": TOPO_PR[0]["p"][1],
     "ini": em("f9", "Paraná"), "fim": ini("f10"), "h": 220},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)   # número dito logo no começo da fala: o contador começa com a fala
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
H = em("f1", "15") - 1.05   # o hero (data grande) fica até o contador dos 15 dias começar (a data é dita durante a capa)
BR6P = BR6 - 1.1
T40 = em("f7", "40") - 1.1
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:96px">CHUVA FORTE</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">hoje em Minas e no Rio</div>'}]
paineis = [
    {"ini": H, "fim": ini("f2"), "k": "MINAS E RIO · ATÉ 13/11",
     "contador": conta(15, "f1", "15", "#5ec8ff", "DIAS PARA A CHUVA DE UM MÊS"),
     "l": "previsão de chuva acima do normal no Sudeste", "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "O SATÉLITE · FAIXA DE NUVENS",
     "itens": [{"t": em("f2", "faixa"), "txt": "🛰️ nuvens carregadas"},
               {"t": em("f2", "Pará"), "txt": "☁️ do sul do Pará"},
               {"t": em("f2", "Minas"), "txt": "⛈️ até Minas e o Rio"}],
     "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "HOJE · CHUVA FORTE (PREVISÃO)",
     "itens": [{"t": em("f3", "Juiz"), "txt": "⛈️ Juiz de Fora"},
               {"t": em("f3", "serra"), "txt": "⛈️ serra do Rio e Grande Rio"},
               {"t": em("f3", "Espírito"), "txt": "⛈️ sul do Espírito Santo"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f4"), "fim": em("f4", "Paulo") - .1, "k": "CENTRO-OESTE · HOJE",
     "itens": [{"t": em("f4", "Goiânia"), "txt": "🌧️ pancadas em Goiânia"},
               {"t": em("f4", "Brasília"), "txt": "🌧️ e em Brasília"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": em("f4", "Paulo") - .1, "fim": ini("f5"), "k": "SÃO PAULO · GAROA",
     "contador": conta(13, "f4", "13", "#96d2ff", "°C · MÍNIMA HOJE", de=20, lead=.9),
     "l": "céu nublado e garoa na capital", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "OESTE DE SC · MADRUGADA",
     "itens": [{"t": em("f5", "trovoada"), "txt": "⛈️ trovoada"},
               {"t": em("f5", "granizo"), "txt": "🧊 pode ter caído granizo"},
               {"t": em("f5", "Xanxerê"), "txt": "📍 Xanxerê e Chapecó"}],
     "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f6"), "fim": BR6P, "k": "INMET · CHUVAS INTENSAS 30/10",
     "contador": conta(795, "f6", "795", "#ff8c1a", "CIDADES EM MINAS"),
     "l": "aviso amarelo de chuvas intensas para hoje", "borda": "rgba(255,140,26,.8)"},
    {"ini": BR6P, "fim": ini("f7"), "k": "INMET · BRASIL · HOJE 30/10",
     "contador": conta(2166, "f6", "2.166", "#ff8c1a", "CIDADES NO BRASIL", de=795),
     "l": f"SC {POR_UF['SC']}, RS {POR_UF['RS']}, GO {POR_UF['GO']}, PR {POR_UF['PR']}, RJ {POR_UF['RJ']}", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f7"), "fim": T40, "k": "TERESINA · MÁXIMA HOJE",
     "contador": conta(37, "f7", "37", "#ff2a1f", "°C (PREVISÃO)", de=30),
     "l": "o Piauí é o estado mais quente", "borda": "rgba(255,42,31,.8)"},
    {"ini": T40, "fim": ini("f8"), "k": "INTERIOR DO PIAUÍ",
     "contador": conta(40, "f7", "40", "#ff2a1f", "°C (PREVISÃO)", de=37),
     "l": f"INMET: baixa umidade em {len(SECO)} cidades do Nordeste", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "SERRA DE SC · SÁBADO 31/10",
     "contador": conta(5, "f8", "5", "#96d2ff", "°C · MÍNIMA (PREVISÃO)", de=15),
     "l": "de 5 a 7 °C ao amanhecer", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "ATÉ 13/11 · CHUVA PREVISTA",
     "itens": [{"t": em("f9", "Minas"), "txt": "🌧️ Minas e Goiás"},
               {"t": em("f9", "Rio"), "txt": "🌧️ Rio e Espírito Santo"},
               {"t": em("f9", "Paraná"), "txt": "🌧️ Paraná"}],
     "l": f"colunas: chuva prevista somada de 30/10 a 13/11 · Open-Meteo · até {TOPO_PR[1]} mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": GEADA - .1, "k": "DE 4 A 12/11 · O FRIO VOLTA",
     "itens": [{"t": em("f10", "temperatura"), "txt": "📉 queda brusca da temperatura"},
               {"t": em("f10", "Sul"), "txt": "❄️ Sul e Sudeste"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": GEADA - .1, "fim": ini("f11"), "k": "RISCO DE GEADA NA SERRA",
     "itens": [{"t": GEADA, "txt": "❄️ topo da serra, 8 e 9/11 (previsão)"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "onde"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f11", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
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
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f3"), "fim": ini("f5"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · foto do granizo: ilustração"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>INMET</b>, avisos de chuvas intensas de 30/10"},
    {"ini": ini("f7"), "fim": ini("f9"), "html": f"<b>{MET}</b> · previsão · <b>INMET</b>, aviso de baixa umidade"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · <b>Open-Meteo</b>, chuva prevista somada de 30/10 a 13/11"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b> · previsão · foto da geada: ilustração"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chover": "#5ec8ff", "chuvas": "#5ec8ff", "pancadas": "#5ec8ff", "nuvens": "#96d2ff", "frio": "#96d2ff",
         "geada": "#96d2ff", "graus": "#ff2a1f", "calor": "#ff2a1f", "forte": "#ff8c1a", "garoa": "#96d2ff", "granizo": "#96d2ff",
         "trovoada": "#ff8c1a", "intensas": "#ff8c1a", "aviso": "#ff8c1a", "satelite": AM, "carregadas": "#5ec8ff",
         "bruscamente": "#96d2ff", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"minas", "rio", "para", "juiz", "fora", "serra", "grande", "espirito", "santo", "goias", "goiania", "brasilia", "sao", "paulo",
         "sul", "sudeste", "santa", "catarina", "xanxere", "chapeco", "brasil", "piaui", "teresina", "parana", "inemaclub", "onde"}
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
     "marca": "INEMA · CLIMA DO DIA", "selo": DATA[:5] + " · INMET · Open-Meteo · NOAA",
     "camera": camera, "sat": SAT, "imagens": imagens, "colunas": colunas, "telas": telas, "estados": estados, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"INMET hoje {len(HOJE_CI)} (MG {POR_UF['MG']}) · seco {len(SECO)} · colunas {len(col)} ({C100} ≥ 100 mm, MG {TOPO_MG[1]}, PR {TOPO_PR[1]})")
