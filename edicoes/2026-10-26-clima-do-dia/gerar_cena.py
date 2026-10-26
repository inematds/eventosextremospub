#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 26/10/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS),
dos avisos do INMET e da chuva prevista de 26/10 a 9/11 na grade do Brasil (Open-Meteo, om/prev15_grade.json,
gravado por coleta/previsao15d.py --dia 2026-10-25).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, 2,9 °C na serra de SC), contador da mínima no Morro da Igreja e em
São Joaquim com o Sul pintado de frio, foto da fumaça na Amazônia (ilustração) e infravermelho do GOES-19 com câmera inclinada na
chuva do AM, AC e RO, chuva no ES e leste de MG, aviso de tempestade de hoje (608 em MG → 1.608 no país), Nordeste seco com 40 °C
entre AL, SE e BA, chuva de terça na Bahia, frio abaixo de zero na serra com foto da geada no pomar (ilustração), chuva forte
de quinta no Sudeste e volta ao Sul, colunas 3D da chuva prevista até 9/11 (Open-Meteo).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "26/10/2026"
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
SERRA = {"lon": -49.6, "lat": -28.15, "zoom": 6.7}     # f1: Morro da Igreja (SC)
SUL = {"lon": -51.5, "lat": -27.0, "zoom": 5.0}        # f2: São Joaquim → massa de ar frio no Sul
AMZ = {"lon": -64.0, "lat": -7.5, "zoom": 4.5}         # f3: chuva no AM, AC e RO (IR)
SE = {"lon": -43.8, "lat": -19.3, "zoom": 5.3}         # f4: ES e leste de MG
MG = {"lon": -44.8, "lat": -18.5, "zoom": 5.1}         # f5: aviso em 608 cidades de MG
PAIS = {"lon": -48.0, "lat": -13.0, "zoom": 3.9}       # f5: total do país
NE = {"lon": -39.0, "lat": -8.8, "zoom": 5.0}          # f6: Nordeste seco, 40 °C entre AL, SE e BA
BA = {"lon": -41.0, "lat": -12.0, "zoom": 5.3}         # f7: chuva de terça na Bahia
GEO = {"lon": -50.0, "lat": -28.4, "zoom": 6.4}        # f8: serra abaixo de zero, geada em São Joaquim
QUI = {"lon": -46.5, "lat": -23.5, "zoom": 4.7}        # f9: chuva forte de quinta no Sudeste e volta ao Sul
COL = {"lon": -49.0, "lat": -23.5, "zoom": 4.35}       # f10: colunas 3D até 9/11
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
TOT5 = em("f5", "1.608")
FUMACA = em("f3", "fumaça")
CHOVE = em("f3", "chove")
GEAR = em("f8", "geada")
camera = [
    K(0, BR), K(CAPA, BR), K(em("f1", "amanheceu") + .3, SERRA, 0, 0),
    K(fim("f1") - .2, {**SERRA, "zoom": 6.8}, 4, 0),
    K(ini("f2") + 1.0, {**SERRA, "lon": -49.93, "lat": -28.29}, 0, 0), K(em("f2", "massa"), SUL, 0, 0), K(fim("f2") - .2, {**SUL, "zoom": 5.1}, 0, 0),
    K(CHOVE + .3, AMZ, 45, -15), K(fim("f3") - .2, {**AMZ, "lon": -62.5, "zoom": 4.6}, 48, -2),
    K(ini("f4") + 1.0, SE, 0, 0), K(fim("f4") - .2, {**SE, "zoom": 5.4}, 4, 0),
    K(ini("f5") + 1.0, MG, 0, 0), K(TOT5 - 1.2, {**MG, "zoom": 5.2}, 0, 0), K(TOT5 + .4, PAIS, 0, 0), K(fim("f5") - .2, {**PAIS, "zoom": 3.95}, 0, 0),
    K(ini("f6") + 1.0, NE, 0, 0), K(fim("f6") - .2, {**NE, "zoom": 5.1}, 4, 0),
    K(ini("f7") + 1.0, BA, 0, 0), K(fim("f7") - .2, {**BA, "zoom": 5.4}, 4, 0),
    K(ini("f8") + 1.0, GEO, 30, -10), K(fim("f8") - .2, {**GEO, "zoom": 6.5}, 34, 6),
    K(ini("f9") + 1.0, QUI, 0, 0), K(fim("f9") - .2, {**QUI, "zoom": 4.8}, 4, 0),
    K(ini("f10") + 1.0, COL, 55, -20), K(em("f10", "Centro-Oeste"), {**COL, "zoom": 4.4}, 56, 0), K(fim("f10") - .2, {**COL, "zoom": 4.45}, 56, 18),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na chuva da Amazônia (f3)
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
              "ini": CHOVE - .3, "fim": ini("f4") + .4, "dur": fim("f3") - CHOVE + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])
assert len(BONS) >= 20, f"poucos quadros bons de infravermelho: {len(BONS)}"

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de 26/10 a 9/11 (Open-Meteo, grade de 1,5°)
G15 = json.loads((AQUI / "om/prev15_grade.json").read_text())
CS = {"PR", "SC", "RS", "SP", "RJ", "MG", "ES", "MS", "MT", "GO", "DF"}   # Sul, Sudeste e Centro-Oeste
dias = G15["pts"][0]["dias"]
assert dias[0] == "2026-10-26" and dias[14] == "2026-11-09", (dias[0], dias[14])
SOMA = [(p, round(sum(x or 0 for x in p["chuva"][:15]))) for p in G15["pts"] if p["uf"] in CS]
ACIMA = [(p, v) for p, v in SOMA if v >= 100]
assert len(ACIMA) >= 20, f"poucos pontos acima de 100 mm: {len(ACIMA)}"   # a fala diz "muitas áreas"
col = [{"id": i, "p": p["p"], "v": v, "cor": [60, 150, 255] if v >= 100 else [120, 190, 255]} for i, (p, v) in enumerate(SOMA) if v >= 40]
ordem = {c["id"]: (c["p"][1] + 34) * .04 for c in col}   # sobe do Sul para o Centro-Oeste
colunas = [{"id": "chuva3d", "ini": ini("f10") + .2, "fim": ini("f11") + .2, "dados": col, "raio": 70000, "escala": 2000, "ordem": ordem, "varredura": 1}]
TOPO, VTOPO = max(SOMA, key=lambda x: x[1])

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, fumaça e geada
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/fumaca.png", "ini": FUMACA - .1, "fim": CHOVE - .2, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/geada.png", "ini": GEAR - .1, "fim": ini("f9") + .3, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_geo = lambda g, minimo=5: sorted({UF[c[:2]] for c in g if sum(x[:2] == c[:2] for x in g) >= minimo})
TEMP_HOJE = geo(56192)   # tempestade amarela 26/10: 1.608 (MG 608, BA 263, GO 193, TO 139, ES 78...)
assert aviso[56192]["descricao"] == "Tempestade" and aviso[56192]["inicio"].startswith("2026-10-26")
assert len(TEMP_HOJE) == 1608 and sum(c[:2] == "31" for c in TEMP_HOJE) == 608, len(TEMP_HOJE)
HOJE = ufs_geo(TEMP_HOJE)
SECO = geo(56176)   # baixa umidade 26/10: 355 cidades do Nordeste
assert aviso[56176]["descricao"] == "Baixa Umidade" and len(SECO) == 355, len(SECO)
QUINTA = geo(56195)   # tempestade quinta 29/10: 2.777 (SP 645, MG 536, PR 399, SC 295...)
assert aviso[56195]["descricao"] == "Tempestade" and aviso[56195]["inicio"].startswith("2026-10-29") and len(QUINTA) == 2777, len(QUINTA)
NE_SECO = ["MA", "PI", "CE", "RN", "PB", "PE"]
estados = [
    {"id": "serra", "ini": em("f1", "amanheceu"), "fim": ini("f2") + .3, "ufs": ["SC"], "cor": FRIO, "alfa": .4},
    {"id": "sul", "ini": em("f2", "massa"), "fim": FUMACA, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .4},
    {"id": "nchuva", "ini": CHOVE, "fim": ini("f4") + .3, "ufs": ["AM", "AC", "RO"], "cor": AZUL, "alfa": .3},
    {"id": "sechuva", "ini": em("f4", "Espírito"), "fim": ini("f5") + .3, "ufs": ["ES", "MG"], "cor": AZUL, "alfa": .45},
    {"id": "spseco", "ini": em("f4", "Paulo"), "fim": ini("f5") + .3, "ufs": ["SP"], "cor": LAR, "alfa": .35},
    {"id": "mg", "ini": ini("f5"), "fim": TOT5 - .9, "ufs": ["MG"], "cor": LAR, "alfa": .6},
    {"id": "hoje", "ini": TOT5 - 1.0, "fim": ini("f6") + .3, "ufs": HOJE, "cor": LAR, "alfa": .5},
    {"id": "seco", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": NE_SECO, "cor": LAR, "alfa": .35},
    {"id": "calor", "ini": em("f6", "Alagoas"), "fim": ini("f7") + .3, "ufs": ["AL", "SE", "BA"], "cor": VERM, "alfa": .45},
    {"id": "terca", "ini": em("f7", "Bahia"), "fim": ini("f8") + .3, "ufs": ["BA", "MG"], "cor": AZUL, "alfa": .35},
    {"id": "frio", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["RS", "SC"], "cor": FRIO, "alfa": .4},
    {"id": "quinta", "ini": em("f9", "forte"), "fim": ini("f10") + .3, "ufs": ["MG", "RJ", "ES"], "cor": AZUL, "alfa": .45},
    {"id": "volta", "ini": em("f9", "volta"), "fim": ini("f10") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .25},
]

pinos = [
    {"nome": "Morro da Igreja (SC)", "sub": "2,9 °C hoje cedo", "lon": -49.37, "lat": -28.12, "ini": em("f1", "Morro"), "fim": ini("f2"), "h": 160},
    {"nome": "São Joaquim (SC)", "sub": "3,9 °C hoje cedo", "lon": -49.93, "lat": -28.29, "ini": em("f2", "Joaquim"), "fim": FUMACA, "h": 160},
    {"nome": "Manaus (AM)", "sub": "pancadas hoje", "lon": -60.02, "lat": -3.10, "ini": em("f3", "Amazonas"), "fim": ini("f4"), "h": 140},
    {"nome": "Rio Branco (AC)", "sub": "chuva hoje", "lon": -67.81, "lat": -9.97, "ini": em("f3", "Acre"), "fim": ini("f4"), "h": 120},
    {"nome": "Alagoas, Sergipe e Bahia", "sub": "35 a 40 °C hoje", "lon": -37.6, "lat": -10.6, "ini": em("f6", "Alagoas"), "fim": ini("f7"), "h": 160},
    {"nome": "Feira de Santana (BA)", "sub": "chuva na terça (previsão)", "lon": -38.97, "lat": -12.27, "ini": em("f7", "Feira"), "fim": ini("f8"), "h": 120},
    {"nome": "Juazeiro (BA)", "sub": "chuva na terça (previsão)", "lon": -40.50, "lat": -9.41, "ini": em("f7", "Juazeiro"), "fim": ini("f8"), "h": 200},
    {"nome": "São Joaquim (SC)", "sub": "abaixo de 0 °C na terça (previsão)", "lon": -49.93, "lat": -28.29, "ini": em("f8", "zero"), "fim": GEAR, "h": 160},
    {"nome": "Rio de Janeiro (RJ)", "sub": "chuva forte na quinta (previsão)", "lon": -43.20, "lat": -22.91, "ini": em("f9", "Rio"), "fim": ini("f10"), "h": 160},
    {"nome": f"{VTOPO} mm até 9/11", "sub": f"maior soma prevista ({TOPO['uf']}) · Open-Meteo", "lon": TOPO["p"][0], "lat": TOPO["p"][1],
     "ini": em("f10", "100"), "fim": ini("f11"), "h": 220},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)   # número dito logo no começo da fala: o contador começa com a fala
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
H = em("f1", "2,9") - .4   # o hero (data grande) fica até 0,4 s antes do "2,9" (a capa já mostra 2,9 °C: contador curto)
TOTAL = TOT5 - 1.1   # o painel do total do país entra 1,1 s antes do número
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#3c96ff;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:96px">FRIO NO SUL</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">e calor de 40 °C no Nordeste</div>'}]
paineis = [
    {"ini": H, "fim": ini("f2"), "k": "MÍNIMA DE HOJE CEDO",
     "contador": conta(2.9, "f1", "2,9", "#96d2ff", "°C NO MORRO DA IGREJA (SC)", dec=1, de=4, lead=.3),
     "l": "Urubici, na serra catarinense", "borda": "rgba(150,210,255,.85)"},
    {"ini": ini("f2"), "fim": FUMACA - .1, "k": "MÍNIMA DE HOJE CEDO",
     "contador": conta(3.9, "f2", "3,9", "#96d2ff", "°C EM SÃO JOAQUIM (SC)", dec=1, de=15),
     "l": "massa de ar frio no Sul", "borda": "rgba(150,210,255,.85)"},
    {"ini": CHOVE - .2, "fim": ini("f4"), "k": "HOJE NA AMAZÔNIA",
     "itens": [{"t": CHOVE - .2, "txt": "🔥 fumaça de queimadas"},
               {"t": em("f3", "Amazonas"), "txt": "🌧️ chuva no Amazonas"},
               {"t": em("f3", "Acre"), "txt": "🌧️ no Acre e em Rondônia"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE NO SUDESTE",
     "itens": [{"t": em("f4", "Espírito"), "txt": "🌧️ chuva no ES e no leste de MG"},
               {"t": em("f4", "Paulo"), "txt": "☀️ São Paulo seco"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": TOTAL, "k": "AVISO DE TEMPESTADE · HOJE",
     "contador": conta(608, "f5", "608", "#ff8c1a", "CIDADES DE MINAS"),
     "l": "INMET", "borda": "rgba(255,140,26,.8)"},
    {"ini": TOTAL, "fim": ini("f6"), "k": "AVISO DE TEMPESTADE · HOJE",
     "contador": conta(1608, "f5", "1.608", "#ff8c1a", "CIDADES NO PAÍS"),
     "l": "MG, BA, GO, TO, ES e mais · INMET", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "MÁXIMA PREVISTA HOJE",
     "contador": conta(40, "f6", "40", "#ff2a1f", "°C ENTRE AL, SE E BA"),
     "l": "Nordeste seco · baixa umidade em 355 cidades (INMET)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "TERÇA, 27/10 (PREVISÃO)",
     "itens": [{"t": em("f7", "Bahia"), "txt": "🌧️ chuva volta à Bahia"},
               {"t": em("f7", "Feira"), "txt": "📍 de Feira de Santana a Juazeiro"},
               {"t": em("f7", "norte"), "txt": "🌧️ e no norte de Minas"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f8"), "fim": GEAR - .1, "k": "TERÇA, 27/10 (PREVISÃO)",
     "itens": [{"t": em("f8", "zero"), "txt": "🌡️ abaixo de 0 °C na serra"},
               {"t": em("f8", "geada"), "txt": "❄️ geada em São Joaquim"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "QUINTA, 29/10 (PREVISÃO)",
     "itens": [{"t": em("f9", "forte"), "txt": "⛈️ chuva forte em MG, RJ e ES"},
               {"t": em("f9", "volta"), "txt": "🌧️ a chuva volta ao Sul"}],
     "l": "INMET: aviso de tempestade em 2.777 cidades na quinta", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "CHUVA ATÉ 9/11 (PREVISÃO)",
     "contador": conta(100, "f10", "100", "#5ec8ff", "MM OU MAIS"),
     "l": f"{len(ACIMA)} pontos do Sul, Sudeste e Centro-Oeste acima de 100 mm (Open-Meteo)", "borda": "rgba(60,150,255,.7)"},
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
    {"ini": CAPA, "fim": ini("f3"), "html": f"<b>{MET}</b> · mínimas de hoje cedo"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE} · <b>{MET}</b> · foto da fumaça: ilustração"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INMET</b>, aviso de tempestade para 26/10 (1.608 municípios)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · <b>INMET</b>: baixa umidade em 355 cidades"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · previsão · foto da geada: ilustração"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · previsão · <b>INMET</b>, aviso para 29/10 (2.777 municípios)"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": f"<b>Open-Meteo</b>, chuva prevista somada de 26/10 a 9/11 · <b>{MET}</b>"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "chover": "#5ec8ff", "chuvas": "#5ec8ff", "tempestade": "#ff8c1a", "alerta": "#ff8c1a",
         "seco": "#ff8c1a", "frio": "#96d2ff", "geada": "#96d2ff", "milimetros": "#5ec8ff", "zero": "#96d2ff",
         "graus": "#ff2a1f", "maxima": "#ff2a1f", "fumaca": "#ff8c1a", "queimadas": "#ff8c1a",
         "forte": "#ff8c1a", "aviso": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "santa", "catarina", "sao", "paulo", "minas", "rio", "amazonas", "rondonia", "nordeste", "sudeste", "morro", "igreja",
         "joaquim", "serra", "amazonia", "acre", "espirito", "alagoas", "sergipe", "bahia", "feira", "santana", "juazeiro",
         "centrooeste", "pais", "inemaclub", "onde"}
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
     "marca": "INEMA · CLIMA DO DIA", "selo": DATA[:5] + " · INMET · NOAA",
     "camera": camera, "sat": SAT, "colunas": colunas, "telas": telas, "estados": estados, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"colunas {len(col)} ({len(ACIMA)} ≥ 100 mm, topo {VTOPO} mm em {TOPO['uf']} {TOPO['p']})")
