#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 10/11/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md: El Niño mais forte que o de 2015 e a chuva até o Natal),
da anomalia da temperatura do mar (GHRSST MUR via NASA GIBS, 09/11), do timelapse do GOES-19 (NASA GIBS), dos avisos
do INMET de hoje e da chuva prevista de 11 a 20/11 na grade do Brasil (Open-Meteo, om/prev15_grade.json, gravado por
coleta/previsao15d.py --dia 2026-11-10).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "EL NIÑO / MAIS FORTE / QUE EM 2015 / +2,9 °C"), Pacífico com a
anomalia real do mar (pino Niño 3.4 +2,9 °C, Pacífico central 2015 × 2026), Brasil com mais chuva no centro-sul e menos no
norte, INMET chuvas intensas hoje (685 cidades) com o IR do GOES-19, colunas 3D da chuva prevista até 20/11 no centro-sul
(163 mm em MT), Sul acima da média até o Natal (câmera inclinada), Pará só 4 mm em 10 dias, veranico em MT/TO/Matopiba,
geada isolada no Sul (0 a 4 °C) e lavoura com geada e solo encharcado (foto do Codex, ilustração).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "10/11/2026"
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
PAC = {"lon": -100.0, "lat": -10.0, "zoom": 2.55}      # f1: Pacífico equatorial + América do Sul
N34 = {"lon": -135.0, "lat": -3.0, "zoom": 3.0}        # f2: Pacífico central (Niño 3.4), 2015 × 2026
BRL = {"lon": -55.0, "lat": -15.0, "zoom": 3.6}        # f3: Brasil, centro-sul × norte
CN = {"lon": -49.0, "lat": -10.5, "zoom": 4.4}         # f4: chuvas intensas hoje (GO, TO, MA, PI, PA, MT) + IR
COL = {"lon": -51.5, "lat": -19.5, "zoom": 4.4}        # f5: colunas 3D da chuva prevista no centro-sul
SUL = {"lon": -51.5, "lat": -25.5, "zoom": 4.5}        # f6: Sul acima da média até o Natal (colunas seguem)
PA = {"lon": -53.0, "lat": -4.5, "zoom": 4.6}          # f7: Pará só 4 mm
SECO = {"lon": -48.0, "lat": -10.0, "zoom": 4.4}       # f8: MT, TO e Matopiba
SERRA = {"lon": -51.0, "lat": -27.5, "zoom": 5.6}      # f9: geada isolada no Sul
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.0  # quadro 0 = capa cheia do Codex até aqui
NINO = em("f1", "2,9") - .4   # a câmera parte para o Pacífico quando a data grande sai
LAV = em("f10", "Frio")
camera = [
    K(0, BR), K(CAPA, BR), K(NINO - .3, {**PAC, "lon": -80.0, "zoom": 3.0}, 0, 0),
    K(NINO + 1.3, PAC, 0, 0), K(fim("f1") - .2, {**PAC, "zoom": 2.6}, 0, 0),
    K(ini("f2") + 1.3, N34, 20, -6), K(fim("f2") - .2, {**N34, "lon": -130.0}, 25, 6),
    K(ini("f3") + 1.6, BRL, 0, 0), K(fim("f3") - .2, {**BRL, "zoom": 3.7}, 0, 0),
    K(ini("f4") + 1.0, CN, 0, 0), K(fim("f4") - .2, {**CN, "zoom": 4.5}, 4, 0),
    K(ini("f5") + 1.2, COL, 55, -20), K(fim("f5") - .2, {**COL, "zoom": 4.5}, 56, 10),
    K(ini("f6") + 1.0, SUL, 50, 15), K(fim("f6") - .2, {**SUL, "zoom": 4.6}, 52, 30),
    K(ini("f7") + 1.0, PA, 0, 0), K(fim("f7") - .2, {**PA, "zoom": 4.7}, 4, 0),
    K(ini("f8") + 1.0, SECO, 0, 0), K(fim("f8") - .2, {**SECO, "zoom": 4.5}, 4, 0),
    K(ini("f9") + 1.0, SERRA, 35, -10), K(fim("f9") - .2, {**SERRA, "zoom": 5.7}, 40, 6),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) nas chuvas intensas de hoje (f4)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 130]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# câmera inclinada / fora do Brasil: o Blue Marble do mundo por baixo do geocolor (sem borda preta)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": ini("f4") - .3, "fim": ini("f5") + .3, "dur": ini("f5") - ini("f4") + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])
assert len(BONS) >= 36, f"poucos quadros bons de infravermelho: {len(BONS)}"

# anomalia da temperatura do mar (GHRSST MUR via NASA GIBS, 09/11/2026, recorte -180,-60,-20,32, EPSG:3857)
ANOM_DIA = (AQUI / "sat/web/anomalia-data.txt").read_text().strip()
assert ANOM_DIA == "2026-11-09", ANOM_DIA
ANOM = {"src": "sat/web/anomalia.png", "bbox": [-180, -60, -20, 32], "alfa": .85}
imagens = [{**ANOM, "ini": NINO - .3, "fim": ini("f3") + 1.6, "fade": .8}]

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de 11 a 20/11 no centro-sul (Open-Meteo, grade de 1,5°)
G15 = json.loads((AQUI / "om/prev15_grade.json").read_text())
CS = {"MT", "MS", "GO", "DF", "MG", "SP", "RJ", "ES", "PR", "SC", "RS"}   # onde o boletim diz que chove bem / acima da média
dias = G15["pts"][0]["dias"]
ND = 10
assert dias[0] == "2026-11-11" and dias[ND - 1] == "2026-11-20", (dias[0], dias[ND - 1])
soma = lambda p: round(sum(x or 0 for x in p["chuva"][:ND]))
SOMA = [(p, soma(p)) for p in G15["pts"] if p["uf"] in CS]
col = [{"id": i, "p": p["p"], "v": v, "cor": [60, 150, 255] if v >= 100 else [120, 190, 255]} for i, (p, v) in enumerate(SOMA) if v >= 40]
ordem = {c["id"]: (c["p"][1] + 34) * .04 for c in col}   # sobe do Sul para o Centro-Oeste
colunas = [{"id": "chuva3d", "ini": ini("f5") + .2, "fim": ini("f7") + .2, "dados": col, "raio": 60000, "escala": 2600, "ordem": ordem, "varredura": 1}]
TOPO, VTOPO = max(SOMA, key=lambda x: x[1])
assert TOPO["uf"] == "MT" and VTOPO == 163 and len(col) >= 80, (TOPO["uf"], VTOPO, len(col))   # a fala f5 diz "163 milímetros em Mato Grosso"
VRS = max(v for p, v in SOMA if p["uf"] == "RS")
SECO_PA, VPA = min(((p, soma(p)) for p in G15["pts"] if p["uf"] == "PA"), key=lambda x: x[1])
assert VPA == 4, VPA   # a fala f7 diz "só 4 milímetros em 10 dias"

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e lavoura com geada
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/lavoura.png", "ini": LAV - .1, "fim": ini("f11") + .2, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET (hoje 10/11)
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
assert aviso[56371]["descricao"] == "Chuvas Intensas" and aviso[56371]["inicio"].startswith("2026-11-10"), 56371
INT = geo(56371)                   # chuvas intensas hoje: 685 cidades
assert len(INT) == 685, len(INT)
UFCOD = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN",
         "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC",
         "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
from collections import Counter
POR_UF = Counter(UFCOD[c[:2]] for c in INT)
assert (POR_UF["GO"], POR_UF["TO"], POR_UF["MA"]) == (202, 139, 110), POR_UF
INT_UF = [u for u, k in POR_UF.items() if k >= 25]   # GO, TO, MA, PI, PA, MT

# ---------------------------------------------------------------- estados
CSUL = ["MT", "MS", "GO", "DF", "MG", "SP", "RJ", "ES", "PR", "SC", "RS"]
NORTE = ["AM", "PA", "RR", "AP", "AC", "RO"]
MATOPIBA = ["MA", "PI", "BA"]
estados = [
    {"id": "csul", "ini": em("f3", "centro"), "fim": ini("f4") + .3, "ufs": CSUL, "cor": AZUL, "alfa": .35},
    {"id": "norte", "ini": em("f3", "norte"), "fim": ini("f4") + .3, "ufs": NORTE, "cor": LAR, "alfa": .4},
    {"id": "inmet", "ini": em("f4", "chuvas"), "fim": ini("f5") + .3, "ufs": INT_UF, "cor": AZUL, "alfa": .4},
    {"id": "co5", "ini": em("f5", "Centro"), "fim": ini("f6") + .3, "ufs": ["MT", "MS", "GO", "DF"], "cor": AZUL, "alfa": .25},
    {"id": "sul6", "ini": em("f6", "Sul"), "fim": ini("f7") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .3},
    {"id": "pa7", "ini": em("f7", "Amazônia"), "fim": ini("f8") + .3, "ufs": ["AM", "PA"], "cor": LAR, "alfa": .3},
    {"id": "pa7b", "ini": em("f7", "Pará"), "fim": ini("f8") + .3, "ufs": ["PA"], "cor": LAR, "alfa": .3},
    {"id": "seco", "ini": em("f8", "Mato"), "fim": ini("f9") + .3, "ufs": ["MT", "TO"], "cor": LAR, "alfa": .45},
    {"id": "matopiba", "ini": em("f8", "Matopiba"), "fim": ini("f9") + .3, "ufs": MATOPIBA, "cor": LAR, "alfa": .35},
    {"id": "frio9", "ini": em("f9", "frio"), "fim": ini("f10") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .4},
]

pinos = [
    {"nome": "Centro do Pacífico · Niño 3.4", "sub": "+2,9 °C acima da média (09/11)", "lon": -112.0, "lat": -2.0, "ini": em("f1", "2,9") - .2, "fim": ini("f2"), "h": 200},
    {"nome": "Pacífico central", "sub": "2015: ~2 °C · 2026: acima de 2 °C desde agosto", "lon": -135.0, "lat": -1.0, "ini": em("f2", "Pacífico"), "fim": ini("f3"), "h": 200},
    {"nome": "Goiás", "sub": f"{POR_UF['GO']} cidades com aviso hoje", "lon": -49.6, "lat": -16.0, "ini": em("f4", "Goiás"), "fim": ini("f5"), "h": 180},
    {"nome": "Tocantins", "sub": f"{POR_UF['TO']} cidades com aviso hoje", "lon": -48.3, "lat": -10.2, "ini": em("f4", "Tocantins"), "fim": ini("f5"), "h": 220},
    {"nome": f"{VTOPO} mm até 20/11", "sub": f"maior soma prevista (MT) · Open-Meteo", "lon": TOPO["p"][0], "lat": TOPO["p"][1],
     "ini": em("f5", "163"), "fim": ini("f6"), "h": 240},
    {"nome": f"{VPA} mm até 20/11", "sub": "Pará · soma prevista · Open-Meteo", "lon": SECO_PA["p"][0], "lat": SECO_PA["p"][1],
     "ini": em("f7", "4"), "fim": ini("f8"), "h": 200},
    {"nome": "Matopiba", "sub": "risco de veranico (previsão)", "lon": -46.0, "lat": -9.5, "ini": em("f8", "Matopiba"), "fim": ini("f9"), "h": 160},
    {"nome": "Serra catarinense", "sub": "geada isolada ontem e hoje", "lon": -49.93, "lat": -28.29, "ini": em("f9", "geada"), "fim": ini("f10"), "h": 200},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)   # número dito logo no começo da fala: o contador começa com a fala
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
H = NINO   # o hero (data grande) fica até 0,4 s antes do "2,9" (a capa já mostra +2,9 °C: contador curto)
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:112px">EL NIÑO</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">mais forte que o de 2015</div>'}]
paineis = [
    {"ini": H, "fim": ini("f2"), "k": "EL NIÑO · CENTRO DO PACÍFICO",
     "contador": conta(2.9, "f1", "2,9", "#ff2a1f", "°C ACIMA DA MÉDIA", dec=1, de=1, lead=.3),
     "l": "mais forte que o El Niño de 2015", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "2015 × 2026 · NESTA ÉPOCA",
     "itens": [{"t": em("f2", "ano"), "txt": "📅 2015: uns 2 °C acima"},
               {"t": em("f2", "Agora"), "txt": "🔥 2026: acima de 2 °C desde agosto"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "EL NIÑO NO BRASIL",
     "itens": [{"t": em("f3", "1950"), "txt": "🏆 o mais forte desde 1950"},
               {"t": em("f3", "centro"), "txt": "🌧️ mais chuva no centro-sul"},
               {"t": em("f3", "norte"), "txt": "🟠 menos chuva no norte"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "INMET · CHUVAS INTENSAS HOJE",
     "contador": conta(685, "f4", "685", "#5ec8ff", "CIDADES NO BRASIL"),
     "l": f"GO {POR_UF['GO']} · TO {POR_UF['TO']} · MA {POR_UF['MA']} · PI {POR_UF['PI']} · PA {POR_UF['PA']} · MT {POR_UF['MT']}",
     "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "CHUVA PREVISTA · 11 A 20/11",
     "contador": conta(VTOPO, "f5", "163", "#5ec8ff", "MM EM MATO GROSSO"),
     "l": "colunas: soma prevista · Open-Meteo", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SUL · ATÉ 24/12 (PREVISÃO)",
     "itens": [{"t": em("f6", "acima"), "txt": "🌧️ chuva acima da média"},
               {"t": em("f6", "Natal"), "txt": "🎄 até a véspera de Natal"},
               {"t": em("f6", "Paraná"), "txt": "📍 do RS ao PR"}],
     "l": f"Open-Meteo: até {VRS} mm no RS de 11 a 20/11", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "AMAZÔNIA PREOCUPA",
     "itens": [{"t": em("f7", "Pará"), "txt": f"🟠 Pará: só {VPA} mm em 10 dias"},
               {"t": em("f7", "dias"), "txt": "📉 chuva abaixo da média"}],
     "l": "soma prevista de 11 a 20/11 · Open-Meteo", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "RISCO DE VERANICO",
     "itens": [{"t": em("f8", "Mato"), "txt": "🟠 Mato Grosso e Tocantins"},
               {"t": em("f8", "Matopiba"), "txt": "🟠 Matopiba"},
               {"t": em("f8", "corte"), "txt": "☀️ corte na chuva"}],
     "l": "previsão", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "SUL · FRIO FORA DE ÉPOCA",
     "itens": [{"t": em("f9", "geada"), "txt": "❄️ geada isolada ontem e hoje"},
               {"t": em("f9", "graus"), "txt": "🥶 de 0 a 4 °C"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "LAVOURAS DE VERÃO",
     "itens": [{"t": em("f10", "sol"), "txt": "☁️ frio e falta de sol"},
               {"t": em("f10", "encharcado"), "txt": "💧 solo encharcado"},
               {"t": em("f10", "soja"), "txt": "🌱 soja, milho e feijão"}],
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
        if c["ini"] < a["ini"]:   # contador não pode começar antes do painel
            c["dur"] -= a["ini"] - c["ini"]; c["ini"] = a["ini"]
        assert c["dur"] > .2 and c["ini"] + c["dur"] <= a["fim"], ("contador fora do painel", a["k"])

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f4"), "html": f"<b>{MET}</b> · anomalia da temperatura do mar em 09/11: GHRSST MUR via <b>NASA</b> GIBS"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>INMET</b>, aviso de chuvas intensas de 10/11 · satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f5"), "fim": ini("f8"), "html": f"<b>{MET}</b> · <b>Open-Meteo</b>, chuva prevista somada de 11 a 20/11"},
    {"ini": ini("f8"), "fim": ini("f10"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": f"<b>{MET}</b> · foto da lavoura: ilustração"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "chuvas": "#5ec8ff", "milimetros": "#5ec8ff", "encharcado": "#5ec8ff",
         "frio": "#96d2ff", "geada": "#96d2ff", "abaixo": "#96d2ff", "graus": "#ff2a1f", "nino": "#ff2a1f", "forte": "#ff2a1f",
         "acima": "#ff2a1f", "veranico": "#ff8c1a", "corte": "#ff8c1a", "preocupa": "#ff8c1a", "intensas": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"pacifico", "brasil", "centrosul", "norte", "goias", "tocantins", "centrooeste", "mato", "grosso", "sul", "rio", "grande",
         "parana", "amazonia", "para", "matopiba", "natal", "inemaclub", "onde"}
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
     "marca": "INEMA · CLIMA DO DIA", "selo": DATA[:5] + " · NASA · INMET · Open-Meteo",
     "camera": camera, "sat": SAT, "imagens": imagens, "colunas": colunas, "telas": telas, "estados": estados, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"anomalia do mar {ANOM_DIA} · INMET chuvas intensas {len(INT)} · colunas {len(col)} (topo {VTOPO} mm em {TOPO['uf']} {TOPO['p']}) · PA {VPA} mm")
