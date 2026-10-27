#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 27/10/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), da anomalia da temperatura do mar (GHRSST MUR via NASA GIBS, 25/10),
do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET e da chuva prevista de 28/10 a 11/11 na grade do Brasil
(Open-Meteo, om/prev15_grade.json, gravado por coleta/previsao15d.py --dia 2026-10-27).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, El Niño +2,9 °C), anomalia real do mar no Pacífico (Niño 3.4, boias,
20 milhões de km² de água quente) e na mancha fria perto da Bacia do Prata, foto da geada de hoje (ilustração), pinos da geada
prevista em novembro (Guarapuava, Palmas, serra de SC, norte gaúcho), Sul abaixo da média até 10/12, colunas 3D da chuva prevista
até 11/11 (Open-Meteo), infravermelho do GOES-19 no Sul e foto do granizo (ilustração), centro-norte com veranico, Nordeste quente.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "27/10/2026"
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
N34 = {"lon": -135.0, "lat": -3.0, "zoom": 3.0}        # f2: boias do centro do Pacífico
PACL = {"lon": -105.0, "lat": -12.0, "zoom": 2.4}      # f3: toda a água quente
PRATA = {"lon": -53.0, "lat": -35.5, "zoom": 4.4}      # f4: água fria perto da Bacia do Prata
SERRA = {"lon": -51.0, "lat": -27.0, "zoom": 5.9}      # f5: geada em novembro (Guarapuava a Palmas, serra de SC, norte do RS)
SUL = {"lon": -51.5, "lat": -27.0, "zoom": 5.0}        # f6: Sul abaixo da média
COL = {"lon": -50.0, "lat": -24.5, "zoom": 4.5}        # f7: colunas 3D da chuva prevista
SEV = {"lon": -51.5, "lat": -27.0, "zoom": 4.9}        # f8: tempo severo no Sul (IR)
SECO = {"lon": -50.0, "lat": -9.0, "zoom": 4.0}        # f9: MT, TO, PA e Matopiba
NE = {"lon": -40.0, "lat": -8.5, "zoom": 4.6}          # f10: Nordeste quente
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
NINO = em("f1", "2,9") - .4   # a câmera parte para o Pacífico quando a data grande sai
GEA4 = em("f4", "geada")
GRAN = em("f8", "granizo")
camera = [
    K(0, BR), K(CAPA, BR), K(NINO - .3, {**PAC, "lon": -80.0, "zoom": 3.0}, 0, 0),
    K(NINO + 1.3, PAC, 0, 0), K(fim("f1") - .2, {**PAC, "zoom": 2.6}, 0, 0),
    K(ini("f2") + 1.3, N34, 20, -6), K(fim("f2") - .2, {**N34, "lon": -130.0}, 25, 6),
    K(ini("f3") + 1.3, PACL, 0, 0), K(fim("f3") - .2, {**PACL, "zoom": 2.45}, 0, 0),
    K(ini("f4") + 1.3, PRATA, 15, -6), K(GEA4 - .2, {**PRATA, "zoom": 4.5}, 20, 4),
    K(ini("f5") + 1.0, SERRA, 35, -10), K(fim("f5") - .2, {**SERRA, "zoom": 6.0}, 40, 6),
    K(ini("f6") + 1.0, SUL, 0, 0), K(fim("f6") - .2, {**SUL, "zoom": 5.1}, 4, 0),
    K(ini("f7") + 1.0, COL, 55, -20), K(em("f7", "Paulo"), {**COL, "zoom": 4.55}, 56, 0), K(fim("f7") - .2, {**COL, "zoom": 4.6}, 56, 18),
    K(ini("f8") + 1.0, SEV, 0, 0), K(fim("f8") - .2, {**SEV, "zoom": 5.0}, 0, 0),
    K(ini("f9") + 1.0, SECO, 0, 0), K(fim("f9") - .2, {**SECO, "zoom": 4.05}, 4, 0),
    K(ini("f10") + 1.0, NE, 0, 0), K(fim("f10") - .2, {**NE, "zoom": 4.7}, 4, 0),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) no Sul (f8, tempo severo)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# câmera inclinada / fora do Brasil: o Blue Marble do mundo por baixo do geocolor (sem borda preta)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": ini("f8") - .3, "fim": GRAN + .3, "dur": GRAN - ini("f8") + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])
assert len(BONS) >= 20, f"poucos quadros bons de infravermelho: {len(BONS)}"

# anomalia da temperatura do mar (GHRSST MUR via NASA GIBS, 25/10/2026, recorte -180,-60,-20,32, EPSG:3857)
ANOM_DIA = (AQUI / "sat/web/anomalia-data.txt").read_text().strip()
assert ANOM_DIA == "2026-10-25", ANOM_DIA
ANOM = {"src": "sat/web/anomalia.png", "bbox": [-180, -60, -20, 32], "alfa": .85}
imagens = [{**ANOM, "ini": NINO - .3, "fim": GEA4 + .2, "fade": .8}]

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de 28/10 a 11/11 (Open-Meteo, grade de 1,5°)
G15 = json.loads((AQUI / "om/prev15_grade.json").read_text())
CS = {"PR", "SC", "RS", "SP", "MS", "MG", "GO"}   # onde o boletim diz chuva acima da média em novembro
dias = G15["pts"][0]["dias"]
assert dias[0] == "2026-10-28" and dias[14] == "2026-11-11", (dias[0], dias[14])
SOMA = [(p, round(sum(x or 0 for x in p["chuva"][:15]))) for p in G15["pts"] if p["uf"] in CS]
ACIMA = [(p, v) for p, v in SOMA if v >= 100]
assert len(ACIMA) >= 40, f"poucos pontos acima de 100 mm: {len(ACIMA)}"
col = [{"id": i, "p": p["p"], "v": v, "cor": [60, 150, 255] if v >= 100 else [120, 190, 255]} for i, (p, v) in enumerate(SOMA) if v >= 40]
ordem = {c["id"]: (c["p"][1] + 34) * .04 for c in col}   # sobe do Sul para o Centro-Oeste
colunas = [{"id": "chuva3d", "ini": ini("f7") + .2, "fim": ini("f8") + .2, "dados": col, "raio": 70000, "escala": 2000, "ordem": ordem, "varredura": 1}]
TOPO, VTOPO = max(SOMA, key=lambda x: x[1])
assert TOPO["uf"] == "RS" and VTOPO == 183, (TOPO, VTOPO)

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, geada e granizo
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/geada.png", "ini": GEA4 - .1, "fim": ini("f5") + .3, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/granizo.png", "ini": GRAN - .1, "fim": ini("f9") + .3, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET (só a nota do tempo severo)
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
QUINTA = set(aviso[56195]["geocodes"].split(","))   # tempestade quinta 29/10: 2.777 (SP 645, MG 536, PR 399, SC 295, RS 107...)
assert aviso[56195]["descricao"] == "Tempestade" and aviso[56195]["inicio"].startswith("2026-10-29") and len(QUINTA) == 2777, len(QUINTA)
SUL_QUI = sum(c[:2] in ("41", "42", "43") for c in QUINTA)
assert SUL_QUI == 801, SUL_QUI

# ---------------------------------------------------------------- estados
SECO_UF = ["MT", "TO", "PA"]
MATOPIBA = ["MA", "PI", "BA"]
NE_UF = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
estados = [
    {"id": "fria", "ini": em("f4", "Sul"), "fim": GEA4, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .4},
    {"id": "geada", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["PR", "SC", "RS"], "cor": FRIO, "alfa": .35},
    {"id": "sul", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .45},
    {"id": "c_sul", "ini": em("f7", "Sul"), "fim": ini("f8") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .3},
    {"id": "c_ms", "ini": em("f7", "Mato"), "fim": ini("f8") + .3, "ufs": ["MS"], "cor": AZUL, "alfa": .3},
    {"id": "c_sp", "ini": em("f7", "Paulo"), "fim": ini("f8") + .3, "ufs": ["SP"], "cor": AZUL, "alfa": .3},
    {"id": "c_mg", "ini": em("f7", "Minas"), "fim": ini("f8") + .3, "ufs": ["MG"], "cor": AZUL, "alfa": .25},
    {"id": "c_go", "ini": em("f7", "Goiás"), "fim": ini("f8") + .3, "ufs": ["GO"], "cor": AZUL, "alfa": .2},
    {"id": "severo", "ini": ini("f8"), "fim": GRAN, "ufs": ["RS", "SC", "PR"], "cor": LAR, "alfa": .3},
    {"id": "seco", "ini": em("f9", "Mato"), "fim": ini("f10") + .3, "ufs": SECO_UF, "cor": LAR, "alfa": .45},
    {"id": "matopiba", "ini": em("f9", "Matopiba"), "fim": ini("f10") + .3, "ufs": MATOPIBA, "cor": LAR, "alfa": .35},
    {"id": "calor", "ini": ini("f10"), "fim": ini("f11") + .3, "ufs": NE_UF, "cor": VERM, "alfa": .4},
]

pinos = [
    {"nome": "Centro do Pacífico · Niño 3.4", "sub": "+2,9 °C acima da média", "lon": -112.0, "lat": -2.0, "ini": em("f1", "2,9") - .2, "fim": ini("f2"), "h": 200},
    {"nome": "Boias do Pacífico", "sub": "mais de 3 °C acima da média", "lon": -135.0, "lat": -1.0, "ini": em("f2", "boias"), "fim": ini("f3"), "h": 200},
    {"nome": "Bacia do Prata", "sub": "mancha de água fria (25/10)", "lon": -54.5, "lat": -37.5, "ini": em("f4", "Prata") - .2, "fim": GEA4 - .1, "h": 180},
    {"nome": "Guarapuava (PR)", "sub": "geada em novembro (previsão)", "lon": -51.46, "lat": -25.39, "ini": em("f5", "Guarapuava"), "fim": ini("f6"), "h": 280},
    {"nome": "Palmas (PR)", "sub": "geada em novembro (previsão)", "lon": -51.99, "lat": -26.48, "ini": em("f5", "Palmas"), "fim": ini("f6"), "h": 90},
    {"nome": "Serra catarinense", "sub": "geada em novembro (previsão)", "lon": -49.93, "lat": -28.29, "ini": em("f5", "serra"), "fim": ini("f6"), "h": 160},
    {"nome": "Norte gaúcho", "sub": "geada em novembro (previsão)", "lon": -50.93, "lat": -28.51, "ini": em("f5", "gaúcho"), "fim": ini("f6"), "h": 260},
    {"nome": f"{VTOPO} mm até 11/11", "sub": f"maior soma prevista ({TOPO['uf']}) · Open-Meteo", "lon": TOPO["p"][0], "lat": TOPO["p"][1],
     "ini": em("f7", "Sul", 1), "fim": ini("f8"), "h": 220},
    {"nome": "Matopiba", "sub": "risco de veranico (previsão)", "lon": -46.0, "lat": -9.5, "ini": em("f9", "Matopiba"), "fim": ini("f10"), "h": 160},
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
                 '<div class="t4" style="font-size:44px;line-height:1.35">o mais forte já registrado</div>'}]
paineis = [
    {"ini": H, "fim": ini("f2"), "k": "EL NIÑO · CENTRO DO PACÍFICO",
     "contador": conta(2.9, "f1", "2,9", "#ff2a1f", "°C ACIMA DA MÉDIA", dec=1, de=1, lead=.3),
     "l": "o mais forte já registrado, desde 1950", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "ÁGUA QUENTE NO PACÍFICO",
     "contador": conta(20, "f2", "20", "#ff2a1f", "MILHÕES DE KM²"),
     "l": "nas boias, mais de 3 °C acima da média", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "OCEANO AQUECIDO HÁ QUASE",
     "contador": conta(6, "f3", "6", "#ff2a1f", "MESES"),
     "l": "deve durar até julho de 2027 (previsão)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f4"), "fim": GEA4 - .1, "k": "POR QUE ESFRIA NO SUL",
     "itens": [{"t": em("f4", "fria"), "txt": "🌊 água fria perto da Bacia do Prata"},
               {"t": GEA4 - .5, "txt": "❄️ geada hoje cedo"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "GEADA EM NOVEMBRO (PREVISÃO)",
     "itens": [{"t": em("f5", "Guarapuava"), "txt": "❄️ de Guarapuava a Palmas (PR)"},
               {"t": em("f5", "serra"), "txt": "❄️ serra catarinense"},
               {"t": em("f5", "gaúcho"), "txt": "❄️ norte gaúcho"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SUL · ATÉ 10/12 (PREVISÃO)",
     "itens": [{"t": em("f6", "abaixo"), "txt": "🧊 temperatura abaixo da média"},
               {"t": em("f6", "onda"), "txt": "🚫 sem onda de calor prolongada"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "NOVEMBRO · CHUVA ACIMA DA MÉDIA",
     "itens": [{"t": em("f7", "Sul"), "txt": "🌧️ Sul e Mato Grosso do Sul"},
               {"t": em("f7", "Paulo"), "txt": "🌧️ São Paulo e Minas"},
               {"t": em("f7", "Goiás"), "txt": "🌧️ sul de Goiás"}],
     "l": f"Open-Meteo: até {VTOPO} mm de 28/10 a 11/11 (previsão)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f8"), "fim": GRAN - .1, "k": "SUL · RISCO DE TEMPO SEVERO",
     "itens": [{"t": em("f8", "frequente"), "txt": "🌧️ chuva frequente"},
               {"t": em("f8", "severo"), "txt": "⛈️ granizo e vento forte"}],
     "l": f"INMET: aviso de tempestade na quinta em {SUL_QUI} cidades do Sul", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "CHUVA ABAIXO DA MÉDIA",
     "itens": [{"t": em("f9", "Mato"), "txt": "🟠 Mato Grosso e Tocantins"},
               {"t": em("f9", "Pará"), "txt": "🟠 Pará e Matopiba"},
               {"t": em("f9", "veranico"), "txt": "☀️ risco de veranico"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "NORDESTE · ATÉ DEZEMBRO",
     "itens": [{"t": em("f10", "calor"), "txt": "🔥 o calor predomina"},
               {"t": em("f10", "acima"), "txt": "🌡️ temperatura acima da média"}],
     "borda": "rgba(255,42,31,.7)"},
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
    {"ini": CAPA, "fim": ini("f4"), "html": f"<b>{MET}</b> · anomalia da temperatura do mar em 25/10: GHRSST MUR via <b>NASA</b> GIBS"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · anomalia do mar em 25/10: GHRSST MUR via <b>NASA</b> GIBS · foto da geada: ilustração"},
    {"ini": ini("f5"), "fim": ini("f7"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b> · <b>Open-Meteo</b>, chuva prevista somada de 28/10 a 11/11"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE} · <b>INMET</b>, aviso para 29/10 · foto do granizo: ilustração"},
    {"ini": ini("f9"), "fim": ini("f11"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "chuvas": "#5ec8ff", "frio": "#96d2ff", "fria": "#96d2ff", "geada": "#96d2ff",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "quente": "#ff2a1f", "nino": "#ff2a1f", "severo": "#ff8c1a", "granizo": "#96d2ff",
         "vento": "#ff8c1a", "veranico": "#ff8c1a", "abaixo": "#96d2ff", "acima": "#ff2a1f", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"pacifico", "oceano", "bacia", "prata", "sul", "guarapuava", "palmas", "serra", "catarinense", "norte", "gaucho", "mato", "grosso",
         "sao", "paulo", "minas", "goias", "tocantins", "para", "matopiba", "nordeste", "inemaclub", "onde"}
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
     "marca": "INEMA · CLIMA DO DIA", "selo": DATA[:5] + " · NASA · INMET · Open-Meteo",
     "camera": camera, "sat": SAT, "imagens": imagens, "colunas": colunas, "telas": telas, "estados": estados, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"anomalia do mar {ANOM_DIA} · colunas {len(col)} ({len(ACIMA)} ≥ 100 mm, topo {VTOPO} mm em {TOPO['uf']} {TOPO['p']})")
