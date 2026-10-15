#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 15/10/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS)
e dos avisos do INMET (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, -3 °C na serra), infravermelho do GOES-19 na frente fria,
alerta laranja de SP e o total do Brasil, frio por dia (sábado, domingo, segunda), foto da geada no pomar (ilustração).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "15/10/2026"
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
SERRA = {"lon": -50.0, "lat": -27.9, "zoom": 6.3}     # f1/f9: Serra Catarinense
SULLIT = {"lon": -49.5, "lat": -27.5, "zoom": 4.7}    # f2: frente fria e baixa pressão no litoral
SPE = {"lon": -48.6, "lat": -22.3, "zoom": 5.3}       # f3: estado de São Paulo
BRA = {"lon": -50.0, "lat": -17.5, "zoom": 3.95}      # f3: o Brasil do alerta
CO = {"lon": -50.5, "lat": -18.5, "zoom": 4.4}        # f4: MT, GO, MG e SP
PRRIB = {"lon": -48.8, "lat": -24.9, "zoom": 6.0}     # f4: Vale do Ribeira e leste do PR
NE = {"lon": -43.0, "lat": -9.0, "zoom": 5.3}         # f5: Nordeste seco, PI e BA
SE = {"lon": -44.3, "lat": -21.8, "zoom": 5.3}        # f6: SP, RJ e ES
CSUL7 = {"lon": -51.5, "lat": -24.3, "zoom": 4.75}    # f7: SC, Campo Grande e SP
PALMAS = {"lon": -51.6, "lat": -26.8, "zoom": 6.1}    # f8: Campos de Palmas
CSUL = {"lon": -50.0, "lat": -21.0, "zoom": 4.3}      # f8: ar frio até Goiânia e Brasília
SUL = {"lon": -51.5, "lat": -26.0, "zoom": 4.7}       # f10: próxima massa fria
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
SER = em("f1", "Serra")
BRASIL = em("f3", "Brasil")
TARDE = em("f4", "tarde")
GOI = em("f8", "Goiânia")
camera = [
    K(0, BR), K(CAPA, BR), K(SER - .3, {**BR, "lon": -51.5, "lat": -22.0, "zoom": 4.4}, 10, 0),
    K(SER + 1.3, SERRA, 45, -18), K(fim("f1") - .2, {**SERRA, "zoom": 6.4}, 50, 0),
    K(ini("f2") + 1.0, SULLIT, 0, 0), K(fim("f2") - .2, {**SULLIT, "lon": -49.0}, 0, 0),
    K(ini("f3") + 1.0, SPE, 10, 0), K(BRASIL - .2, {**SPE, "zoom": 5.2}, 10, 0), K(BRASIL + 1.2, BRA, 0, 0), K(fim("f3") - .2, {**BRA, "zoom": 3.9}, 0, 0),
    K(ini("f4") + 1.0, CO, 8, 0), K(TARDE - .1, {**CO, "lon": -50.0}, 8, 0), K(TARDE + 1.2, PRRIB, 25, -6), K(fim("f4") - .2, {**PRRIB, "lon": -48.6}, 28, 4),
    K(ini("f5") + 1.0, NE, 6, -2), K(fim("f5") - .2, {**NE, "lon": -43.2}, 8, 2),
    K(ini("f6") + 1.0, SE, 22, -6), K(fim("f6") - .2, {**SE, "lon": -44.0}, 26, 4),
    K(ini("f7") + 1.0, CSUL7, 15, -4), K(fim("f7") - .2, {**CSUL7, "zoom": 4.85}, 18, 4),
    K(ini("f8") + 1.0, PALMAS, 35, -8), K(GOI - .2, {**PALMAS, "zoom": 6.2}, 38, 4), K(GOI + 1.2, CSUL, 5, 0), K(fim("f8") - .2, {**CSUL, "zoom": 4.35}, 5, 2),
    K(ini("f9") + 1.0, SERRA, 45, -10), K(fim("f9") - .2, {**SERRA, "zoom": 6.5}, 50, 8),
    K(ini("f10") + 1.0, SUL, 10, 0), K(fim("f10") - .2, {**SUL, "zoom": 4.8}, 12, 2),
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


SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": ini("f2") - .3, "fim": ini("f3") + .4, "dur": fim("f2") - ini("f2") + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e geada no pomar
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/geada.png", "ini": em("f9", "geada") - .1, "fim": ini("f10") + .3, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
HOJE = ufs_av(56071)     # tempestade laranja 15/10: 2.163 (MG 815, SP 645, GO 246, PR 104, MT 103, RJ 92, ES 78, MS 41)
assert len(geo(56071)) == 2163, len(geo(56071))
assert sum(c[:2] == "35" for c in geo(56071)) == 645
assert aviso[56071]["severidade"] == "Perigo" and aviso[56071]["descricao"] == "Tempestade"
assert len(geo(56079)) == 816 and aviso[56079]["descricao"] == "Baixa Umidade"   # baixa umidade 15/10: 816 (PI 187)
NORDESTE = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
estados = [
    {"id": "serra", "ini": SER - .2, "fim": ini("f2") + .3, "ufs": ["SC"], "cor": FRIO, "alfa": .4},
    {"id": "frente", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .3},
    {"id": "sp", "ini": ini("f3"), "fim": BRASIL + .3, "ufs": ["SP"], "cor": LAR, "alfa": .6},
    {"id": "hoje", "ini": BRASIL, "fim": ini("f4") + .3, "ufs": HOJE, "cor": LAR, "alfa": .55},
    {"id": "chuva", "ini": ini("f4"), "fim": TARDE + .3, "ufs": ["MT", "GO", "MG", "SP"], "cor": AZUL, "alfa": .4},
    {"id": "tarde", "ini": TARDE, "fim": ini("f5") + .3, "ufs": ["PR", "SP"], "cor": AZUL, "alfa": .4},
    {"id": "seco", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": NORDESTE, "cor": [255, 90, 20], "alfa": .3},
    {"id": "quente", "ini": em("f5", "Piauí") - .2, "fim": ini("f6") + .3, "ufs": ["PI", "BA"], "cor": VERM, "alfa": .45},
    {"id": "amanha", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["SP", "RJ", "ES"], "cor": AZUL, "alfa": .45},
    {"id": "sab", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .4},
    {"id": "sab2", "ini": em("f7", "Campo") - .2, "fim": ini("f8") + .3, "ufs": ["MS", "SP"], "cor": FRIO, "alfa": .3},
    {"id": "dom", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .45},
    {"id": "dom2", "ini": GOI - .2, "fim": ini("f9") + .3, "ufs": ["MS", "SP", "MG", "GO", "DF"], "cor": FRIO, "alfa": .3},
    {"id": "seg", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["SC", "RS"], "cor": FRIO, "alfa": .45},
    {"id": "prox", "ini": ini("f10"), "fim": ini("f11") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .4},
]

pinos = [
    {"nome": "Serra Catarinense", "sub": "até -3 °C na segunda", "lon": -49.93, "lat": -28.29, "ini": SER, "fim": ini("f2"), "h": 200},
    {"nome": "Leste do Paraná", "sub": "chuva à tarde", "lon": -49.27, "lat": -25.43, "ini": em("f4", "leste"), "fim": ini("f5"), "h": 170},
    {"nome": "Vale do Ribeira", "sub": "chuva mais intensa à tarde", "lon": -47.84, "lat": -24.49, "ini": em("f4", "Ribeira"), "fim": ini("f5"), "h": 220},
    {"nome": "Teresina (PI)", "sub": "38,7 °C previstos hoje", "lon": -42.80, "lat": -5.09, "ini": em("f5", "Piauí"), "fim": ini("f6"), "h": 170},
    {"nome": "Bahia", "sub": "35 a 40 °C", "lon": -42.5, "lat": -12.0, "ini": em("f5", "Bahia"), "fim": ini("f6"), "h": 150},
    {"nome": "Grande São Paulo", "sub": "rajadas de 50 a 60 km/h", "lon": -46.63, "lat": -23.55, "ini": em("f6", "Paulo"), "fim": ini("f7"), "h": 320},
    {"nome": "Rio de Janeiro", "sub": "chuva forte", "lon": -43.20, "lat": -22.90, "ini": em("f6", "Rio"), "fim": ini("f7"), "h": 130},
    {"nome": "Espírito Santo", "sub": "chuva forte", "lon": -40.34, "lat": -20.32, "ini": em("f6", "Espírito"), "fim": ini("f7"), "h": 230},
    {"nome": "Santa Catarina", "sub": "5 a 8 °C no sábado", "lon": -50.33, "lat": -27.82, "ini": em("f7", "Santa"), "fim": ini("f8"), "h": 170},
    {"nome": "Campo Grande", "sub": "esfria", "lon": -54.62, "lat": -20.47, "ini": em("f7", "Campo"), "fim": ini("f8"), "h": 150},
    {"nome": "São Paulo", "sub": "esfria", "lon": -46.63, "lat": -23.55, "ini": em("f7", "Paulo"), "fim": ini("f8"), "h": 150},
    {"nome": "Campos de Palmas (PR)", "sub": "0 a 3 °C e geada no domingo", "lon": -51.99, "lat": -26.48, "ini": em("f8", "Palmas") - .2, "fim": GOI, "h": 180},
    {"nome": "Goiânia", "sub": "ar frio", "lon": -49.25, "lat": -16.68, "ini": GOI, "fim": ini("f9"), "h": 150},
    {"nome": "Brasília", "sub": "ar frio", "lon": -47.88, "lat": -15.79, "ini": em("f8", "Brasília"), "fim": ini("f9"), "h": 230},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
conta = lambda ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0: {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra) - lead, "dur": lead, "cor": cor, "unid": unid}
H = SER - .1   # o hero (data grande) fica até a câmera chegar à serra
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:112px">-3 °C</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">na Serra Catarinense na segunda</div>'}]
D_BR = max(BRASIL + .4, em("f3", "2.163") - LEAD)   # o total do Brasil sobe de 645 a 2.163 até a palavra
paineis = [
    {"ini": H + .1, "fim": ini("f2"), "k": "SERRA CATARINENSE · SEGUNDA (PREVISÃO)",
     "contador": conta(-3, "f1", "3", "#96d2ff", "°C", de=15, lead=em("f1", "3") - SER),   # a temperatura cai até o -3
     "l": "2 a 3 graus abaixo de zero · geada", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "POR QUE VAI ESFRIAR",
     "itens": [{"t": em("f2", "frente"), "txt": "🌀 uma frente fria avança"},
               {"t": em("f2", "baixa"), "txt": "🌊 baixa pressão no litoral"},
               {"t": em("f2", "vento"), "txt": "🌬️ vento frio do sul"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f3"), "fim": BRASIL, "k": "ALERTA LARANJA DE TEMPESTADE · SP",
     "contador": conta(645, "f3", "645", "#ff8c1a", "CIDADES EM SP"),
     "l": "todas as cidades do estado · INMET, 15/10", "borda": "rgba(255,140,26,.7)"},
    {"ini": BRASIL, "fim": ini("f4"), "k": "BRASIL INTEIRO · HOJE",
     "contador": {"de": 645, "ate": 2163, "dec": 0, "ini": D_BR, "dur": max(.4, em("f3", "2.163") - D_BR), "cor": "#ff8c1a", "unid": "CIDADES NO BRASIL"},
     "l": "MG 815 · SP 645 · GO 246 · PR 104 · MT 103 · RJ 92 · ES 78", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE · QUINTA, 15/10 · CHUVA FORTE",
     "itens": [{"t": em("f4", "Mato"), "txt": "⛈️ Mato Grosso e Goiás"},
               {"t": em("f4", "Minas"), "txt": "⛈️ Minas e São Paulo"},
               {"t": TARDE, "txt": "🌧️ à tarde: Vale do Ribeira e leste do PR"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "NORDESTE SECO · CALOR",
     "contador": conta(40, "f5", "40", "#ff2a1f", "°C"),
     "l": "35 a 40 °C no PI e na BA · baixa umidade em 816 cidades (INMET)", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "AMANHÃ · SEXTA, 16/10 (PREVISÃO)",
     "contador": conta(60, "f6", "60", "#5ec8ff", "KM/H"),
     "l": "rajadas na Grande SP · chuva forte em SP, RJ e ES", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SÁBADO, 17/10 · FRIO (PREVISÃO)",
     "contador": conta(5, "f7", "5", "#96d2ff", "°C", de=15, lead=em("f7", "5") - ini("f7") - .2),
     "l": "de 5 a 8 °C em SC · esfria em Campo Grande e São Paulo", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "DOMINGO, 18/10 · GEADA (PREVISÃO)",
     "contador": conta(0, "f8", "0", "#96d2ff", "°C", de=8, lead=em("f8", "0") - ini("f8") - .2),
     "l": "0 a 3 °C nos Campos de Palmas · ar frio até Goiânia e Brasília", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "SEGUNDA E TERÇA · GEADA (PREVISÃO)",
     "itens": [{"t": em("f9", "geada"), "txt": "❄️ até -3 °C na Serra Catarinense"},
               {"t": em("f9", "maçã"), "txt": "🍎 maçã na fase mais crítica"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "PRÓXIMO FIM DE SEMANA (PREVISÃO)",
     "itens": [{"t": em("f10", "massa"), "txt": "🌬️ nova massa de ar frio no Sul, 24/10"},
               {"t": em("f10", "fim"), "txt": "❄️ pode ter geada na serra no dia 25"}],
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
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>{MET}</b> · previsão de temperatura mínima"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE} · <b>{MET}</b>"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INMET</b>, aviso laranja de tempestade para 15/10 (2.163 municípios)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · baixa umidade: <b>INMET</b> · Teresina: <b>Open-Meteo</b>, máxima prevista para 15/10"},
    {"ini": ini("f6"), "fim": ini("f9"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · foto da geada: ilustração"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "tempestade": "#ff8c1a", "alerta": "#ff8c1a", "laranja": "#ff8c1a",
         "rajadas": "#5ec8ff", "vento": "#96d2ff", "forte": "#ff8c1a", "seco": "#ff8c1a", "frio": "#96d2ff", "fria": "#96d2ff", "geada": "#96d2ff",
         "zero": "#96d2ff", "danos": "#ff8c1a", "graus": "#ff2a1f", "maximas": "#ff2a1f", "comenta": AM,
         "inteligencia": AM, "artificial": AM}
LUGAR = {"serra", "catarinense", "sul", "litoral", "sao", "paulo", "brasil", "mato", "grosso", "goias", "minas", "vale", "ribeira",
         "leste", "parana", "nordeste", "piaui", "bahia", "rio", "espirito", "santo", "santa", "catarina", "campo", "grande",
         "campos", "palmas", "goiania", "brasilia", "inemaclub", "onde"}
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
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"tempestade hoje {HOJE}")
