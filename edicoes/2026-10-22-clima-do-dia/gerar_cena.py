#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 22/10/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS),
dos avisos do INMET e da chuva prevista de quinta a domingo nas cidades do Sul (Open-Meteo, pesquisa/bruto/openmeteo_sul_4d.json,
gravado por coleta_sul.py).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, até 200 mm no Sul e granizo), infravermelho do GOES-19 com câmera
inclinada sobre o Sul e o Sudeste, avisos de tempestade do INMET (645 em SP → 2.762 no país; laranja em 835 no sábado),
chuva forte no AM e AC e Nordeste seco, 40 °C em Teresina, pinos da chuva forte de sexta e foto do granizo (ilustração),
colunas 3D da chuva prevista até domingo (Guarapuava, Chapecó, Joinville...), domingo de eleição com chuva em SP,
frio de terça (11 °C em SP) e foto da geada (ilustração).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "22/10/2026"
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
SUL1 = {"lon": -51.0, "lat": -25.5, "zoom": 4.8}       # f1: granizo no PR e SC, 200 mm no Sul
CHUVA = {"lon": -50.0, "lat": -25.0, "zoom": 4.6}      # f2: chuva do Paraguai/Argentina sobre Sul e Sudeste (IR)
SP = {"lon": -48.5, "lat": -22.5, "zoom": 5.4}         # f3: aviso em todas as cidades de SP
PAIS = {"lon": -51.0, "lat": -17.0, "zoom": 3.9}       # f3: total do país
NORTE = {"lon": -60.0, "lat": -7.0, "zoom": 4.0}       # f4: oeste do AM e AC
NE = {"lon": -42.0, "lat": -8.0, "zoom": 4.2}          # f4: Nordeste seco
TER = {"lon": -43.5, "lat": -6.5, "zoom": 5.0}         # f5: 40 °C em Teresina
SEXTA = {"lon": -51.0, "lat": -26.8, "zoom": 5.7}      # f6: Curitiba, Joinville, Chapecó, Passo Fundo
SAB = {"lon": -50.5, "lat": -25.8, "zoom": 5.0}        # f7: aviso laranja de sábado
COL = {"lon": -51.0, "lat": -26.4, "zoom": 6.0}        # f8: colunas 3D até domingo
DOM = {"lon": -47.0, "lat": -23.7, "zoom": 6.2}        # f9: Grande SP e litoral
FRIA = {"lon": -48.5, "lat": -26.0, "zoom": 5.1}       # f10: SP 11 °C e geada na Serra Catarinense
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
GRANIZO1 = em("f1", "granizo")
TOT3 = em("f3", "2.762")
camera = [
    K(0, BR), K(CAPA, BR), K(GRANIZO1 + .4, SUL1, 0, 0),
    K(fim("f1") - .2, {**SUL1, "zoom": 4.9}, 0, 0),
    K(ini("f2") + 1.3, CHUVA, 45, -18), K(fim("f2") - .2, {**CHUVA, "lon": -48.5, "zoom": 4.7}, 48, -4),
    K(ini("f3") + 1.0, SP, 0, 0), K(TOT3 - 1.2, {**SP, "zoom": 5.5}, 0, 0), K(TOT3 + .4, PAIS, 0, 0), K(fim("f3") - .2, {**PAIS, "zoom": 3.95}, 0, 0),
    K(ini("f4") + 1.0, NORTE, 0, 0), K(em("f4", "Nordeste") + .4, NE, 0, 0), K(fim("f4") - .2, {**NE, "zoom": 4.25}, 0, 0),
    K(ini("f5") + 1.2, TER, 0, 0), K(fim("f5") - .2, {**TER, "zoom": 5.1}, 4, 0),
    K(ini("f6") + 1.2, SEXTA, 30, -10), K(fim("f6") - .2, {**SEXTA, "zoom": 5.8}, 34, 6),
    K(ini("f7") + 1.0, SAB, 0, 0), K(fim("f7") - .2, {**SAB, "zoom": 5.1}, 4, 0),
    K(ini("f8") + 1.0, COL, 55, -20), K(em("f8", "Chapecó"), {**COL, "zoom": 6.05}, 56, 0), K(fim("f8") - .2, {**COL, "zoom": 6.1}, 56, 18),
    K(ini("f9") + 1.0, DOM, 0, 0), K(fim("f9") - .2, {**DOM, "zoom": 6.3}, 4, 0),
    K(ini("f10") + 1.0, FRIA, 30, -10), K(fim("f10") - .2, {**FRIA, "zoom": 5.2}, 34, 6),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na chuva do Sul e Sudeste (f2)
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
              "ini": ini("f2") - .3, "fim": ini("f3") + .4, "dur": fim("f2") - ini("f2") + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])
assert len(BONS) >= 20, f"poucos quadros bons de infravermelho: {len(BONS)}"

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de quinta a domingo (22 a 25/10), Open-Meteo
S4 = json.loads((B / "openmeteo_sul_4d.json").read_text())
assert S4["dias"][0] == "2026-10-22" and S4["dias"][-1] == "2026-10-25", S4["dias"]
CID = {k: v for k, v in S4["cidades"].items() if k != "São Paulo"}
MM = {k: v["soma"] for k, v in CID.items()}
assert 148 <= MM["Guarapuava"] <= 160 and MM["Chapecó"] > 100 and MM["Joinville"] > 100, MM   # a fala diz "cento e cinquenta" e "mais de cem"
col = [{"id": i, "p": [v["lon"], v["lat"]], "v": MM[c], "cor": [60, 150, 255] if MM[c] >= 100 else [120, 190, 255]} for i, (c, v) in enumerate(CID.items())]
ordem = {c["id"]: i * .15 for i, c in enumerate(col)}
colunas = [{"id": "chuva3d", "ini": ini("f8") + .2, "fim": ini("f9") + .2, "dados": col, "raio": 19000, "escala": 2400, "ordem": ordem, "varredura": 1}]
fmm = lambda v: f"{v:.0f}"
P = lambda c: (CID[c]["lon"], CID[c]["lat"])

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, granizo e geada
GRANIZO = em("f6", "granizo")
GEAR = em("f10", "gear")
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": GRANIZO - .1, "fim": ini("f7") + .3, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/geada.png", "ini": GEAR - .1, "fim": ini("f11") + .3, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_geo = lambda g, minimo=5: sorted({UF[c[:2]] for c in g if sum(x[:2] == c[:2] for x in g) >= minimo})
TEMP_HOJE = geo(56140) | geo(56141)   # tempestade amarela 22/10: 2.762 (SP 645, MG 527, RS 477, PR 399, SC 279...)
assert all(aviso[i]["descricao"] == "Tempestade" and aviso[i]["inicio"].startswith("2026-10-22") for i in (56140, 56141))
assert len(TEMP_HOJE) == 2762 and sum(c[:2] == "35" for c in TEMP_HOJE) == 645, len(TEMP_HOJE)
HOJE = ufs_geo(TEMP_HOJE)
SEX = ufs_geo(geo(56144))    # tempestade laranja sexta 23/10: 590 (PR 277, RS 184, SC 109, MS 19, SP 1)
assert len(geo(56144)) == 590 and aviso[56144]["severidade"] == "Perigo" and aviso[56144]["inicio"].startswith("2026-10-23")
SABADO = ufs_geo(geo(56154), 50)  # só UF com 50+ cidades (MG 7 e RJ 8 não pintam o estado inteiro); tempestade laranja sábado 24/10: 835 (PR 323, SP 196, SC 192, RS 109, RJ 8, MG 7)
assert len(geo(56154)) == 835 and aviso[56154]["severidade"] == "Perigo" and aviso[56154]["inicio"].startswith("2026-10-24")
assert len(geo(56156)) == 684 and aviso[56156]["descricao"] == "Baixa Umidade"   # baixa umidade 22 e 23/10: 684 cidades
NORDESTE = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
estados = [
    {"id": "gran", "ini": GRANIZO1, "fim": ini("f2") + .3, "ufs": ["PR", "SC"], "cor": AZUL, "alfa": .4},
    {"id": "chuva", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["RS", "SC", "PR", "SP", "MG", "RJ"], "cor": AZUL, "alfa": .28},
    {"id": "sp", "ini": ini("f3"), "fim": TOT3 - .9, "ufs": ["SP"], "cor": LAR, "alfa": .6},
    {"id": "hoje", "ini": TOT3 - 1.0, "fim": ini("f4") + .3, "ufs": HOJE, "cor": LAR, "alfa": .5},
    {"id": "norte", "ini": ini("f4"), "fim": em("f4", "Nordeste") + .3, "ufs": ["AM", "AC"], "cor": AZUL, "alfa": .45},
    {"id": "seco", "ini": em("f4", "Nordeste"), "fim": ini("f5") + .3, "ufs": NORDESTE, "cor": LAR, "alfa": .4},
    {"id": "calor", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["PI"], "cor": VERM, "alfa": .45},
    {"id": "sexta", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": SEX, "cor": [255, 90, 20], "alfa": .45},
    {"id": "sabado", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": SABADO, "cor": [255, 90, 20], "alfa": .5},
    {"id": "dom", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["SP"], "cor": AZUL, "alfa": .45},
    {"id": "frio", "ini": ini("f10"), "fim": ini("f11") + .3, "ufs": ["SP", "PR", "SC"], "cor": FRIO, "alfa": .4},
]

pinos = [
    {"nome": "Teresina (PI)", "sub": "até 40 °C hoje", "lon": -42.80, "lat": -5.09, "ini": em("f5", "Teresina"), "fim": ini("f6"), "h": 160},
    {"nome": "Curitiba (PR)", "sub": "chuva forte na sexta", "lon": -49.27, "lat": -25.43, "ini": em("f6", "Curitiba"), "fim": GRANIZO, "h": 200},
    {"nome": "Joinville (SC)", "sub": "chuva forte na sexta", "lon": -48.85, "lat": -26.30, "ini": em("f6", "Joinville"), "fim": GRANIZO, "h": 90},
    {"nome": "Chapecó (SC)", "sub": "chuva forte na sexta", "lon": -52.62, "lat": -27.10, "ini": em("f6", "Chapecó"), "fim": GRANIZO, "h": 160},
    {"nome": "Passo Fundo (RS)", "sub": "chuva forte na sexta", "lon": -52.41, "lat": -28.26, "ini": em("f6", "Passo"), "fim": GRANIZO, "h": 60},
    {"nome": "Guarapuava (PR)", "sub": "mais de 150 mm até domingo (previsão)", "lon": P("Guarapuava")[0], "lat": P("Guarapuava")[1],
     "ini": em("f8", "Guarapuava"), "fim": ini("f9"), "h": 220},
    {"nome": "Chapecó (SC)", "sub": f"{fmm(MM['Chapecó'])} mm até domingo (previsão)", "lon": P("Chapecó")[0], "lat": P("Chapecó")[1],
     "ini": em("f8", "Chapecó"), "fim": ini("f9"), "h": 160},
    {"nome": "Joinville (SC)", "sub": f"{fmm(MM['Joinville'])} mm até domingo (previsão)", "lon": P("Joinville")[0], "lat": P("Joinville")[1],
     "ini": em("f8", "Joinville"), "fim": ini("f9"), "h": 120},
    {"nome": "Grande São Paulo", "sub": "chuva forte possível no domingo", "lon": -46.63, "lat": -23.55, "ini": em("f9", "Grande"), "fim": ini("f10"), "h": 180},
    {"nome": "Litoral paulista", "sub": "chuva forte possível no domingo", "lon": -46.33, "lat": -23.96, "ini": em("f9", "litoral"), "fim": ini("f10"), "h": 60},
    {"nome": "São Paulo", "sub": "11 °C na terça de manhã", "lon": -46.63, "lat": -23.55, "ini": em("f10", "Paulo"), "fim": GEAR, "h": 160},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)   # número dito logo no começo da fala: o contador começa com a fala
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
H = em("f1", "200") - 1.25   # o hero (data grande) sai 1,25 s antes do "200" (o contador chega no número)
TOTAL = TOT3 - 1.1   # o painel do total do país entra 1,1 s antes do número
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:104px">GRANIZO</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">no Paraná e em Santa Catarina</div>'}]
paineis = [
    {"ini": H + .1, "fim": ini("f2"), "k": "ATÉ DOMINGO (PREVISÃO)",
     "contador": conta(200, "f1", "200", "#5ec8ff", "MM NO SUL"),
     "l": "PR, SC e norte do RS · granizo já caiu hoje", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "DE ONDE VEM A CHUVA",
     "itens": [{"t": em("f2", "Paraguai"), "txt": "⛈️ Paraguai e Argentina"},
               {"t": em("f2", "cobre"), "txt": "➡️ Sul, SP, sul de MG e Rio"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": TOTAL, "k": "AVISO DE TEMPESTADE · HOJE",
     "contador": conta(645, "f3", "645", "#ff8c1a", "CIDADES DE SÃO PAULO"),
     "l": "todas as cidades do estado · INMET", "borda": "rgba(255,140,26,.8)"},
    {"ini": TOTAL, "fim": ini("f4"), "k": "AVISO DE TEMPESTADE · HOJE",
     "contador": conta(2762, "f3", "2.762", "#ff8c1a", "CIDADES NO PAÍS"),
     "l": "do Sul ao Norte · INMET", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE NO NORTE E NO NORDESTE",
     "itens": [{"t": em("f4", "Amazonas"), "txt": "🌧️ chuva forte no AM e no AC"},
               {"t": em("f4", "Nordeste"), "txt": "☀️ Nordeste quase todo seco"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "MÁXIMA PREVISTA HOJE",
     "contador": conta(40, "f5", "40", "#ff2a1f", "°C EM TERESINA"),
     "l": "sexta: mais de 42 °C no Piauí", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f6"), "fim": GRANIZO - .1, "k": "SEXTA, 23/10 · CHUVA FORTE",
     "itens": [{"t": em("f6", "Curitiba"), "txt": "⛈️ Curitiba"},
               {"t": em("f6", "Joinville"), "txt": "⛈️ Joinville"},
               {"t": em("f6", "Chapecó"), "txt": "⛈️ Chapecó"},
               {"t": em("f6", "Passo"), "txt": "⛈️ Passo Fundo"}],
     "borda": "rgba(255,90,20,.85)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SÁBADO, 24/10 · AVISO LARANJA",
     "contador": conta(835, "f7", "835", "#ff5a14", "CIDADES"),
     "l": "pontos com mais de 100 mm · INMET", "borda": "rgba(255,90,20,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA ATÉ DOMINGO (PREVISÃO)",
     "contador": conta(150, "f8", "150", "#5ec8ff", "MM EM GUARAPUAVA"),
     "l": f"Chapecó {fmm(MM['Chapecó'])} mm · Joinville {fmm(MM['Joinville'])} mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "DOMINGO, 25/10 · ELEIÇÃO",
     "itens": [{"t": em("f9", "Grande"), "txt": "⛈️ chuva forte na Grande SP"},
               {"t": em("f9", "litoral"), "txt": "🌊 e no litoral paulista"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "TERÇA, 27/10 (PREVISÃO)",
     "itens": [{"t": em("f10", "11"), "txt": "🌡️ São Paulo com 11 °C de manhã"},
               {"t": GEAR, "txt": "❄️ geada na Serra Catarinense"}],
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
        assert a["ini"] - .01 <= c["ini"] and c["ini"] + c["dur"] <= a["fim"], ("contador fora do painel", a["k"])

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE} · <b>{MET}</b>"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INMET</b>, aviso de tempestade para 22/10 (2.762 municípios)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · <b>INMET</b>: baixa umidade em 684 cidades"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · previsão · foto do granizo: ilustração"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>INMET</b>, aviso laranja de tempestade para 24/10 (835 municípios) · <b>{MET}</b>"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>Open-Meteo</b>, chuva prevista de 22 a 25/10"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": f"<b>{MET}</b> · previsão · foto da geada: ilustração"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "chover": "#5ec8ff", "chuvas": "#5ec8ff", "tempestade": "#ff8c1a", "alerta": "#ff8c1a",
         "seco": "#ff8c1a", "frio": "#96d2ff", "esfria": "#96d2ff", "geada": "#96d2ff", "gear": "#96d2ff", "milimetros": "#5ec8ff",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "quente": "#ff2a1f", "granizo": "#96d2ff", "trovoada": "#ff8c1a", "laranja": "#ff8c1a",
         "forte": "#ff8c1a", "aviso": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "parana", "santa", "catarina", "paraguai", "argentina", "sao", "paulo", "minas", "rio", "amazonas", "acre", "nordeste",
         "teresina", "piaui", "curitiba", "joinville", "chapeco", "passo", "fundo", "guarapuava", "grande", "litoral", "paulista",
         "serra", "catarinense", "pais", "inemaclub", "onde"}
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
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · colunas {MM}")
