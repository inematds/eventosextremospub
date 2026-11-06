#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 06/11/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da chuva prevista de 07 a 08/11 na grade do Brasil (Open-Meteo, om/prev15_grade.json, gravado por
coleta/previsao15d.py --dia 2026-11-06).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "ALERTA VERMELHO NO SUL / 325 CIDADES / TEMPORAL NO SÁBADO"),
INMET tempestade grande perigo no sábado (325 no Sul → 3.170 no Brasil), frente fria na Argentina (câmera inclinada, IR do GOES-19),
Rio do Sul 5,64 m, Nordeste 42 °C, colunas 3D da chuva prevista de 07 a 08/11 (Open-Meteo), vendaval no litoral de SP e RJ
(foto do Codex, ilustração), São Paulo 30 → 18 °C, geada (foto do Codex, ilustração) e serra catarinense abaixo de zero,
semana fria e chuva no Nordeste entre 10 e 20/11.
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
LAR, AMA, VERM, AZUL, FRIO = [255, 140, 26], [250, 204, 21], [255, 42, 31], [60, 150, 255], [150, 210, 255]

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
SUL = {"lon": -51.8, "lat": -27.6, "zoom": 5.3}        # f1/f2: alerta vermelho no RS, SC e PR
INB = {"lon": -50.0, "lat": -18.0, "zoom": 4.0}        # f2: o Brasil todo (3.170 cidades)
ARG = {"lon": -58.5, "lat": -31.5, "zoom": 4.7}        # f3: frente fria na Argentina (câmera inclinada, Blue Marble por baixo)
PRSC = {"lon": -51.5, "lat": -26.0, "zoom": 5.5}       # f3: chuva no Paraná e em Santa Catarina
RDS = {"lon": -49.6, "lat": -27.1, "zoom": 7.4}        # f4: Rio do Sul
NE = {"lon": -40.5, "lat": -8.5, "zoom": 5.0}          # f5: Piauí, Pernambuco e norte da Bahia
COL = {"lon": -51.6, "lat": -28.2, "zoom": 5.7}        # f6: colunas 3D da chuva prevista de 07 a 08/11
COSTA = {"lon": -45.2, "lat": -23.3, "zoom": 6.0}      # f7: litoral de São Paulo e do Rio
SP = {"lon": -46.8, "lat": -23.4, "zoom": 6.2}         # f8: São Paulo
CAMP = {"lon": -55.0, "lat": -30.3, "zoom": 6.0}       # f9: campanha gaúcha
SERRA = {"lon": -49.9, "lat": -28.2, "zoom": 6.8}      # f9: serra catarinense
SSE = {"lon": -49.0, "lat": -23.5, "zoom": 4.6}        # f10: Sul e Sudeste
NEC = {"lon": -42.0, "lat": -9.0, "zoom": 4.6}         # f10: Nordeste
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.0  # quadro 0 = capa cheia do Codex até aqui
BR2 = em("f2", "3.170")
PR3 = em("f3", "Paraná")
VENTO = em("f7", "vento")
LIT7 = em("f7", "litoral")
GEADA = em("f9", "geada")
SEG9 = em("f9", "segunda")
NE10 = em("f10", "chuva")
camera = [
    K(0, BR), K(CAPA, BR), K(ini("f1") + 3.6, SUL), K(fim("f1") - .2, {**SUL, "zoom": 5.45}, 0, 0),
    K(BR2 - .6, {**SUL, "zoom": 5.5}, 0, 0), K(BR2 + .6, INB, 0, 0), K(fim("f2") - .2, {**INB, "zoom": 4.05}, 0, 0),
    K(ini("f3") + 1.0, ARG, 30, -10), K(PR3 - .3, {**ARG, "zoom": 4.85}, 32, 0),
    K(PR3 + 1.0, PRSC, 0, 0), K(fim("f3") - .2, {**PRSC, "zoom": 5.6}, 0, 0),
    K(ini("f4") + 1.0, RDS, 35, -8), K(fim("f4") - .2, {**RDS, "zoom": 7.55}, 42, 6),
    K(ini("f5") + 1.0, NE, 0, 0), K(fim("f5") - .2, {**NE, "zoom": 5.1}, 4, 0),
    K(ini("f6") + 1.2, COL, 55, -20), K(fim("f6") - .2, {**COL, "zoom": 5.8}, 56, 12),
    K(ini("f7") + 1.0, COSTA, 0, 0), K(fim("f7") - .2, {**COSTA, "zoom": 6.15}, 4, 0),
    K(ini("f8") + 1.0, SP, 0, 0), K(fim("f8") - .2, {**SP, "zoom": 6.35}, 4, 0),
    K(ini("f9") + 1.0, CAMP, 0, 0), K(SEG9 - .2, {**CAMP, "zoom": 6.1}, 0, 0), K(SEG9 + 1.0, SERRA, 0, 0), K(fim("f9") - .2, {**SERRA, "zoom": 6.9}, 4, 0),
    K(ini("f10") + 1.0, SSE, 0, 0), K(NE10 - .2, {**SSE, "zoom": 4.65}, 0, 0), K(NE10 + 1.0, NEC, 0, 0), K(fim("f10") - .2, {**NEC, "zoom": 4.7}, 4, 0),
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


# câmera inclinada e Argentina: o Blue Marble do mundo por baixo do geocolor (sem borda preta)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": ini("f3") - .3, "fim": ini("f4") + .3, "dur": ini("f4") - ini("f3") + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])
assert len(BONS) >= 36, f"poucos quadros bons de infravermelho: {len(BONS)}"
imagens = []

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de 07 a 08/11 (Open-Meteo, grade de 1,5°)
G15 = json.loads((AQUI / "om/prev15_grade.json").read_text())
CS = {"RS", "SC", "PR"}   # onde o boletim diz que a frente fria passa no sábado
dias = G15["pts"][0]["dias"]
ND = 2
assert dias[0] == "2026-11-07" and dias[ND - 1] == "2026-11-08", (dias[0], dias[ND - 1])
SOMA = [(p, round(sum(x or 0 for x in p["chuva"][:ND]))) for p in G15["pts"] if p["uf"] in CS]
col = [{"id": i, "p": p["p"], "v": v, "cor": [60, 150, 255] if v >= 50 else [120, 190, 255]} for i, (p, v) in enumerate(SOMA) if v >= 15]
ordem = {c["id"]: (-c["p"][1] - 25) * .12 for c in col}   # sobe do RS para SC e o PR, como a frente
colunas = [{"id": "chuva3d", "ini": ini("f6") + .3, "fim": ini("f7") + .3, "dados": col, "raio": 60000, "escala": 4200, "ordem": ordem, "varredura": 1}]
TOPO = max(SOMA, key=lambda x: x[1])
assert TOPO[1] == 84 and len(col) >= 6, (TOPO[0]["uf"], TOPO[1], len(col))   # a fala f6 diz "84 milímetros"
UFN = {"RS": "norte do RS", "SC": "oeste de SC", "PR": "PR"}

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, vendaval e geada
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/vendaval.png", "ini": VENTO - .1, "fim": LIT7 + .2, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/geada.png", "ini": GEADA - .1, "fim": SEG9 - .1, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET (sábado 07/11 e domingo 08/11)
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
for i in (56308, 56309, 56310):
    assert aviso[i]["descricao"] == "Tempestade" and aviso[i]["inicio"].startswith("2026-11-07"), i
assert aviso[56310]["severidade"] == "Grande Perigo", aviso[56310]["severidade"]
VERMELHO = geo(56310)                         # tempestade, grande perigo (vermelho) no sábado: RS 124, SC 112, PR 89
assert len(VERMELHO) == 325, len(VERMELHO)
SAB_T = geo(56308) | geo(56309) | geo(56310)  # aviso de tempestade no sábado: 3.170 cidades
assert len(SAB_T) == 3170, len(SAB_T)
UFCOD = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN",
         "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC",
         "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
from collections import Counter
POR_UF = Counter(UFCOD[c[:2]] for c in SAB_T)
VER_UF = Counter(UFCOD[c[:2]] for c in VERMELHO)
assert (VER_UF["RS"], VER_UF["SC"], VER_UF["PR"]) == (124, 112, 89), VER_UF
SAB_UF = [u for u, k in POR_UF.items() if k >= 40]   # estados com 40+ municípios no aviso
assert aviso[56281]["descricao"] == "Declínio de Temperatura" and aviso[56281]["inicio"].startswith("2026-11-08"), aviso[56281]["descricao"]
FRIO8 = Counter(UFCOD[c[:2]] for c in geo(56281))      # declínio de temperatura no domingo 08/11
FRIO_UF = [u for u, k in FRIO8.items() if k >= 20]
assert aviso[56285]["descricao"] == "Baixa Umidade" and aviso[56286]["descricao"] == "Baixa Umidade"
SECO = len(geo(56285) | geo(56286))                    # baixa umidade hoje no Nordeste

# ---------------------------------------------------------------- estados
estados = [
    {"id": "sul1", "ini": em("f1", "frente"), "fim": em("f1", "vermelho"), "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .3},
    {"id": "verm", "ini": em("f1", "vermelho"), "fim": BR2 - .1, "ufs": list(VER_UF), "cor": VERM, "alfa": .45},
    {"id": "sab_br", "ini": BR2 - .1, "fim": ini("f3") + .3, "ufs": SAB_UF, "cor": LAR, "alfa": .35},
    {"id": "pr3", "ini": PR3, "fim": ini("f4") + .3, "ufs": ["PR"], "cor": AZUL, "alfa": .35},
    {"id": "sc3", "ini": em("f3", "Catarina"), "fim": ini("f4") + .3, "ufs": ["SC"], "cor": AZUL, "alfa": .35},
    {"id": "vale", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["SC"], "cor": AZUL, "alfa": .3},
    {"id": "ne", "ini": em("f5", "Nordeste"), "fim": ini("f6") + .3, "ufs": ["MA", "CE", "RN", "PB", "AL", "SE"], "cor": LAR, "alfa": .22},
    {"id": "calor", "ini": em("f5", "Piauí"), "fim": ini("f6") + .3, "ufs": ["PI", "PE", "BA"], "cor": VERM, "alfa": .45},
    {"id": "chuva6", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .3},
    {"id": "vento", "ini": LIT7, "fim": ini("f8") + .3, "ufs": ["SP", "RJ"], "cor": FRIO, "alfa": .35},
    {"id": "frio", "ini": em("f8", "despenca"), "fim": ini("f9") + .3, "ufs": FRIO_UF, "cor": FRIO, "alfa": .32},
    {"id": "camp", "ini": ini("f9"), "fim": SEG9, "ufs": ["RS"], "cor": FRIO, "alfa": .4},
    {"id": "serra", "ini": SEG9, "fim": ini("f10") + .3, "ufs": ["SC"], "cor": FRIO, "alfa": .4},
    {"id": "fria", "ini": em("f10", "fria"), "fim": NE10, "ufs": ["RS", "SC", "PR", "SP", "RJ", "MG", "ES"], "cor": FRIO, "alfa": .3},
    {"id": "chuva_ne", "ini": NE10, "fim": ini("f11") + .3, "ufs": ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"], "cor": AZUL, "alfa": .35},
]

pinos = [
    {"nome": "Rio Grande do Sul", "sub": f"{VER_UF['RS']} cidades em alerta vermelho", "lon": -53.0, "lat": -28.6, "ini": em("f1", "vermelho"), "fim": BR2 - .3, "h": 160},
    {"nome": "Santa Catarina", "sub": f"{VER_UF['SC']} cidades em alerta vermelho", "lon": -50.3, "lat": -27.2, "ini": em("f1", "tempestade"), "fim": BR2 - .3, "h": 200},
    {"nome": "Paraná", "sub": f"{VER_UF['PR']} cidades em alerta vermelho", "lon": -51.6, "lat": -25.2, "ini": em("f1", "sábado"), "fim": BR2 - .3, "h": 470},
    {"nome": "Argentina", "sub": "frente fria se formando", "lon": -60.5, "lat": -32.5, "ini": em("f3", "Argentina"), "fim": PR3 + .6, "h": 180},
    {"nome": "Paraná", "sub": "chuva desde hoje", "lon": -51.6, "lat": -25.0, "ini": PR3, "fim": ini("f4"), "h": 200},
    {"nome": "Santa Catarina", "sub": "chuva e trovoada à noite", "lon": -50.5, "lat": -27.2, "ini": em("f3", "Catarina"), "fim": ini("f4"), "h": 140},
    {"nome": "Rio do Sul", "sub": "rio Itajaí-Açu em 5,64 m", "lon": -49.64, "lat": -27.21, "ini": em("f4", "Sul"), "fim": ini("f5"), "h": 300},
    {"nome": "Piauí", "sub": "38 a 42 °C hoje", "lon": -42.6, "lat": -7.6, "ini": em("f5", "Piauí"), "fim": ini("f6"), "h": 220},
    {"nome": "Pernambuco", "sub": "calor forte", "lon": -37.9, "lat": -8.3, "ini": em("f5", "Pernambuco"), "fim": ini("f6"), "h": 140},
    {"nome": f"{TOPO[1]} mm até 08/11", "sub": f"{UFN[TOPO[0]['uf']]} · soma prevista · Open-Meteo", "lon": TOPO[0]["p"][0], "lat": TOPO[0]["p"][1],
     "ini": em("f6", "84"), "fim": ini("f7"), "h": 220},
    {"nome": "litoral de São Paulo", "sub": "rajadas de até 80 km/h", "lon": -46.3, "lat": -23.95, "ini": LIT7, "fim": ini("f8"), "h": 160},
    {"nome": "Rio de Janeiro", "sub": "vento forte na frente fria", "lon": -43.2, "lat": -22.9, "ini": em("f7", "Rio"), "fim": ini("f8"), "h": 240},
    {"nome": "São Paulo", "sub": "30 °C sábado · 18 °C domingo", "lon": -46.63, "lat": -23.55, "ini": em("f8", "Paulo"), "fim": ini("f9"), "h": 220},
    {"nome": "campanha gaúcha", "sub": "geada no domingo de manhã", "lon": -55.5, "lat": -30.6, "ini": SEG9 - .9, "fim": SEG9, "h": 180},
    {"nome": "serra catarinense", "sub": "abaixo de zero na segunda", "lon": -49.93, "lat": -28.29, "ini": SEG9 + .2, "fim": ini("f10"), "h": 200},
    {"nome": "Nordeste", "sub": "chuva entre 10 e 20/11", "lon": -40.5, "lat": -7.5, "ini": NE10 + .3, "fim": ini("f11"), "h": 200},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)   # número dito logo no começo da fala: o contador começa com a fala
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
H = em("f1", "INMET") - .1   # o hero (data grande) fica até "o INMET"
BR2P = BR2 - 1.1
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:96px">FRENTE FRIA</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">alerta vermelho de temporal no Sul</div>'}]
paineis = [
    {"ini": H, "fim": ini("f2"), "k": "INMET · SÁBADO 07/11",
     "itens": [{"t": H, "txt": "🔴 alerta vermelho"},
               {"t": em("f1", "tempestade"), "txt": "⛈️ tempestade no Sul"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": BR2P, "k": "INMET · ALERTA VERMELHO 07/11",
     "contador": conta(325, "f2", "325", "#ff2a1f", "CIDADES NO SUL"),
     "l": f"grande perigo · RS {VER_UF['RS']}, SC {VER_UF['SC']}, PR {VER_UF['PR']}", "borda": "rgba(255,42,31,.8)"},
    {"ini": BR2P, "fim": ini("f3"), "k": "INMET · TEMPESTADE · BRASIL SÁBADO",
     "contador": conta(3170, "f2", "3.170", "#ff8c1a", "CIDADES NO BRASIL", de=325),
     "l": f"MG {POR_UF['MG']}, SP {POR_UF['SP']}, RS {POR_UF['RS']}, PR {POR_UF['PR']}, SC {POR_UF['SC']}", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "FRENTE FRIA · HOJE 06/11",
     "itens": [{"t": em("f3", "Argentina"), "txt": "❄️ se forma na Argentina"},
               {"t": PR3, "txt": "🌧️ Paraná: chuva hoje"},
               {"t": em("f3", "Catarina"), "txt": "⛈️ Santa Catarina: à noite"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "RIO DO SUL · RIO ITAJAÍ-AÇU",
     "contador": conta(5.64, "f4", "5,64", "#5ec8ff", "METROS HOJE", dec=2, de=7.56),
     "l": "ontem 7,56 m · desce 4 a 6 cm por hora", "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "NORDESTE · HOJE 06/11",
     "contador": conta(42, "f5", "42", "#ff2a1f", "°C (PREVISÃO)", de=30),
     "l": f"PI, PE e norte da BA · INMET: baixa umidade em {SECO} cidades", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SÁBADO E DOMINGO · CHUVA NO SUL",
     "contador": conta(84, "f6", "84", "#5ec8ff", "MM PREVISTOS"),
     "l": "colunas: chuva prevista somada de 07 a 08/11 · Open-Meteo", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "VENTO · SÁBADO PARA DOMINGO",
     "contador": conta(80, "f7", "80", "#96d2ff", "KM/H EM RAJADAS"),
     "l": "litoral de São Paulo e do Rio", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "SÃO PAULO · DOMINGO 08/11",
     "contador": conta(18, "f8", "18", "#96d2ff", "°C (PREVISÃO)", de=30),
     "l": f"Rio: 35 → 25 °C · INMET: declínio de temperatura em {len(geo(56281)):,} cidades".replace(",", "."),
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "AR FRIO · DOMINGO E SEGUNDA",
     "itens": [{"t": GEADA, "txt": "❄️ domingo: geada na campanha"},
               {"t": SEG9, "txt": "🥶 segunda: abaixo de zero"}],
     "l": "serra catarinense (previsão)", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "PRÓXIMOS DIAS",
     "itens": [{"t": em("f10", "fria"), "txt": "🥶 semana fria no Sul e Sudeste"},
               {"t": NE10, "txt": "🌧️ chuva no Nordeste de 10 a 20/11"}],
     "l": "previsão", "borda": "rgba(60,150,255,.8)"},
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
    {"ini": CAPA, "fim": ini("f3"), "html": f"<b>INMET</b>, avisos de tempestade de 07/11 · <b>{MET}</b>"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b> · satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · nível do rio"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · previsão · <b>INMET</b>, baixa umidade"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · <b>Open-Meteo</b>, chuva prevista somada de 07 a 08/11"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b> · previsão · foto do vendaval: ilustração"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · previsão · <b>INMET</b>, declínio de temperatura"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · previsão · foto da geada: ilustração"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b> · previsão"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "rio": "#5ec8ff", "metros": "#5ec8ff", "milimetros": "#5ec8ff", "frio": "#96d2ff", "fria": "#96d2ff",
         "geada": "#96d2ff", "zero": "#96d2ff", "despenca": "#96d2ff", "graus": "#ff2a1f", "calor": "#ff2a1f",
         "vermelho": "#ff2a1f", "tempestade": "#ff8c1a", "alerta": "#ff8c1a", "aviso": "#ff8c1a", "vento": "#96d2ff",
         "quilometros": "#96d2ff", "frente": "#96d2ff", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "sudeste", "brasil", "nordeste", "argentina", "parana", "santa", "catarina", "itajaiacu", "piaui", "pernambuco",
         "bahia", "gaucho", "gaucha", "campanha", "serra", "catarinense", "sao", "paulo", "inemaclub", "onde"}
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
      f"INMET vermelho {len(VERMELHO)} · tempestade sábado {len(SAB_T)} · colunas {len(col)} (máx {TOPO[0]['uf']} {TOPO[1]} mm)")
