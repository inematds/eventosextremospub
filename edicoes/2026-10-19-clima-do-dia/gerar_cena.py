#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 19/10/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS),
dos avisos do INMET e da chuva prevista para 7 dias (Open-Meteo, pesquisa/bruto/previsao7d.json).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, geada e -2,1 °C em Urubici), infravermelho do GOES-19
na massa de ar frio, alerta de chuvas intensas na Bahia e o total do Brasil, calor no Nordeste, foto da geada (ilustração),
tempestade no Sul na quarta e o total do Brasil na quinta (INMET), colunas 3D da chuva prevista até domingo no Sul.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "19/10/2026"
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
SERRA = {"lon": -49.6, "lat": -28.0, "zoom": 6.3}      # f1: Urubici, Serra Catarinense
CSUL = {"lon": -50.5, "lat": -23.5, "zoom": 4.3}       # f2: massa de ar frio no centro-sul
SUL = {"lon": -50.6, "lat": -27.6, "zoom": 5.3}        # f3: Guarapuava, Curitiba, Porto Alegre
NORTE = {"lon": -52.0, "lat": -9.5, "zoom": 3.95}      # f4: chuva no Norte, Minas e Bahia
BA = {"lon": -41.6, "lat": -12.8, "zoom": 5.1}         # f5: Bahia
BRA = {"lon": -50.0, "lat": -15.0, "zoom": 3.9}        # f5/f8: o Brasil do alerta
NE = {"lon": -41.5, "lat": -7.5, "zoom": 5.0}          # f6: Nordeste quente
PIMT = {"lon": -48.5, "lat": -10.5, "zoom": 4.25}      # f6: quarta, Piauí e Mato Grosso
PALMAS = {"lon": -50.8, "lat": -27.3, "zoom": 6.0}     # f7: alto de SC e Campos de Palmas
SULW = {"lon": -51.5, "lat": -27.0, "zoom": 4.8}       # f8: tempestade no Sul na quarta
COL = {"lon": -49.6, "lat": -26.4, "zoom": 5.6}        # f9: colunas 3D Curitiba, Florianópolis, Porto Alegre
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
SER = em("f1", "Serra")
BR5 = em("f5", "Brasil")
QUA6 = em("f6", "quarta")
QUI8 = em("f8", "quinta")
GEAR = em("f7", "gear")
camera = [
    K(0, BR), K(CAPA, BR), K(SER - .3, {**BR, "lon": -51.5, "lat": -22.0, "zoom": 4.4}, 10, 0),
    K(SER + 1.3, SERRA, 45, -18), K(fim("f1") - .2, {**SERRA, "zoom": 6.4}, 50, 0),
    K(ini("f2") + 1.0, CSUL, 0, 0), K(fim("f2") - .2, {**CSUL, "zoom": 4.4}, 0, 0),
    K(ini("f3") + 1.0, SUL, 20, -6), K(fim("f3") - .2, {**SUL, "lon": -50.2}, 25, 6),
    K(ini("f4") + 1.0, NORTE, 0, 0), K(fim("f4") - .2, {**NORTE, "zoom": 4.0}, 4, 0),
    K(ini("f5") + 1.0, BA, 10, 0), K(BR5 - .2, {**BA, "zoom": 5.2}, 10, 0), K(BR5 + 1.2, BRA, 0, 0), K(fim("f5") - .2, {**BRA, "zoom": 3.95}, 0, 0),
    K(ini("f6") + 1.0, NE, 6, -2), K(QUA6 - .1, {**NE, "lon": -41.8}, 8, 0), K(QUA6 + 1.3, PIMT, 4, 0), K(fim("f6") - .2, {**PIMT, "zoom": 4.3}, 4, 2),
    K(ini("f7") + 1.0, PALMAS, 40, -10), K(fim("f7") - .2, {**PALMAS, "zoom": 6.1}, 45, 6),
    K(ini("f8") + 1.0, SULW, 10, 0), K(QUI8 - .2, {**SULW, "zoom": 4.85}, 12, 0), K(QUI8 + 1.2, BRA, 0, 0), K(fim("f8") - .2, {**BRA, "zoom": 3.95}, 0, 0),
    K(ini("f9") + 1.0, COL, 50, -18), K(em("f9", "Florianópolis"), {**COL, "zoom": 5.7}, 52, 8), K(fim("f9") - .2, {**COL, "zoom": 5.75}, 52, 16),
    K(ini("f10") + 1.0, SERRA, 35, -10), K(fim("f10") - .2, {**SERRA, "zoom": 6.4}, 40, 6),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na massa de ar frio (f2)
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

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA de hoje a domingo (19 a 25/10) nas capitais do Sul, Open-Meteo
import ast
CAPS = ast.literal_eval(re.search(r"^CAP = (\{.*?\})\n", (AQUI / "../../coleta/ultimas24h.py").read_text(), re.S | re.M).group(1))
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-19" and P7["dias"][-1] == "2026-10-25", P7["dias"]   # 25/10 = domingo
MM = dict(P7["acumulado_7d_top"])
SUL3 = ["Curitiba", "Florianópolis", "Porto Alegre"]
assert 145 <= MM["Curitiba"] <= 155 and 95 <= MM["Florianópolis"] < 100, MM   # a fala diz "150 em Curitiba" e "quase 100 em Florianópolis"
col = [{"id": i, "p": [CAPS[c][2], CAPS[c][1]], "v": MM[c], "cor": [60, 150, 255] if MM[c] >= 90 else [120, 190, 255]} for i, c in enumerate(SUL3)]
ordem = {c["id"]: i * .2 for i, c in enumerate(col)}
colunas = [{"id": "chuva3d", "ini": ini("f9") + .2, "fim": ini("f10") + .2, "dados": col, "raio": 22000, "escala": 2300, "ordem": ordem, "varredura": 1}]
fmm = lambda v: f"{v:.1f}".replace(".", ",")
TERESINA = P7["por_dia"][0]["tmax_pico"]
assert TERESINA[1] == "Teresina", TERESINA

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e geada
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/geada.png", "ini": GEAR - .1, "fim": ini("f8") + .3, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
CHUVA = ufs_av(56112)    # chuvas intensas 19 e 20/10: 1.144 (BA 382)
assert len(geo(56112)) == 1144 and sum(c[:2] == "29" for c in geo(56112)) == 382, len(geo(56112))
assert aviso[56112]["descricao"] == "Chuvas Intensas" and aviso[56112]["inicio"].startswith("2026-10-19")
QUA = ufs_av(56117)      # tempestade quarta 21/10: 407 (PR 178, RS 131, SC 87, MS 11)
assert len(geo(56117)) == 407 and aviso[56117]["descricao"] == "Tempestade" and aviso[56117]["inicio"].startswith("2026-10-21")
QUI = ufs_av(56118)      # tempestade quinta 22/10: 2.745
assert len(geo(56118)) == 2745 and aviso[56118]["descricao"] == "Tempestade" and aviso[56118]["inicio"].startswith("2026-10-22")
NORDESTE = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
NORTE_UF = ["AC", "AM", "RO", "RR", "PA", "TO"]
estados = [
    {"id": "serra", "ini": SER - .2, "fim": ini("f2") + .3, "ufs": ["SC"], "cor": FRIO, "alfa": .4},
    {"id": "massa", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["RS", "SC", "PR", "SP", "MS", "MG", "RJ", "GO", "DF"], "cor": FRIO, "alfa": .3},
    {"id": "sul", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .35},
    {"id": "chuva", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": NORTE_UF + ["MG", "BA"], "cor": AZUL, "alfa": .4},
    {"id": "ba", "ini": ini("f5"), "fim": BR5 + .3, "ufs": ["BA"], "cor": AMA, "alfa": .55},
    {"id": "hoje", "ini": BR5, "fim": ini("f6") + .3, "ufs": CHUVA, "cor": AMA, "alfa": .5},
    {"id": "calor", "ini": ini("f6"), "fim": QUA6 + .3, "ufs": NORDESTE, "cor": [255, 90, 20], "alfa": .35},
    {"id": "40", "ini": QUA6, "fim": ini("f7") + .3, "ufs": ["PI", "MT"], "cor": VERM, "alfa": .45},
    {"id": "geada", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": ["SC", "PR"], "cor": FRIO, "alfa": .45},
    {"id": "qua", "ini": ini("f8"), "fim": QUI8 + .3, "ufs": QUA, "cor": LAR, "alfa": .5},
    {"id": "qui", "ini": QUI8, "fim": ini("f9") + .3, "ufs": QUI, "cor": LAR, "alfa": .5},
    {"id": "sul7", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .35},
    {"id": "fimmes", "ini": ini("f10"), "fim": ini("f11") + .3, "ufs": ["SC"], "cor": FRIO, "alfa": .4},
]

pinos = [
    {"nome": "Urubici (SC)", "sub": "-2,1 °C hoje cedo", "lon": -49.59, "lat": -28.01, "ini": em("f1", "Urubici"), "fim": ini("f2"), "h": 200},
    {"nome": "Guarapuava (PR)", "sub": "-0,9 °C", "lon": -51.46, "lat": -25.39, "ini": em("f3", "Guarapuava"), "fim": ini("f4"), "h": 160},
    {"nome": "Curitiba", "sub": "6 °C", "lon": -49.27, "lat": -25.43, "ini": em("f3", "Curitiba"), "fim": ini("f4"), "h": 260},
    {"nome": "Porto Alegre", "sub": "7,3 °C", "lon": -51.23, "lat": -30.03, "ini": em("f3", "Porto"), "fim": ini("f4"), "h": 140},
    {"nome": "Minas Gerais", "sub": "chuva hoje", "lon": -43.5, "lat": -17.0, "ini": em("f4", "Minas"), "fim": ini("f5"), "h": 160},
    {"nome": "Bahia", "sub": "chuva hoje", "lon": -42.0, "lat": -11.3, "ini": em("f4", "Bahia"), "fim": ini("f5"), "h": 220},
    {"nome": "Teresina (PI)", "sub": f"{fmm(TERESINA[0])} °C previstos hoje", "lon": -42.80, "lat": -5.09, "ini": em("f6", "38"), "fim": QUA6, "h": 170},
    {"nome": "Piauí", "sub": "acima de 40 °C na quarta", "lon": -42.9, "lat": -8.0, "ini": em("f6", "Piauí") - .2, "fim": ini("f7"), "h": 150},
    {"nome": "Mato Grosso", "sub": "acima de 40 °C na quarta", "lon": -55.9, "lat": -14.5, "ini": em("f6", "Mato"), "fim": ini("f7"), "h": 150},
    {"nome": "Florianópolis", "sub": f"{fmm(MM['Florianópolis'])} mm até domingo", "lon": -48.55, "lat": -27.59, "ini": em("f9", "Florianópolis"), "fim": ini("f10"), "h": 120},
    {"nome": "Curitiba", "sub": f"{fmm(MM['Curitiba'])} mm até domingo", "lon": -49.27, "lat": -25.43, "ini": em("f9", "Curitiba"), "fim": ini("f10"), "h": 120},
    {"nome": "São Joaquim (SC)", "sub": "geada em 26 e 27/10", "lon": -49.93, "lat": -28.29, "ini": em("f10", "geada"), "fim": ini("f11"), "h": 200},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0):
    lead = min(lead, em(fid, palavra) - ini(fid) - .05)   # número dito logo no começo da fala: o contador começa com a fala
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra) - lead, "dur": lead, "cor": cor, "unid": unid}
H = SER - .1   # o hero (data grande) fica até a câmera chegar à serra
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:112px">GEADA</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">no Sul · -2,1 °C em Urubici</div>'}]
D_BR5 = max(BR5 + .4, em("f5", "1.144") - LEAD)   # o total do Brasil sobe de 382 a 1.144 até a palavra
D_BR8 = max(QUI8 + .4, em("f8", "2.745") - LEAD)  # o total da quinta sobe de 407 a 2.745 até a palavra
paineis = [
    {"ini": H + .1, "fim": ini("f2"), "k": "URUBICI (SC) · MÍNIMA DE HOJE",
     "contador": conta(-2.1, "f1", "2,1", "#96d2ff", "°C", dec=1, de=15, lead=max(.6, em("f1", "2,1") - H - .2)),   # a temperatura cai até o -2,1
     "l": "geada na Serra Catarinense", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "POR QUE ESFRIOU",
     "itens": [{"t": em("f2", "massa"), "txt": "🌬️ massa de ar frio e seco"},
               {"t": em("f2", "centro-sul"), "txt": "🧊 domina o centro-sul"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "MÍNIMAS DE HOJE · SUL",
     "itens": [{"t": em("f3", "Guarapuava"), "txt": "❄️ Guarapuava (PR) -0,9 °C"},
               {"t": em("f3", "Curitiba"), "txt": "🌡️ Curitiba 6 °C"},
               {"t": em("f3", "Porto"), "txt": "🌡️ Porto Alegre 7,3 °C"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE · SEGUNDA, 19/10",
     "itens": [{"t": em("f4", "seco"), "txt": "☀️ centro-sul seco"},
               {"t": em("f4", "chove"), "txt": "🌧️ chuva no Norte, em Minas e na Bahia"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": BR5, "k": "ALERTA DE CHUVAS INTENSAS · BA",
     "contador": conta(382, "f5", "382", "#FACC15", "CIDADES NA BAHIA"),
     "l": "INMET · 19 e 20/10", "borda": "rgba(250,204,21,.8)"},
    {"ini": BR5, "fim": ini("f6"), "k": "BRASIL INTEIRO · HOJE",
     "contador": {"de": 382, "ate": 1144, "dec": 0, "ini": D_BR5, "dur": max(.4, em("f5", "1.144") - D_BR5), "cor": "#FACC15", "unid": "CIDADES NO BRASIL"},
     "l": "BA 382 · TO 139 · PI 127 · MG 114", "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "CALOR · MÁXIMAS",
     "contador": conta(38, "f6", "38", "#ff2a1f", "°C NO NORDESTE"),
     "l": "quarta: acima de 40 °C no Piauí e em Mato Grosso (previsão)", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "TERÇA, 20/10 · GEADA (PREVISÃO)",
     "itens": [{"t": em("f7", "Santa"), "txt": "❄️ alto de Santa Catarina"},
               {"t": em("f7", "Palmas"), "txt": "❄️ Campos de Palmas (PR)"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f8"), "fim": QUI8, "k": "QUARTA, 21/10 · TEMPESTADE",
     "contador": conta(407, "f8", "407", "#ff8c1a", "CIDADES NO SUL E MS"),
     "l": "INMET · PR 178 · RS 131 · SC 87 · MS 11", "borda": "rgba(255,140,26,.7)"},
    {"ini": QUI8, "fim": ini("f9"), "k": "QUINTA, 22/10 · BRASIL",
     "contador": {"de": 407, "ate": 2745, "dec": 0, "ini": D_BR8, "dur": max(.4, em("f8", "2.745") - D_BR8), "cor": "#ff8c1a", "unid": "CIDADES COM TEMPESTADE"},
     "l": "INMET · SP 645 · MG 545 · RS 497 · PR 399", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "CHUVA ATÉ DOMINGO, 25/10 (PREVISÃO)",
     "contador": conta(150, "f9", "150", "#5ec8ff", "MM EM CURITIBA"),
     "l": f"Curitiba {fmm(MM['Curitiba'])} · Florianópolis {fmm(MM['Florianópolis'])} · Porto Alegre {fmm(MM['Porto Alegre'])} mm",
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "FIM DO MÊS (PREVISÃO)",
     "itens": [{"t": em("f10", "frio"), "txt": "🌬️ o frio volta"},
               {"t": em("f10", "geada"), "txt": "❄️ 26 e 27/10: geada na Serra Catarinense"}],
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
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>{MET}</b> · temperatura mínima de hoje"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE} · <b>{MET}</b>"},
    {"ini": ini("f3"), "fim": ini("f5"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INMET</b>, aviso de chuvas intensas para 19 e 20/10 (1.144 municípios)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · previsão · Teresina: <b>Open-Meteo</b>, máxima prevista para 19/10"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b> · previsão · foto da geada: ilustração"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>INMET</b>, avisos de tempestade para 21/10 (407 municípios) e 22/10 (2.745)"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>Open-Meteo</b>, chuva prevista de 19 a 25/10 nas capitais · <b>{MET}</b>"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b> · previsão"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "chuvas": "#5ec8ff", "tempestade": "#ff8c1a", "alerta": "#ff8c1a", "intensas": "#ff8c1a",
         "seco": "#ff8c1a", "frio": "#96d2ff", "geada": "#96d2ff", "zero": "#96d2ff", "gear": "#96d2ff", "milimetros": "#5ec8ff",
         "graus": "#ff2a1f", "maximas": "#ff2a1f", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"serra", "catarinense", "sul", "urubici", "guarapuava", "parana", "curitiba", "porto", "alegre", "centrosul", "norte", "minas",
         "bahia", "brasil", "nordeste", "piaui", "mato", "grosso", "santa", "catarina", "campos", "palmas", "florianopolis",
         "inemaclub", "regiao"}
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
      f"chuvas intensas hoje {CHUVA} · tempestade qua {QUA} qui {len(QUI)} UFs · chuva até domingo {[(c, MM[c]) for c in SUL3]}")
