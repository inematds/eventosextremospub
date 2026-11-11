#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 11/11/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md: granizo ontem no Crato, núcleos de trovoada no Centro-Oeste,
rio alto em Blumenau, nordestão no litoral do Sul, frio na serra, chuva ganhando força no Nordeste no fim de semana,
chuva acima da média no centro-sul até 21/11), dos avisos do INMET de hoje e de amanhã (tempestade: 1487 cidades hoje,
2084 amanhã), do timelapse do GOES-19 (NASA GIBS) e da chuva prevista de 11 a 21/11 na grade do Brasil (Open-Meteo,
om/prev15_grade.json, gravado por coleta/previsao15d.py --dia 2026-11-10).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "ALERTA DE / TEMPESTADE / HOJE / 1.487 CIDADES"), data grande,
foto do granizo (Codex, ilustração) na palavra "granizo", Brasil com os estados do aviso de tempestade (contador 1487),
IR do GOES-19 no Centro-Oeste (Brasília, Goiânia, Cuiabá), Goiás 246 → total 1487, Nordeste (Crato, Fortaleza),
Blumenau e litoral do Sul inclinados (vento 40–60 km/h), capitais (27 °C SP, 29 °C POA), aviso de amanhã (2084),
serra catarinense (São Joaquim < 10 °C, 5–8 °C na sexta), colunas 3D da chuva prevista até 21/11 girando no Nordeste
e depois no centro-sul (Vale do Itajaí).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "11/11/2026"
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

# ---------------------------------------------------------------- avisos do INMET (hoje 11/11 e amanhã 12/11)
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
for i, d in ((56376, "2026-11-11"), (56378, "2026-11-11"), (56381, "2026-11-12")):
    assert aviso[i]["descricao"] == "Tempestade" and aviso[i]["inicio"].startswith(d), i
TEMP = geo(56376) | geo(56378)     # tempestade hoje: 1487 cidades (união dos dois avisos)
AMANHA = geo(56381)                # tempestade amanhã: 2084 cidades
assert (len(TEMP), len(AMANHA)) == (1487, 2084), (len(TEMP), len(AMANHA))   # as falas f1 e f7 dizem 1487 e 2084
UFCOD = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN",
         "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC",
         "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
UF_H = Counter(UFCOD[c[:2]] for c in TEMP)
UF_A = Counter(UFCOD[c[:2]] for c in AMANHA)
assert (UF_H["GO"], UF_H["SC"], UF_H["PR"]) == (246, 257, 256), UF_H     # f3: "Goiás tem 246 cidades em alerta"
assert (UF_A["SP"], UF_A["MG"]) == (644, 553), UF_A                       # f7: "mais em São Paulo e Minas"
HOJE_UF = [u for u, k in UF_H.items() if k >= 25]     # SC PR GO SP MT TO MS MG PA MA RS
AMANHA_UF = [u for u, k in UF_A.items() if k >= 25]   # SP MG PR GO MT TO MS RJ

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
BRL = {"lon": -52.0, "lat": -16.0, "zoom": 3.65}       # f1: Brasil com os estados do aviso de tempestade
CO = {"lon": -51.5, "lat": -15.5, "zoom": 4.7}         # f2: núcleos de trovoada (Brasília, Goiânia, Cuiabá) + IR
CS = {"lon": -50.5, "lat": -21.5, "zoom": 4.3}         # f3: Goiás → Santa Catarina e Paraná
NE = {"lon": -39.5, "lat": -6.0, "zoom": 5.3}          # f4: Crato, Fortaleza e o sertão
SC = {"lon": -49.0, "lat": -27.6, "zoom": 6.1}         # f5: Blumenau e o litoral (inclinada)
SSE = {"lon": -48.5, "lat": -26.5, "zoom": 4.9}        # f6: São Paulo e Porto Alegre
SE = {"lon": -47.5, "lat": -20.5, "zoom": 4.5}         # f7: aviso de amanhã (SP, MG)
SERRA = {"lon": -49.9, "lat": -28.3, "zoom": 6.3}      # f8: São Joaquim
NEC = {"lon": -42.0, "lat": -12.5, "zoom": 4.6}        # f9: colunas no Nordeste (MA, PI, PE, BA)
CSC = {"lon": -51.0, "lat": -21.5, "zoom": 4.3}        # f10: colunas no centro-sul
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.0  # quadro 0 = capa cheia do Codex até aqui
GRA = em("f1", "granizo") - .1     # foto do granizo entra na palavra
HOJE = em("f1", "hoje") - .1       # e sai para o mapa no "hoje há alerta"
camera = [
    K(0, BR), K(HOJE - .3, BR), K(HOJE + 1.2, BRL), K(fim("f1") - .2, {**BRL, "zoom": 3.75}),
    K(ini("f2") + 1.0, CO, 0, 0), K(fim("f2") - .2, {**CO, "zoom": 4.85}, 6, 0),
    K(ini("f3") + 1.0, CS, 0, 0), K(fim("f3") - .2, {**CS, "lat": -23.5, "zoom": 4.4}, 6, 0),
    K(ini("f4") + 1.0, NE, 0, 0), K(fim("f4") - .2, {**NE, "zoom": 5.45}, 6, 0),
    K(ini("f5") + 1.1, SC, 45, -12), K(fim("f5") - .2, {**SC, "zoom": 6.2}, 48, 8),
    K(ini("f6") + 1.0, SSE, 0, 0), K(fim("f6") - .2, {**SSE, "zoom": 5.0}, 6, 0),
    K(ini("f7") + 1.0, SE, 0, 0), K(fim("f7") - .2, {**SE, "zoom": 4.6}, 6, 0),
    K(ini("f8") + 1.1, SERRA, 40, -10), K(fim("f8") - .2, {**SERRA, "zoom": 6.4}, 44, 6),
    K(ini("f9") + 1.2, NEC, 55, -20), K(fim("f9") - .2, {**NEC, "zoom": 4.7}, 56, 12),
    K(ini("f10") + 1.2, CSC, 55, 15), K(fim("f10") - .2, {**CSC, "lon": -50.0, "lat": -25.0, "zoom": 4.7}, 52, 35),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) nos núcleos de trovoada (f2)
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

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de 11 a 21/11 (Open-Meteo, grade de 1,5°)
G15 = json.loads((AQUI / "om/prev15_grade.json").read_text())
dias = G15["pts"][0]["dias"]
ND = 11
assert dias[0] == "2026-11-11" and dias[ND - 1] == "2026-11-21", (dias[0], dias[ND - 1])
soma = lambda p: round(sum(x or 0 for x in p["chuva"][:ND]))
SOMA = [(p, soma(p)) for p in G15["pts"]]
col = [{"id": i, "p": p["p"], "v": v, "cor": [60, 150, 255] if v >= 100 else [120, 190, 255]} for i, (p, v) in enumerate(SOMA) if v >= 40]
ordem = {c["id"]: (c["p"][1] + 34) * .03 for c in col}   # sobe do Sul para o Norte
colunas = [{"id": "chuva3d", "ini": ini("f9") + .2, "fim": ini("f11") + .2, "dados": col, "raio": 60000, "escala": 2600, "ordem": ordem, "varredura": 1}]
TOPO, VTOPO = max(SOMA, key=lambda x: x[1])
assert TOPO["uf"] == "MS" and VTOPO == 194 and len(col) >= 200, (TOPO["uf"], VTOPO, len(col))
VUF = lambda uf: max(v for p, v in SOMA if p["uf"] == uf)
NE_TOP = max(((p, v) for p, v in SOMA if p["uf"] in {"MA", "PI", "PE", "BA"}), key=lambda x: x[1])
VSC = VUF("SC")

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e granizo
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": GRA, "fim": HOJE, "fade": .25, "zoom": .05, "selo": "ilustração"}]

# ---------------------------------------------------------------- estados
estados = [
    {"id": "hoje1", "ini": HOJE, "fim": ini("f2") + .3, "ufs": HOJE_UF, "cor": LAR, "alfa": .4},
    {"id": "co2", "ini": em("f2", "Brasília"), "fim": ini("f3") + .3, "ufs": ["GO", "DF", "MT"], "cor": LAR, "alfa": .25},
    {"id": "am2", "ini": em("f2", "Amazonas"), "fim": ini("f3") + .3, "ufs": ["AM"], "cor": AZUL, "alfa": .3},
    {"id": "go3", "ini": em("f3", "Goiás"), "fim": ini("f4") + .3, "ufs": ["GO"], "cor": VERM, "alfa": .45},
    {"id": "sul3", "ini": em("f3", "Santa"), "fim": ini("f4") + .3, "ufs": ["SC", "PR"], "cor": VERM, "alfa": .45},
    {"id": "ne4", "ini": em("f4", "Nordeste"), "fim": ini("f5") + .3, "ufs": ["CE", "PB", "PE"], "cor": LAR, "alfa": .3},
    {"id": "sc5", "ini": em("f5", "Blumenau"), "fim": ini("f6") + .3, "ufs": ["SC"], "cor": AZUL, "alfa": .3},
    {"id": "am7", "ini": em("f7", "alerta"), "fim": ini("f8") + .3, "ufs": AMANHA_UF, "cor": LAR, "alfa": .4},
    {"id": "spmg7", "ini": em("f7", "Paulo"), "fim": ini("f8") + .3, "ufs": ["SP", "MG"], "cor": VERM, "alfa": .4},
    {"id": "frio8", "ini": em("f8", "esfria"), "fim": ini("f9") + .3, "ufs": ["SC", "RS", "PR"], "cor": FRIO, "alfa": .35},
    {"id": "ne9", "ini": em("f9", "Nordeste"), "fim": ini("f10") + .3, "ufs": ["MA", "PI", "PE", "BA"], "cor": AZUL, "alfa": .25},
    {"id": "cs10", "ini": em("f10", "centro-sul"), "fim": ini("f11") + .3, "ufs": ["MT", "MS", "GO", "DF", "MG", "SP", "RJ", "ES", "PR", "SC", "RS"], "cor": AZUL, "alfa": .2},
]

pinos = [
    {"nome": "Crato (CE)", "sub": "granizo ontem (10/11)", "lon": -39.41, "lat": -7.23, "ini": HOJE + .3, "fim": ini("f2"), "h": 200},
    {"nome": "Brasília", "sub": "núcleo de trovoada", "lon": -47.88, "lat": -15.79, "ini": em("f2", "Brasília"), "fim": ini("f3"), "h": 260},
    {"nome": "Goiânia", "sub": "núcleo de trovoada", "lon": -49.25, "lat": -16.68, "ini": em("f2", "Goiânia"), "fim": ini("f3"), "h": 150},
    {"nome": "Cuiabá", "sub": "núcleo de trovoada", "lon": -56.10, "lat": -15.60, "ini": em("f2", "Cuiabá"), "fim": ini("f3"), "h": 200},
    {"nome": "Goiás", "sub": f"{UF_H['GO']} cidades em alerta", "lon": -49.6, "lat": -15.8, "ini": em("f3", "Goiás"), "fim": ini("f4"), "h": 200},
    {"nome": "SC e PR", "sub": f"SC {UF_H['SC']} · PR {UF_H['PR']} cidades", "lon": -50.5, "lat": -26.5, "ini": em("f3", "Santa"), "fim": ini("f4"), "h": 160},
    {"nome": "Crato (CE)", "sub": "pancadas hoje", "lon": -39.41, "lat": -7.23, "ini": em("f4", "Crato"), "fim": ini("f5"), "h": 160},
    {"nome": "Fortaleza", "sub": "pancadas hoje", "lon": -38.54, "lat": -3.73, "ini": em("f4", "Fortaleza"), "fim": ini("f5"), "h": 200},
    {"nome": "Blumenau", "sub": "o rio ainda está alto", "lon": -49.07, "lat": -26.92, "ini": em("f5", "Blumenau"), "fim": ini("f6"), "h": 200},
    {"nome": "Litoral do Sul", "sub": "vento nordeste 40–60 km/h", "lon": -48.6, "lat": -28.4, "ini": em("f5", "litoral"), "fim": ini("f6"), "h": 140},
    {"nome": "São Paulo", "sub": "27 °C hoje", "lon": -46.63, "lat": -23.55, "ini": em("f6", "Paulo"), "fim": ini("f7"), "h": 200},
    {"nome": "Porto Alegre", "sub": "29 °C hoje", "lon": -51.23, "lat": -30.03, "ini": em("f6", "Porto"), "fim": ini("f7"), "h": 160},
    {"nome": "São Paulo", "sub": f"{UF_A['SP']} cidades em alerta amanhã", "lon": -48.5, "lat": -22.3, "ini": em("f7", "Paulo"), "fim": ini("f8"), "h": 180},
    {"nome": "Minas Gerais", "sub": f"{UF_A['MG']} cidades em alerta amanhã", "lon": -44.5, "lat": -18.5, "ini": em("f7", "Minas"), "fim": ini("f8"), "h": 220},
    {"nome": "São Joaquim (SC)", "sub": "mínima abaixo de 10 °C", "lon": -49.93, "lat": -28.29, "ini": em("f8", "Joaquim"), "fim": ini("f9"), "h": 200},
    {"nome": f"{NE_TOP[1]} mm até 21/11", "sub": f"soma prevista ({NE_TOP[0]['uf']}) · Open-Meteo", "lon": NE_TOP[0]["p"][0], "lat": NE_TOP[0]["p"][1],
     "ini": em("f9", "Nordeste"), "fim": ini("f10"), "h": 260},
    {"nome": f"{VTOPO} mm até 21/11", "sub": f"maior soma prevista ({TOPO['uf']}) · Open-Meteo", "lon": TOPO["p"][0], "lat": TOPO["p"][1],
     "ini": em("f10", "centro-sul"), "fim": ini("f11"), "h": 150},
    {"nome": "Vale do Itajaí", "sub": "atenção domingo e segunda", "lon": -49.07, "lat": -26.92, "ini": em("f10", "Itajaí"), "fim": ini("f11"), "h": 200},
]

# ---------------------------------------------------------------- textos
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
H = GRA   # o hero (data grande) fica da capa até a palavra "granizo"
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:104px">TEMPESTADE</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">alerta em 1.487 cidades</div>'}]
paineis = [
    {"ini": HOJE, "fim": ini("f2"), "k": "INMET · TEMPESTADE HOJE",
     "contador": conta(len(TEMP), "f1", "1487", "#ff2a1f", "CIDADES NO BRASIL", lead=.9),
     "l": "chuva de até 50 mm, vento e granizo", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "NÚCLEOS DE TROVOADA",
     "itens": [{"t": em("f2", "calor"), "txt": "🌡️ calor + umidade"},
               {"t": em("f2", "Brasília"), "txt": "⛈️ Brasília, Goiânia e Cuiabá"},
               {"t": em("f2", "Amazonas"), "txt": "🌧️ e no Amazonas"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "INMET · TEMPESTADE HOJE",
     "contador": conta(UF_H["GO"], "f3", "246", "#ff2a1f", "CIDADES EM GOIÁS"),
     "itens": [{"t": em("f3", "Santa"), "txt": f"⛈️ SC {UF_H['SC']} · PR {UF_H['PR']}"},
               {"t": em("f3", "Paraná"), "txt": f"🇧🇷 total no Brasil: {len(TEMP):,}".replace(",", ".")}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "NORDESTE · HOJE",
     "itens": [{"t": em("f4", "Crato"), "txt": "⛈️ do Crato a Fortaleza"},
               {"t": em("f4", "sertão"), "txt": "🌵 pancadas no sertão"},
               {"t": em("f4", "passa"), "txt": "⚠️ chuva acima do previsto"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "SUL · RIO ALTO E VENTO",
     "contador": conta(60, "f5", "60", "#ff8c1a", "KM/H NO LITORAL", de=40, lead=.8),
     "l": "Blumenau: o rio ainda está alto", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "MÁXIMAS DE HOJE",
     "itens": [{"t": em("f6", "27"), "txt": "🌤️ São Paulo 27 °C"},
               {"t": em("f6", "29"), "txt": "🌤️ Porto Alegre 29 °C"}],
     "l": "Rio 28 · BH 25 · Curitiba 26 · Floripa 24", "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "INMET · TEMPESTADE AMANHÃ",
     "contador": conta(len(AMANHA), "f7", "2084", "#ff2a1f", "CIDADES · 12/11"),
     "l": f"SP {UF_A['SP']} · MG {UF_A['MG']} · PR {UF_A['PR']} · GO {UF_A['GO']}", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "FRIO NA SERRA",
     "itens": [{"t": em("f8", "Joaquim"), "txt": "❄️ São Joaquim abaixo de 10 °C"},
               {"t": em("f8", "sexta"), "txt": "🥶 sexta: de 5 a 8 °C na serra"}],
     "l": "previsão", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "FIM DE SEMANA · NORDESTE",
     "itens": [{"t": em("f9", "Maranhão"), "txt": "🌧️ Maranhão e Piauí"},
               {"t": em("f9", "Pernambuco"), "txt": "🌧️ sertão de Pernambuco"},
               {"t": em("f9", "Bahia"), "txt": "🌧️ Bahia"}],
     "l": "colunas: chuva prevista somada até 21/11", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "ATÉ 21/11 (PREVISÃO)",
     "itens": [{"t": em("f10", "acima"), "txt": "🌧️ chuva acima da média no centro-sul"},
               {"t": em("f10", "Itajaí"), "txt": "⚠️ Vale do Itajaí: domingo e segunda"}],
     "l": f"Open-Meteo: até {VTOPO} mm em {TOPO['uf']} · {VSC} mm em SC", "borda": "rgba(60,150,255,.8)"},
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
    {"ini": CAPA, "fim": HOJE, "html": f"<b>{MET}</b> · foto do granizo: ilustração"},
    {"ini": HOJE, "fim": ini("f2"), "html": f"<b>INMET</b>, avisos de tempestade de 11/11 · <b>{MET}</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INMET</b>, avisos de tempestade de 11/11"},
    {"ini": ini("f4"), "fim": ini("f7"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>, aviso de tempestade de 12/11"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f9"), "fim": ini("f11"), "html": f"<b>{MET}</b> · <b>Open-Meteo</b>, chuva prevista somada de 11 a 21/11"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chover": "#5ec8ff", "trovoada": "#5ec8ff", "umidade": "#5ec8ff",
         "esfria": "#96d2ff", "frio": "#96d2ff", "graus": "#ff2a1f", "granizo": "#ff2a1f", "tempestade": "#ff2a1f", "temporal": "#ff2a1f",
         "alerta": "#ff8c1a", "vento": "#ff8c1a", "alto": "#ff8c1a", "calor": "#ff8c1a", "acima": "#ff2a1f", "forca": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"crato", "ceara", "brasilia", "goiania", "cuiaba", "amazonas", "goias", "santa", "catarina", "parana", "nordeste", "fortaleza",
         "sertao", "blumenau", "sul", "sao", "paulo", "porto", "alegre", "sudeste", "minas", "joaquim", "maranhao", "piaui", "pernambuco",
         "bahia", "centrosul", "vale", "itajai", "inemaclub", "onde"}
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
      f"INMET tempestade hoje {len(TEMP)} (GO {UF_H['GO']}) · amanhã {len(AMANHA)} · colunas {len(col)} (topo {VTOPO} mm em {TOPO['uf']}) · "
      f"NE {NE_TOP[1]} mm ({NE_TOP[0]['uf']}) · SC {VSC} mm")
