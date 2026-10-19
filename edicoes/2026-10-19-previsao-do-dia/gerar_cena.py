#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 19/10/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png), infravermelho do GOES-19 sobre o Sul (ar frio e seco),
gráfico da chuva prevista no Sul em 7 dias, alertas do INMET (chuvas intensas hoje, geada amanhã, tempestade na quinta),
colunas 3D da chuva prevista no domingo nas capitais, foto da enchente (ilustração) no rio Iguaçu.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "19/10/2026"
MET = "Meteorologia · " + DATA
OM = "<b>Open-Meteo</b>, previsão nas capitais"
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
SULIR = {"lon": -51.0, "lat": -26.5, "zoom": 4.9}    # f1/f2: o Sul no IR (céu limpo do ar frio e seco)
SUL = {"lon": -51.5, "lat": -28.6, "zoom": 5.5}      # f3: Sul hoje e o litoral gaúcho
NNE = {"lon": -50.0, "lat": -9.0, "zoom": 4.0}       # f4: Norte e interior do Nordeste
SERRA = {"lon": -49.95, "lat": -28.1, "zoom": 6.4}   # f5: topo da Serra Catarinense
OESTE = {"lon": -52.6, "lat": -26.6, "zoom": 5.9}    # f6: oeste de SC e sudoeste do PR
QUI = {"lon": -49.5, "lat": -24.5, "zoom": 4.6}      # f7: tempestade na quinta (Sul, SP, MG)
COL = {"lon": -50.0, "lat": -24.8, "zoom": 5.0}      # f8: colunas 3D no domingo
SOPR = {"lon": -52.9, "lat": -26.0, "zoom": 6.6}     # f9: sudoeste do Paraná e o rio Iguaçu
OSC = {"lon": -53.4, "lat": -27.6, "zoom": 6.0}      # f10: oeste catarinense e noroeste gaúcho
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
NORTE = em("f4", "Norte")
CURI = em("f8", "Curitiba")
ENCH = em("f9", "enchente")
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, SULIR, 0, 0), K(fim("f1") - .2, {**SULIR, "zoom": 5.0}, 0, 0),
    K(ini("f2") + 1.0, {**SULIR, "lat": -27.0}, 20, -6), K(fim("f2") - .2, {**SULIR, "lat": -27.2, "zoom": 5.1}, 24, 6),
    K(ini("f3") + 1.0, SUL, 15, -4), K(fim("f3") - .2, {**SUL, "zoom": 5.6}, 18, 4),
    K(NORTE + .9, NNE, 0, 0), K(fim("f4") - .2, {**NNE, "zoom": 4.05}, 0, 0),
    K(ini("f5") + 1.0, SERRA, 35, -8), K(fim("f5") - .2, {**SERRA, "zoom": 6.5}, 40, 6),
    K(ini("f6") + 1.0, OESTE, 15, 0), K(fim("f6") - .2, {**OESTE, "zoom": 6.0}, 18, 4),
    K(ini("f7") + 1.0, QUI, 0, 0), K(fim("f7") - .2, {**QUI, "zoom": 4.65}, 0, 0),
    K(CURI - .3, COL, 52, -20), K(fim("f8") - .2, {**COL, "zoom": 5.05}, 56, 16),
    K(ini("f9") + 1.0, SOPR, 25, -6), K(fim("f9") - .2, {**SOPR, "zoom": 6.7}, 28, 6),
    K(ini("f10") + 1.0, OSC, 20, -4), K(fim("f10") - .2, {**OSC, "zoom": 6.1}, 22, 4),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) sobre o Sul (f1–f2)
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
              "ini": CAPA - .3, "fim": ini("f3") + .3, "dur": ini("f3") - CAPA + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

# ---------------------------------------------------------------- previsão Open-Meteo nas capitais (pesquisa/bruto/resumo.json)
OMC = json.loads((B / "resumo.json").read_text())["openmeteo_capitais"]["linhas"]
chuva = lambda cap, dia: next(l["chuva"] for l in OMC if l["cap"] == cap and l["dia"] == dia)
DOM = "2026-10-25"
assert chuva("Curitiba", DOM) == 98.7 and round(chuva("Florianópolis", DOM)) == 40 and round(chuva("Porto Alegre", DOM)) == 36

# colunas 3D: chuva PREVISTA no domingo, 25/10, nas capitais do Sul e vizinhas (altura = mm)
CAPS = [("Curitiba", -49.27, -25.43), ("Florianópolis", -48.55, -27.60), ("Porto Alegre", -51.23, -30.03), ("São Paulo", -46.63, -23.55),
        ("Campo Grande", -54.65, -20.47), ("Rio de Janeiro", -43.20, -22.91)]
cor_mm = lambda mm: [150, 215, 255] if mm < 10 else [60, 150, 255] if mm < 50 else [120, 90, 255]
col = [{"id": i, "p": [lon, lat], "v": chuva(c, DOM), "cor": cor_mm(chuva(c, DOM))} for i, (c, lon, lat) in enumerate(CAPS)]
ordem = {c["id"]: i * .15 for i, c in enumerate(col)}
colunas = [{"id": "chuvadom", "ini": CURI - .4, "fim": ini("f9") + .5, "dados": col, "raio": 30000, "escala": 6000, "ordem": ordem, "varredura": 1}]

# gráfico: chuva prevista no Sul em 7 dias (soma das capitais do Sul)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-19" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
assert SULV[0] < 1 and SULV[1] < 1 and round(SULV[-1]) == 176   # seco hoje e amanhã; a chuva sobe até domingo (175,5 mm somados)
series = [{"nome": "Sul", "cor": "#5ec8ff", "v": SULV}]

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e enchente
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/enchente.png", "ini": ENCH - .1, "fim": fim("f9") - .1, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
CHUVA = ufs_av(56112)    # chuvas intensas amarelo 19–20/10: 1144 (BA 382, TO 139, PI 127, MG 114, AM 62, MA 60)
assert len(geo(56112)) == 1144 and aviso[56112]["descricao"] == "Chuvas Intensas" and aviso[56112]["inicio"].startswith("2026-10-19")
assert por_uf(56112, "BA") == 382 and por_uf(56112, "TO") == 139
GEADA = ufs_av(56121)    # geada amarelo 20/10 até 9 h: 59 (SC 56, RS 2, PR 1)
assert len(geo(56121)) == 59 and por_uf(56121, "SC") == 56 and aviso[56121]["descricao"] == "Geada" and aviso[56121]["inicio"].startswith("2026-10-20")
TEMP = ufs_av(56118)     # tempestade amarelo quinta 22/10: 2745 (SP 645, MG 545, RS 497, PR 399, SC 295, RJ 92)
assert len(geo(56118)) == 2745 and por_uf(56118, "SP") == 645 and por_uf(56118, "MG") == 545
assert aviso[56118]["descricao"] == "Tempestade" and aviso[56118]["inicio"].startswith("2026-10-22")
estados = [
    {"id": "sul0", "ini": CAPA, "fim": ini("f3") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .25},
    {"id": "sulhoje", "ini": ini("f3"), "fim": NORTE + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .35},
    {"id": "chuvas", "ini": NORTE - .2, "fim": ini("f5") + .3, "ufs": CHUVA, "cor": AMA, "alfa": .45},
    {"id": "geada", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": GEADA, "cor": FRIO, "alfa": .5},
    {"id": "calor", "ini": em("f6", "esquenta") - .2, "fim": ini("f7") + .3, "ufs": ["SC", "PR"], "cor": LAR, "alfa": .35},
    {"id": "tempest", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": TEMP, "cor": LAR, "alfa": .45},
    {"id": "baixa", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .35},
    {"id": "pr", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["PR"], "cor": VERM, "alfa": .4},
    {"id": "scrs", "ini": ini("f10"), "fim": ini("f11") + .3, "ufs": ["SC", "RS"], "cor": AZUL, "alfa": .4},
]

pinos = [
    {"nome": "Paraná", "sub": "até 300 mm até 31/10 · estimativa", "lon": -51.6, "lat": -24.9, "ini": em("f1", "Paraná"), "fim": ini("f2"), "h": 200},
    {"nome": "Litoral gaúcho", "sub": "garoa hoje", "lon": -51.0, "lat": -31.0, "ini": em("f3", "litoral"), "fim": ini("f4"), "h": 200},
    {"nome": "Topo da Serra Catarinense", "sub": "geada fraca · terça cedo", "lon": -49.93, "lat": -28.29, "ini": em("f5", "geada"), "fim": ini("f6"), "h": 200},
    {"nome": "Oeste de SC e sudoeste do PR", "sub": "até 28 °C · terça à tarde", "lon": -52.62, "lat": -26.6, "ini": em("f6", "oeste"), "fim": ini("f7"), "h": 200},
    {"nome": "Curitiba", "sub": "98,7 mm previstos no domingo", "lon": -49.27, "lat": -25.43, "ini": CURI, "fim": ini("f9"), "h": 330},
    {"nome": "Pato Branco", "sub": "chuva forte · fim de semana", "lon": -52.67, "lat": -26.23, "ini": em("f9", "Pato"), "fim": ENCH, "h": 300},
    {"nome": "Francisco Beltrão", "sub": "chuva forte · fim de semana", "lon": -53.06, "lat": -26.08, "ini": em("f9", "Francisco"), "fim": ENCH, "h": 130},
    {"nome": "Oeste catarinense", "sub": "até 200 mm até 31/10", "lon": -52.62, "lat": -27.10, "ini": em("f10", "oeste"), "fim": ini("f11"), "h": 200},
    {"nome": "Noroeste gaúcho", "sub": "chuva forte · fim de semana", "lon": -54.2, "lat": -28.0, "ini": em("f10", "noroeste"), "fim": ini("f11"), "h": 170},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
conta = lambda ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0: {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra) - lead, "dur": lead, "cor": cor, "unid": unid}
lead_de = lambda fid, palavra: min(LEAD, em(fid, palavra) - ini(fid) - .05)   # o contador não começa antes do painel
hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o número da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:92px;color:#5ec8ff">ATÉ 300 MM</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">de chuva no Paraná até 31/10 · estimativa</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "POR QUE · SUL · CHUVA PREVISTA EM 7 DIAS",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f2") + .3, "dur": 1.6},
     "l": "ar frio e seco perde força · baixa pressão a partir de quarta · mm somados nas capitais do Sul", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "HOJE, 19/10 · SUL (PREVISÃO)",
     "contador": conta(20, "f3", "20", "#96d2ff", "°C DE MÁXIMA", de=5, lead=lead_de("f3", "20")),
     "l": "tempo seco · frio de manhã · garoa no litoral gaúcho", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE · CHUVAS INTENSAS",
     "contador": conta(1144, "f4", "1144", "#facc15", "CIDADES EM ALERTA"),
     "l": "BA 382 · TO 139 · PI 127 · MG 114 · alerta amarelo (INMET)", "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "TERÇA, 20/10 · GEADA (PREVISÃO)",
     "contador": conta(59, "f5", "59", "#96d2ff", "CIDADES EM ALERTA"),
     "l": "SC 56 · RS 2 · PR 1 · até 9 h (INMET)", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "TERÇA À TARDE (PREVISÃO)",
     "contador": conta(28, "f6", "28", "#ff8c1a", "°C DE MÁXIMA", de=8),
     "l": "oeste de SC e sudoeste do PR · mínima perto de 8 °C cedo", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "QUINTA, 22/10 · TEMPESTADE",
     "contador": conta(2745, "f7", "2745", "#ff8c1a", "CIDADES EM ALERTA"),
     "l": "SP 645 · MG 545 · RS 497 · PR 399 · SC 295 (INMET)", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "DOMINGO, 25/10 · CHUVA PREVISTA",
     "contador": conta(98.7, "f8", "100", "#5ec8ff", "MM EM CURITIBA", dec=1),
     "l": "Florianópolis 40 · Porto Alegre 36 · coluna = mm previstos", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f9"), "fim": ENCH - .1, "k": "SUDOESTE DO PR · FIM DE SEMANA (PREVISÃO)",
     "itens": [{"t": em("f9", "Pato"), "txt": "📍 Pato Branco"},
               {"t": em("f9", "Francisco"), "txt": "📍 Francisco Beltrão"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "ATÉ 31/10 · OESTE DE SC (PREVISÃO)",
     "contador": conta(200, "f10", "200", "#5ec8ff", "MM", de=0),
     "l": "oeste catarinense e noroeste gaúcho · estimativa de modelo", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "onde"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f11", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
     "borda": "rgba(250,204,21,.8)"},
]
for a, b in zip(paineis, paineis[1:]):
    assert a["fim"] <= b["ini"] + 1e-6, (a["k"], b["k"])
for a in paineis:
    assert a["ini"] < a["fim"], ("painel vazio", a["k"])
    if a.get("contador"):
        c = a["contador"]
        assert a["ini"] - .01 <= c["ini"] and c["ini"] + c["dur"] <= a["fim"] + .01, ("contador fora do painel", a["k"], c, a["ini"], a["fim"])

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>{MET}</b> · satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · {OM}, 19 a 25/10"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INMET</b>, aviso amarelo de chuvas intensas, 19 e 20/10 (1.144 municípios)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso de geada para 20/10 (59 municípios)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso amarelo de tempestade para 22/10 (2.745 municípios)"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · {OM} para 25/10 · altura da coluna = milímetros previstos"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · foto da enchente: ilustração"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chuvas": "#5ec8ff", "milimetros": "#5ec8ff", "garoar": "#5ec8ff", "enchente": "#ff2a1f",
         "temporais": "#ff8c1a", "tempestade": "#ff8c1a", "alerta": "#ff8c1a", "intensas": "#ff8c1a", "pancadas": "#ff8c1a",
         "trovoada": "#ff8c1a", "esquenta": "#ff8c1a", "baixa": "#ff8c1a", "pressao": "#ff8c1a",
         "frio": "#96d2ff", "seco": "#96d2ff", "geada": "#96d2ff", "graus": "#96d2ff",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"parana", "sul", "norte", "nordeste", "litoral", "gaucho", "serra", "catarinense", "santa", "catarina", "oeste", "sudoeste",
         "noroeste", "curitiba", "pato", "branco", "francisco", "beltrao", "rio", "iguacu", "inemaclub", "onde"}
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
     "marca": "INEMA · PREVISÃO DO DIA", "selo": DATA[:5] + " · INMET · NOAA",
     "camera": camera, "sat": SAT, "imagens": [], "colunas": colunas, "telas": telas, "estados": estados, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"chuvas hoje {CHUVA} · geada {GEADA} · tempestade qui {TEMP} · 7 dias {ROTD} · Sul {SULV}")
