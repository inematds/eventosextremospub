#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 29/10/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da chuva prevista de 29/10 a 02/11 (Finados) na grade do Brasil (Open-Meteo, om/prev15_grade.json, gravado por
coleta/previsao15d.py --dia 2026-10-28).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, tempestade no Maranhão, 50 mm), núcleo de chuva no Maranhão no
infravermelho do GOES-19, pancadas de hoje no centro-sul (aviso de chuvas intensas do INMET), Sul seco no RS e pancadas em SC,
sexta com chuva forte em BH, Triângulo e Grande Rio, SC no centro, vale e serra, alerta do INMET para sexta (Minas 853 → Brasil 3.226),
Nordeste quente de 34 a 38 °C, colunas 3D da chuva prevista até segunda (Open-Meteo) do centro-sul, geada no outro sábado
nos Campos de Palmas (foto do Codex, ilustração).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "29/10/2026"
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
MA = {"lon": -45.0, "lat": -5.0, "zoom": 5.2}          # f1: núcleo de chuva no Maranhão
MA_IR = {"lon": -44.5, "lat": -6.0, "zoom": 4.7}       # f2: satélite (IR) no Maranhão e no Piauí
HOJE = {"lon": -47.5, "lat": -19.0, "zoom": 4.8}       # f3: GO, DF, Triângulo, sul de Minas, nordeste de SP, Rio
SUL = {"lon": -51.5, "lat": -28.5, "zoom": 5.2}        # f4: RS seco, SC com pancadas
SEX = {"lon": -44.8, "lat": -21.0, "zoom": 5.5}        # f5: BH, Triângulo, Grande Rio
SC = {"lon": -50.4, "lat": -27.3, "zoom": 6.3}         # f6: centro, vale e serra de SC
INM = {"lon": -48.5, "lat": -18.5, "zoom": 4.1}        # f7: Minas e depois o Brasil (aviso do INMET)
NE = {"lon": -40.0, "lat": -7.0, "zoom": 4.8}          # f8: Nordeste quente
COL = {"lon": -46.0, "lat": -20.5, "zoom": 5.0}        # f9: colunas 3D da chuva prevista até segunda
PALMAS = {"lon": -51.9, "lat": -26.6, "zoom": 6.4}     # f10: geada nos Campos de Palmas
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.0  # quadro 0 = capa cheia do Codex até aqui
GEADA = em("f10", "geada")
ZERO = em("f10", "0")
camera = [
    K(0, BR), K(CAPA, BR), K(ini("f1") + 3.0, MA), K(fim("f1") - .2, {**MA, "zoom": 5.35}, 0, 0),
    K(ini("f2") + 1.2, MA_IR, 0, 0), K(fim("f2") - .2, {**MA_IR, "zoom": 4.8}, 0, 0),
    K(ini("f3") + 1.2, HOJE, 0, 0), K(fim("f3") - .2, {**HOJE, "zoom": 4.9}, 4, 0),
    K(ini("f4") + 1.0, SUL, 0, 0), K(fim("f4") - .2, {**SUL, "zoom": 5.3}, 4, 0),
    K(ini("f5") + 1.2, SEX, 35, -8), K(fim("f5") - .2, {**SEX, "zoom": 5.6}, 40, 6),
    K(ini("f6") + 1.0, SC, 40, -10), K(fim("f6") - .2, {**SC, "zoom": 6.4}, 45, 6),
    K(ini("f7") + 1.0, {**INM, "lon": -45.0, "lat": -18.5, "zoom": 5.0}, 0, 0), K(em("f7", "3.226") - .6, {**INM, "lon": -45.0, "lat": -18.5, "zoom": 5.05}, 0, 0),
    K(em("f7", "3.226") + .6, INM, 0, 0), K(fim("f7") - .2, {**INM, "zoom": 4.15}, 0, 0),
    K(ini("f8") + 1.0, NE, 0, 0), K(fim("f8") - .2, {**NE, "zoom": 4.9}, 4, 0),
    K(ini("f9") + 1.0, COL, 55, -20), K(em("f9", "Minas"), {**COL, "zoom": 5.05}, 56, 0), K(fim("f9") - .2, {**COL, "zoom": 5.1}, 56, 18),
    K(ini("f10") + 1.0, PALMAS, 35, -8), K(fim("f10") - .2, {**PALMAS, "zoom": 6.5}, 40, 4),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) no Maranhão (f2)
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
assert len(BONS) >= 40, f"poucos quadros bons de infravermelho: {len(BONS)}"
imagens = []

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de 29/10 a 02/11 (Open-Meteo, grade de 1,5°)
G15 = json.loads((AQUI / "om/prev15_grade.json").read_text())
CS = {"MG", "SP", "RJ", "ES", "GO", "DF"}   # onde o boletim diz que a chuva soma muito até segunda
dias = G15["pts"][0]["dias"]
assert dias[0] == "2026-10-29" and dias[4] == "2026-11-02", (dias[0], dias[4])
SOMA = [(p, round(sum(x or 0 for x in p["chuva"][:5]))) for p in G15["pts"] if p["uf"] in CS]
C50 = sum(v >= 50 for p, v in SOMA)
assert len(SOMA) == 51 and C50 == 17, (len(SOMA), C50)
col = [{"id": i, "p": p["p"], "v": v, "cor": [60, 150, 255] if v >= 50 else [120, 190, 255]} for i, (p, v) in enumerate(SOMA) if v >= 20]
ordem = {c["id"]: (c["p"][1] + 24) * .05 for c in col}   # sobe de SP e do Rio para Goiás
colunas = [{"id": "chuva3d", "ini": ini("f9") + .2, "fim": ini("f10") + .2, "dados": col, "raio": 70000, "escala": 5000, "ordem": ordem, "varredura": 1}]
TOPO = max(SOMA, key=lambda x: x[1])
assert TOPO[1] == 85 and TOPO[0]["uf"] == "MG", TOPO

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e geada
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/geada.png", "ini": GEADA - .1, "fim": ini("f11") + .3, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
HOJE_CI = geo(56211)   # chuvas intensas hoje 29/10: 2.804 (SP 645, MG 511, PR 399, SC 295, GO 246...)
assert aviso[56211]["descricao"] == "Chuvas Intensas" and aviso[56211]["inicio"].startswith("2026-10-29") and len(HOJE_CI) == 2804, len(HOJE_CI)
SEX_CI = geo(56215)    # chuvas intensas sexta 30/10: 3.226 (MG 853, SP 645, PR 399, SC 283, GO 246...)
assert aviso[56215]["descricao"] == "Chuvas Intensas" and aviso[56215]["inicio"].startswith("2026-10-30") and len(SEX_CI) == 3226, len(SEX_CI)
UFCOD = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN",
         "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC",
         "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
from collections import Counter
SEX_POR_UF = Counter(UFCOD[c[:2]] for c in SEX_CI)
assert SEX_POR_UF["MG"] == 853, SEX_POR_UF["MG"]
SEX_UF = [u for u, k in SEX_POR_UF.items() if k >= 40]   # estados com 40+ municípios no aviso
HOJE_UF = [UFCOD[c] for c, k in Counter(c[:2] for c in HOJE_CI).items() if k >= 40]

# ---------------------------------------------------------------- estados
estados = [
    {"id": "ma1", "ini": em("f1", "Maranhão"), "fim": ini("f3") + .3, "ufs": ["MA"], "cor": AZUL, "alfa": .4},
    {"id": "h_go", "ini": em("f3", "Goiás"), "fim": ini("f4") + .3, "ufs": ["GO", "DF"], "cor": AZUL, "alfa": .35},
    {"id": "h_mg", "ini": em("f3", "Triângulo"), "fim": ini("f4") + .3, "ufs": ["MG"], "cor": AZUL, "alfa": .35},
    {"id": "h_sp", "ini": em("f3", "Paulo"), "fim": ini("f4") + .3, "ufs": ["SP"], "cor": AZUL, "alfa": .35},
    {"id": "h_rj", "ini": em("f3", "Rio"), "fim": ini("f4") + .3, "ufs": ["RJ"], "cor": AZUL, "alfa": .35},
    {"id": "s_rs", "ini": em("f4", "Grande"), "fim": ini("f5") + .3, "ufs": ["RS"], "cor": LAR, "alfa": .3},
    {"id": "s_sc", "ini": em("f4", "Santa"), "fim": ini("f5") + .3, "ufs": ["SC"], "cor": AZUL, "alfa": .4},
    {"id": "x_mg", "ini": em("f5", "Belo"), "fim": ini("f6") + .3, "ufs": ["MG"], "cor": LAR, "alfa": .35},
    {"id": "x_rj", "ini": em("f5", "Grande"), "fim": ini("f6") + .3, "ufs": ["RJ"], "cor": LAR, "alfa": .4},
    {"id": "x_sc", "ini": em("f6", "Santa"), "fim": ini("f7") + .3, "ufs": ["SC"], "cor": LAR, "alfa": .45},
    {"id": "i_mg", "ini": em("f7", "Minas"), "fim": em("f7", "3.226") - .1, "ufs": ["MG"], "cor": LAR, "alfa": .45},
    {"id": "i_br", "ini": em("f7", "3.226") - .1, "fim": ini("f8") + .3, "ufs": SEX_UF, "cor": LAR, "alfa": .35},
    {"id": "calor", "ini": em("f8", "quente"), "fim": ini("f9") + .3, "ufs": ["PI", "CE", "RN", "PB", "PE", "AL", "SE"], "cor": VERM, "alfa": .4},
    {"id": "frio", "ini": em("f10", "frio"), "fim": ini("f11") + .3, "ufs": ["PR", "SC", "RS"], "cor": FRIO, "alfa": .4},
]

pinos = [
    {"nome": "Maranhão", "sub": "até 50 mm hoje (previsão)", "lon": -45.0, "lat": -5.0, "ini": em("f1", "Maranhão"), "fim": ini("f2"), "h": 200},
    {"nome": "Núcleo de chuva", "sub": "modelo dava 5 a 15 mm", "lon": -44.5, "lat": -5.5, "ini": em("f2", "modelo"), "fim": ini("f3"), "h": 220},
    {"nome": "Goiânia", "sub": "pancadas hoje", "lon": -49.25, "lat": -16.68, "ini": em("f3", "Goiás"), "fim": ini("f4"), "h": 200},
    {"nome": "Triângulo Mineiro", "sub": "pancadas hoje", "lon": -48.28, "lat": -18.92, "ini": em("f3", "Triângulo"), "fim": ini("f4"), "h": 300},
    {"nome": "Rio de Janeiro", "sub": "pancadas hoje", "lon": -43.2, "lat": -22.9, "ini": em("f3", "Rio"), "fim": ini("f4"), "h": 160},
    {"nome": "Porto Alegre", "sub": "tempo seco", "lon": -51.23, "lat": -30.03, "ini": em("f4", "seco"), "fim": ini("f5"), "h": 160},
    {"nome": "Florianópolis", "sub": "pancadas à tarde e à noite", "lon": -48.55, "lat": -27.6, "ini": em("f4", "Santa"), "fim": ini("f5"), "h": 240},
    {"nome": "Belo Horizonte", "sub": "chuva forte na sexta", "lon": -43.94, "lat": -19.92, "ini": em("f5", "Belo"), "fim": ini("f6"), "h": 260},
    {"nome": "Uberlândia", "sub": "Triângulo · chuva forte", "lon": -48.28, "lat": -18.92, "ini": em("f5", "Triângulo"), "fim": ini("f6"), "h": 180},
    {"nome": "Grande Rio", "sub": "chuva forte na sexta", "lon": -43.2, "lat": -22.9, "ini": em("f5", "Grande"), "fim": ini("f6"), "h": 160},
    {"nome": "Vale do Itajaí", "sub": "chuva forte na sexta", "lon": -49.07, "lat": -26.92, "ini": em("f6", "vale"), "fim": ini("f7"), "h": 200},
    {"nome": "Serra de SC", "sub": "chuva forte na sexta", "lon": -50.33, "lat": -28.28, "ini": em("f6", "serra"), "fim": ini("f7"), "h": 140},
    {"nome": f"{TOPO[1]} mm até segunda", "sub": "maior soma prevista · Open-Meteo", "lon": TOPO[0]["p"][0], "lat": TOPO[0]["p"][1],
     "ini": em("f9", "Minas"), "fim": ini("f10"), "h": 260},
    {"nome": "Campos de Palmas", "sub": "o frio volta (previsão)", "lon": -51.99, "lat": -26.48, "ini": em("f10", "frio"), "fim": GEADA - .1, "h": 220},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)   # número dito logo no começo da fala: o contador começa com a fala
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
H = em("f1", "50") - 1.05   # o hero (data grande) fica até o contador do Maranhão começar (a data é dita durante a capa)
BR7 = em("f7", "3.226") - 1.1
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:104px">50 mm</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">núcleo de chuva no Maranhão, hoje</div>'}]
paineis = [
    {"ini": H, "fim": ini("f2"), "k": "MARANHÃO · HOJE 29/10",
     "contador": conta(50, "f1", "50", "#5ec8ff", "MM DE CHUVA (PREVISÃO)"),
     "l": "em poucas horas, em alguns pontos", "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "O MODELO × O SATÉLITE",
     "itens": [{"t": em("f2", "satélite"), "txt": "🛰️ nuvem crescendo no Maranhão"},
               {"t": em("f2", "modelo"), "txt": "📉 modelo: de 5 a 15 mm"},
               {"t": em("f2", "mais"), "txt": "⛈️ bem mais em alguns pontos"}],
     "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "HOJE · QUINTA 29/10",
     "itens": [{"t": em("f3", "Goiás"), "txt": "🌧️ Goiás e Brasília"},
               {"t": em("f3", "Triângulo"), "txt": "🌧️ Triângulo e sul de Minas"},
               {"t": em("f3", "Paulo"), "txt": "🌧️ nordeste de SP e o Rio"}],
     "l": f"INMET: chuvas intensas hoje em {len(HOJE_CI):,} municípios".replace(",", "."), "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "SUL · HOJE",
     "itens": [{"t": em("f4", "seco"), "txt": "☀️ Rio Grande do Sul: seco"},
               {"t": em("f4", "Santa"), "txt": "🌦️ SC: pancadas à tarde e à noite"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "SEXTA 30/10 · CHUVA FORTE (PREVISÃO)",
     "itens": [{"t": em("f5", "Belo"), "txt": "⛈️ Belo Horizonte"},
               {"t": em("f5", "Triângulo"), "txt": "⛈️ Triângulo Mineiro"},
               {"t": em("f5", "Grande"), "txt": "⛈️ Grande Rio"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SANTA CATARINA · SEXTA (PREVISÃO)",
     "itens": [{"t": em("f6", "centro"), "txt": "⛈️ centro do estado"},
               {"t": em("f6", "vale"), "txt": "⛈️ vale"},
               {"t": em("f6", "serra"), "txt": "⛈️ serra"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f7"), "fim": BR7, "k": "INMET · CHUVAS INTENSAS 30/10",
     "contador": conta(853, "f7", "853", "#ff8c1a", "CIDADES EM MINAS"),
     "l": "aviso amarelo de chuvas intensas para sexta", "borda": "rgba(255,140,26,.8)"},
    {"ini": BR7, "fim": ini("f8"), "k": "INMET · BRASIL · SEXTA 30/10",
     "contador": conta(3226, "f7", "3.226", "#ff8c1a", "CIDADES NO BRASIL"),
     "l": f"SP {SEX_POR_UF['SP']}, PR {SEX_POR_UF['PR']}, SC {SEX_POR_UF['SC']}, GO {SEX_POR_UF['GO']}", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "NORDESTE · MÁXIMAS (PREVISÃO)",
     "contador": conta(38, "f8", "38", "#ff2a1f", "°C", de=34, lead=.8),
     "l": "de 34 a 38 °C, quase sem chuva", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "ATÉ SEGUNDA 02/11 · FINADOS",
     "itens": [{"t": em("f9", "Goiás"), "txt": "🌧️ Goiás e Minas"},
               {"t": em("f9", "Paulo"), "txt": "🌧️ São Paulo e Rio"},
               {"t": em("f9", "Espírito"), "txt": "🌧️ Espírito Santo"}],
     "l": f"colunas: chuva prevista somada de 29/10 a 02/11 · Open-Meteo · até {TOPO[1]} mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": GEADA - .1, "k": "O FRIO VOLTA",
     "itens": [{"t": em("f10", "frio"), "txt": "❄️ ar frio no Sul"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": GEADA - .1, "fim": ini("f11"), "k": "CAMPOS DE PALMAS · SÁBADO 07/11",
     "contador": conta(0, "f10", "0", "#96d2ff", "°C · GEADA (PREVISÃO)", de=10),
     "l": "novembro ainda não está livre de geada no Sul", "borda": "rgba(150,210,255,.8)"},
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
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso de chuvas intensas de 29/10"},
    {"ini": ini("f4"), "fim": ini("f7"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>INMET</b>, aviso de chuvas intensas para 30/10"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · <b>Open-Meteo</b>, chuva prevista somada de 29/10 a 02/11"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b> · previsão · foto da geada: ilustração"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chover": "#5ec8ff", "chuvas": "#5ec8ff", "pancadas": "#5ec8ff", "nuvem": "#96d2ff", "frio": "#96d2ff",
         "geada": "#96d2ff", "graus": "#ff2a1f", "grau": "#96d2ff", "quente": "#ff2a1f", "seco": "#ff8c1a", "forte": "#ff8c1a",
         "intensas": "#ff8c1a", "alerta": "#ff8c1a", "milimetros": "#5ec8ff", "satelite": AM, "soma": "#5ec8ff",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"maranhao", "goias", "brasilia", "triangulo", "mineiro", "sul", "minas", "nordeste", "sao", "paulo", "rio", "grande", "santa",
         "catarina", "belo", "horizonte", "vale", "serra", "brasil", "espirito", "santo", "campos", "palmas", "inemaclub", "onde"}
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
      f"INMET hoje {len(HOJE_CI)}, sexta {len(SEX_CI)} (MG {SEX_POR_UF['MG']}) · colunas {len(col)} ({C50} ≥ 50 mm, topo {TOPO[1]})")
