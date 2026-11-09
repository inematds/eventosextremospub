#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 09/11/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da chuva prevista de 10 a 16/11 na grade do Brasil (Open-Meteo, om/prev15_grade.json, gravado por
coleta/previsao15d.py --dia 2026-11-09).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "GEADA EM NOVEMBRO / 0,8 °C / SERRA CATARINENSE"),
serra catarinense com câmera inclinada (Morro da Igreja 0,8 °C), geada (foto do Codex, ilustração), São Joaquim e Florianópolis,
ar frio e frente fria no litoral (IR do GOES-19, câmera inclinada), máximas de inverno no Sudeste, INMET tempestade hoje
(1.273 cidades) e chuvas intensas no Norte, Nordeste até 40 °C, abaixo de zero amanhã na serra, Vale do Itajaí
(rio 7,30 m em Rio do Sul, barragem de Ituporanga 109%: foto do Codex, ilustração), chuva volta ao Sul, colunas 3D da chuva
prevista no centro do país até 16/11 (Open-Meteo) e chuva acima da média de 10 a 20/11.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "09/11/2026"
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
SERRA = {"lon": -49.6, "lat": -28.2, "zoom": 7.6}      # f1: Morro da Igreja (Urubici), câmera inclinada
SC = {"lon": -49.4, "lat": -27.9, "zoom": 6.6}         # f2: São Joaquim e Florianópolis
FRENTE = {"lon": -48.5, "lat": -22.0, "zoom": 4.7}     # f3: ar frio no centro-sul, frente fria no litoral (IR)
SE = {"lon": -45.0, "lat": -21.6, "zoom": 5.6}         # f4: São Paulo, Rio e BH
NORTE = {"lon": -55.0, "lat": -10.5, "zoom": 4.0}      # f5: chuva no Norte e aviso de tempestade
NE = {"lon": -39.0, "lat": -9.6, "zoom": 6.0}          # f6: sertão de PE, norte da BA
FRIO2 = {"lon": -52.0, "lat": -27.2, "zoom": 5.5}      # f7: serra catarinense, sul do PR e campanha gaúcha
VALE = {"lon": -49.6, "lat": -27.3, "zoom": 8.4}       # f8: Rio do Sul e Ituporanga
SUL = {"lon": -51.0, "lat": -27.4, "zoom": 5.5}        # f9: chuva volta ao Sul
COL = {"lon": -49.0, "lat": -13.0, "zoom": 4.6}        # f10: colunas 3D da chuva prevista no centro do país
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.0  # quadro 0 = capa cheia do Codex até aqui
GEADA = em("f2", "geada")
SJ = em("f2", "Joaquim")
BARR = em("f8", "barragem")
camera = [
    K(0, BR), K(CAPA, BR), K(ini("f1") + 3.6, SERRA, 45, -15), K(fim("f1") - .2, {**SERRA, "zoom": 7.8}, 50, 5),
    K(SJ - .2, SC, 0, 0), K(fim("f2") - .2, {**SC, "zoom": 6.7}, 4, 0),
    K(ini("f3") + 1.0, FRENTE, 30, -10), K(fim("f3") - .2, {**FRENTE, "zoom": 4.8}, 32, 0),
    K(ini("f4") + 1.0, SE, 0, 0), K(fim("f4") - .2, {**SE, "zoom": 5.7}, 4, 0),
    K(ini("f5") + 1.0, NORTE, 0, 0), K(fim("f5") - .2, {**NORTE, "zoom": 4.05}, 0, 0),
    K(ini("f6") + 1.0, NE, 0, 0), K(fim("f6") - .2, {**NE, "zoom": 6.1}, 4, 0),
    K(ini("f7") + 1.0, FRIO2, 0, 0), K(fim("f7") - .2, {**FRIO2, "zoom": 5.6}, 4, 0),
    K(ini("f8") + 1.0, VALE, 40, -10), K(fim("f8") - .2, {**VALE, "zoom": 8.6}, 45, 6),
    K(ini("f9") + 1.0, SUL, 0, 0), K(fim("f9") - .2, {**SUL, "zoom": 5.6}, 4, 0),
    K(ini("f10") + 1.2, COL, 55, -20), K(fim("f10") - .2, {**COL, "zoom": 4.75}, 56, 15),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na frente fria (f3)
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
              "ini": ini("f3") - .3, "fim": ini("f4") + .3, "dur": ini("f4") - ini("f3") + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])
assert len(BONS) >= 36, f"poucos quadros bons de infravermelho: {len(BONS)}"
imagens = []

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de 10 a 16/11 no centro do país (Open-Meteo, grade de 1,5°)
G15 = json.loads((AQUI / "om/prev15_grade.json").read_text())
CS = {"TO", "GO", "MT", "MG", "BA", "MA", "PI", "MS", "DF"}   # onde o boletim diz que a chuva fica acima da média
dias = G15["pts"][0]["dias"]
ND = 7
assert dias[0] == "2026-11-10" and dias[ND - 1] == "2026-11-16", (dias[0], dias[ND - 1])
SOMA = [(p, round(sum(x or 0 for x in p["chuva"][:ND]))) for p in G15["pts"] if p["uf"] in CS]
col = [{"id": i, "p": p["p"], "v": v, "cor": [60, 150, 255] if v >= 80 else [120, 190, 255]} for i, (p, v) in enumerate(SOMA) if v >= 40]
ordem = {c["id"]: (c["p"][0] + 62) * .08 for c in col}   # varre de oeste para leste
colunas = [{"id": "chuva3d", "ini": ini("f10") + .3, "fim": ini("f11") + .3, "dados": col, "raio": 55000, "escala": 3200, "ordem": ordem, "varredura": 1}]
TOPO = max(SOMA, key=lambda x: x[1])
assert TOPO[1] == 136 and TOPO[0]["uf"] == "TO" and len(col) >= 30, (TOPO[0]["uf"], TOPO[1], len(col))   # a fala f10 diz "136 milímetros"

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, geada e barragem
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/geada.png", "ini": GEADA - .1, "fim": SJ - .1, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/barragem.png", "ini": BARR - .1, "fim": fim("f8") + .1, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET (hoje 09/11 e amanhã 10/11)
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
assert aviso[56358]["descricao"] == "Tempestade" and aviso[56358]["inicio"].startswith("2026-11-09"), 56358
assert aviso[56355]["descricao"] == "Chuvas Intensas" and aviso[56355]["inicio"].startswith("2026-11-09"), 56355
TEMP = geo(56358)                  # tempestade hoje: 1.273 cidades
assert len(TEMP) == 1273, len(TEMP)
INT = geo(56355)                   # chuvas intensas hoje no Norte: 146 cidades
assert len(INT) == 146, len(INT)
UFCOD = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN",
         "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC",
         "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
from collections import Counter
POR_UF = Counter(UFCOD[c[:2]] for c in TEMP)
assert (POR_UF["BA"], POR_UF["MG"], POR_UF["GO"]) == (299, 281, 244), POR_UF
TEMP_UF = [u for u, k in POR_UF.items() if k >= 25]   # estados com 25+ municípios no aviso de tempestade
INT_UF = sorted(Counter(UFCOD[c[:2]] for c in INT))  # AC, AM, MT, PA, RO

# ---------------------------------------------------------------- estados
estados = [
    {"id": "sc1", "ini": em("f1", "Frio"), "fim": ini("f3") + .3, "ufs": ["SC"], "cor": FRIO, "alfa": .35},
    {"id": "frio3", "ini": em("f3", "frio"), "fim": ini("f4") + .3, "ufs": ["RS", "SC", "PR", "SP", "RJ", "MG", "ES", "MS"], "cor": FRIO, "alfa": .3},
    {"id": "se4", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["SP", "RJ", "MG"], "cor": FRIO, "alfa": .35},
    {"id": "norte", "ini": em("f5", "Norte"), "fim": ini("f6") + .3, "ufs": INT_UF, "cor": AZUL, "alfa": .4},
    {"id": "temp", "ini": em("f5", "tempestade"), "fim": ini("f6") + .3, "ufs": TEMP_UF, "cor": LAR, "alfa": .35},
    {"id": "calor", "ini": em("f6", "Nordeste"), "fim": ini("f7") + .3, "ufs": ["PE", "BA", "SE", "AL"], "cor": VERM, "alfa": .42},
    {"id": "frio7", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .35},
    {"id": "vale", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["SC"], "cor": AZUL, "alfa": .3},
    {"id": "sul9", "ini": em("f9", "Sul"), "fim": ini("f10") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .35},
    {"id": "centro", "ini": em("f10", "centro"), "fim": ini("f11") + .3, "ufs": sorted(CS), "cor": AZUL, "alfa": .22},
]

pinos = [
    {"nome": "Morro da Igreja", "sub": "0,8 °C hoje de manhã · Urubici (SC)", "lon": -49.48, "lat": -28.12, "ini": em("f1", "Morro"), "fim": GEADA - .1, "h": 260},
    {"nome": "São Joaquim", "sub": "1,8 °C e geada", "lon": -49.93, "lat": -28.29, "ini": SJ, "fim": ini("f3"), "h": 200},
    {"nome": "Florianópolis", "sub": "10 °C ao amanhecer", "lon": -48.55, "lat": -27.59, "ini": em("f2", "Florianópolis"), "fim": ini("f3"), "h": 340},
    {"nome": "frente fria", "sub": "no litoral, organiza a chuva", "lon": -40.5, "lat": -21.5, "ini": em("f3", "litoral"), "fim": ini("f4"), "h": 220},
    {"nome": "São Paulo", "sub": "máxima de 18 °C", "lon": -46.63, "lat": -23.55, "ini": em("f4", "Paulo"), "fim": ini("f5"), "h": 160},
    {"nome": "Rio de Janeiro", "sub": "máxima de 22 °C", "lon": -43.2, "lat": -22.9, "ini": em("f4", "Rio"), "fim": ini("f5"), "h": 300},
    {"nome": "Belo Horizonte", "sub": "máxima de 23 °C", "lon": -43.94, "lat": -19.92, "ini": em("f4", "Horizonte"), "fim": ini("f5"), "h": 220},
    {"nome": "Acre e Rondônia", "sub": "pancadas fortes · INMET: chuvas intensas", "lon": -64.0, "lat": -10.5, "ini": em("f5", "pancadas"), "fim": ini("f6"), "h": 200},
    {"nome": "sertão de Pernambuco", "sub": "até 40 °C", "lon": -38.3, "lat": -8.2, "ini": em("f6", "Pernambuco"), "fim": ini("f7"), "h": 260},
    {"nome": "norte da Bahia", "sub": "35 a 40 °C", "lon": -40.3, "lat": -10.2, "ini": em("f6", "Bahia"), "fim": ini("f7"), "h": 160},
    {"nome": "serra catarinense", "sub": "abaixo de zero amanhã", "lon": -49.93, "lat": -28.29, "ini": em("f7", "zero"), "fim": ini("f8"), "h": 200},
    {"nome": "sul do Paraná", "sub": "geada isolada", "lon": -51.5, "lat": -25.9, "ini": em("f7", "Paraná"), "fim": ini("f8"), "h": 110},
    {"nome": "campanha gaúcha", "sub": "geada isolada", "lon": -55.0, "lat": -30.6, "ini": em("f7", "campanha"), "fim": ini("f8"), "h": 160},
    {"nome": "Rio do Sul", "sub": "rio Itajaí do Sul em 7,30 m", "lon": -49.64, "lat": -27.21, "ini": em("f8", "Rio", 1), "fim": BARR - .1, "h": 300},
    {"nome": "Vale do Itajaí", "sub": "chuva aumenta no fim de semana", "lon": -49.4, "lat": -27.0, "ini": em("f9", "Itajaí"), "fim": ini("f10"), "h": 260},
    {"nome": f"{TOPO[1]} mm até 16/11", "sub": f"{TOPO[0]['uf']} · soma prevista · Open-Meteo", "lon": TOPO[0]["p"][0], "lat": TOPO[0]["p"][1],
     "ini": em("f10", "136"), "fim": ini("f11"), "h": 220},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)   # número dito logo no começo da fala: o contador começa com a fala
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
H = em("f1", "Morro") - .1   # o hero (data grande + 0,8 °C) fica até "Morro da Igreja"
P8B = BARR - .1             # painel da barragem
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#3c96ff;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:96px">FRIO DE INVERNO</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">0,8 °C na serra catarinense</div>'}]
paineis = [
    {"ini": H, "fim": ini("f2"), "k": "MORRO DA IGREJA · HOJE CEDO",
     "itens": [{"t": H, "txt": "🥶 Morro da Igreja: 0,8 °C"},
               {"t": em("f1", "serra"), "txt": "Urubici 0,9 · Bom Jardim 1,4 °C"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "SANTA CATARINA · 09/11",
     "itens": [{"t": GEADA, "txt": "❄️ geada na serra"},
               {"t": SJ, "txt": "🥶 São Joaquim: 1,8 °C"},
               {"t": em("f2", "Florianópolis"), "txt": "🌡️ Florianópolis: 10 °C"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "POR QUE ESTÁ FRIO",
     "itens": [{"t": em("f3", "frio"), "txt": "🥶 ar frio no Sul e Sudeste"},
               {"t": em("f3", "litoral"), "txt": "🌀 frente fria no litoral"},
               {"t": em("f3", "centro"), "txt": "🌧️ chuva no centro e no norte"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "MÁXIMA HOJE · SÃO PAULO",
     "contador": conta(18, "f4", "18", "#96d2ff", "°C (PREVISÃO)", de=28),
     "l": "Rio 22 °C · BH 23 °C · Vitória 24 °C", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "INMET · TEMPESTADE HOJE",
     "contador": conta(1273, "f5", "1.273", "#ff8c1a", "CIDADES NO BRASIL"),
     "l": f"BA {POR_UF['BA']}, MG {POR_UF['MG']}, GO {POR_UF['GO']}, PI {POR_UF['PI']}, TO {POR_UF['TO']}", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "NORDESTE · HOJE 09/11",
     "contador": conta(40, "f6", "40", "#ff2a1f", "°C (PREVISÃO)", de=30),
     "l": "sertão de PE, norte da BA, SE e AL", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "AMANHÃ · TERÇA 10/11",
     "itens": [{"t": em("f7", "zero"), "txt": "🥶 serra de SC abaixo de 0 °C"},
               {"t": em("f7", "geada"), "txt": "❄️ geada no sul do PR e no RS"}],
     "l": "previsão", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f8"), "fim": P8B, "k": "RIO DO SUL · RIO ITAJAÍ DO SUL",
     "contador": conta(7.30, "f8", "7,30", "#5ec8ff", "METROS HOJE", dec=2, de=5.0),
     "l": "medido às 5h50 de 09/11", "borda": "rgba(94,200,255,.8)"},
    {"ini": P8B, "fim": ini("f9"), "k": "BARRAGEM DE ITUPORANGA",
     "contador": conta(109, "f8", "109%", "#5ec8ff", "% DA CAPACIDADE", de=80),
     "l": "vertendo · Taió perto de 75%", "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "SUL · PRÓXIMOS DIAS",
     "itens": [{"t": em("f9", "quinta"), "txt": "🌧️ chuva volta qui e sex"},
               {"t": em("f9", "fim"), "txt": "⛈️ Vale do Itajaí: mais chuva no fim de semana"}],
     "l": "previsão", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "CHUVA PREVISTA · 10 A 16/11",
     "contador": conta(136, "f10", "136", "#5ec8ff", "MM PREVISTOS"),
     "l": "colunas: soma prevista · Open-Meteo · 10 a 20/11 acima da média", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "onde"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f11", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
     "borda": "rgba(250,204,21,.8)"},
]
for a, b in zip(paineis, paineis[1:]):
    assert a["fim"] <= b["ini"] + 1e-6, (a["k"], b["k"])
for a in paineis:
    if a.get("contador"):
        c = a["contador"]
        if c["ini"] < a["ini"]:   # contador não pode começar antes do painel (barragem logo depois do rio)
            c["dur"] -= a["ini"] - c["ini"]; c["ini"] = a["ini"]
        assert c["dur"] > .3 and c["ini"] + c["dur"] <= a["fim"], ("contador fora do painel", a["k"])

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f3"), "html": f"<b>{MET}</b> · temperaturas da manhã · foto da geada: ilustração"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b> · satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · previsão das máximas"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · <b>INMET</b>, avisos de tempestade e chuvas intensas de 09/11"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · nível do rio e das barragens · foto da barragem: ilustração"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b> · <b>Open-Meteo</b>, chuva prevista somada de 10 a 16/11"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "rio": "#5ec8ff", "metros": "#5ec8ff", "milimetros": "#5ec8ff", "barragem": "#5ec8ff", "vertendo": "#5ec8ff",
         "frio": "#96d2ff", "fria": "#96d2ff", "inverno": "#96d2ff", "geada": "#96d2ff", "zero": "#96d2ff", "grau": "#96d2ff",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "tempestade": "#ff8c1a", "aviso": "#ff8c1a", "pancadas": "#5ec8ff",
         "frente": "#96d2ff", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "sudeste", "norte", "brasil", "nordeste", "centro", "parana", "santa", "catarina", "catarinense", "serra", "morro", "igreja",
         "sao", "joaquim", "florianopolis", "paulo", "belo", "horizonte", "pernambuco", "bahia", "campanha", "gaucha", "vale", "itajai",
         "ituporanga", "inemaclub", "onde"}
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
     "marca": "INEMA · CLIMA DO DIA", "selo": DATA[:5] + " · INMET · Open-Meteo · NOAA",
     "camera": camera, "sat": SAT, "imagens": imagens, "colunas": colunas, "telas": telas, "estados": estados, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"INMET tempestade {len(TEMP)} · chuvas intensas {len(INT)} · colunas {len(col)} (máx {TOPO[0]['uf']} {TOPO[1]} mm)")
