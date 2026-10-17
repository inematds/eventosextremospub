#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 17/10/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), da anomalia do mar (GHRSST MUR, GIBS),
dos avisos do INMET e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png), infravermelho do GOES-19 sobre o Sul e o Atlântico (ciclone),
anomalia da temperatura do mar (água fria ao largo do RS), ventos costeiros, alerta laranja de MG e o total do Brasil,
colunas 3D da chuva prevista hoje nas capitais, foto da geada (ilustração) e gráfico da chuva prevista no Sul em 7 dias.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "17/10/2026"
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
BRA = {"lon": -52.0, "lat": -13.0, "zoom": 3.8}      # f6: Sudeste, Centro-Oeste e Norte
CICL = {"lon": -48.5, "lat": -24.5, "zoom": 4.9}     # f1: Sul e Sudeste no IR (o recorte do satélite acaba em 35° S)
MAR = {"lon": -49.5, "lat": -34.5, "zoom": 4.9}      # f2: o mar ao largo do RS (anomalia)
SUL = {"lon": -51.5, "lat": -29.2, "zoom": 5.6}      # f3: Sul, litoral gaúcho e catarinense
SE = {"lon": -44.5, "lat": -20.5, "zoom": 5.0}       # f4: Sudeste
MG = {"lon": -44.6, "lat": -18.6, "zoom": 5.3}       # f4: Minas Gerais
BRT = {"lon": -48.0, "lat": -17.0, "zoom": 4.1}      # f4: o total do Brasil
COL = {"lon": -45.5, "lat": -21.5, "zoom": 5.0}      # f5: colunas 3D nas capitais
SERRA = {"lon": -50.6, "lat": -27.6, "zoom": 6.3}    # f7/f8: Serra Catarinense e Campos de Palmas
PR = {"lon": -51.8, "lat": -25.6, "zoom": 5.8}       # f9/f10: Paraná e oeste de SC
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
MAR_T = em("f2", "mar")
MINAS, BRASIL = em("f4", "Minas"), em("f4", "Brasil")
RIO = em("f5", "Rio")
ZERO = em("f8", "zero")
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, CICL, 0, 0), K(fim("f1") - .2, {**CICL, "zoom": 5.0}, 0, 0),
    K(ini("f2") + 1.2, MAR, 35, -10), K(fim("f2") - .2, {**MAR, "zoom": 5.0}, 40, 8),
    K(ini("f3") + 1.0, SUL, 15, -4), K(fim("f3") - .2, {**SUL, "zoom": 5.7}, 18, 4),
    K(ini("f4") + 1.0, SE, 10, 0), K(MINAS - .2, {**SE, "lon": -44.8}, 10, 0), K(MINAS + .9, MG, 10, 0),
    K(BRASIL - .1, {**MG, "zoom": 5.35}, 10, 0), K(BRASIL + 1.0, BRT, 0, 0), K(fim("f4") - .2, {**BRT, "zoom": 4.15}, 0, 0),
    K(RIO + .6, COL, 52, -20), K(fim("f5") - .2, {**COL, "zoom": 5.05}, 56, 16),
    K(ini("f6") + 1.0, BRA, 0, 0), K(fim("f6") - .2, {**BRA, "zoom": 3.85}, 0, 0),
    K(ini("f7") + 1.0, SERRA, 30, -8), K(fim("f7") - .2, {**SERRA, "zoom": 6.4}, 34, 4),
    K(ini("f8") + .8, {**SERRA, "lon": -50.3, "lat": -27.9}, 40, -6), K(fim("f8") - .2, {**SERRA, "lon": -50.2, "lat": -28.0, "zoom": 6.5}, 44, 6),
    K(ini("f9") + 1.0, PR, 10, 0), K(fim("f9") - .2, {**PR, "lon": -51.6}, 12, 2),
    K(ini("f10") + 1.0, {**PR, "zoom": 5.6}, 0, 0), K(fim("f10") - .2, {**PR, "zoom": 5.7}, 0, 0),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) sobre o Sul e o Atlântico (f1–f2)
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
              "ini": CAPA - .3, "fim": MAR_T + .3, "dur": MAR_T - CAPA + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

# anomalia da temperatura do mar (GHRSST MUR via NASA GIBS, 16/10/2026, recorte -70,-45,-25,-15, EPSG:3857)
# amostrada pela paleta do GIBS: -2,4 °C em 38° S 52° W; até -3 °C ao largo do Uruguai; +1 a +2 °C ao largo de SP/RJ
ANOM = {"src": "sat/web/anomalia.png", "bbox": [-70, -45, -25, -15], "alfa": .85}
imagens = [{**ANOM, "ini": MAR_T - .3, "fim": ini("f3") + .4, "fade": .8}]

# ---------------------------------------------------------------- previsão Open-Meteo nas capitais (pesquisa/bruto/resumo.json)
OMC = json.loads((B / "resumo.json").read_text())["openmeteo_capitais"]["linhas"]
chuva = lambda cap, dia: next(l["chuva"] for l in OMC if l["cap"] == cap and l["dia"] == dia)
assert round(chuva("Rio de Janeiro", "2026-10-17")) == 26 and round(chuva("Vitória", "2026-10-17")) == 13

# colunas 3D: chuva PREVISTA hoje nas capitais do Sudeste e vizinhas (altura = mm)
CAPS = [("Rio de Janeiro", -43.20, -22.91), ("Vitória", -40.31, -20.32), ("São Paulo", -46.63, -23.55), ("Belo Horizonte", -43.94, -19.92),
        ("Curitiba", -49.27, -25.43), ("Goiânia", -49.25, -16.68), ("Brasília", -47.88, -15.79), ("Campo Grande", -54.65, -20.47),
        ("Salvador", -38.50, -12.97)]
cor_mm = lambda mm: [150, 215, 255] if mm < 10 else [60, 150, 255] if mm < 25 else [120, 90, 255]
col = [{"id": i, "p": [lon, lat], "v": chuva(c, "2026-10-17"), "cor": cor_mm(chuva(c, "2026-10-17"))} for i, (c, lon, lat) in enumerate(CAPS)]
ordem = {c["id"]: i * .15 for i, c in enumerate(col)}
colunas = [{"id": "chuvahoje", "ini": RIO - .2, "fim": ini("f6") + .5, "dados": col, "raio": 30000, "escala": 20000, "ordem": ordem, "varredura": 1}]

# gráfico: chuva prevista no Sul em 7 dias (soma das capitais do Sul)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-17" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sáb", "dom", "seg", "ter", "qua", "qui", "sex"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
assert SULV[2] == 0 and SULV[3] == 0 and round(SULV[-1]) == 53   # o Sul seca no começo da semana e a chuva volta na sexta (53 mm somados)
series = [{"nome": "Sul", "cor": "#5ec8ff", "v": SULV}]

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e geada
GEADA = em("f8", "geada")
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/geada.png", "ini": GEADA - .1, "fim": em("f8", "temperatura") - .2, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
VENTO = ufs_av(56095)    # ventos costeiros laranja 17/10: 115 (SC 71, RS 43, PR 1)
assert len(geo(56095)) == 115 and aviso[56095]["descricao"] == "Ventos Costeiros" and aviso[56095]["inicio"].startswith("2026-10-17")
assert por_uf(56095, "SC") == 71 and por_uf(56095, "RS") == 43
SAB = ufs_av(56096)      # tempestade laranja 17/10: 370 (MG 245, ES 78, RJ 26, BA 21)
assert len(geo(56096)) == 370 and por_uf(56096, "MG") == 245
assert aviso[56096]["severidade"] == "Perigo" and aviso[56096]["descricao"] == "Tempestade" and aviso[56096]["inicio"].startswith("2026-10-17")
SUDESTE, CO, NORTE = ["SP", "RJ", "ES", "MG"], ["MS", "MT", "GO", "DF"], ["RO", "AC", "AM", "RR", "PA", "AP", "TO"]
estados = [
    {"id": "sul0", "ini": CAPA, "fim": ini("f3") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .25},
    {"id": "solsul", "ini": em("f3", "sol") - .2, "fim": em("f3", "litoral") + .3, "ufs": ["PR", "SC", "RS"], "cor": AMA, "alfa": .3},
    {"id": "vento", "ini": em("f3", "litoral") - .2, "fim": ini("f4") + .3, "ufs": VENTO, "cor": LAR, "alfa": .45},
    {"id": "se", "ini": ini("f4"), "fim": MINAS + .3, "ufs": SAB, "cor": LAR, "alfa": .4},
    {"id": "mg", "ini": MINAS - .2, "fim": BRASIL + .3, "ufs": ["MG"], "cor": LAR, "alfa": .6},
    {"id": "sabbr", "ini": BRASIL - .2, "fim": ini("f5") + .3, "ufs": SAB, "cor": LAR, "alfa": .55},
    {"id": "dse", "ini": em("f6", "Sudeste") - .2, "fim": ini("f7") + .3, "ufs": SUDESTE, "cor": LAR, "alfa": .4},
    {"id": "dco", "ini": em("f6", "Centro-Oeste") - .2, "fim": ini("f7") + .3, "ufs": CO, "cor": LAR, "alfa": .4},
    {"id": "dn", "ini": em("f6", "Norte") - .2, "fim": ini("f7") + .3, "ufs": NORTE, "cor": LAR, "alfa": .4},
    {"id": "frio", "ini": ini("f7"), "fim": ini("f9") + .3, "ufs": ["SC", "RS", "PR"], "cor": FRIO, "alfa": .4},
    {"id": "pr", "ini": em("f9", "chuva") - .2, "fim": ini("f11") + .3, "ufs": ["PR", "SC"], "cor": LAR, "alfa": .4},
]

pinos = [
    {"nome": "Serra Catarinense", "sub": "geada e abaixo de 0 °C · segunda", "lon": -49.59, "lat": -28.01, "ini": em("f1", "Serra"), "fim": ini("f2"), "h": 200},
    {"nome": "Mar ao largo do RS", "sub": "até 2 °C abaixo do normal", "lon": -52.0, "lat": -38.0, "ini": MAR_T, "fim": ini("f3"), "h": 220},
    {"nome": "Centro-leste gaúcho", "sub": "pancadas passageiras hoje", "lon": -51.3, "lat": -29.9, "ini": em("f3", "pancadas"), "fim": em("f3", "litoral"), "h": 200},
    {"nome": "Litoral de SC e RS", "sub": "ventos costeiros · alerta laranja", "lon": -48.6, "lat": -27.6, "ini": em("f3", "115") - .3, "fim": ini("f4"), "h": 200},
    {"nome": "Minas Gerais", "sub": "245 cidades em alerta laranja", "lon": -44.6, "lat": -18.6, "ini": MINAS, "fim": BRASIL, "h": 220},
    {"nome": "Rio de Janeiro", "sub": "26 mm previstos hoje", "lon": -43.20, "lat": -22.91, "ini": RIO, "fim": ini("f6"), "h": 330},
    {"nome": "Urubici · Serra Catarinense", "sub": "5 °C no domingo", "lon": -49.59, "lat": -28.01, "ini": em("f7", "Serra"), "fim": ini("f8"), "h": 200},
    {"nome": "Campos de Palmas", "sub": "5 °C no domingo", "lon": -51.99, "lat": -26.48, "ini": em("f7", "Palmas"), "fim": ini("f8"), "h": 180},
    {"nome": "Topo da serra", "sub": "abaixo de 0 °C · segunda", "lon": -49.59, "lat": -28.01, "ini": ZERO - .3, "fim": ini("f9"), "h": 200},
    {"nome": "Oeste de Santa Catarina", "sub": "chuva na terça à noite", "lon": -52.6, "lat": -26.9, "ini": em("f9", "oeste"), "fim": ini("f10"), "h": 200},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
conta = lambda ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0: {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra) - lead, "dur": lead, "cor": cor, "unid": unid}
hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o número da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:92px;color:#96d2ff">ABAIXO DE 0 °C</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">geada prevista na segunda na Serra Catarinense</div>'}]
D_BR = max(BRASIL - LEAD, em("f4", "245") + .3)   # o total do Brasil sobe de 245 a 370 até a palavra
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "POR QUE · PREVISÃO",
     "itens": [{"t": em("f2", "ciclone"), "txt": "🌀 ciclone extratropical no Atlântico"},
               {"t": MAR_T, "txt": "🌊 mar agitado · água até 2 °C mais fria que o normal"},
               {"t": em("f2", "frio"), "txt": "❄️ ar frio no Sul"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "HOJE, 17/10 · VENTOS COSTEIROS",
     "contador": conta(115, "f3", "115", "#ff8c1a", "CIDADES EM ALERTA"),
     "l": "SC 71 · RS 43 · PR 1 · alerta laranja (INMET)", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f4"), "fim": D_BR, "k": "ALERTA LARANJA · MINAS GERAIS",
     "contador": conta(245, "f4", "245", "#ff8c1a", "CIDADES EM MG", lead=min(LEAD, em("f4", "245") - ini("f4") - .05)),
     "l": "tempestade hoje · INMET, 17/10", "borda": "rgba(255,140,26,.7)"},
]
paineis.append({"ini": paineis[-1]["fim"], "fim": ini("f5"), "k": "BRASIL INTEIRO · HOJE",
                "contador": {"de": 245, "ate": 370, "dec": 0, "ini": D_BR, "dur": max(.4, em("f4", "370") - D_BR),
                             "cor": "#ff8c1a", "unid": "CIDADES NO BRASIL"},
                "l": "MG 245 · ES 78 · RJ 26 · BA 21 · alerta laranja", "borda": "rgba(255,140,26,.7)"})
paineis += [
    {"ini": ini("f5"), "fim": ini("f6"), "k": "CHUVA PREVISTA HOJE · CAPITAIS",
     "contador": conta(26, "f5", "26", "#5ec8ff", "MM"),
     "l": "Rio de Janeiro · Vitória 13 · coluna = mm previstos", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "DOMINGO, 18/10 (PREVISÃO)",
     "itens": [{"t": em("f6", "Sudeste"), "txt": "⛈️ pancadas no Sudeste"},
               {"t": em("f6", "Centro-Oeste"), "txt": "⛈️ no Centro-Oeste"},
               {"t": em("f6", "Norte"), "txt": "⛈️ e no Norte"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "FRIO · DOMINGO (PREVISÃO)",
     "contador": conta(5, "f7", "5", "#96d2ff", "°C AO AMANHECER", de=20),
     "l": "Serra Catarinense e Campos de Palmas · 8 a 10 °C nas demais áreas", "borda": "rgba(150,210,255,.8)"},
    {"ini": em("f8", "temperatura") - .2, "fim": ini("f9"), "k": "SEGUNDA, 19/10 · GEADA (PREVISÃO)",
     "contador": conta(0, "f8", "zero", "#96d2ff", "°C OU MENOS", de=5, lead=min(LEAD, ZERO - em("f8", "temperatura") + .15)),
     "l": "topo da Serra Catarinense · geada também em Palmas e no meio-oeste", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "TERÇA, 20/10 (PREVISÃO)",
     "itens": [{"t": em("f9", "frio"), "txt": "🌡️ o frio perde força"},
               {"t": em("f9", "chuva"), "txt": "🌧️ à noite, chuva no PR e no oeste de SC"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "SUL · CHUVA PREVISTA EM 7 DIAS (MM SOMADOS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f10") + .3, "dur": 1.6},
     "l": "soma nas capitais do Sul · 53 mm na sexta, 23/10", "borda": "rgba(60,150,255,.7)"},
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
    {"ini": CAPA, "fim": MAR_T, "html": f"<b>{MET}</b> · satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": MAR_T, "fim": ini("f3"), "html": f"<b>{MET}</b> · anomalia da temperatura do mar em 16/10: GHRSST MUR via <b>NASA</b> GIBS"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b> · <b>INMET</b>, ventos costeiros para 17/10 (115 municípios)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INMET</b>, aviso laranja de tempestade para 17/10: MG 245, Brasil 370 municípios"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"{OM} para 17/10 · altura da coluna = milímetros previstos"},
    {"ini": ini("f6"), "fim": GEADA, "html": f"<b>{MET}</b>"},
    {"ini": GEADA, "fim": ini("f9"), "html": f"<b>{MET}</b> · foto da geada: ilustração"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": f"<b>{MET}</b> · {OM}, 17 a 23/10"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "temporais": "#ff8c1a", "tempestade": "#ff8c1a",
         "alerta": "#ff8c1a", "laranja": "#ff8c1a", "ciclone": "#ff8c1a", "pancadas": "#ff8c1a", "agitado": "#ff8c1a",
         "ventos": "#ff8c1a", "costeiros": "#ff8c1a", "frio": "#96d2ff", "geada": "#96d2ff", "graus": "#96d2ff", "zero": "#96d2ff",
         "sol": AM, "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sudeste", "minas", "rio", "janeiro", "brasil", "sul", "parana", "santa", "catarina", "catarinense", "gaucho", "litoral",
         "atlantico", "mar", "serra", "campos", "palmas", "centrooeste", "norte", "oeste", "centroleste", "inemaclub", "onde"}
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
     "camera": camera, "sat": SAT, "imagens": imagens, "colunas": colunas, "telas": telas, "estados": estados, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"vento hoje {VENTO} · tempestade hoje {SAB} · 7 dias {ROTD} · Sul {SULV}")
