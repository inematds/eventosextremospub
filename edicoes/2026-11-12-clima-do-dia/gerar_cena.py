#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 12/11/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md: calor e umidade com núcleos de chuva em SP, Goiânia e Brasília,
chuva à tarde no Sul com risco de granizo e vento, mais de 100 mm ontem no Mato Grosso, chuva de Fortaleza a Recife e
no sul da Bahia, frio no sábado (São Joaquim 5–7 °C, SP e BH 15 °C de mínima), chuva avançando no Nordeste no domingo,
15 dias com chuva acima da média no centro-sul e no Nordeste, nova massa de ar frio a partir do dia 20), dos avisos do
INMET de hoje (tempestade em 2746 cidades: SP 645, MG 551, PR 399; acumulado de chuva na Bahia), da máxima de Teresina
(Open-Meteo, previsao7d.json), do timelapse do GOES-19 (NASA GIBS) e da chuva prevista de 12 a 26/11 na grade do Brasil
(Open-Meteo, om/prev15_grade.json, gravado por coleta/previsao15d.py --dia 2026-11-11).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "ALERTA DE / TEMPESTADE / HOJE / 2.746 CIDADES"), data grande,
Brasil com os estados do aviso de tempestade (contador 2746), foto do granizo (Codex, ilustração) na palavra "granizo",
IR do GOES-19 sobre SP/Goiânia/Brasília, SP 645 → total 2746, Sul inclinado (trovoada, granizo, vento), foto do toró
(Codex, ilustração) no Mato Grosso, Nordeste (Fortaleza, Recife, sul da Bahia, Teresina 39 °C), serra catarinense e
mínimas de sábado, colunas 3D da chuva prevista até 26/11 girando no Nordeste e depois no centro-sul, frio do dia 20.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "12/11/2026"
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
        if n(palavra) == n(p["w"]) or (len(n(palavra)) > 3 and n(palavra) in n(p["w"])):
            achou += 1
            if achou == k:
                return p["t"]
    raise KeyError(f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in FALA[fid]["palavras"]))


ini = lambda fid: FALA[fid]["ini"]
fim = lambda fid: FALA[fid]["fim"]
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
LAR, AMA, VERM, AZUL, FRIO = [255, 140, 26], [250, 204, 21], [255, 42, 31], [60, 150, 255], [150, 210, 255]

# ---------------------------------------------------------------- avisos do INMET (hoje 12/11)
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
assert aviso[56383]["descricao"] == "Tempestade" and aviso[56383]["inicio"].startswith("2026-11-12")
assert aviso[56387]["descricao"] == "Acumulado de Chuva" and aviso[56387]["inicio"].startswith("2026-11-12")
TEMP = geo(56383)                  # tempestade hoje: 2746 cidades
ACUM = geo(56387)                  # acumulado de chuva hoje: 26 cidades (24 na Bahia)
assert len(TEMP) == 2746, len(TEMP)   # f1 diz 2746
UFCOD = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN",
         "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC",
         "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
UF_H = Counter(UFCOD[c[:2]] for c in TEMP)
UF_AC = Counter(UFCOD[c[:2]] for c in ACUM)
assert (UF_H["SP"], UF_H["MG"], UF_H["PR"]) == (645, 551, 399), UF_H     # f3: SP 645, Minas 551, Paraná 399
assert UF_AC["BA"] == 24, UF_AC
HOJE_UF = [u for u, k in UF_H.items() if k >= 25]

# ---------------------------------------------------------------- Teresina (Open-Meteo, previsao7d.json)
P7 = json.loads((B / "previsao7d.json").read_text())
TPICO = P7["por_dia"][0]["tmax_pico"]
assert P7["por_dia"][0]["dia"] == "2026-11-12" and TPICO[1] == "Teresina" and round(TPICO[0]) == 39, TPICO   # f6: 39 graus

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
BRL = {"lon": -51.0, "lat": -17.0, "zoom": 3.65}       # f1: Brasil com os estados do aviso de tempestade
NUC = {"lon": -48.5, "lat": -19.5, "zoom": 4.75}       # f2: núcleos de chuva (SP, Goiânia, Brasília) + IR
SE = {"lon": -48.0, "lat": -21.5, "zoom": 4.5}         # f3: SP, MG, PR
SUL = {"lon": -51.0, "lat": -27.0, "zoom": 5.3}        # f4: PR, SC, norte do RS (inclinada)
MT = {"lon": -54.5, "lat": -12.5, "zoom": 4.9}         # f5: Mato Grosso, Tocantins, Maranhão
NE = {"lon": -40.5, "lat": -9.0, "zoom": 4.9}          # f6: Fortaleza a Recife, sul da Bahia, Teresina
SERRA = {"lon": -49.9, "lat": -28.0, "zoom": 6.0}      # f7: São Joaquim
SEF = {"lon": -46.5, "lat": -22.5, "zoom": 5.0}        # f7: mínimas de SP e BH
NEC = {"lon": -42.0, "lat": -10.5, "zoom": 4.6}        # f8: colunas no Nordeste
CSC = {"lon": -47.5, "lat": -18.0, "zoom": 4.2}        # f9: colunas no centro-sul
FRS = {"lon": -50.0, "lat": -25.5, "zoom": 4.4}        # f10: nova massa de ar frio
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.0  # quadro 0 = capa cheia do Codex até aqui
HOJE = em("f1", "Hoje") - .1       # sai da data grande para o mapa no "Hoje há alerta"
HERO_F = em("f1", "tempestade")    # a data grande fica até "tempestade" (Nei: data grande na abertura)
GRA = em("f1", "granizo") - .1     # foto do granizo entra na palavra
TORO = em("f5", "caíram") - .1     # foto do toró no Mato Grosso
TORO_F = em("f5", "Hoje") - .1
camera = [
    K(0, BR), K(HOJE - .3, BR), K(HOJE + 1.2, BRL), K(fim("f1") - .2, {**BRL, "zoom": 3.75}),
    K(ini("f2") + 1.0, NUC, 0, 0), K(fim("f2") - .2, {**NUC, "zoom": 4.9}, 6, 0),
    K(ini("f3") + 1.0, SE, 0, 0), K(fim("f3") - .2, {**SE, "zoom": 4.6}, 6, 0),
    K(ini("f4") + 1.1, SUL, 45, -12), K(fim("f4") - .2, {**SUL, "zoom": 5.4}, 48, 8),
    K(ini("f5") + 1.0, MT, 0, 0), K(fim("f5") - .2, {**MT, "lon": -51.0, "lat": -9.5, "zoom": 4.8}, 6, 0),
    K(ini("f6") + 1.0, NE, 0, 0), K(fim("f6") - .2, {**NE, "zoom": 5.0}, 6, 0),
    K(ini("f7") + 1.1, SERRA, 40, -10), K(em("f7", "Paulo") - .3, {**SERRA, "zoom": 6.1}, 42, 0),
    K(em("f7", "Paulo") + 1.0, SEF, 0, 0), K(fim("f7") - .2, {**SEF, "lat": -21.5, "zoom": 5.1}, 6, 0),
    K(ini("f8") + 1.2, NEC, 55, -20), K(fim("f8") - .2, {**NEC, "zoom": 4.7}, 56, 12),
    K(ini("f9") + 1.2, CSC, 55, 15), K(fim("f9") - .2, {**CSC, "lon": -48.5, "lat": -20.0, "zoom": 4.4}, 52, 35),
    K(ini("f10") + 1.1, FRS, 0, 0), K(fim("f10") - .2, {**FRS, "zoom": 4.55}, 6, 0),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) nos núcleos de chuva (f2)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 130]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": ini("f2") - .3, "fim": ini("f3") + .3, "dur": ini("f3") - ini("f2") + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])
assert len(BONS) >= 36, f"poucos quadros bons de infravermelho: {len(BONS)}"
imagens = []

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de 12 a 26/11 (Open-Meteo, grade de 1,5°)
G15 = json.loads((AQUI / "om/prev15_grade.json").read_text())
dias = G15["pts"][0]["dias"]
ND = 15
assert dias[0] == "2026-11-12" and dias[ND - 1] == "2026-11-26", (dias[0], dias[ND - 1])
soma = lambda p: round(sum(x or 0 for x in p["chuva"][:ND]))
SOMA = [(p, soma(p)) for p in G15["pts"]]
col = [{"id": i, "p": p["p"], "v": v, "cor": [60, 150, 255] if v >= 150 else [120, 190, 255]} for i, (p, v) in enumerate(SOMA) if v >= 60]
ordem = {c["id"]: (c["p"][1] + 34) * .03 for c in col}   # sobe do Sul para o Norte
colunas = [{"id": "chuva3d", "ini": ini("f8") + .2, "fim": ini("f10") + .2, "dados": col, "raio": 60000, "escala": 1700, "ordem": ordem, "varredura": 1}]
TOPO, VTOPO = max(SOMA, key=lambda x: x[1])
assert TOPO["uf"] == "MG" and VTOPO == 316 and len(col) >= 150, (TOPO["uf"], VTOPO, len(col))
VUF = lambda uf: max(v for p, v in SOMA if p["uf"] == uf)
NE_TOP = max(((p, v) for p, v in SOMA if p["uf"] in {"MA", "PI", "PE", "PB", "BA"}), key=lambda x: x[1])
VGO = VUF("GO")

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, granizo, toró
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": GRA, "fim": ini("f2") + .2, "fade": .25, "zoom": .05, "selo": "ilustração"},
         {"src": "capa-dia/toro.png", "ini": TORO, "fim": TORO_F, "fade": .25, "zoom": .05, "selo": "ilustração"}]

# ---------------------------------------------------------------- estados
estados = [
    {"id": "hoje1", "ini": HOJE, "fim": ini("f2") + .3, "ufs": HOJE_UF, "cor": LAR, "alfa": .4},
    {"id": "nuc2", "ini": em("f2", "Paulo"), "fim": ini("f3") + .3, "ufs": ["SP", "GO", "DF"], "cor": LAR, "alfa": .25},
    {"id": "sp3", "ini": em("f3", "Paulo"), "fim": ini("f4") + .3, "ufs": ["SP"], "cor": VERM, "alfa": .45},
    {"id": "mg3", "ini": em("f3", "Minas"), "fim": ini("f4") + .3, "ufs": ["MG"], "cor": VERM, "alfa": .4},
    {"id": "pr3", "ini": em("f3", "Paraná"), "fim": ini("f4") + .3, "ufs": ["PR"], "cor": VERM, "alfa": .4},
    {"id": "sul4", "ini": em("f4", "Paraná"), "fim": ini("f5") + .3, "ufs": ["PR", "SC"], "cor": VERM, "alfa": .4},
    {"id": "rs4", "ini": em("f4", "gaúcho"), "fim": ini("f5") + .3, "ufs": ["RS"], "cor": LAR, "alfa": .25},
    {"id": "mt5", "ini": em("f5", "Mato"), "fim": ini("f6") + .3, "ufs": ["MT"], "cor": AZUL, "alfa": .35},
    {"id": "toma5", "ini": em("f5", "Tocantins"), "fim": ini("f6") + .3, "ufs": ["TO", "MA"], "cor": LAR, "alfa": .3},
    {"id": "ne6", "ini": em("f6", "Nordeste"), "fim": ini("f7") + .3, "ufs": ["CE", "RN", "PB", "PE"], "cor": AZUL, "alfa": .3},
    {"id": "ba6", "ini": em("f6", "Bahia"), "fim": ini("f7") + .3, "ufs": ["BA"], "cor": AZUL, "alfa": .3},
    {"id": "pi6", "ini": em("f6", "Teresina"), "fim": ini("f7") + .3, "ufs": ["PI"], "cor": VERM, "alfa": .35},
    {"id": "frio7", "ini": em("f7", "frio"), "fim": ini("f8") + .3, "ufs": ["SC", "RS", "PR", "SP", "MG"], "cor": FRIO, "alfa": .3},
    {"id": "ne8", "ini": em("f8", "Nordeste"), "fim": ini("f9") + .3, "ufs": ["PE", "PB", "BA", "PI", "MA"], "cor": AZUL, "alfa": .25},
    {"id": "cs9", "ini": em("f9", "acima"), "fim": ini("f10") + .3,
     "ufs": ["MT", "MS", "GO", "DF", "MG", "SP", "RJ", "ES", "PR", "SC", "RS", "BA", "PI", "MA", "PE", "PB", "CE", "RN", "AL", "SE"], "cor": AZUL, "alfa": .2},
    {"id": "amz9", "ini": em("f9", "Amazônia"), "fim": ini("f10") + .3, "ufs": ["AM", "PA", "RR", "AP", "AC"], "cor": LAR, "alfa": .3},
    {"id": "frio10", "ini": em("f10", "frio"), "fim": ini("f11") + .3, "ufs": ["RS", "SC", "PR", "SP", "MG", "RJ", "ES", "MS"], "cor": FRIO, "alfa": .35},
]

pinos = [
    {"nome": "São Paulo", "sub": "núcleo de chuva", "lon": -46.63, "lat": -23.55, "ini": em("f2", "Paulo"), "fim": ini("f3"), "h": 200},
    {"nome": "Goiânia", "sub": "núcleo de chuva", "lon": -49.25, "lat": -16.68, "ini": em("f2", "Goiânia"), "fim": ini("f3"), "h": 150},
    {"nome": "Brasília", "sub": "núcleo de chuva", "lon": -47.88, "lat": -15.79, "ini": em("f2", "Brasília"), "fim": ini("f3"), "h": 260},
    {"nome": "São Paulo", "sub": f"{UF_H['SP']} cidades em alerta", "lon": -48.5, "lat": -22.3, "ini": em("f3", "Paulo"), "fim": ini("f4"), "h": 180},
    {"nome": "Minas Gerais", "sub": f"{UF_H['MG']} cidades em alerta", "lon": -44.5, "lat": -18.5, "ini": em("f3", "Minas"), "fim": ini("f4"), "h": 220},
    {"nome": "Paraná", "sub": f"{UF_H['PR']} cidades em alerta", "lon": -51.6, "lat": -24.6, "ini": em("f3", "Paraná"), "fim": ini("f4"), "h": 150},
    {"nome": "Paraná e SC", "sub": "chuva à tarde", "lon": -50.5, "lat": -26.0, "ini": em("f4", "Paraná"), "fim": ini("f5"), "h": 200},
    {"nome": "Norte do RS", "sub": "trovoada, granizo e vento", "lon": -52.4, "lat": -28.3, "ini": em("f4", "gaúcho"), "fim": ini("f5"), "h": 150},
    {"nome": "Mato Grosso", "sub": "mais de 100 mm ontem", "lon": -55.5, "lat": -13.0, "ini": TORO_F, "fim": ini("f6"), "h": 200},
    {"nome": "Tocantins", "sub": "pancadas hoje", "lon": -48.3, "lat": -10.2, "ini": em("f5", "Tocantins"), "fim": ini("f6"), "h": 150},
    {"nome": "Maranhão", "sub": "pancadas hoje", "lon": -45.3, "lat": -5.0, "ini": em("f5", "Maranhão"), "fim": ini("f6"), "h": 180},
    {"nome": "Fortaleza", "sub": "chuva hoje", "lon": -38.54, "lat": -3.73, "ini": em("f6", "Fortaleza"), "fim": ini("f7"), "h": 200},
    {"nome": "Recife", "sub": "chuva hoje", "lon": -34.88, "lat": -8.05, "ini": em("f6", "Recife"), "fim": ini("f7"), "h": 160},
    {"nome": "Sul da Bahia", "sub": f"INMET: acumulado de chuva em {UF_AC['BA']} cidades", "lon": -39.6, "lat": -14.8, "ini": em("f6", "Bahia"), "fim": ini("f7"), "h": 180},
    {"nome": "Teresina", "sub": f"máxima de {round(TPICO[0])} °C hoje", "lon": -42.80, "lat": -5.09, "ini": em("f6", "Teresina"), "fim": ini("f7"), "h": 240},
    {"nome": "São Joaquim (SC)", "sub": "sábado: 5 a 7 °C", "lon": -49.93, "lat": -28.29, "ini": em("f7", "Joaquim"), "fim": em("f7", "Paulo"), "h": 200},
    {"nome": "São Paulo", "sub": "sábado: mínima de 15 °C", "lon": -46.63, "lat": -23.55, "ini": em("f7", "Paulo"), "fim": ini("f8"), "h": 160},
    {"nome": "Belo Horizonte", "sub": "sábado: mínima de 15 °C", "lon": -43.94, "lat": -19.92, "ini": em("f7", "Belo"), "fim": ini("f8"), "h": 200},
    {"nome": f"{NE_TOP[1]} mm até 26/11", "sub": f"soma prevista ({NE_TOP[0]['uf']}) · Open-Meteo", "lon": NE_TOP[0]["p"][0], "lat": NE_TOP[0]["p"][1],
     "ini": em("f8", "Nordeste"), "fim": ini("f9"), "h": 260},
    {"nome": f"{VTOPO} mm até 26/11", "sub": f"maior soma prevista ({TOPO['uf']}) · Open-Meteo", "lon": TOPO["p"][0], "lat": TOPO["p"][1],
     "ini": em("f9", "acima"), "fim": ini("f10"), "h": 220},
]

# ---------------------------------------------------------------- textos
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
hero = [{"ini": CAPA - .2, "fim": HERO_F,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:104px">TEMPESTADE</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">alerta em 2.746 cidades</div>'}]
paineis = [
    {"ini": HERO_F, "fim": GRA, "k": "INMET · TEMPESTADE HOJE",
     "contador": conta(len(TEMP), "f1", "2746", "#ff2a1f", "CIDADES NO BRASIL", lead=.9),
     "l": "chuva, raios, vento e granizo", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "NÚCLEOS DE CHUVA",
     "itens": [{"t": em("f2", "calor"), "txt": "🌡️ calor + umidade"},
               {"t": em("f2", "Paulo"), "txt": "⛈️ São Paulo"},
               {"t": em("f2", "Goiânia"), "txt": "⛈️ Goiânia e Brasília"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "INMET · TEMPESTADE HOJE",
     "contador": conta(UF_H["SP"], "f3", "645", "#ff2a1f", "CIDADES EM SÃO PAULO"),
     "itens": [{"t": em("f3", "551"), "txt": f"⛈️ MG {UF_H['MG']} · PR {UF_H['PR']}"},
               {"t": em("f3", "399"), "txt": f"🇧🇷 TOTAL NO BRASIL: {len(TEMP):,}".replace(",", ".")}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "SUL · HOJE À TARDE",
     "itens": [{"t": em("f4", "trovoada"), "txt": "⛈️ trovoada"},
               {"t": em("f4", "granizo"), "txt": "🧊 granizo"},
               {"t": em("f4", "vento"), "txt": "💨 vento forte"}],
     "l": "PR, SC e norte do RS", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "MATO GROSSO · ONTEM",
     "contador": conta(100, "f5", "100", "#5ec8ff", "MM EM POUCO TEMPO"),
     "itens": [{"t": em("f5", "Tocantins"), "txt": "🌧️ hoje: Tocantins e Maranhão"}],
     "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "NORDESTE · HOJE",
     "itens": [{"t": em("f6", "Fortaleza"), "txt": "🌧️ de Fortaleza a Recife"},
               {"t": em("f6", "Bahia"), "txt": "🌧️ sul da Bahia"}],
     "contador": conta(39, "f6", "39", "#ff2a1f", "°C EM TERESINA"),
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SÁBADO · MÍNIMAS",
     "itens": [{"t": em("f7", "Joaquim"), "txt": "❄️ São Joaquim 5 a 7 °C"},
               {"t": em("f7", "Paulo"), "txt": "🥶 São Paulo 15 °C"},
               {"t": em("f7", "Belo"), "txt": "🥶 Belo Horizonte 15 °C"}],
     "l": "previsão", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "DOMINGO · NORDESTE",
     "itens": [{"t": em("f8", "Pernambuco"), "txt": "🌧️ sertão de PE e Paraíba"},
               {"t": em("f8", "Bahia"), "txt": "🌧️ Bahia, Piauí e Maranhão"}],
     "l": "colunas: chuva prevista somada até 26/11", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "15 DIAS (PREVISÃO)",
     "itens": [{"t": em("f9", "acima"), "txt": "🌧️ acima da média: CO, SE, Sul e NE"},
               {"t": em("f9", "Amazônia"), "txt": "🟧 abaixo: Amazônia"}],
     "l": f"Open-Meteo: até {VTOPO} mm em {TOPO['uf']} · {VGO} mm em GO", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "A PARTIR DE 20/11",
     "itens": [{"t": em("f10", "frio"), "txt": "❄️ nova massa de ar frio"},
               {"t": em("f10", "Sudeste"), "txt": "🥶 Sul e Sudeste"}],
     "l": "previsão", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "onde"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f11", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
     "borda": "rgba(250,204,21,.8)"},
]
for a, b in zip(paineis, paineis[1:]):
    assert a["fim"] <= b["ini"] + 1e-6, (a["k"], b["k"])
for a in paineis:
    if a.get("contador"):
        c = a["contador"]
        if c["ini"] < a["ini"]:
            c["dur"] -= a["ini"] - c["ini"]; c["ini"] = a["ini"]
        assert c["dur"] > .2 and c["ini"] + c["dur"] <= a["fim"], ("contador fora do painel", a["k"])

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": HERO_F, "html": f"<b>{MET}</b> · <b>INMET</b>"},
    {"ini": HERO_F, "fim": GRA, "html": f"<b>INMET</b>, aviso de tempestade de 12/11 · <b>{MET}</b>"},
    {"ini": GRA, "fim": ini("f2"), "html": f"<b>{MET}</b> · foto do granizo: ilustração"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INMET</b>, aviso de tempestade de 12/11"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · foto do temporal: ilustração"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · <b>INMET</b>, acumulado de chuva · <b>Open-Meteo</b>, máxima de Teresina"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f8"), "fim": ini("f10"), "html": f"<b>{MET}</b> · <b>Open-Meteo</b>, chuva prevista somada de 12 a 26/11"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "umidade": "#5ec8ff", "pancada": "#5ec8ff", "milimetros": "#5ec8ff",
         "frio": "#96d2ff", "minima": "#96d2ff", "graus": "#ff2a1f", "granizo": "#ff2a1f", "tempestade": "#ff2a1f", "trovoada": "#ff2a1f",
         "alerta": "#ff8c1a", "vento": "#ff8c1a", "calor": "#ff8c1a", "acima": "#ff2a1f", "abaixo": "#ff8c1a", "avancar": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "sao", "paulo", "goiania", "brasilia", "minas", "parana", "santa", "catarina", "gaucho", "mato", "grosso", "tocantins",
         "maranhao", "nordeste", "fortaleza", "recife", "bahia", "teresina", "joaquim", "belo", "horizonte", "sertao", "pernambuco",
         "paraiba", "piaui", "centrooeste", "sudeste", "amazonia", "inemaclub", "onde"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        if bloco and len(" ".join(b["w"] for b in bloco) + " " + w) > 19:
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
     "marca": "INEMA · CLIMA DO DIA", "selo": DATA[:5] + " · NASA · INMET · Open-Meteo",
     "camera": camera, "sat": SAT, "imagens": imagens, "colunas": colunas, "telas": telas, "estados": estados, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"INMET tempestade hoje {len(TEMP)} (SP {UF_H['SP']} MG {UF_H['MG']} PR {UF_H['PR']}) · acumulado BA {UF_AC['BA']} · "
      f"colunas {len(col)} (topo {VTOPO} mm em {TOPO['uf']}) · NE {NE_TOP[1]} mm ({NE_TOP[0]['uf']}) · GO {VGO} mm · Teresina {TPICO[0]}")
