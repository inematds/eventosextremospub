#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 08/11/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "633 CIDADES EM PERIGO DE TEMPESTADE · 421 SÓ EM MINAS HOJE"),
aviso de perigo (laranja) do INMET de hoje (633: MG 421) pintado, alta pressão no Sul × pancadas no SE/CO, foto do granizo
(ilustração) no critério do aviso, aviso de tempestade de hoje (1.894), Belo Horizonte 58 mm na segunda, colunas 3D da chuva
prevista em 7 dias nas capitais do SE/CO, máxima de BH 27 → 19 °C, aviso de segunda (1.176), Sul firma (Serra Gaúcha, Vale do
Itajaí), gráfico dos 7 dias.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "08/11/2026"
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
BR = {"lon": -50.0, "lat": -16.0, "zoom": 3.9}
MG = {"lon": -45.6, "lat": -18.6, "zoom": 5.4}        # f1: 633 cidades em perigo, 421 em Minas
SULSE = {"lon": -49.0, "lat": -22.5, "zoom": 4.3}     # f2: alta pressão no Sul × pancadas no SE/CO
CRIT = {"lon": -45.0, "lat": -19.2, "zoom": 5.8}      # f3: critério do aviso laranja
SE = {"lon": -47.5, "lat": -19.0, "zoom": 4.8}        # f4: MG, GO, SP, ES na faixa laranja; 1.894
BHC = {"lon": -43.94, "lat": -19.92, "zoom": 7.6}     # f5/f7: Belo Horizonte
COL = {"lon": -47.0, "lat": -17.5, "zoom": 4.9}       # f6: colunas 3D (7 dias nas capitais)
MGBA = {"lon": -44.0, "lat": -15.0, "zoom": 4.7}      # f8: segunda, de Minas até a Bahia
SUL = {"lon": -51.0, "lat": -27.6, "zoom": 5.4}       # f9: Sul firma; Serra Gaúcha, Vale do Itajaí
SUL7 = {"lon": -50.5, "lat": -24.0, "zoom": 4.5}      # f10: próximos dias
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
GRAN = em("f3", "vento") - .1       # foto do granizo em "vento de até 100 quilômetros por hora e granizo"
GFIM = fim("f3") - .15
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, MG, 0, 0), K(fim("f1") - .2, {**MG, "zoom": 5.5}, 0, 0),
    K(ini("f2") + 1.0, SULSE, 0, 0), K(fim("f2") - .2, {**SULSE, "zoom": 4.4}, 0, 0),
    K(ini("f3") + 1.0, CRIT, 30, -8), K(fim("f3") - .2, {**CRIT, "zoom": 6.0}, 40, 6),
    K(ini("f4") + 1.2, SE, 35, -10), K(fim("f4") - .2, {**SE, "zoom": 4.9}, 45, 8),
    K(ini("f5") + 1.2, BHC, 35, -10), K(fim("f5") - .2, {**BHC, "zoom": 7.8}, 45, 10),
    K(ini("f6") + 1.2, COL, 55, -20), K(fim("f6") - .2, {**COL, "zoom": 5.0}, 56, 15),
    K(ini("f7") + 1.0, {**BHC, "zoom": 5.6}, 0, 0), K(fim("f7") - .2, {**BHC, "zoom": 5.8}, 0, 0),
    K(ini("f8") + 1.0, MGBA, 0, 0), K(fim("f8") - .2, {**MGBA, "zoom": 4.8}, 0, 0),
    K(ini("f9") + 1.0, SUL, 30, 0), K(fim("f9") - .2, {**SUL, "zoom": 5.6}, 40, 10),
    K(ini("f10") + 1.0, SUL7, 0, 0), K(fim("f10") - .2, {**SUL7, "zoom": 4.6}, 0, 0),
    K(ini("f11") + 1.4, {"lon": -50.0, "lat": -16.0, "zoom": 4.4}, 0, 0), K(DUR, {"lon": -50.0, "lat": -16.0, "zoom": 4.5}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) (f1–f2)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 130]
assert len(BONS) >= 36, BONS
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


IRF = fim("f2") - .3
# câmera inclinada: o Blue Marble do mundo por baixo do geocolor (sem borda preta)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": CAPA - .3, "fim": IRF, "dur": IRF - CAPA, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

# ---------------------------------------------------------------- previsão Open-Meteo nas capitais (7 dias)
OMC = json.loads((B / "openmeteo_capitais_3d.json").read_text())
CAPS = {"Belo Horizonte": (-19.93, -43.97), "Brasília": (-15.78, -47.89), "Goiânia": (-16.7, -49.26), "Vitória": (-20.35, -40.34),
        "Palmas": (-10.16, -48.32), "Cuiabá": (-15.64, -56.1), "Rio de Janeiro": (-22.95, -43.22)}


def cap(nome):
    la, lo = CAPS[nome]
    x = min(OMC, key=lambda c: abs(c["latitude"] - la) + abs(c["longitude"] - lo))
    assert abs(x["latitude"] - la) < .1 and abs(x["longitude"] - lo) < .1, nome
    assert x["daily"]["time"][0] == "2026-11-08", x["daily"]["time"]
    return x


BH = cap("Belo Horizonte")["daily"]
BH_SEG = BH["precipitation_sum"][1]
BH_7D = round(sum(v or 0 for v in BH["precipitation_sum"]))
BH_TX = (round(BH["temperature_2m_max"][0]), round(BH["temperature_2m_max"][1]))
assert round(BH_SEG) == 58 and BH_7D == 115 and BH_TX == (27, 19), (BH_SEG, BH_7D, BH_TX)   # falas f5, f6, f7
SOMA7 = {nm: round(sum(v or 0 for v in cap(nm)["daily"]["precipitation_sum"])) for nm in CAPS}
assert SOMA7["Brasília"] > 90, SOMA7   # f6: "passa de 90 em Brasília"

# colunas 3D: chuva PREVISTA somada em 7 dias nas capitais do Sudeste e Centro-Oeste
col = [{"id": i, "p": [cap(nm)["longitude"], cap(nm)["latitude"]], "v": v, "cor": [60, 150, 255] if v >= 80 else [120, 190, 255]}
       for i, (nm, v) in enumerate(SOMA7.items())]
ordem = {c["id"]: i * .15 for i, c in enumerate(sorted(col, key=lambda c: -c["v"]))}
colunas = [{"id": "chuva7d", "ini": ini("f6") + .3, "fim": ini("f7") + .3, "dados": col, "raio": 45000, "escala": 4200, "ordem": ordem, "varredura": 1}]

P7 = json.loads((B / "previsao7d.json").read_text())
HOJE_D = "2026-11-08"
assert P7["dias"][0] == HOJE_D and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
SEV = [d["por_regiao_mm"]["SE"] for d in P7["por_dia"]]
COV = [d["por_regiao_mm"]["CO"] for d in P7["por_dia"]]
assert SEV[1] == max(SEV) and round(SEV[0]) == 48 and round(SEV[1]) == 74, SEV   # Sudeste: pico na segunda
series = [{"nome": "Sudeste", "cor": "#ff8c1a", "v": SEV}, {"nome": "Centro-Oeste", "cor": "#a78bfa", "v": COV},
          {"nome": "Sul", "cor": "#5ec8ff", "v": SULV}]

rios = []

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, granizo
assert GFIM - GRAN > 1.0, (GRAN, GFIM)
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .02},
         {"src": "capa-dia/granizo.png", "ini": GRAN, "fim": GFIM, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
PER = ufs_av(56346)   # tempestade PERIGO (laranja) hoje 8/11, 08h45–23h59: 633 (MG 421)
assert len(geo(56346)) == 633 and aviso[56346]["descricao"] == "Tempestade" and aviso[56346]["severidade"] == "Perigo"
assert aviso[56346]["inicio"].startswith("2026-11-08") and PER == ["ES", "GO", "MG", "MS", "SP"], PER
assert (por_uf(56346, "MG"), por_uf(56346, "GO"), por_uf(56346, "SP"), por_uf(56346, "ES")) == (421, 83, 71, 38)
HOJE_T = set()
for a in AV["hoje"]:
    if a["descricao"] == "Tempestade" and a["inicio"].startswith("2026-11-08"):
        HOJE_T |= set(a["geocodes"].split(","))
assert len(HOJE_T) == 1894, len(HOJE_T)   # f4: 1.894
HOJE_UF = sorted({UF[c[:2]] for c in HOJE_T if sum(x[:2] == c[:2] for x in HOJE_T) >= 5})
hoje_uf = lambda uf: sum(UF[c[:2]] == uf for c in HOJE_T)
assert (hoje_uf("MG"), hoje_uf("SP"), hoje_uf("GO"), hoje_uf("RJ"), hoje_uf("ES")) == (853, 439, 246, 92, 78)
SEG = ufs_av(56352)   # tempestade segunda 9/11: 1.176
assert len(geo(56352)) == 1176 and aviso[56352]["descricao"] == "Tempestade" and aviso[56352]["inicio"].startswith("2026-11-09")
assert (por_uf(56352, "MG"), por_uf(56352, "BA"), por_uf(56352, "GO"), por_uf(56352, "ES")) == (514, 267, 241, 78)
FRIO_UF = ufs_av(56333)   # declínio de temperatura segunda 9/11 (MG 748)
assert aviso[56333]["descricao"] == "Declínio de Temperatura" and aviso[56333]["inicio"].startswith("2026-11-09") and por_uf(56333, "MG") == 748
estados = [
    {"id": "perigo", "ini": CAPA, "fim": ini("f2") + .3, "ufs": PER, "cor": LAR, "alfa": .45},
    {"id": "alta", "ini": em("f2", "alta"), "fim": em("f2", "pancadas") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .35},
    {"id": "pancadas", "ini": em("f2", "pancadas"), "fim": ini("f3") + .3, "ufs": ["MG", "SP", "RJ", "ES", "GO", "DF", "MS", "MT"], "cor": LAR, "alfa": .35},
    {"id": "perigo2", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": PER, "cor": LAR, "alfa": .45},
    {"id": "hoje", "ini": em("f4", "Minas"), "fim": ini("f5") + .3, "ufs": HOJE_UF, "cor": LAR, "alfa": .4},
    {"id": "bh", "ini": em("f5", "Belo"), "fim": ini("f6") + .3, "ufs": ["MG"], "cor": AZUL, "alfa": .3},
    {"id": "frio", "ini": em("f7", "temperatura"), "fim": ini("f8") + .3, "ufs": FRIO_UF, "cor": FRIO, "alfa": .35},
    {"id": "segunda", "ini": em("f8", "aviso"), "fim": ini("f9") + .3, "ufs": SEG, "cor": LAR, "alfa": .4},
    {"id": "sul", "ini": em("f9", "Sul"), "fim": ini("f10") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .3},
]

pinos = [
    {"nome": "Minas Gerais, hoje", "sub": "421 cidades em perigo de tempestade (INMET)", "lon": -44.5, "lat": -18.3, "ini": em("f1", "Minas"), "fim": ini("f2"), "h": 200},
    {"nome": "Sul", "sub": "alta pressão empurra a chuva (previsão)", "lon": -52.0, "lat": -28.5, "ini": em("f2", "alta"), "fim": ini("f3"), "h": 120},
    {"nome": "Sudeste e Centro-Oeste", "sub": "pancadas fortes (previsão)", "lon": -46.5, "lat": -19.0, "ini": em("f2", "Sudeste"), "fim": ini("f3"), "h": 220},
    {"nome": "Goiás", "sub": "83 cidades em perigo (INMET)", "lon": -49.6, "lat": -16.0, "ini": em("f4", "Goiás"), "fim": ini("f5"), "h": 120},
    {"nome": "São Paulo", "sub": "71 cidades em perigo (INMET)", "lon": -48.5, "lat": -21.8, "ini": em("f4", "Paulo"), "fim": ini("f5"), "h": 60},
    {"nome": "Espírito Santo", "sub": "38 cidades em perigo (INMET)", "lon": -40.7, "lat": -19.6, "ini": em("f4", "Espírito"), "fim": ini("f5"), "h": 240},
    {"nome": "Belo Horizonte", "sub": f"{round(BH_SEG)} mm na segunda (previsão)", "lon": -43.94, "lat": -19.92, "ini": em("f5", "Belo"), "fim": ini("f6"), "h": 180},
    {"nome": "Belo Horizonte", "sub": f"máxima {BH_TX[0]} °C hoje → {BH_TX[1]} °C segunda (previsão)", "lon": -43.94, "lat": -19.92, "ini": em("f7", "Belo"), "fim": ini("f8"), "h": 180},
    {"nome": "Bahia, segunda", "sub": "267 cidades em aviso de tempestade (INMET)", "lon": -41.5, "lat": -13.0, "ini": em("f8", "Bahia"), "fim": ini("f9"), "h": 160},
    {"nome": "Serra Gaúcha", "sub": "garoa hoje (previsão)", "lon": -51.2, "lat": -29.15, "ini": em("f9", "Serra"), "fim": ini("f10"), "h": 25},
    {"nome": "Vale do Itajaí", "sub": "fique de olho nos rios", "lon": -49.64, "lat": -27.21, "ini": em("f9", "Vale"), "fim": ini("f10"), "h": 200},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0


def conta(ate, fid, palavra, cor, unid, dec=0, de=0, k=1, desde=None):
    t = em(fid, palavra, k)
    lead = max(.4, min(LEAD, t - (desde if desde is not None else ini(fid))))   # número logo no começo: o contador cabe no painel
    return {"de": de, "ate": ate, "dec": dec, "ini": t - lead, "dur": lead, "cor": cor, "unid": unid}


hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o fato da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:76px;color:#FACC15">633 CIDADES</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">em perigo de tempestade hoje · 421 em Minas · INMET</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "HOJE, 8/11 · PREVISÃO",
     "itens": [{"t": em("f2", "alta"), "txt": "🌀 Alta pressão empurra a chuva no Sul"}, {"t": em("f2", "pancadas"), "txt": "⛈️ Pancadas fortes no Sudeste e Centro-Oeste"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f3"), "fim": GRAN - .1, "k": "PERIGO · CRITÉRIO DO INMET",
     "itens": [{"t": em("f3", "100"), "txt": "🌧️ Até 100 mm no dia"}],
     "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE, 8/11 · AVISO DE TEMPESTADE",
     "contador": conta(1894, "f4", "1.894", "#ff8c1a", "CIDADES"),
     "l": "MG 853 · SP 439 · GO 246 · RJ 92 · ES 78 (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "BELO HORIZONTE · SEGUNDA, 9/11",
     "contador": conta(round(BH_SEG), "f5", "58", "#5ec8ff", "MM"),
     "l": "chuva prevista no dia (Open-Meteo)", "borda": "rgba(60,150,255,.85)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "CHUVA PREVISTA · 7 DIAS",
     "contador": conta(BH_7D, "f6", "115", "#5ec8ff", "MM EM BH"),
     "l": f"Brasília {SOMA7['Brasília']} · Goiânia {SOMA7['Goiânia']} · Vitória {SOMA7['Vitória']} mm (Open-Meteo)", "borda": "rgba(60,150,255,.85)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "BH · MÁXIMA NA SEGUNDA (PREVISÃO)",
     "contador": conta(BH_TX[1], "f7", "19", "#5ec8ff", "°C", de=BH_TX[0]),
     "l": f"{BH_TX[0]} °C hoje → {BH_TX[1]} °C na segunda (Open-Meteo)", "borda": "rgba(60,150,255,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "SEGUNDA, 9/11 · AVISO DE TEMPESTADE",
     "contador": conta(1176, "f8", "1.176", "#ff8c1a", "CIDADES"),
     "l": "MG 514 · BA 267 · GO 241 · ES 78 (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "SUL · HOJE (PREVISÃO)",
     "itens": [{"t": em("f9", "embora"), "txt": "🌤️ A chuva vai embora"}, {"t": em("f9", "garoa"), "txt": "🌫️ Garoa no centro-leste e na Serra Gaúcha"},
               {"t": em("f9", "Vale"), "txt": "🌊 Vale do Itajaí: olho nos rios"}],
     "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "PRÓXIMOS 7 DIAS (CHUVA PREVISTA)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f10") + .3, "dur": 1.6},
     "l": f"Sudeste: {round(SEV[0])} mm hoje → {round(SEV[1])} mm na segunda · mm somados nas capitais", "borda": "rgba(94,200,255,.7)"},
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

GOES = f"satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"
fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>INMET</b>, tempestade perigo 08/11 (633 municípios) · {GOES}"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · {GOES}"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INMET</b>, critério do aviso de perigo · foto do granizo: ilustração"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INMET</b>, avisos de tempestade para 08/11 (1.894 municípios)"},
    {"ini": ini("f5"), "fim": ini("f8"), "html": f"{OM}, 08/11 a 14/11"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>INMET</b>, aviso de tempestade para 09/11 (1.176 municípios)"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": f"<b>{MET}</b> · {OM}, 08/11 a 14/11"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "pancadas": "#5ec8ff", "garoa": "#5ec8ff", "frias": "#5ec8ff", "despenca": "#5ec8ff", "cair": "#5ec8ff",
         "rios": "#ff2a1f", "granizo": "#ff2a1f", "perigo": "#ff2a1f", "laranja": "#ff8c1a", "tempestade": "#ff8c1a",
         "vento": "#ff8c1a", "aviso": "#ff8c1a", "alerta": "#ff2a1f", "atencao": "#ff2a1f", "fortes": "#ff8c1a",
         "alta": "#5ec8ff", "pressao": "#5ec8ff", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"minas", "gerais", "goias", "sao", "paulo", "espirito", "santo", "belo", "horizonte", "brasilia", "bahia", "sudeste",
         "centrooeste", "centroleste", "serra", "gaucha", "vale", "itajai", "sul", "hoje", "amanha", "domingo", "segunda",
         "segundafeira", "terca", "quinta", "sexta", "inemaclub", "onde", "inmet"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        prox = t["palavras"][i + 1]["w"] if i + 1 < len(t["palavras"]) else ""
        longo = sum(len(b["w"]) + 1 for b in bloco) + len(prox) > 20   # "marcaram 500 milímetros" passava da borda
        if len(bloco) == 3 or longo or w[-1:] in ".?!,:;" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · PREVISÃO DO DIA", "selo": DATA[:5] + " · INMET · NOAA · Open-Meteo",
     "camera": camera, "sat": SAT, "imagens": [], "colunas": colunas, "rios": rios, "telas": telas, "estados": estados, "pinos": pinos,
     "hero": hero, "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"perigo {PER} · hoje {HOJE_UF} · segunda {SEG} · frio {FRIO_UF} · 7d {SOMA7}")
