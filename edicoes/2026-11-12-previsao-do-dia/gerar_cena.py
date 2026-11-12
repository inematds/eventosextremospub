#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 12/11/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "SEXTA: 794 CIDADES DE MINAS EM ALERTA DE TEMPESTADE"),
IR de 24 h no Sul (baixa pressão fraca, sem ciclone, pancadas mal distribuídas), aviso de tempestade de hoje (2.746, SP 645)
com granizo (ilustração), pancadas tarde/noite no SE e manhã no CO, aviso de sexta (2.343, MG 794), calor em Teresina
(40 °C no sábado), fim de semana de sol e calorão, gráfico do Sul (domingo 15 = maior risco de temporal) e colunas 3D
da chuva prevista em 7 dias nas capitais (Cuiabá 119 mm).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "12/11/2026"
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
MG = {"lon": -44.6, "lat": -18.6, "zoom": 5.2}        # f1 e f6: Minas, 794 cidades em alerta na sexta
SUL2 = {"lon": -52.0, "lat": -28.0, "zoom": 5.2}      # f2: baixa pressão fraca, Sul quente e abafado
SC = {"lon": -51.0, "lat": -26.8, "zoom": 5.5}        # f3: temporal isolado SC, norte gaúcho, PR
CON = {"lon": -49.0, "lat": -17.0, "zoom": 4.2}       # f4: 2.746 cidades hoje, SP 645, granizo
SECO = {"lon": -49.5, "lat": -17.5, "zoom": 4.6}      # f5: SP e MG tarde/noite; MT, GO, sudeste da BA de manhã
TER = {"lon": -43.3, "lat": -6.5, "zoom": 5.1}        # f7: Teresina 40 °C no sábado (lon -41 mostrava a borda leste)
FDS = {"lon": -51.0, "lat": -25.5, "zoom": 4.7}       # f8: sol no Sul, SP e MS
SUL3 = {"lon": -51.5, "lat": -25.8, "zoom": 5.1}      # f9: domingo 15 (centro ao norte: o Sul desce, o pino sai de baixo do gráfico)
COL = {"lon": -52.0, "lat": -15.5, "zoom": 4.5}       # f10: colunas 3D (7 dias nas capitais)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
GRAN = em("f4", "risco") - .1      # foto do granizo em "com risco de granizo"
GFIM = ini("f5") + .25
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, MG, 0, 0), K(fim("f1") - .2, {**MG, "zoom": 5.3}, 0, 0),
    K(ini("f2") + 1.0, SUL2, 30, -8), K(fim("f2") - .2, {**SUL2, "zoom": 5.4}, 40, 6),
    K(ini("f3") + 1.0, SC, 30, 6), K(fim("f3") - .2, {**SC, "zoom": 5.6}, 0, 0),
    K(ini("f4") + 1.0, CON, 0, 0), K(GRAN, {**CON, "zoom": 4.3}, 0, 0),
    K(ini("f5") + 1.0, SECO, 0, 0), K(fim("f5") - .2, {**SECO, "zoom": 4.7}, 0, 0),
    K(ini("f6") + 1.0, MG, 0, 0), K(fim("f6") - .2, {**MG, "zoom": 5.3}, 0, 0),
    K(ini("f7") + 1.0, TER, 0, 0), K(fim("f7") - .2, {**TER, "zoom": 5.2}, 0, 0),
    K(ini("f8") + 1.0, FDS, 0, 0), K(fim("f8") - .2, {**FDS, "zoom": 4.8}, 0, 0),
    K(ini("f9") + 1.0, SUL3, 35, -10), K(fim("f9") - .2, {**SUL3, "zoom": 5.3}, 45, 8),
    K(ini("f10") + 1.2, COL, 55, -20), K(fim("f10") - .2, {**COL, "zoom": 4.6}, 56, 15),
    K(ini("f11") + 1.4, {"lon": -50.0, "lat": -16.0, "zoom": 4.4}, 0, 0), K(DUR, {"lon": -50.0, "lat": -16.0, "zoom": 4.5}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) (f1–f3)
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


IRF = fim("f3") - .3
# câmera inclinada: o Blue Marble do mundo por baixo do geocolor (sem borda preta)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": CAPA - .3, "fim": IRF, "dur": IRF - CAPA, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

# ---------------------------------------------------------------- previsão Open-Meteo nas capitais (7 dias)
OMC = json.loads((B / "openmeteo_capitais_3d.json").read_text())
CAPS = {"Cuiabá": (-15.64, -56.1), "Goiânia": (-16.7, -49.26), "Palmas": (-10.16, -48.32), "Brasília": (-15.78, -47.89),
        "Belo Horizonte": (-19.92, -43.94), "Porto Velho": (-8.75, -63.93), "Campo Grande": (-20.49, -54.65)}
OUTRAS = {"Porto Alegre": (-30.03, -51.23), "Teresina": (-5.09, -42.8)}


def cap(nome):
    la, lo = {**CAPS, **OUTRAS}[nome]
    x = min(OMC, key=lambda c: abs(c["latitude"] - la) + abs(c["longitude"] - lo))
    assert abs(x["latitude"] - la) < .15 and abs(x["longitude"] - lo) < .15, (nome, x["latitude"], x["longitude"])
    assert x["daily"]["time"][0] == "2026-11-12", x["daily"]["time"]
    return x


SOMA7 = {nm: round(sum(v or 0 for v in cap(nm)["daily"]["precipitation_sum"])) for nm in CAPS}
assert SOMA7["Cuiabá"] == 119 and SOMA7["Goiânia"] == 71 and SOMA7["Palmas"] == 61, SOMA7   # f10
assert max(SOMA7.values()) == SOMA7["Cuiabá"], SOMA7
PA = cap("Porto Alegre")["daily"]
PA_TX = [round(v) for v in PA["temperature_2m_max"]]
TE = cap("Teresina")["daily"]
TE_TX = [round(v) for v in TE["temperature_2m_max"]]
assert TE_TX[0] == 39 and TE_TX[2] == 40 and TE["time"][2] == "2026-11-14", TE_TX   # f7: 40 °C no sábado

# colunas 3D: chuva PREVISTA somada em 7 dias nas capitais do Centro-Oeste, Norte e Sudeste
col = [{"id": i, "p": [cap(nm)["longitude"], cap(nm)["latitude"]], "v": v, "cor": [60, 150, 255] if v >= 60 else [120, 190, 255]}
       for i, (nm, v) in enumerate(SOMA7.items())]
ordem = {c["id"]: i * .15 for i, c in enumerate(sorted(col, key=lambda c: -c["v"]))}
colunas = [{"id": "chuva7d", "ini": ini("f10") + .3, "fim": ini("f11") + .3, "dados": col, "raio": 45000, "escala": 4200, "ordem": ordem, "varredura": 1}]

P7 = json.loads((B / "previsao7d.json").read_text())
HOJE_D = "2026-11-12"
assert P7["dias"][0] == HOJE_D and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qui", "sex", "sáb", "dom", "seg", "ter", "qua"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
assert max(SULV) == SULV[3], SULV   # domingo, 15: pico da chuva no Sul
series = [{"nome": "Chuva no Sul (mm)", "cor": "#5ec8ff", "v": SULV}]

rios = []

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, granizo
assert GFIM - GRAN > .8, (GRAN, GFIM)
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .02},
         {"src": "capa-dia/granizo.png", "ini": GRAN, "fim": GFIM, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
HOJE = ufs_av(56383, 20)    # tempestade hoje 12/11: 2.746 (SP 645, MG 551, PR 399, GO 246, SC 213)
assert len(geo(56383)) == 2746 and aviso[56383]["descricao"] == "Tempestade" and aviso[56383]["inicio"].startswith("2026-11-12")
assert (por_uf(56383, "SP"), por_uf(56383, "MG"), por_uf(56383, "PR"), por_uf(56383, "GO"), por_uf(56383, "SC")) == (645, 551, 399, 246, 213)
assert "granizo" in aviso[56383]["riscos"][0] and "40-60 km/h" in aviso[56383]["riscos"][0]
SEXTA = ufs_av(56389, 20)   # tempestade sexta 13/11: 2.343 (MG 794, SP 645, GO 246, MT 141, TO 103, RJ 92)
assert len(geo(56389)) == 2343 and aviso[56389]["descricao"] == "Tempestade" and aviso[56389]["inicio"].startswith("2026-11-13")
assert (por_uf(56389, "MG"), por_uf(56389, "SP"), por_uf(56389, "GO"), por_uf(56389, "MT"), por_uf(56389, "TO"), por_uf(56389, "RJ")) == (794, 645, 246, 141, 103, 92)
estados = [
    {"id": "minas", "ini": CAPA, "fim": ini("f2") + .3, "ufs": ["MG"], "cor": LAR, "alfa": .5},
    {"id": "sul_quente", "ini": em("f2", "quente"), "fim": ini("f3") + .3, "ufs": ["PR", "SC", "RS"], "cor": LAR, "alfa": .3},
    {"id": "sul_temporal", "ini": em("f3", "Santa"), "fim": ini("f4") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .4},
    {"id": "hoje", "ini": ini("f4"), "fim": GRAN + .3, "ufs": HOJE, "cor": LAR, "alfa": .45},
    {"id": "tarde", "ini": em("f5", "Paulo"), "fim": em("f5", "Mato") + .3, "ufs": ["SP", "MG"], "cor": AZUL, "alfa": .4},
    {"id": "manha", "ini": em("f5", "Mato"), "fim": ini("f6") + .3, "ufs": ["MT", "GO", "BA"], "cor": AZUL, "alfa": .4},
    {"id": "sexta", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": SEXTA, "cor": LAR, "alfa": .45},
    {"id": "calor_pi", "ini": em("f7", "calor"), "fim": ini("f8") + .3, "ufs": ["PI"], "cor": VERM, "alfa": .45},
    {"id": "sol", "ini": em("f8", "sol"), "fim": ini("f9") + .3, "ufs": ["PR", "SC", "RS", "SP", "MS"], "cor": LAR, "alfa": .35},
    {"id": "domingo", "ini": em("f9", "risco"), "fim": ini("f10") + .3, "ufs": ["PR", "SC", "RS"], "cor": VERM, "alfa": .4},
]

pinos = [
    {"nome": "Sul, hoje", "sub": "quente e abafado, acima de 30 °C (previsão)", "lon": -52.5, "lat": -28.8, "ini": em("f2", "quente"), "fim": ini("f3"), "h": 150},
    {"nome": "Santa Catarina e Paraná", "sub": "temporal isolado à tarde (previsão)", "lon": -50.5, "lat": -26.6, "ini": em("f3", "temporal"), "fim": ini("f4"), "h": 160},
    {"nome": "São Paulo, hoje", "sub": "645 cidades em alerta de tempestade (INMET)", "lon": -48.5, "lat": -22.3, "ini": em("f4", "645"), "fim": GRAN, "h": 180},
    {"nome": "Mato Grosso e Goiás", "sub": "pancadas já pela manhã (previsão)", "lon": -52.5, "lat": -15.0, "ini": em("f5", "manhã"), "fim": ini("f6"), "h": 150},
    {"nome": "Minas Gerais, sexta", "sub": "794 cidades em alerta de tempestade (INMET)", "lon": -44.6, "lat": -18.6, "ini": em("f6", "794"), "fim": ini("f7"), "h": 170},
    {"nome": "Teresina", "sub": f"máxima {TE_TX[0]} °C hoje → {TE_TX[2]} °C sábado (previsão)", "lon": -42.8, "lat": -5.09, "ini": em("f7", "Teresina"), "fim": ini("f8"), "h": 160},
    {"nome": "Sul, domingo 15", "sub": "maior risco de temporal (previsão)", "lon": -52.5, "lat": -29.2, "ini": em("f9", "temporal"), "fim": ini("f10"), "h": 90},
    {"nome": "Cuiabá", "sub": f"{SOMA7['Cuiabá']} mm em 7 dias (previsão)", "lon": -56.1, "lat": -15.6, "ini": em("f10", "Cuiabá"), "fim": ini("f11"), "h": 280},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0


def conta(ate, fid, palavra, cor, unid, dec=0, de=0, k=1, desde=None):
    t = em(fid, palavra, k)
    lead = max(.4, min(LEAD, t - (desde if desde is not None else ini(fid))))   # número logo no começo: o contador cabe no painel
    return {"de": de, "ate": ate, "dec": dec, "ini": t - lead, "dur": lead, "cor": cor, "unid": unid}


GD = max(ini("f9") + 1.0, em("f9", "domingo"))   # "domingo" é a 3ª palavra: o gráfico começa com o painel
GS = em("f9", "Sul")
hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o fato da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:76px;color:#FACC15">794 CIDADES</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">de Minas em alerta de tempestade amanhã, sexta (INMET)</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "HOJE, 12/11 · PREVISÃO",
     "itens": [{"t": em("f2", "ciclone"), "txt": "🌀 Sem ciclone: baixa pressão fraca"}, {"t": em("f2", "quente"), "txt": "🌡️ Sul quente e abafado, acima de 30 °C"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "HOJE À TARDE · PREVISÃO",
     "itens": [{"t": em("f3", "pancadas"), "txt": "🌦️ Pancadas mal distribuídas"}, {"t": em("f3", "temporal"), "txt": "⛈️ Temporal isolado: SC, norte do RS e PR"}],
     "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f4"), "fim": GRAN - .05, "k": "HOJE, 12/11 · ALERTA DE TEMPESTADE",
     "contador": conta(2746, "f4", "2.746", "#ff8c1a", "CIDADES"),
     "l": "SP 645 · MG 551 · PR 399 · GO 246 · SC 213 · granizo e vento de 40 a 60 km/h (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": GFIM, "fim": ini("f6"), "k": "HOJE · ONDE CHOVE (PREVISÃO)",
     "itens": [{"t": max(GFIM, em("f5", "tarde")), "txt": "🌇 SP e MG: tarde e noite"}, {"t": em("f5", "manhã"), "txt": "🌅 MT, GO e sudeste da BA: já de manhã"}],
     "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SEXTA, 13/11 · ALERTA DE TEMPESTADE",
     "contador": conta(794, "f6", "794", "#ff8c1a", "CIDADES EM MINAS"),
     "l": "2.343 cidades no país · SP 645 · GO 246 · MT 141 · TO 103 · RJ 92 (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "PIAUÍ · CALOR (PREVISÃO)",
     "contador": conta(TE_TX[2], "f7", "40", "#ff2a1f", "°C"),
     "l": f"Teresina: {TE_TX[0]} °C hoje → {TE_TX[2]} °C no sábado (Open-Meteo)", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "FIM DE SEMANA · PREVISÃO",
     "itens": [{"t": em("f8", "sol"), "txt": "☀️ Sol no Sul, em SP e no MS"}, {"t": em("f8", "calorão"), "txt": "🌡️ Calorão acima de 30 °C"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "SUL · PRÓXIMOS 7 DIAS (PREVISÃO)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": GD - 1.0, "dur": GS - GD + 1.0,
                 "linha": {"nome": "Máxima em Porto Alegre", "cor": "#ff8c1a", "v": PA_TX, "unid": "°C"}},
     "l": "domingo, 15/11: maior risco de temporal · chuva em mm somados nas capitais do Sul (Open-Meteo)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "CHUVA PREVISTA · 7 DIAS",
     "contador": conta(SOMA7["Cuiabá"], "f10", "119", "#5ec8ff", "MM EM CUIABÁ"),
     "l": f"Goiânia {SOMA7['Goiânia']} · Palmas {SOMA7['Palmas']} · Brasília {SOMA7['Brasília']} · Belo Horizonte {SOMA7['Belo Horizonte']} mm (Open-Meteo)", "borda": "rgba(60,150,255,.85)"},
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
    for g in ("ranking", "grafico"):
        if a.get(g):
            assert a["ini"] - .01 <= a[g]["ini"] and a[g]["ini"] + a[g]["dur"] <= a["fim"] + .01, (g + " fora do painel", a["k"])

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

GOES = f"satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"
fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "<b>INMET</b>, aviso de tempestade 13/11 (2.343 municípios, MG 794)"},
    {"ini": ini("f2"), "fim": ini("f4"), "html": f"<b>{MET}</b> · {GOES}"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso de tempestade 12/11 (2.746 municípios) · foto do granizo: ilustração"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INMET</b>, aviso de tempestade 13/11 (2.343 municípios)"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"{OM}, 12/11 a 18/11"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · {OM}, 12/11 a 18/11"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b> · {OM}, 12/11 a 18/11"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "pancadas": "#5ec8ff", "chove": "#5ec8ff", "milimetros": "#5ec8ff",
         "granizo": "#ff2a1f", "tempestade": "#ff8c1a", "temporal": "#ff8c1a", "ciclone": "#ff8c1a",
         "alerta": "#ff2a1f", "atencao": "#ff2a1f", "risco": "#ff2a1f", "atinge": "#ff2a1f", "dispara": "#ff2a1f",
         "calor": "#ff2a1f", "calorao": "#ff2a1f", "quente": "#ff2a1f", "abafado": "#ff2a1f", "graus": "#ff2a1f", "sol": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "minas", "gerais", "santa", "catarina", "parana", "gaucho", "sao", "paulo", "mato", "grosso", "goias", "bahia",
         "piaui", "teresina", "cuiaba", "pais", "hoje", "amanha", "quinta", "sabado", "domingo", "inemaclub", "onde", "do"}
LUGAR.discard("do")
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
      f"hoje {HOJE} · sexta {SEXTA} · 7d {SOMA7} · Teresina {TE_TX} · Sul {SULV}")
