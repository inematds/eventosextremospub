#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 16/10/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS)
e dos avisos do INMET (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, geada no fim de semana e -3 °C na serra), infravermelho do GOES-19
no ciclone e na frente fria, alerta laranja de MG e o total do Brasil, colunas 3D da chuva prevista até domingo (Open-Meteo),
foto do temporal no Rio e da geada (ilustração), frio por dia (sábado, domingo, segunda).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "16/10/2026"
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
SERRA = {"lon": -50.0, "lat": -27.9, "zoom": 6.3}     # f1: Serra Catarinense
CICLONE = {"lon": -48.5, "lat": -27.0, "zoom": 4.2}   # f2: ciclone e ar frio no Sul
SELIT = {"lon": -44.5, "lat": -23.0, "zoom": 5.0}     # f2: frente fria no litoral do Sudeste
MG = {"lon": -44.6, "lat": -18.6, "zoom": 5.2}        # f3: Minas
BRA = {"lon": -48.0, "lat": -17.5, "zoom": 4.0}       # f3: o Brasil do alerta
SECH = {"lon": -44.0, "lat": -19.0, "zoom": 4.75}     # f4: BH, SP, Campinas, Rio, ES e sul da BA
COL = {"lon": -43.6, "lat": -23.6, "zoom": 5.55}      # f5: colunas 3D Rio, Vitória, SP e BH
NE = {"lon": -41.5, "lat": -8.0, "zoom": 5.0}         # f6: Nordeste seco
RSUL = {"lon": -52.0, "lat": -29.8, "zoom": 5.3}      # f7: serra, litoral do Sul e campanha gaúcha
PALMAS = {"lon": -50.9, "lat": -27.3, "zoom": 6.0}    # f8: Serra Catarinense e Campos de Palmas
CSUL = {"lon": -50.5, "lat": -21.6, "zoom": 4.85}     # f9: MS, SP e sul de Minas
SUL = {"lon": -51.5, "lat": -26.0, "zoom": 4.6}       # f10: chuva volta ao Sul, nova massa fria
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
SER = em("f1", "Serra")
SUDESTE = em("f2", "Sudeste")
BRASIL = em("f3", "Brasil")
TEMPORAL = em("f5", "temporal")
camera = [
    K(0, BR), K(CAPA, BR), K(SER - .3, {**BR, "lon": -51.5, "lat": -22.0, "zoom": 4.4}, 10, 0),
    K(SER + 1.3, SERRA, 45, -18), K(fim("f1") - .2, {**SERRA, "zoom": 6.4}, 50, 0),
    K(ini("f2") + 1.0, CICLONE, 0, 0), K(SUDESTE - .3, {**CICLONE, "lon": -47.5, "lat": -25.5}, 0, 0), K(fim("f2") - .2, SELIT, 10, 0),
    K(ini("f3") + 1.0, MG, 10, 0), K(BRASIL - .2, {**MG, "zoom": 5.1}, 10, 0), K(BRASIL + 1.2, BRA, 0, 0), K(fim("f3") - .2, {**BRA, "zoom": 3.95}, 0, 0),
    K(ini("f4") + 1.0, SECH, 10, -4), K(em("f4", "Bahia") - .6, {**SECH, "lat": -19.4}, 12, 0), K(fim("f4") - .1, {**SECH, "lat": -17.6, "lon": -42.5}, 12, 4),
    K(ini("f5") + 1.0, COL, 55, -22), K(TEMPORAL, {**COL, "zoom": 5.7}, 58, 14), K(fim("f5") - .2, {**COL, "zoom": 5.75}, 58, 20),
    K(ini("f6") + 1.0, NE, 6, -2), K(fim("f6") - .2, {**NE, "lon": -41.7}, 8, 2),
    K(ini("f7") + 1.0, RSUL, 25, -8), K(fim("f7") - .2, {**RSUL, "lon": -52.6}, 30, 6),
    K(ini("f8") + 1.0, PALMAS, 40, -10), K(fim("f8") - .2, {**PALMAS, "zoom": 6.1}, 45, 6),
    K(ini("f9") + 1.0, CSUL, 12, -4), K(fim("f9") - .2, {**CSUL, "zoom": 4.95}, 14, 4),
    K(ini("f10") + 1.0, SUL, 10, 0), K(fim("f10") - .2, {**SUL, "zoom": 4.7}, 12, 2),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) no ciclone e na frente fria (f2)
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

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de hoje a domingo (16 a 18/10) nas capitais do Sudeste, Open-Meteo
import ast
CAPS = ast.literal_eval(re.search(r"^CAP = (\{.*?\})\n", (AQUI / "../../coleta/ultimas24h.py").read_text(), re.S | re.M).group(1))
OM = dict(zip(CAPS, json.loads((B / "openmeteo_capitais_3d.json").read_text())))
assert OM["Rio de Janeiro"]["daily"]["time"][:3] == ["2026-10-16", "2026-10-17", "2026-10-18"]
mm3 = lambda c: round(sum(OM[c]["daily"]["precipitation_sum"][:3]), 1)
SE4 = ["Rio de Janeiro", "Vitória", "São Paulo", "Belo Horizonte"]
MM = {c: mm3(c) for c in SE4}
assert 49 <= MM["Rio de Janeiro"] <= 55, MM   # a fala diz "50 milímetros no Rio"
col = [{"id": i, "p": [CAPS[c][2], CAPS[c][1]], "v": MM[c], "cor": [60, 150, 255] if MM[c] >= 45 else [120, 190, 255]} for i, c in enumerate(SE4)]
ordem = {c["id"]: i * .2 for i, c in enumerate(col)}
colunas = [{"id": "chuva3d", "ini": ini("f5") + .2, "fim": TEMPORAL + .2, "dados": col, "raio": 22000, "escala": 6000, "ordem": ordem, "varredura": 1}]
fmm = lambda v: f"{v:.1f}".replace(".", ",")

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, temporal no Rio e geada
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/temporal.png", "ini": TEMPORAL - .1, "fim": ini("f6") + .3, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/geada.png", "ini": em("f8", "0") - .1, "fim": ini("f9") + .3, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
HOJE = ufs_av(56091)     # tempestade laranja 16/10: 563 (MG 364, RJ 92, SP 55, ES 52)
assert len(geo(56091)) == 563, len(geo(56091))
assert sum(c[:2] == "31" for c in geo(56091)) == 364
assert aviso[56091]["severidade"] == "Perigo" and aviso[56091]["descricao"] == "Tempestade" and aviso[56091]["inicio"].startswith("2026-10-16")
assert len(geo(56084)) == 830 and aviso[56084]["descricao"] == "Baixa Umidade"   # baixa umidade 16/10: 830 (PI 185)
assert len(geo(56095)) == 115 and aviso[56095]["descricao"] == "Ventos Costeiros"  # ventos costeiros sábado 17/10: SC 71, RS 43
NORDESTE = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
estados = [
    {"id": "serra", "ini": SER - .2, "fim": ini("f2") + .3, "ufs": ["SC"], "cor": FRIO, "alfa": .4},
    {"id": "frio", "ini": ini("f2"), "fim": SUDESTE + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .3},
    {"id": "frente", "ini": SUDESTE, "fim": ini("f3") + .3, "ufs": ["SP", "RJ", "ES"], "cor": AZUL, "alfa": .35},
    {"id": "mg", "ini": ini("f3"), "fim": BRASIL + .3, "ufs": ["MG"], "cor": LAR, "alfa": .6},
    {"id": "hoje", "ini": BRASIL, "fim": ini("f4") + .3, "ufs": HOJE, "cor": LAR, "alfa": .55},
    {"id": "chuva", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["MG", "SP", "RJ", "ES", "BA"], "cor": AZUL, "alfa": .4},
    {"id": "rio", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["RJ", "ES"], "cor": AZUL, "alfa": .45},
    {"id": "seco", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": NORDESTE, "cor": [255, 90, 20], "alfa": .35},
    {"id": "sab", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": ["RS", "SC"], "cor": FRIO, "alfa": .4},
    {"id": "dom", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["SC", "PR"], "cor": FRIO, "alfa": .45},
    {"id": "seg", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["MS", "SP", "MG"], "cor": FRIO, "alfa": .4},
    {"id": "qua", "ini": ini("f10"), "fim": em("f10", "massa") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .4},
    {"id": "prox", "ini": em("f10", "massa"), "fim": ini("f11") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .4},
]

pinos = [
    {"nome": "Serra Catarinense", "sub": "até -3 °C na segunda", "lon": -49.93, "lat": -28.29, "ini": SER, "fim": ini("f2"), "h": 200},
    {"nome": "Belo Horizonte", "sub": "chuva hoje", "lon": -43.94, "lat": -19.92, "ini": em("f4", "Belo"), "fim": em("f4", "Bahia") - .3, "h": 330},
    {"nome": "São Paulo e Campinas", "sub": "chuva hoje", "lon": -46.63, "lat": -23.55, "ini": em("f4", "Paulo"), "fim": em("f4", "Bahia") - .3, "h": 60},
    {"nome": "Rio de Janeiro", "sub": "chuva hoje", "lon": -43.20, "lat": -22.90, "ini": em("f4", "Rio"), "fim": em("f4", "Bahia") - .3, "h": 110},
    {"nome": "Espírito Santo", "sub": "chuva hoje", "lon": -40.34, "lat": -20.32, "ini": em("f4", "Espírito"), "fim": em("f4", "Bahia") - .3, "h": 200},
    {"nome": "Sul da Bahia", "sub": "chuva hoje", "lon": -39.05, "lat": -14.79, "ini": em("f4", "Bahia"), "fim": ini("f5"), "h": 140},
    {"nome": "Rio de Janeiro", "sub": f"{fmm(MM['Rio de Janeiro'])} mm até domingo", "lon": -43.20, "lat": -22.90, "ini": em("f5", "Rio"), "fim": TEMPORAL, "h": 300},
    {"nome": "Teresina (PI)", "sub": "38,5 °C previstos hoje", "lon": -42.80, "lat": -5.09, "ini": em("f6", "38"), "fim": ini("f7"), "h": 170},
    {"nome": "Litoral do Sul", "sub": "rajadas de 70 km/h", "lon": -50.2, "lat": -30.4, "ini": em("f7", "litoral"), "fim": ini("f8"), "h": 170},
    {"nome": "Campanha gaúcha", "sub": "5 °C no sábado", "lon": -54.10, "lat": -31.33, "ini": em("f7", "campanha"), "fim": ini("f8"), "h": 150},
    {"nome": "Serra Catarinense", "sub": "geada no domingo", "lon": -49.93, "lat": -28.29, "ini": em("f8", "Serra"), "fim": em("f8", "0"), "h": 200},
    {"nome": "Campos de Palmas (PR)", "sub": "geada no domingo", "lon": -51.99, "lat": -26.48, "ini": em("f8", "Palmas") - .2, "fim": em("f8", "0"), "h": 160},
    {"nome": "Sul de MS", "sub": "abaixo de 10 °C", "lon": -55.73, "lat": -22.54, "ini": em("f9", "Mato"), "fim": ini("f10"), "h": 150},
    {"nome": "São Paulo", "sub": "abaixo de 10 °C", "lon": -46.63, "lat": -23.55, "ini": em("f9", "Paulo"), "fim": ini("f10"), "h": 130},
    {"nome": "Sul de Minas", "sub": "abaixo de 10 °C", "lon": -45.94, "lat": -22.23, "ini": em("f9", "Minas"), "fim": ini("f10"), "h": 230},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
conta = lambda ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0: {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra) - lead, "dur": lead, "cor": cor, "unid": unid}
H = SER - .1   # o hero (data grande) fica até a câmera chegar à serra
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:112px">GEADA</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">no domingo · -3 °C na serra na segunda</div>'}]
D_BR = max(BRASIL + .4, em("f3", "563") - LEAD)   # o total do Brasil sobe de 364 a 563 até a palavra
paineis = [
    {"ini": H + .1, "fim": ini("f2"), "k": "SERRA CATARINENSE · SEGUNDA (PREVISÃO)",
     "contador": conta(-3, "f1", "3", "#96d2ff", "°C", de=15, lead=em("f1", "3") - SER),   # a temperatura cai até o -3
     "l": "2 a 3 graus abaixo de zero · geada", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "POR QUE VAI ESFRIAR",
     "itens": [{"t": em("f2", "ciclone"), "txt": "🌀 um ciclone no Sul"},
               {"t": em("f2", "ar"), "txt": "🌬️ empurra o ar frio"},
               {"t": em("f2", "frente"), "txt": "🌧️ frente fria no litoral do Sudeste"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f3"), "fim": BRASIL, "k": "ALERTA LARANJA DE TEMPESTADE · MG",
     "contador": conta(364, "f3", "364", "#ff8c1a", "CIDADES EM MINAS"),
     "l": "INMET · sexta, 16/10", "borda": "rgba(255,140,26,.7)"},
    {"ini": BRASIL, "fim": ini("f4"), "k": "BRASIL INTEIRO · HOJE",
     "contador": {"de": 364, "ate": 563, "dec": 0, "ini": D_BR, "dur": max(.4, em("f3", "563") - D_BR), "cor": "#ff8c1a", "unid": "CIDADES NO BRASIL"},
     "l": "MG 364 · RJ 92 · SP 55 · ES 52", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE · SEXTA, 16/10 · CHUVA",
     "itens": [{"t": em("f4", "Belo"), "txt": "🌧️ BH, São Paulo e Campinas"},
               {"t": em("f4", "Rio"), "txt": "🌧️ Rio e Espírito Santo"},
               {"t": em("f4", "Bahia"), "txt": "🌧️ sul da Bahia"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "CHUVA ATÉ DOMINGO (PREVISÃO)",
     "contador": conta(50, "f5", "50", "#5ec8ff", "MM NO RIO"),
     "l": f"Rio {fmm(MM['Rio de Janeiro'])} · Vitória {fmm(MM['Vitória'])} · SP {fmm(MM['São Paulo'])} · BH {fmm(MM['Belo Horizonte'])} mm",
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "NORDESTE SECO · CALOR",
     "contador": conta(38, "f6", "38", "#ff2a1f", "°C"),
     "l": "35 a 38 °C · baixa umidade em 830 cidades (INMET)", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SÁBADO, 17/10 · VENTO (PREVISÃO)",
     "contador": conta(70, "f7", "70", "#5ec8ff", "KM/H"),
     "l": "rajadas na serra e no litoral do Sul · 5 °C na campanha gaúcha", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "DOMINGO, 18/10 · GEADA (PREVISÃO)",
     "contador": conta(0, "f8", "0", "#96d2ff", "°C", de=8, lead=em("f8", "0") - ini("f8") - .2),
     "l": "0 a 3 °C · Serra Catarinense e Campos de Palmas", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "SEGUNDA, 19/10 · FRIO (PREVISÃO)",
     "contador": conta(10, "f9", "10", "#96d2ff", "°C", de=20, lead=em("f9", "10") - ini("f9") - .2),
     "l": "abaixo de 10 °C no sul de MS, em SP e no sul de Minas", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "PRÓXIMOS DIAS (PREVISÃO)",
     "itens": [{"t": em("f10", "chuva"), "txt": "🌧️ quarta, 21/10: chuva volta ao Sul"},
               {"t": em("f10", "massa"), "txt": "🌬️ nova massa de ar frio no fim do mês"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "região"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f11", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
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
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INMET</b>, aviso laranja de tempestade para 16/10 (563 municípios)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>Open-Meteo</b>, chuva prevista de 16 a 18/10 nas capitais · <b>{MET}</b> · foto do temporal: ilustração"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · baixa umidade: <b>INMET</b> · Teresina: <b>Open-Meteo</b>, máxima prevista para 16/10"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · previsão · foto da geada: ilustração"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>{MET}</b> · previsão"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "tempestade": "#ff8c1a", "alerta": "#ff8c1a", "laranja": "#ff8c1a",
         "rajadas": "#5ec8ff", "vento": "#96d2ff", "forte": "#ff8c1a", "seco": "#ff8c1a", "frio": "#96d2ff", "fria": "#96d2ff", "geada": "#96d2ff",
         "zero": "#96d2ff", "gear": "#96d2ff", "temporal": "#ff8c1a", "milimetros": "#5ec8ff", "ciclone": "#96d2ff", "graus": "#ff2a1f", "maximas": "#ff2a1f", "comenta": AM,
         "inteligencia": AM, "artificial": AM}
LUGAR = {"serra", "catarinense", "sul", "litoral", "sudeste", "sao", "paulo", "brasil", "mato", "grosso", "minas", "belo", "horizonte",
         "campinas", "nordeste", "bahia", "rio", "espirito", "santo", "campanha", "gaucha", "campos", "palmas", "inemaclub", "regiao"}
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
      f"tempestade hoje {HOJE} · chuva até domingo {MM}")
