#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 13/11/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md: calor e umidade com pancadas isoladas e toró pontual, Piauí perto
de 40 °C, amanhecer frio no Sul no sábado (5 a 7 °C na serra, 14 °C em Curitiba e Porto Alegre), oeste paulista a 35 °C,
granizo e vento no Sul, pancadão no Rio e em SP no domingo, chuva voltando ao sertão do Nordeste, 15 dias acima da média
com a Amazônia abaixo, ar frio de volta depois do dia 20), dos avisos do INMET (tempestade hoje em 2653 cidades: MG 853,
SP 645; baixa umidade em 381; tempestade no Sul no sábado em 964; tempestade no domingo em 4299), da máxima de Teresina
(Open-Meteo, previsao7d.json), do timelapse do GOES-19 (NASA GIBS) e da chuva prevista de 13 a 27/11 na grade do Brasil
(Open-Meteo, om/prev15_grade.json, gravado por coleta/previsao15d.py --dia 2026-11-12).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "ALERTA DE / TEMPESTADE / HOJE / 2.653 CIDADES"), data grande,
Brasil com os estados do aviso (contador 2653), IR do GOES-19 sobre o centro-sul, MG 853 → SP 645 → total 2653, Piauí
39,5 °C e umidade baixa (381), Sul inclinado no amanhecer frio, oeste paulista 35 °C, foto do granizo (Codex, ilustração),
domingo com 4299 cidades e foto do pancadão em SP (Codex, ilustração), colunas 3D da chuva prevista até 27/11 girando
no Nordeste e depois no centro-sul, frio depois do dia 20.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "13/11/2026"
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

# ---------------------------------------------------------------- avisos do INMET (13/11 e fim de semana)
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
assert aviso[56392]["descricao"] == "Tempestade" and aviso[56392]["inicio"].startswith("2026-11-13")
assert aviso[56393]["descricao"] == "Baixa Umidade" and aviso[56393]["inicio"].startswith("2026-11-13")
assert aviso[56398]["descricao"] == "Tempestade" and aviso[56398]["inicio"].startswith("2026-11-14")
assert aviso[56399]["descricao"] == "Tempestade" and aviso[56399]["inicio"].startswith("2026-11-15")
TEMP = geo(56392)                  # tempestade hoje: 2653 cidades
UMID = geo(56393)                  # baixa umidade hoje: 381 cidades
SABS = geo(56398)                  # tempestade no sábado no Sul: 964 cidades
DOM = geo(56399)                   # tempestade no domingo: 4299 cidades
assert (len(TEMP), len(UMID), len(SABS), len(DOM)) == (2653, 381, 964, 4299), (len(TEMP), len(UMID), len(SABS), len(DOM))
UFCOD = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN",
         "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC",
         "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
uf = lambda S: Counter(UFCOD[c[:2]] for c in S)
UF_H, UF_U, UF_S, UF_D = uf(TEMP), uf(UMID), uf(SABS), uf(DOM)
assert (UF_H["MG"], UF_H["SP"]) == (853, 645), UF_H     # f3: Minas 853, São Paulo 645
HOJE_UF = [u for u, k in UF_H.items() if k >= 25]
UMID_UF = [u for u, k in UF_U.items() if k >= 15]
SUL_UF = [u for u in ("PR", "SC", "RS") if UF_S[u]]
DOM_UF = [u for u, k in UF_D.items() if k >= 25]

# ---------------------------------------------------------------- Teresina (Open-Meteo, previsao7d.json)
P7 = json.loads((B / "previsao7d.json").read_text())
TPICO = P7["por_dia"][0]["tmax_pico"]
assert P7["por_dia"][0]["dia"] == "2026-11-13" and TPICO[1] == "Teresina" and 39 <= TPICO[0] < 40.5, TPICO   # f4: perto de 40 graus

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
BRL = {"lon": -51.0, "lat": -16.5, "zoom": 3.65}       # f1: Brasil com os estados do aviso de tempestade
NUC = {"lon": -47.5, "lat": -18.5, "zoom": 4.6}        # f2: pancadas no centro-sul + IR
SE = {"lon": -46.0, "lat": -20.0, "zoom": 4.75}        # f3: Minas e São Paulo
NE = {"lon": -40.5, "lat": -7.0, "zoom": 5.0}          # f4: Piauí e umidade baixa
SUL = {"lon": -51.0, "lat": -27.5, "zoom": 5.3}        # f5: amanhecer frio no Sul (inclinada)
OSP = {"lon": -50.5, "lat": -22.5, "zoom": 5.2}        # f6: oeste paulista
BRD = {"lon": -48.0, "lat": -17.0, "zoom": 3.9}        # f7: domingo, 4299 cidades
NEC = {"lon": -41.5, "lat": -9.5, "zoom": 4.6}         # f8: colunas no Nordeste
CSC = {"lon": -47.0, "lat": -17.5, "zoom": 4.2}        # f9: colunas no centro-sul
FRS = {"lon": -50.0, "lat": -25.5, "zoom": 4.4}        # f10: ar frio depois do dia 20
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.0  # quadro 0 = capa cheia do Codex até aqui
HOJE = em("f1", "Hoje") - .1       # sai da data grande para o mapa no "Hoje há alerta"
HERO_F = em("f1", "tempestade")    # a data grande fica até "tempestade" (Nei: data grande na abertura)
GRA = em("f6", "granizo") - .1     # foto do granizo entra na palavra
TORO = em("f7", "pancadão") - .1   # foto do pancadão em SP
camera = [
    K(0, BR), K(HOJE - .3, BR), K(HOJE + 1.2, BRL), K(fim("f1") - .2, {**BRL, "zoom": 3.75}),
    K(ini("f2") + 1.0, NUC, 0, 0), K(fim("f2") - .2, {**NUC, "zoom": 4.8}, 6, 0),
    K(ini("f3") + 1.0, SE, 0, 0), K(fim("f3") - .2, {**SE, "lon": -47.5, "lat": -21.0, "zoom": 4.85}, 6, 0),
    K(ini("f4") + 1.0, NE, 0, 0), K(fim("f4") - .2, {**NE, "zoom": 5.15}, 6, 0),
    K(ini("f5") + 1.1, SUL, 45, -12), K(fim("f5") - .2, {**SUL, "zoom": 5.4}, 48, 8),
    K(ini("f6") + 1.0, OSP, 0, 0), K(GRA, {**OSP, "lon": -51.0, "lat": -24.0, "zoom": 5.0}, 6, 0),
    K(ini("f7") + 1.0, BRD, 0, 0), K(fim("f7") - .2, {**BRD, "zoom": 4.0}, 4, 0),
    K(ini("f8") + 1.2, NEC, 55, -20), K(fim("f8") - .2, {**NEC, "zoom": 4.7}, 56, 12),
    K(ini("f9") + 1.2, CSC, 55, 15), K(fim("f9") - .2, {**CSC, "lon": -48.0, "lat": -19.5, "zoom": 4.4}, 52, 35),
    K(ini("f10") + 1.1, FRS, 0, 0), K(fim("f10") - .2, {**FRS, "zoom": 4.55}, 6, 0),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) nas pancadas (f2)
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

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de 13 a 27/11 (Open-Meteo, grade de 1,5°)
G15 = json.loads((AQUI / "om/prev15_grade.json").read_text())
dias = G15["pts"][0]["dias"]
ND = 15
assert dias[0] == "2026-11-13" and dias[ND - 1] == "2026-11-27", (dias[0], dias[ND - 1])
soma = lambda p: round(sum(x or 0 for x in p["chuva"][:ND]))
SOMA = [(p, soma(p)) for p in G15["pts"]]
col = [{"id": i, "p": p["p"], "v": v, "cor": [60, 150, 255] if v >= 150 else [120, 190, 255]} for i, (p, v) in enumerate(SOMA) if v >= 60]
ordem = {c["id"]: (c["p"][1] + 34) * .03 for c in col}   # sobe do Sul para o Norte
colunas = [{"id": "chuva3d", "ini": ini("f8") + .2, "fim": ini("f10") + .2, "dados": col, "raio": 60000, "escala": 1700, "ordem": ordem, "varredura": 1}]
TOPO, VTOPO = max(SOMA, key=lambda x: x[1])
assert TOPO["uf"] == "ES" and VTOPO == 354 and len(col) >= 150, (TOPO["uf"], VTOPO, len(col))
VUF = lambda u: max(v for p, v in SOMA if p["uf"] == u)
# sertão do Nordeste: MA, PI, PE, PB, CE e o norte da Bahia (acima de 12° S)
NE_TOP = max(((p, v) for p, v in SOMA if p["uf"] in {"MA", "PI", "PE", "PB", "CE"} or (p["uf"] == "BA" and p["p"][1] > -12)), key=lambda x: x[1])
VMG = VUF("MG")

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, granizo, pancadão
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": GRA, "fim": ini("f7") + .2, "fade": .25, "zoom": .05, "selo": "ilustração"},
         {"src": "capa-dia/toro.png", "ini": TORO, "fim": ini("f8") + .2, "fade": .25, "zoom": .05, "selo": "ilustração"}]

# ---------------------------------------------------------------- estados
estados = [
    {"id": "hoje1", "ini": HOJE, "fim": ini("f2") + .3, "ufs": HOJE_UF, "cor": LAR, "alfa": .4},
    {"id": "nuc2", "ini": em("f2", "pancadas"), "fim": ini("f3") + .3, "ufs": ["MG", "SP", "GO", "DF"], "cor": LAR, "alfa": .25},
    {"id": "mg3", "ini": em("f3", "Minas"), "fim": ini("f4") + .3, "ufs": ["MG"], "cor": VERM, "alfa": .45},
    {"id": "sp3", "ini": em("f3", "Paulo"), "fim": ini("f4") + .3, "ufs": ["SP"], "cor": VERM, "alfa": .45},
    {"id": "pi4", "ini": em("f4", "Piauí"), "fim": ini("f5") + .3, "ufs": ["PI"], "cor": VERM, "alfa": .4},
    {"id": "um4", "ini": em("f4", "umidade"), "fim": ini("f5") + .3, "ufs": [u for u in UMID_UF if u != "PI"], "cor": LAR, "alfa": .3},
    {"id": "frio5", "ini": em("f5", "frio"), "fim": ini("f6") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .35},
    {"id": "sp6", "ini": em("f6", "paulista"), "fim": ini("f7") + .3, "ufs": ["SP"], "cor": LAR, "alfa": .35},
    {"id": "sul6", "ini": em("f6", "Sul"), "fim": ini("f7") + .3, "ufs": SUL_UF, "cor": VERM, "alfa": .35},
    {"id": "dom7", "ini": em("f7", "sobe"), "fim": ini("f8") + .3, "ufs": DOM_UF, "cor": VERM, "alfa": .35},
    {"id": "ne8", "ini": em("f8", "Nordeste"), "fim": ini("f9") + .3, "ufs": ["MA", "PI", "PE", "PB", "BA"], "cor": AZUL, "alfa": .25},
    {"id": "cs9", "ini": em("f9", "acima"), "fim": ini("f10") + .3,
     "ufs": ["MT", "MS", "GO", "DF", "MG", "SP", "RJ", "ES", "PR", "SC", "RS", "BA", "PI", "MA", "PE", "PB", "CE", "RN", "AL", "SE", "TO"], "cor": AZUL, "alfa": .2},
    {"id": "amz9", "ini": em("f9", "Amazônia"), "fim": ini("f10") + .3, "ufs": ["AM", "PA", "RR", "AP", "AC"], "cor": LAR, "alfa": .3},
    {"id": "frio10", "ini": em("f10", "frio"), "fim": ini("f11") + .3, "ufs": ["RS", "SC", "PR", "SP", "MS"], "cor": FRIO, "alfa": .35},
]

pinos = [
    {"nome": "Minas Gerais", "sub": "pancadas e trovoadas", "lon": -44.5, "lat": -18.5, "ini": em("f2", "pancadas"), "fim": ini("f3"), "h": 220},
    {"nome": "São Paulo", "sub": "toró pontual", "lon": -47.5, "lat": -22.6, "ini": em("f2", "toró"), "fim": ini("f3"), "h": 160},
    {"nome": "Minas Gerais", "sub": f"{UF_H['MG']} cidades em alerta", "lon": -44.5, "lat": -18.5, "ini": em("f3", "Minas"), "fim": ini("f4"), "h": 220},
    {"nome": "São Paulo", "sub": f"{UF_H['SP']} cidades em alerta", "lon": -48.5, "lat": -22.3, "ini": em("f3", "Paulo"), "fim": ini("f4"), "h": 160},
    {"nome": "Teresina", "sub": f"máxima de {TPICO[0]:.1f} °C hoje".replace(".", ","), "lon": -42.80, "lat": -5.09, "ini": em("f4", "Piauí"), "fim": ini("f5"), "h": 240},
    {"nome": "Umidade baixa", "sub": f"INMET: {len(UMID)} cidades", "lon": -36.5, "lat": -7.2, "ini": em("f4", "umidade"), "fim": ini("f5"), "h": 170},
    {"nome": "Serra (SC e RS)", "sub": "sábado: 5 a 7 °C", "lon": -49.93, "lat": -28.29, "ini": em("f5", "serra"), "fim": ini("f6"), "h": 200},
    {"nome": "Curitiba", "sub": "sábado: 14 °C", "lon": -49.27, "lat": -25.43, "ini": em("f5", "Curitiba"), "fim": ini("f6"), "h": 170},
    {"nome": "Porto Alegre", "sub": "sábado: 14 °C", "lon": -51.23, "lat": -30.03, "ini": em("f5", "Porto"), "fim": ini("f6"), "h": 150},
    {"nome": "Oeste paulista", "sub": "sábado: até 35 °C", "lon": -51.39, "lat": -22.12, "ini": em("f6", "paulista"), "fim": GRA, "h": 200},
    {"nome": f"{NE_TOP[1]} mm até 27/11", "sub": f"soma prevista ({NE_TOP[0]['uf']}) · Open-Meteo", "lon": NE_TOP[0]["p"][0], "lat": NE_TOP[0]["p"][1],
     "ini": em("f8", "Nordeste"), "fim": ini("f9"), "h": 260},
    {"nome": f"{VTOPO} mm até 27/11", "sub": f"maior soma prevista ({TOPO['uf']}) · Open-Meteo", "lon": TOPO["p"][0], "lat": TOPO["p"][1],
     "ini": em("f9", "acima"), "fim": ini("f10"), "h": 220},
]

# ---------------------------------------------------------------- textos
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
mil = lambda v: f"{v:,}".replace(",", ".")
hero = [{"ini": CAPA - .2, "fim": HERO_F,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:104px">TEMPESTADE</div>'
                 f'<div class="t4" style="font-size:44px;line-height:1.35">alerta em {mil(len(TEMP))} cidades</div>'}]
paineis = [
    {"ini": HERO_F, "fim": ini("f2"), "k": "INMET · TEMPESTADE HOJE",
     "contador": conta(len(TEMP), "f1", "2653", "#ff2a1f", "CIDADES NO BRASIL", lead=.9),
     "l": "chuva, raios, vento e granizo", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "POR QUE CHOVE ASSIM",
     "itens": [{"t": em("f2", "calor"), "txt": "🌡️ calor + umidade"},
               {"t": em("f2", "pancadas"), "txt": "⛈️ pancadas isoladas"},
               {"t": em("f2", "toró"), "txt": "🎯 toró num canto, nada no outro"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "INMET · TEMPESTADE HOJE",
     "contador": conta(UF_H["MG"], "f3", "853", "#ff2a1f", "CIDADES EM MINAS"),
     "itens": [{"t": em("f3", "645"), "txt": f"⛈️ São Paulo: {UF_H['SP']}"},
               {"t": em("f3", "cidades", 2), "txt": f"🇧🇷 TOTAL NO BRASIL: {mil(len(TEMP))}"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "NORDESTE · HOJE",
     "contador": conta(TPICO[0], "f4", "40", "#ff2a1f", "°C EM TERESINA", dec=1),
     "itens": [{"t": em("f4", "381"), "txt": f"💧 umidade baixa: {len(UMID)} cidades"}],
     "l": "Piauí perto de 40 °C", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "SÁBADO · AMANHECER",
     "itens": [{"t": em("f5", "serra"), "txt": "❄️ serra: 5 a 7 °C"},
               {"t": em("f5", "Curitiba"), "txt": "🥶 Curitiba e Porto Alegre 14 °C"}],
     "l": "previsão", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f6"), "fim": GRA, "k": "SÁBADO · À TARDE",
     "contador": conta(35, "f6", "35", "#ff2a1f", "°C NO OESTE PAULISTA"),
     "l": f"INMET: tempestade no Sul em {len(SABS)} cidades", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f7") + .2, "fim": TORO, "k": "DOMINGO · INMET",
     "contador": conta(len(DOM), "f7", "4299", "#ff2a1f", "CIDADES COM ALERTA DE TEMPESTADE"),
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "DOMINGO · NORDESTE",
     "itens": [{"t": em("f8", "Maranhão"), "txt": "🌧️ Maranhão e Piauí"},
               {"t": em("f8", "Pernambuco"), "txt": "🌧️ sertão de PE e Paraíba"},
               {"t": em("f8", "Bahia"), "txt": "🌧️ norte da Bahia"}],
     "l": "colunas: chuva prevista somada até 27/11", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "15 DIAS (PREVISÃO)",
     "itens": [{"t": em("f9", "acima"), "txt": "🌧️ acima da média: quase todo o país"},
               {"t": em("f9", "Amazônia"), "txt": "🟧 abaixo: Amazônia"}],
     "l": f"Open-Meteo: até {VTOPO} mm no {TOPO['uf']} · {VMG} mm em MG", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "DEPOIS DE 20/11",
     "itens": [{"t": em("f10", "frio"), "txt": "❄️ o ar frio volta"},
               {"t": em("f10", "Sul"), "txt": "🥶 Sul e São Paulo"}],
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
        assert c["dur"] > .15 and c["ini"] + c["dur"] <= a["fim"], ("contador fora do painel", a["k"])

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": HERO_F, "html": f"<b>{MET}</b> · <b>INMET</b>"},
    {"ini": HERO_F, "fim": ini("f2"), "html": f"<b>INMET</b>, aviso de tempestade de 13/11 · <b>{MET}</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INMET</b>, aviso de tempestade de 13/11"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · <b>Open-Meteo</b>, máxima de Teresina · <b>INMET</b>, baixa umidade"},
    {"ini": ini("f5"), "fim": GRA, "html": f"<b>{MET}</b> · previsão · <b>INMET</b>, tempestade de 14/11"},
    {"ini": GRA, "fim": ini("f7"), "html": f"<b>{MET}</b> · foto do granizo: ilustração"},
    {"ini": ini("f7"), "fim": TORO, "html": "<b>INMET</b>, aviso de tempestade de 15/11"},
    {"ini": TORO, "fim": ini("f8"), "html": f"<b>{MET}</b> · foto do temporal: ilustração"},
    {"ini": ini("f8"), "fim": ini("f10"), "html": f"<b>{MET}</b> · <b>Open-Meteo</b>, chuva prevista somada de 13 a 27/11"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "umidade": "#5ec8ff", "pancadas": "#5ec8ff", "pancadao": "#5ec8ff", "toro": "#5ec8ff",
         "frio": "#96d2ff", "amanhecer": "#96d2ff", "graus": "#ff2a1f", "granizo": "#ff2a1f", "tempestade": "#ff2a1f", "sobe": "#ff2a1f",
         "alerta": "#ff8c1a", "vento": "#ff8c1a", "calor": "#ff8c1a", "acima": "#ff2a1f", "abaixo": "#ff8c1a", "baixa": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "sao", "paulo", "minas", "brasil", "nordeste", "piaui", "serra", "curitiba", "porto", "alegre", "oeste", "paulista",
         "rio", "sertao", "maranhao", "pernambuco", "paraiba", "bahia", "amazonia", "pais", "inemaclub", "onde"}
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
      f"INMET tempestade hoje {len(TEMP)} (MG {UF_H['MG']} SP {UF_H['SP']}) · umidade {len(UMID)} · Sul sáb {len(SABS)} · dom {len(DOM)} · "
      f"colunas {len(col)} (topo {VTOPO} mm em {TOPO['uf']}) · NE {NE_TOP[1]} mm ({NE_TOP[0]['uf']}) · MG {VMG} mm · Teresina {TPICO[0]}")
