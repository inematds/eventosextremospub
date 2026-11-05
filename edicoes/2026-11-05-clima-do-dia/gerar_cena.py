#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 05/11/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da chuva prevista de 06 a 08/11 na grade do Brasil (Open-Meteo, om/prev15_grade.json, gravado por
coleta/previsao15d.py --dia 2026-11-05).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "RIO CHEIO NO SUL / 7,56 M / E MAIS CHUVA NO SÁBADO"), Vale do Itajaí,
Rio do Sul 8,70 → 7,56 m (Blumenau 5,73 m), tempestades no MS, PR e SP no infravermelho do GOES-19, INMET alerta laranja de
tempestade (502 → Brasil 2.308), Teresina 39 °C e Piauí 43 °C no sábado, frente fria vinda da Argentina (câmera inclinada),
colunas 3D da chuva prevista de 06 a 08/11 (Open-Meteo), granizo (foto do Codex, ilustração), enchente no Vale do Itajaí e no
rio Negro (foto do Codex, ilustração), ar frio: geada no domingo (foto do Codex, ilustração) e São Paulo 18 °C à tarde,
São Joaquim −2 °C e São Paulo 10 °C na segunda, chuva no Nordeste a partir de 10/11.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "05/11/2026"
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
VALE = {"lon": -49.6, "lat": -27.0, "zoom": 6.4}       # f1: Vale do Itajaí
RDS = {"lon": -49.4, "lat": -27.1, "zoom": 7.4}        # f2: Rio do Sul e Blumenau
TEM = {"lon": -51.5, "lat": -22.8, "zoom": 5.0}        # f3: tempestades no MS, PR e SP (IR)
INL = {"lon": -51.5, "lat": -23.0, "zoom": 5.0}        # f4: alerta laranja (PR, SP, MS) e depois o Brasil
INB = {"lon": -50.0, "lat": -16.5, "zoom": 4.0}
NE = {"lon": -42.5, "lat": -7.5, "zoom": 5.3}          # f5: Teresina e Piauí
ARG = {"lon": -58.5, "lat": -32.5, "zoom": 4.7}        # f6: frente fria vinda da Argentina (câmera inclinada, Blue Marble por baixo)
COL = {"lon": -51.2, "lat": -28.0, "zoom": 5.6}        # f6: colunas 3D da chuva prevista de 06 a 08/11
ENC = {"lon": -49.8, "lat": -26.6, "zoom": 6.7}        # f7: Vale do Itajaí e rio Negro
SULF = {"lon": -52.0, "lat": -27.0, "zoom": 4.7}       # f8: ar frio no Sul
SP = {"lon": -47.0, "lat": -23.4, "zoom": 6.2}         # f8/f9: São Paulo
SJ = {"lon": -49.9, "lat": -28.3, "zoom": 6.8}         # f9: São Joaquim
NEC = {"lon": -43.5, "lat": -8.5, "zoom": 4.7}         # f10: Maranhão, Piauí e Bahia
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.0  # quadro 0 = capa cheia do Codex até aqui
SP9 = em("f9", "Paulo")
BR4 = em("f4", "2.308")
GRANIZO = em("f6", "granizo")
SAB6 = em("f6", "sábado")
GEADA = em("f8", "geada")
SP8 = em("f8", "Paulo")
ENCH = em("f7", "enchente")
camera = [
    K(0, BR), K(CAPA, BR), K(ini("f1") + 3.2, VALE), K(fim("f1") - .2, {**VALE, "zoom": 6.55}, 0, 0),
    K(ini("f2") + 1.0, RDS, 35, -8), K(fim("f2") - .2, {**RDS, "zoom": 7.55}, 42, 6),
    K(ini("f3") + 1.0, TEM, 0, 0), K(fim("f3") - .2, {**TEM, "zoom": 4.85}, 0, 0),
    K(ini("f4") + 1.0, INL, 0, 0), K(BR4 - .6, {**INL, "zoom": 5.05}, 0, 0),
    K(BR4 + .6, INB, 0, 0), K(fim("f4") - .2, {**INB, "zoom": 4.05}, 0, 0),
    K(ini("f5") + 1.0, NE, 0, 0), K(fim("f5") - .2, {**NE, "zoom": 5.4}, 4, 0),
    K(ini("f6") + 1.0, ARG, 30, -10), K(SAB6 - .3, {**ARG, "zoom": 4.85}, 32, 0),
    K(SAB6 + 1.2, COL, 55, -20), K(GRANIZO, {**COL, "zoom": 5.7}, 56, 10),
    K(ini("f7") + 1.0, ENC, 0, 0), K(fim("f7") - .2, {**ENC, "zoom": 6.85}, 4, 0),
    K(ini("f8") + 1.0, SULF, 0, 0), K(SP8 - .2, SP, 0, 0), K(fim("f8") - .2, {**SP, "zoom": 6.3}, 4, 0),
    K(ini("f9") + 1.0, SJ, 0, 0), K(SP9 - .4, {**SJ, "zoom": 6.9}, 0, 0), K(SP9 + .8, SP, 0, 0), K(fim("f9") - .2, {**SP, "zoom": 6.3}, 4, 0),
    K(ini("f10") + 1.0, NEC, 0, 0), K(fim("f10") - .2, {**NEC, "zoom": 4.8}, 4, 0),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) nas tempestades de hoje (f3)
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

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de 06 a 08/11 (Open-Meteo, grade de 1,5°)
G15 = json.loads((AQUI / "om/prev15_grade.json").read_text())
CS = {"RS", "SC", "PR"}   # onde o boletim diz que a chuva ganha força no sábado
dias = G15["pts"][0]["dias"]
ND = 3
assert dias[0] == "2026-11-06" and dias[ND - 1] == "2026-11-08", (dias[0], dias[ND - 1])
SOMA = [(p, round(sum(x or 0 for x in p["chuva"][:ND]))) for p in G15["pts"] if p["uf"] in CS]
col = [{"id": i, "p": p["p"], "v": v, "cor": [60, 150, 255] if v >= 50 else [120, 190, 255]} for i, (p, v) in enumerate(SOMA) if v >= 15]
ordem = {c["id"]: (-c["p"][1] - 25) * .12 for c in col}   # sobe do RS para SC e o PR, como a frente
colunas = [{"id": "chuva3d", "ini": SAB6, "fim": ini("f7") + .3, "dados": col, "raio": 60000, "escala": 4200, "ordem": ordem, "varredura": 1}]
TOPO = max(SOMA, key=lambda x: x[1])
assert TOPO[0]["uf"] == "SC" and 60 <= TOPO[1] <= 120 and len(col) >= 6, (TOPO[0]["uf"], TOPO[1], len(col))

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, granizo, enchente e geada
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": GRANIZO - .1, "fim": ini("f7") + .3, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/enchente.png", "ini": ENCH - .1, "fim": ini("f8") + .3, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/geada.png", "ini": GEADA - .1, "fim": SP8 - .2, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET (hoje 05/11)
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
for i in (56273, 56290):
    assert aviso[i]["descricao"] == "Tempestade" and aviso[i]["inicio"].startswith("2026-11-05"), i
assert aviso[56273]["severidade"] == "Perigo", aviso[56273]["severidade"]
LARANJA = geo(56273)                          # tempestade, perigo (laranja): PR 251, SP 221, MS 30
assert len(LARANJA) == 502, len(LARANJA)
HOJE_T = geo(56273) | geo(56290)              # aviso de tempestade hoje: 2.308 cidades
assert len(HOJE_T) == 2308, len(HOJE_T)
UFCOD = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN",
         "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC",
         "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
from collections import Counter
POR_UF = Counter(UFCOD[c[:2]] for c in HOJE_T)
LAR_UF = Counter(UFCOD[c[:2]] for c in LARANJA)
assert (LAR_UF["PR"], LAR_UF["SP"], LAR_UF["MS"]) == (251, 221, 30), LAR_UF
HOJE_UF = [u for u, k in POR_UF.items() if k >= 40]   # estados com 40+ municípios no aviso
assert aviso[56281]["descricao"] == "Declínio de Temperatura" and aviso[56281]["inicio"].startswith("2026-11-08"), aviso[56281]["descricao"]
FRIO8 = Counter(UFCOD[c[:2]] for c in geo(56281))      # declínio de temperatura no domingo 08/11
FRIO_UF = [u for u, k in FRIO8.items() if k >= 20]

# ---------------------------------------------------------------- estados
estados = [
    {"id": "vale", "ini": em("f1", "Vale"), "fim": ini("f3") + .3, "ufs": ["SC"], "cor": AZUL, "alfa": .35},
    {"id": "t_ms", "ini": em("f3", "Mato"), "fim": ini("f4") + .3, "ufs": ["MS"], "cor": LAR, "alfa": .35},
    {"id": "t_pr", "ini": em("f3", "Paraná"), "fim": ini("f4") + .3, "ufs": ["PR"], "cor": LAR, "alfa": .35},
    {"id": "t_sp", "ini": em("f3", "Paulo"), "fim": ini("f4") + .3, "ufs": ["SP"], "cor": LAR, "alfa": .35},
    {"id": "i_lar", "ini": em("f4", "502") - 1.0, "fim": BR4 - .1, "ufs": [u for u in LAR_UF], "cor": LAR, "alfa": .5},
    {"id": "i_br", "ini": BR4 - .1, "fim": ini("f5") + .3, "ufs": HOJE_UF, "cor": LAR, "alfa": .35},
    {"id": "ne", "ini": em("f5", "Nordeste"), "fim": ini("f6") + .3, "ufs": ["MA", "CE", "RN", "PB", "PE", "AL", "SE", "BA"], "cor": LAR, "alfa": .22},
    {"id": "calor", "ini": em("f5", "Teresina"), "fim": ini("f6") + .3, "ufs": ["PI"], "cor": VERM, "alfa": .45},
    {"id": "frente", "ini": em("f6", "frente"), "fim": ini("f7") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .3},
    {"id": "enc", "ini": em("f7", "Vale"), "fim": ini("f8") + .3, "ufs": ["SC", "PR"], "cor": AZUL, "alfa": .35},
    {"id": "frio", "ini": em("f8", "frio"), "fim": ini("f9") + .3, "ufs": FRIO_UF, "cor": FRIO, "alfa": .32},
    {"id": "sj", "ini": em("f9", "Joaquim"), "fim": SP9, "ufs": ["SC"], "cor": FRIO, "alfa": .4},
    {"id": "sp9", "ini": SP9, "fim": ini("f10") + .3, "ufs": ["SP"], "cor": FRIO, "alfa": .4},
    {"id": "chuva_ne", "ini": em("f10", "Nordeste"), "fim": ini("f11") + .3, "ufs": ["MA", "PI", "BA"], "cor": AZUL, "alfa": .4},
]

pinos = [
    {"nome": "Vale do Itajaí", "sub": "rio cheio hoje", "lon": -49.40, "lat": -26.95, "ini": em("f1", "Vale"), "fim": ini("f2"), "h": 200},
    {"nome": "Rio do Sul", "sub": "7,56 m hoje · pico de 8,70 m", "lon": -49.64, "lat": -27.21, "ini": em("f2", "Rio"), "fim": ini("f3"), "h": 320},
    {"nome": "Blumenau", "sub": "rio Itajaí-Açu em 5,73 m", "lon": -49.07, "lat": -26.92, "ini": em("f2", "7,56"), "fim": ini("f3"), "h": 110},
    {"nome": "Campo Grande", "sub": "chuva e trovoada", "lon": -54.62, "lat": -20.47, "ini": em("f3", "Mato"), "fim": ini("f4"), "h": 160},
    {"nome": "Cascavel e Curitiba", "sub": "tempestades hoje", "lon": -51.0, "lat": -25.0, "ini": em("f3", "Paraná"), "fim": ini("f4"), "h": 200},
    {"nome": "Grande São Paulo", "sub": "chuva chegando", "lon": -46.63, "lat": -23.55, "ini": em("f3", "Paulo"), "fim": ini("f4"), "h": 240},
    {"nome": "Teresina", "sub": "39 °C hoje", "lon": -42.80, "lat": -5.09, "ini": em("f5", "Teresina"), "fim": ini("f6"), "h": 200},
    {"nome": "Argentina", "sub": "frente fria subindo", "lon": -60.5, "lat": -33.5, "ini": em("f6", "frente"), "fim": SAB6 + .6, "h": 180},
    {"nome": f"{TOPO[1]} mm até 08/11", "sub": "SC · soma prevista · Open-Meteo", "lon": TOPO[0]["p"][0], "lat": TOPO[0]["p"][1],
     "ini": em("f6", "Sul"), "fim": GRANIZO - .1, "h": 220},
    {"nome": "Vale do Itajaí", "sub": "rio já cheio · solo encharcado", "lon": -49.40, "lat": -26.95, "ini": em("f7", "Vale"), "fim": ENCH - .1, "h": 200},
    {"nome": "Rio Negro", "sub": "divisa SC/PR · enchente ou quase", "lon": -49.80, "lat": -26.10, "ini": em("f7", "Negro"), "fim": ENCH - .1, "h": 160},
    {"nome": "São Paulo", "sub": "18 °C à tarde no domingo", "lon": -46.63, "lat": -23.55, "ini": SP8, "fim": ini("f9"), "h": 200},
    {"nome": "São Joaquim", "sub": "−2 °C na segunda (previsão)", "lon": -49.93, "lat": -28.29, "ini": em("f9", "Joaquim"), "fim": SP9, "h": 200},
    {"nome": "São Paulo", "sub": "10 °C de manhã na segunda", "lon": -46.63, "lat": -23.55, "ini": SP9, "fim": ini("f10"), "h": 200},
    {"nome": "Nordeste", "sub": "chuva a partir de 10/11", "lon": -43.5, "lat": -8.5, "ini": em("f10", "Nordeste"), "fim": ini("f11"), "h": 200},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)   # número dito logo no começo da fala: o contador começa com a fala
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
H = em("f1", "sábado") - .1   # o hero (data grande) fica até "no sábado" (~2,4 s depois da capa)
BR4P = BR4 - 1.1
PI5 = em("f5", "Piauí") - .1
SP9P = SP9 - .1
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:96px">RIO CHEIO</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">e mais chuva no Sul no sábado</div>'}]
paineis = [
    {"ini": H, "fim": ini("f2"), "k": "VALE DO ITAJAÍ · HOJE 05/11",
     "itens": [{"t": H, "txt": "🌊 rio ainda cheio"},
               {"t": em("f1", "chuva"), "txt": "🌧️ sábado: chuva forte no Sul"}],
     "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "RIO DO SUL · RIO ITAJAÍ-AÇU",
     "contador": conta(7.56, "f2", "7,56", "#5ec8ff", "METROS HOJE", dec=2, de=8.70),
     "l": "pico de 8,70 m · baixando devagar · Blumenau 5,73 m", "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "TEMPESTADES · HOJE 05/11",
     "itens": [{"t": em("f3", "Mato"), "txt": "⛈️ Mato Grosso do Sul"},
               {"t": em("f3", "Paraná"), "txt": "⛈️ Paraná"},
               {"t": em("f3", "Paulo"), "txt": "⛈️ São Paulo"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f4"), "fim": BR4P, "k": "INMET · ALERTA LARANJA 05/11",
     "contador": conta(502, "f4", "502", "#ff8c1a", "CIDADES · TEMPESTADE"),
     "l": f"perigo · PR {LAR_UF['PR']}, SP {LAR_UF['SP']}, MS {LAR_UF['MS']}", "borda": "rgba(255,140,26,.8)"},
    {"ini": BR4P, "fim": ini("f5"), "k": "INMET · TEMPESTADE · BRASIL HOJE",
     "contador": conta(2308, "f4", "2.308", "#ff8c1a", "CIDADES NO BRASIL", de=502),
     "l": f"SP {POR_UF['SP']}, MG {POR_UF['MG']}, PR {POR_UF['PR']}, GO {POR_UF['GO']}, SC {POR_UF['SC']}", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f5"), "fim": PI5, "k": "TERESINA · HOJE 05/11",
     "contador": conta(39, "f5", "39", "#ff2a1f", "°C (PREVISÃO)", de=30),
     "l": "Nordeste com tempo seco", "borda": "rgba(255,42,31,.8)"},
    {"ini": PI5, "fim": ini("f6"), "k": "PIAUÍ · SÁBADO 07/11",
     "contador": conta(43, "f5", "43", "#ff2a1f", "°C (PREVISÃO)", de=39),
     "l": "o estado mais quente do país", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "FRENTE FRIA · SÁBADO 07/11",
     "itens": [{"t": em("f6", "frente"), "txt": "❄️ frente fria da Argentina"},
               {"t": em("f6", "Sul"), "txt": "🌧️ chuva forte no Sul"},
               {"t": GRANIZO, "txt": "🧊 risco de granizo e vento"}],
     "l": f"colunas: chuva prevista somada de 06 a 08/11 · Open-Meteo · até {TOPO[1]} mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "RISCO DE ENCHENTE",
     "itens": [{"t": em("f7", "solo"), "txt": "💧 solo encharcado"},
               {"t": em("f7", "Vale"), "txt": "🌊 Vale do Itajaí"},
               {"t": em("f7", "Negro"), "txt": "🌊 rio Negro (SC/PR)"}],
     "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "DOMINGO 08/11 · AR FRIO",
     "contador": conta(18, "f8", "18", "#96d2ff", "°C EM SÃO PAULO À TARDE", de=28),
     "l": f"geada na campanha gaúcha · INMET: declínio de temperatura em {len(geo(56281)):,} cidades".replace(",", "."),
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f9"), "fim": SP9P, "k": "SÃO JOAQUIM · SEGUNDA 09/11",
     "contador": conta(-2, "f9", "2", "#96d2ff", "°C (PREVISÃO)", de=10),
     "l": "serra catarinense abaixo de zero", "borda": "rgba(150,210,255,.8)"},
    {"ini": SP9P, "fim": ini("f10"), "k": "SÃO PAULO · SEGUNDA 09/11",
     "contador": conta(10, "f9", "10", "#96d2ff", "°C DE MANHÃ (PREVISÃO)", de=20, lead=min(LEAD, em("f9", "10") - SP9P)),  # avatar fala mais rápido: contador cabe no painel
     "l": "muito frio para novembro", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "A PARTIR DE 10/11 · NORDESTE",
     "itens": [{"t": em("f10", "Maranhão"), "txt": "🌧️ Maranhão"},
               {"t": em("f10", "Piauí"), "txt": "🌧️ Piauí"},
               {"t": em("f10", "Bahia"), "txt": "🌧️ Bahia"}],
     "l": "previsão de chuva", "borda": "rgba(60,150,255,.8)"},
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
    {"ini": CAPA, "fim": ini("f3"), "html": f"<b>{MET}</b> · nível dos rios"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b> · satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>INMET</b>, avisos de tempestade de 05/11"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · <b>Open-Meteo</b>, chuva prevista somada de 06 a 08/11 · foto do granizo: ilustração"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b> · previsão · foto da enchente: ilustração"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · previsão · <b>INMET</b>, declínio de temperatura · foto da geada: ilustração"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>{MET}</b> · previsão"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "cheio": "#5ec8ff", "rio": "#5ec8ff", "metros": "#5ec8ff", "frio": "#96d2ff", "geada": "#96d2ff",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "forte": "#ff8c1a", "granizo": "#96d2ff", "tempestade": "#ff8c1a",
         "tempestades": "#ff8c1a", "laranja": "#ff8c1a", "alerta": "#ff8c1a", "aviso": "#ff8c1a", "vento": "#96d2ff",
         "negativos": "#96d2ff", "encharcado": "#5ec8ff", "enchente": "#5ec8ff", "frente": "#96d2ff", "comenta": AM,
         "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "vale", "itajai", "blumenau", "mato", "grosso", "parana", "sao", "paulo", "brasil", "nordeste", "teresina", "piaui",
         "argentina", "negro", "santa", "catarina", "campanha", "gaucha", "joaquim", "maranhao", "bahia", "inemaclub", "onde"}
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
      f"INMET laranja {len(LARANJA)} · tempestade hoje {len(HOJE_T)} · colunas {len(col)} (máx SC {TOPO[1]} mm)")
