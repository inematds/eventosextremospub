#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 28/10/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da chuva prevista de 29/10 a 12/11 na grade do Brasil (Open-Meteo, om/prev15_grade.json, gravado por
coleta/previsao15d.py --dia 2026-10-28).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, Pará 40 °C × São Paulo 21 °C), pinos de SP e do Pará, infravermelho do
GOES-19 na frente fria (sul da BA e ES), pancadas de hoje no centro-norte (aviso de tempestade do INMET), chuva forte na quinta
(Triângulo, sul de Minas, SP, Rio) com o aviso de chuvas intensas do INMET (2.338 municípios) e a foto do granizo (ilustração),
sexta entre Minas e o Rio, 4 °C no topo da serra no sábado, calor de 35 a 38 °C no Nordeste, colunas 3D da chuva prevista em 15 dias
(Open-Meteo) em Minas, chuva abaixo do normal na Amazônia, no Pará e no Amapá.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "28/10/2026"
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
F1 = {"lon": -51.0, "lat": -13.0, "zoom": 3.85}        # f1: São Paulo (21 °C) e Pará (40 °C) no mesmo quadro
FRENTE = {"lon": -44.0, "lat": -19.5, "zoom": 4.4}     # f2: frente fria no sul da BA e ES, nuvens no centro-sul (IR)
HOJE = {"lon": -48.5, "lat": -11.0, "zoom": 4.0}       # f3: pancadas em MT, GO, TO, MA, BA
QUI = {"lon": -46.0, "lat": -21.0, "zoom": 5.3}        # f4: Triângulo, sul de Minas, SP, Rio
INM = {"lon": -49.0, "lat": -21.5, "zoom": 4.3}        # f5: aviso do INMET (SP, MG, PR, GO, SC...)
SEX = {"lon": -46.0, "lat": -18.5, "zoom": 4.7}        # f6: Minas, Rio, Goiânia, Brasília
SERRA = {"lon": -50.0, "lat": -27.8, "zoom": 6.0}      # f7: 4 °C no topo da serra
NE = {"lon": -40.0, "lat": -7.0, "zoom": 4.8}          # f8: Nordeste quente
COL = {"lon": -45.0, "lat": -19.5, "zoom": 4.9}        # f9: colunas 3D da chuva prevista em Minas
NORTE = {"lon": -55.0, "lat": -3.0, "zoom": 4.1}       # f10: Amazônia, Pará, Amapá
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.0  # quadro 0 = capa cheia do Codex até aqui
GRAN = em("f5", "granizo")
camera = [
    K(0, BR), K(CAPA, BR), K(ini("f1") + 3.0, F1), K(fim("f1") - .2, {**F1, "zoom": 3.95}, 0, 0),
    K(ini("f2") + 1.2, FRENTE, 0, 0), K(fim("f2") - .2, {**FRENTE, "zoom": 4.5}, 0, 0),
    K(ini("f3") + 1.2, HOJE, 0, 0), K(fim("f3") - .2, {**HOJE, "zoom": 4.05}, 4, 0),
    K(ini("f4") + 1.2, QUI, 35, -8), K(fim("f4") - .2, {**QUI, "zoom": 5.4}, 40, 6),
    K(ini("f5") + 1.0, INM, 0, 0), K(fim("f5") - .2, {**INM, "zoom": 4.4}, 0, 0),
    K(ini("f6") + 1.0, SEX, 0, 0), K(fim("f6") - .2, {**SEX, "zoom": 4.8}, 4, 0),
    K(ini("f7") + 1.0, SERRA, 40, -10), K(fim("f7") - .2, {**SERRA, "zoom": 6.1}, 45, 6),
    K(ini("f8") + 1.0, NE, 0, 0), K(fim("f8") - .2, {**NE, "zoom": 4.9}, 4, 0),
    K(ini("f9") + 1.0, COL, 55, -20), K(em("f9", "180"), {**COL, "zoom": 4.95}, 56, 0), K(fim("f9") - .2, {**COL, "zoom": 5.0}, 56, 18),
    K(ini("f10") + 1.0, NORTE, 0, 0), K(fim("f10") - .2, {**NORTE, "zoom": 4.2}, 4, 0),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na frente fria (f2)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
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
assert len(BONS) >= 20, f"poucos quadros bons de infravermelho: {len(BONS)}"
imagens = []

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de 29/10 a 12/11 (Open-Meteo, grade de 1,5°)
G15 = json.loads((AQUI / "om/prev15_grade.json").read_text())
CS = {"MG", "SP", "RJ", "ES", "GO"}   # onde o boletim diz que a chuva ganha corpo em 15 dias
dias = G15["pts"][0]["dias"]
assert dias[0] == "2026-10-29" and dias[14] == "2026-11-12", (dias[0], dias[14])
SOMA = [(p, round(sum(x or 0 for x in p["chuva"][:15]))) for p in G15["pts"] if p["uf"] in CS]
MG = [v for p, v in SOMA if p["uf"] == "MG"]
MG100 = sum(v >= 100 for v in MG)
assert len(MG) == 22 and MG100 == 18, (len(MG), MG100)
col = [{"id": i, "p": p["p"], "v": v, "cor": [60, 150, 255] if v >= 100 else [120, 190, 255]} for i, (p, v) in enumerate(SOMA) if v >= 40]
ordem = {c["id"]: (c["p"][1] + 26) * .04 for c in col}   # sobe do sul de Minas para o norte
colunas = [{"id": "chuva3d", "ini": ini("f9") + .2, "fim": ini("f10") + .2, "dados": col, "raio": 70000, "escala": 2000, "ordem": ordem, "varredura": 1}]
TOPO_MG = max(((p, v) for p, v in SOMA if p["uf"] == "MG"), key=lambda x: x[1])
assert TOPO_MG[1] == 251, TOPO_MG

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e granizo
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": GRAN - .1, "fim": ini("f6") + .3, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
HOJE_T = geo(56204)   # tempestade hoje 28/10: 1.459 (GO 246, SP 239, MA 152, MG 151, MT 141, TO 138, BA 136...)
assert aviso[56204]["descricao"] == "Tempestade" and aviso[56204]["inicio"].startswith("2026-10-28") and len(HOJE_T) == 1459, len(HOJE_T)
QUI_CI = geo(56206) | geo(56207)   # chuvas intensas quinta 29/10: 2.338 (SP 645, MG 519, PR 399, GO 243, SC 168...); 918 em Perigo
assert aviso[56206]["descricao"] == "Chuvas Intensas" and aviso[56206]["inicio"].startswith("2026-10-29") and len(QUI_CI) == 2338, len(QUI_CI)
QUI_P = len(geo(56207))
assert QUI_P == 918, QUI_P
SEX_CI = geo(56209) | geo(56210)   # chuvas intensas sexta 30/10 (MG 853, SP 446, PR 399, SC 295, RS 206, GO 209, RJ 92, ES 78...)
assert aviso[56209]["inicio"].startswith("2026-10-30") and aviso[56210]["inicio"].startswith("2026-10-30")
NSEX = len(SEX_CI)
UFCOD = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN",
         "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC",
         "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
from collections import Counter
QUI_UF = [UFCOD[c] for c, k in Counter(c[:2] for c in QUI_CI).items() if k >= 40]   # estados com 40+ municípios no aviso
assert set(QUI_UF) == {"SP", "MG", "PR", "GO", "SC", "MT", "MS", "RJ", "RO"}, QUI_UF

# ---------------------------------------------------------------- estados
estados = [
    {"id": "sp1", "ini": em("f1", "Paulo"), "fim": em("f1", "Pará") - .1, "ufs": ["SP"], "cor": FRIO, "alfa": .4},
    {"id": "pa1", "ini": em("f1", "Pará"), "fim": ini("f2") + .3, "ufs": ["PA"], "cor": VERM, "alfa": .4},
    {"id": "frente", "ini": em("f2", "Bahia"), "fim": ini("f3") + .3, "ufs": ["BA", "ES"], "cor": FRIO, "alfa": .25},
    {"id": "h_mt", "ini": em("f3", "Mato"), "fim": ini("f4") + .3, "ufs": ["MT"], "cor": AZUL, "alfa": .35},
    {"id": "h_go", "ini": em("f3", "Goiás"), "fim": ini("f4") + .3, "ufs": ["GO", "DF"], "cor": AZUL, "alfa": .35},
    {"id": "h_to", "ini": em("f3", "Tocantins"), "fim": ini("f4") + .3, "ufs": ["TO"], "cor": AZUL, "alfa": .35},
    {"id": "h_ma", "ini": em("f3", "Maranhão"), "fim": ini("f4") + .3, "ufs": ["MA"], "cor": AZUL, "alfa": .35},
    {"id": "h_ba", "ini": em("f3", "Bahia"), "fim": ini("f4") + .3, "ufs": ["BA"], "cor": AZUL, "alfa": .35},
    {"id": "h_sul", "ini": em("f3", "Sul"), "fim": ini("f4") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .2},
    {"id": "q_mg", "ini": em("f4", "Triângulo"), "fim": ini("f5") + .3, "ufs": ["MG"], "cor": LAR, "alfa": .35},
    {"id": "q_sp", "ini": em("f4", "Paulo"), "fim": ini("f5") + .3, "ufs": ["SP"], "cor": LAR, "alfa": .35},
    {"id": "q_rj", "ini": em("f4", "Rio"), "fim": ini("f5") + .3, "ufs": ["RJ"], "cor": LAR, "alfa": .35},
    {"id": "inmet", "ini": ini("f5"), "fim": GRAN, "ufs": QUI_UF, "cor": LAR, "alfa": .35},
    {"id": "s_mg", "ini": em("f6", "Minas"), "fim": ini("f7") + .3, "ufs": ["MG", "RJ"], "cor": AZUL, "alfa": .4},
    {"id": "s_go", "ini": em("f6", "Goiânia"), "fim": ini("f7") + .3, "ufs": ["GO", "DF"], "cor": AZUL, "alfa": .3},
    {"id": "frio", "ini": em("f7", "frio"), "fim": ini("f8") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .4},
    {"id": "calor", "ini": em("f8", "quentes"), "fim": ini("f9") + .3, "ufs": ["PI", "CE", "PE", "PB"], "cor": VERM, "alfa": .45},
    {"id": "n_pa", "ini": em("f10", "Amazônia"), "fim": ini("f11") + .3, "ufs": ["AM", "PA"], "cor": LAR, "alfa": .4},
    {"id": "n_ap", "ini": em("f10", "Amapá"), "fim": ini("f11") + .3, "ufs": ["AP"], "cor": VERM, "alfa": .5},
]

pinos = [
    {"nome": "São Paulo", "sub": "máxima de 21 °C amanhã (previsão)", "lon": -46.63, "lat": -23.55, "ini": em("f1", "Paulo"), "fim": ini("f2"), "h": 180},
    {"nome": "Pará", "sub": "até 40 °C amanhã (previsão)", "lon": -52.0, "lat": -3.5, "ini": em("f1", "Pará"), "fim": ini("f2"), "h": 180},
    {"nome": "Frente fria", "sub": "sul da Bahia e Espírito Santo", "lon": -39.6, "lat": -18.6, "ini": em("f2", "frente"), "fim": ini("f3"), "h": 220},
    {"nome": "Triângulo Mineiro", "sub": "chuva forte na quinta", "lon": -48.28, "lat": -18.92, "ini": em("f4", "Triângulo"), "fim": ini("f5"), "h": 340},
    {"nome": "Sul de Minas", "sub": "chuva forte na quinta", "lon": -45.43, "lat": -21.55, "ini": em("f4", "sul"), "fim": ini("f5"), "h": 170},
    {"nome": "São Paulo", "sub": "chuva forte na quinta", "lon": -46.63, "lat": -23.55, "ini": em("f4", "Paulo"), "fim": ini("f5"), "h": 90},
    {"nome": "Rio de Janeiro", "sub": "chuva forte na quinta", "lon": -43.2, "lat": -22.9, "ini": em("f4", "Rio"), "fim": ini("f5"), "h": 180},
    {"nome": "Goiânia", "sub": "boa chuva na sexta", "lon": -49.25, "lat": -16.68, "ini": em("f6", "Goiânia"), "fim": ini("f7"), "h": 200},
    {"nome": "Brasília", "sub": "boa chuva na sexta", "lon": -47.88, "lat": -15.79, "ini": em("f6", "Brasília"), "fim": ini("f7"), "h": 90},
    {"nome": "Topo da serra", "sub": "4 °C no sábado cedo (previsão)", "lon": -49.93, "lat": -28.29, "ini": em("f7", "serra"), "fim": ini("f8"), "h": 220},
    {"nome": f"{TOPO_MG[1]} mm em 15 dias", "sub": "maior soma prevista em MG · Open-Meteo", "lon": TOPO_MG[0]["p"][0], "lat": TOPO_MG[0]["p"][1],
     "ini": em("f9", "180"), "fim": ini("f10"), "h": 260},
    {"nome": "Amapá", "sub": "o que mais sofre com pouca chuva", "lon": -51.8, "lat": 1.4, "ini": em("f10", "Amapá"), "fim": ini("f11"), "h": 160},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)   # número dito logo no começo da fala: o contador começa com a fala
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
H = em("f1", "21") - 1.05   # o hero (data grande) fica até o contador de SP começar (a data é dita durante a capa)
PA1 = em("f1", "Pará") - .1
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:104px">21 °C × 40 °C</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">São Paulo × Pará, amanhã</div>'}]
paineis = [
    {"ini": H, "fim": PA1, "k": "SÃO PAULO · QUINTA 29/10",
     "contador": conta(21, "f1", "21", "#5ec8ff", "°C DE MÁXIMA", de=30),
     "l": "chuva e nuvem deixam o centro-sul abaixo da média (previsão)", "borda": "rgba(94,200,255,.8)"},
    {"ini": PA1, "fim": ini("f2"), "k": "PARÁ · QUINTA 29/10",
     "contador": conta(40, "f1", "40", "#ff2a1f", "°C DE MÁXIMA", de=30),
     "l": "também no norte do Amazonas (previsão)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "O QUE MANDA NO TEMPO",
     "itens": [{"t": em("f2", "frente"), "txt": "❄️ frente fria no sul da BA e no ES"},
               {"t": em("f2", "nuvem"), "txt": "☁️ muita nuvem no centro-sul"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "HOJE · QUARTA 28/10",
     "itens": [{"t": em("f3", "Mato"), "txt": "🌧️ pancadas em MT e GO"},
               {"t": em("f3", "Tocantins"), "txt": "🌧️ TO, MA e Bahia"},
               {"t": em("f3", "Sul"), "txt": "🌦️ Sul: chuva isolada"}],
     "l": f"INMET: aviso de tempestade hoje em {len(HOJE_T):,} municípios".replace(",", "."), "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "QUINTA · CHUVA FORTE (PREVISÃO)",
     "itens": [{"t": em("f4", "Triângulo"), "txt": "⛈️ Triângulo Mineiro"},
               {"t": em("f4", "sul"), "txt": "⛈️ sul de Minas"},
               {"t": em("f4", "Paulo"), "txt": "⛈️ São Paulo e o Rio"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f5"), "fim": GRAN - .1, "k": "INMET · CHUVAS INTENSAS 29/10",
     "contador": conta(2338, "f5", "2.338", "#ff8c1a", "MUNICÍPIOS EM ALERTA"),
     "l": f"{QUI_P} deles em nível de perigo (laranja)", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SEXTA · 30/10 (PREVISÃO)",
     "itens": [{"t": em("f6", "Minas"), "txt": "⛈️ chuva forte de Minas ao Rio"},
               {"t": em("f6", "Goiânia"), "txt": "🌧️ Goiânia e Brasília"}],
     "l": f"INMET: chuvas intensas na sexta em {NSEX:,} municípios".replace(",", "."), "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SÁBADO CEDO · TOPO DA SERRA",
     "contador": conta(4, "f7", "4", "#96d2ff", "°C (PREVISÃO)", de=15),
     "l": "frio também em MS, SP e no sul de Minas", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "NORDESTE · MÁXIMAS (PREVISÃO)",
     "contador": conta(38, "f8", "38", "#ff2a1f", "°C", de=35, lead=.8),
     "l": "de 35 a 38 °C no Piauí, Ceará, Paraíba e Pernambuco", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "MINAS · 15 DIAS (PREVISÃO)",
     "contador": conta(180, "f9", "180", "#5ec8ff", "MM DE CHUVA"),
     "l": f"acima do normal · Open-Meteo: {MG100} de {len(MG)} pontos de MG com 100 mm ou mais", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "CHUVA ABAIXO DO NORMAL",
     "itens": [{"t": em("f10", "Amazônia"), "txt": "🟠 Amazônia e Pará"},
               {"t": em("f10", "Amapá"), "txt": "🔴 Amapá: o que mais sofre"}],
     "borda": "rgba(255,140,26,.8)"},
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
    {"ini": ini("f3"), "fim": ini("f5"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso de tempestade de 28/10"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>INMET</b>, avisos de chuvas intensas para 29/10 · <b>{MET}</b> · foto do granizo: ilustração"},
    {"ini": ini("f6"), "fim": ini("f9"), "html": f"<b>{MET}</b> · <b>INMET</b>, avisos para 30/10 · previsão"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · <b>Open-Meteo</b>, chuva prevista somada de 29/10 a 12/11"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "chover": "#5ec8ff", "chuvas": "#5ec8ff", "pancadas": "#5ec8ff", "frio": "#96d2ff",
         "fria": "#96d2ff", "frente": "#96d2ff", "nuvem": "#96d2ff", "graus": "#ff2a1f", "quentes": "#ff2a1f", "granizo": "#96d2ff",
         "forte": "#ff8c1a", "intensas": "#ff8c1a", "alerta": "#ff8c1a", "abaixo": "#ff8c1a", "acima": "#5ec8ff", "sofre": "#ff2a1f",
         "milimetros": "#5ec8ff", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sao", "paulo", "para", "bahia", "espirito", "santo", "centrosul", "mato", "grosso", "goias", "tocantins", "maranhao", "sul",
         "triangulo", "mineiro", "minas", "rio", "goiania", "brasilia", "serra", "norte", "nordeste", "piaui", "ceara", "pernambuco",
         "amazonia", "amapa", "inemaclub", "onde"}
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
      f"INMET hoje {len(HOJE_T)}, quinta {len(QUI_CI)} ({QUI_P} perigo), sexta {NSEX} · colunas {len(col)} (MG {MG100}/{len(MG)} ≥ 100 mm, topo {TOPO_MG[1]})")
