#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 13/11/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET,
da previsão Open-Meteo das capitais (pesquisa/bruto) e da anomalia do mar (GHRSST MUR via NASA GIBS, 11/11).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "DOMINGO: 4.299 CIDADES EM ALERTA DE TEMPESTADE"),
Brasil pintado com o aviso de domingo, IR de 24 h (calor + umidade), aviso de hoje (2.653, MG 853) com granizo (ilustração),
Norte e Sudeste à tarde, Nordeste até 44 °C (Teresina 40 °C), Paraguai/norte da Argentina acima de 45 °C (câmera inclinada),
aviso de sábado no Sul (964, RS 497), gráfico do Sul (domingo = pico), colunas 3D de 7 dias (Cuiabá 109 mm) e
o Atlântico Sul com a anomalia real do mar (ciclones dos dias 20 e 25 no oceano).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "13/11/2026"
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
BR = {"lon": -50.0, "lat": -16.0, "zoom": 3.9}        # f1: domingo, 4.299 cidades no país
BR2 = {"lon": -52.0, "lat": -15.0, "zoom": 4.0}       # f2: calor + umidade em todo o país (IR)
MG = {"lon": -46.0, "lat": -19.5, "zoom": 4.7}        # f3: hoje 2.653, MG 853, granizo
NSE = {"lon": -52.0, "lat": -11.0, "zoom": 4.0}       # f4: Norte e Sudeste à tarde
NE = {"lon": -41.5, "lat": -8.0, "zoom": 4.9}         # f5: Nordeste até 44 °C, Teresina 40
PY = {"lon": -59.5, "lat": -24.5, "zoom": 4.9}        # f6: Paraguai e norte da Argentina acima de 45 °C
SUL = {"lon": -52.0, "lat": -27.5, "zoom": 5.2}       # f7: sábado, 964 cidades no Sul, RS 497
SUL3 = {"lon": -52.5, "lat": -27.0, "zoom": 5.1}      # f8: domingo (centro ao norte: o Sul desce, o pino sai de baixo do gráfico)
COL = {"lon": -51.0, "lat": -15.0, "zoom": 4.5}       # f9: colunas 3D (7 dias nas capitais)
MAR = {"lon": -47.0, "lat": -33.5, "zoom": 4.1}       # f10: Atlântico Sul, anomalia do mar, ciclones no oceano
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
GRAN = em("f3", "risco") - .1      # foto do granizo em "com risco de granizo"
GFIM = ini("f4") + .25
camera = [
    K(0, BR), K(CAPA, BR), K(fim("f1") - .2, {**BR, "zoom": 4.0}, 0, 0),
    K(ini("f2") + 1.0, BR2, 30, -8), K(fim("f2") - .2, {**BR2, "zoom": 4.1}, 38, 6),
    K(ini("f3") + 1.0, MG, 0, 0), K(GRAN, {**MG, "zoom": 4.8}, 0, 0),
    K(ini("f4") + 1.0, NSE, 0, 0), K(fim("f4") - .2, {**NSE, "zoom": 4.1}, 0, 0),
    K(ini("f5") + 1.0, NE, 0, 0), K(fim("f5") - .2, {**NE, "zoom": 5.0}, 0, 0),
    K(ini("f6") + 1.0, PY, 35, -10), K(fim("f6") - .2, {**PY, "zoom": 5.0}, 42, 6),
    K(ini("f7") + 1.0, SUL, 0, 0), K(fim("f7") - .2, {**SUL, "zoom": 5.3}, 0, 0),
    K(ini("f8") + 1.0, SUL3, 35, -10), K(fim("f8") - .2, {**SUL3, "zoom": 5.3}, 45, 8),
    K(ini("f9") + 1.2, COL, 55, -20), K(fim("f9") - .2, {**COL, "zoom": 4.6}, 56, 15),
    K(ini("f10") + 1.2, MAR, 30, -6), K(fim("f10") - .2, {**MAR, "zoom": 4.2}, 38, 6),
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
assert len(BONS) >= 20, BONS
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


IRF = fim("f2") - .3
# câmera inclinada / fora do Brasil: o Blue Marble do mundo por baixo do geocolor (sem borda preta)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": CAPA - .3, "fim": IRF, "dur": IRF - CAPA, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

# ---------------------------------------------------------------- anomalia da temperatura do mar (GHRSST MUR via NASA GIBS, 11/11/2026, recorte -70,-50,-20,-10)
ANOM_DIA = (AQUI / "sat/web/anomalia-data.txt").read_text().strip()
assert ANOM_DIA == "2026-11-11", ANOM_DIA
ANOM = {"src": "sat/web/anomalia.png", "bbox": [-70, -50, -20, -10], "alfa": .85}
imagens = [{**ANOM, "ini": ini("f10") + .2, "fim": ini("f11") + .4, "fade": .8}]

# ---------------------------------------------------------------- previsão Open-Meteo nas capitais (7 dias)
OMC = json.loads((B / "openmeteo_capitais_3d.json").read_text())
CAPS = {"Cuiabá": (-15.64, -56.1), "Palmas": (-10.16, -48.32), "Belo Horizonte": (-19.92, -43.94), "Goiânia": (-16.7, -49.26),
        "Brasília": (-15.78, -47.89), "Porto Velho": (-8.75, -63.93), "Campo Grande": (-20.49, -54.65)}
OUTRAS = {"Porto Alegre": (-30.03, -51.23), "Teresina": (-5.09, -42.8)}


def cap(nome):
    la, lo = {**CAPS, **OUTRAS}[nome]
    x = min(OMC, key=lambda c: abs(c["latitude"] - la) + abs(c["longitude"] - lo))
    assert abs(x["latitude"] - la) < .15 and abs(x["longitude"] - lo) < .15, (nome, x["latitude"], x["longitude"])
    assert x["daily"]["time"][0] == "2026-11-13", x["daily"]["time"]
    return x


SOMA7 = {nm: round(sum(v or 0 for v in cap(nm)["daily"]["precipitation_sum"])) for nm in CAPS}
assert SOMA7["Cuiabá"] == 109 and SOMA7["Palmas"] == 73 and SOMA7["Belo Horizonte"] == 67, SOMA7   # f9
assert max(SOMA7.values()) == SOMA7["Cuiabá"], SOMA7
PA = cap("Porto Alegre")["daily"]
PA_TX = [round(v) for v in PA["temperature_2m_max"]]
TE = cap("Teresina")["daily"]
TE_TX = [round(v) for v in TE["temperature_2m_max"]]
assert TE_TX[0] == 40, TE_TX   # f5: Teresina 40 °C hoje

# colunas 3D: chuva PREVISTA somada em 7 dias nas capitais do Centro-Oeste, Norte e Sudeste
col = [{"id": i, "p": [cap(nm)["longitude"], cap(nm)["latitude"]], "v": v, "cor": [60, 150, 255] if v >= 60 else [120, 190, 255]}
       for i, (nm, v) in enumerate(SOMA7.items())]
ordem = {c["id"]: i * .15 for i, c in enumerate(sorted(col, key=lambda c: -c["v"]))}
colunas = [{"id": "chuva7d", "ini": ini("f9") + .3, "fim": ini("f10") + .3, "dados": col, "raio": 45000, "escala": 4200, "ordem": ordem, "varredura": 1}]

P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-11-13" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sex", "sáb", "dom", "seg", "ter", "qua", "qui"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
assert max(SULV) == SULV[2], SULV   # domingo, 15: pico da chuva no Sul
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
DOM = ufs_av(56399, 20)     # tempestade domingo 15/11: 4.299 (MG 853, SP 645, BA 417, PR 399, RS 323, SC 295, GO 246)
assert len(geo(56399)) == 4299 and aviso[56399]["descricao"] == "Tempestade" and aviso[56399]["inicio"].startswith("2026-11-15")
assert (por_uf(56399, "MG"), por_uf(56399, "SP"), por_uf(56399, "BA"), por_uf(56399, "PR"), por_uf(56399, "RS"), por_uf(56399, "SC")) == (853, 645, 417, 399, 323, 295)
HOJE = ufs_av(56392, 20)    # tempestade hoje 13/11: 2.653 (MG 853, SP 645, PR 263, GO 246, TO 134)
assert len(geo(56392)) == 2653 and aviso[56392]["descricao"] == "Tempestade" and aviso[56392]["inicio"].startswith("2026-11-13")
assert (por_uf(56392, "MG"), por_uf(56392, "SP"), por_uf(56392, "PR"), por_uf(56392, "GO"), por_uf(56392, "TO")) == (853, 645, 263, 246, 134)
assert "granizo" in aviso[56392]["riscos"][0] and "40-60 km/h" in aviso[56392]["riscos"][0]
SAB = ufs_av(56398, 20)     # tempestade sábado 14/11 no Sul: 964 (RS 497, SC 295, PR 157)
assert len(geo(56398)) == 964 and aviso[56398]["descricao"] == "Tempestade" and aviso[56398]["inicio"].startswith("2026-11-14")
assert (por_uf(56398, "RS"), por_uf(56398, "SC"), por_uf(56398, "PR")) == (497, 295, 157) and SAB == ["PR", "RS", "SC"], SAB
NORTE_SE = ["AC", "AM", "AP", "PA", "RO", "RR", "TO", "ES", "MG", "RJ", "SP"]
NORDESTE = ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"]
estados = [
    {"id": "domingo_br", "ini": CAPA, "fim": ini("f2") + .3, "ufs": DOM, "cor": LAR, "alfa": .5},
    {"id": "hoje", "ini": ini("f3"), "fim": GRAN + .3, "ufs": HOJE, "cor": LAR, "alfa": .45},
    {"id": "norte_se", "ini": em("f4", "Norte"), "fim": ini("f5") + .3, "ufs": NORTE_SE, "cor": AZUL, "alfa": .4},
    {"id": "nordeste", "ini": em("f5", "Nordeste"), "fim": ini("f6") + .3, "ufs": NORDESTE, "cor": VERM, "alfa": .45},
    {"id": "sabado_sul", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": SAB, "cor": LAR, "alfa": .45},
    {"id": "domingo_rs", "ini": em("f8", "Rio"), "fim": em("f8", "temporais") + .3, "ufs": ["RS"], "cor": AZUL, "alfa": .45},
    {"id": "domingo_sul", "ini": em("f8", "temporais"), "fim": ini("f9") + .3, "ufs": ["PR", "SC", "RS"], "cor": VERM, "alfa": .4},
    {"id": "semana", "ini": em("f9", "Goiás"), "fim": ini("f10") + .3, "ufs": ["GO", "MG", "BA", "MT"], "cor": AZUL, "alfa": .35},
]

# ponto mais quente do Atlântico Sul no recorte (anomalia decodificada pela paleta do GIBS: até +3 °C)
pinos = [
    {"nome": "Minas Gerais, hoje", "sub": "853 cidades em alerta de tempestade (INMET)", "lon": -44.6, "lat": -18.6, "ini": em("f3", "853"), "fim": GRAN, "h": 170},
    {"nome": "Norte e Sudeste", "sub": "pancadas à tarde, risco de temporal (previsão)", "lon": -47.5, "lat": -21.0, "ini": em("f4", "temporal"), "fim": ini("f5"), "h": 150},
    {"nome": "Teresina", "sub": f"máxima de {TE_TX[0]} °C hoje (previsão)", "lon": -42.8, "lat": -5.09, "ini": em("f5", "Teresina"), "fim": ini("f6"), "h": 160},
    {"nome": "Paraguai e norte da Argentina", "sub": "acima de 45 °C (previsão)", "lon": -60.0, "lat": -24.0, "ini": em("f6", "Paraguai"), "fim": ini("f7"), "h": 150},
    {"nome": "Rio Grande do Sul, sábado", "sub": "497 cidades em alerta de tempestade (INMET)", "lon": -53.5, "lat": -29.5, "ini": em("f7", "497"), "fim": ini("f8"), "h": 150},
    {"nome": "Oeste do Sul, domingo", "sub": "temporais à tarde (previsão)", "lon": -53.5, "lat": -27.5, "ini": em("f8", "temporais"), "fim": ini("f9"), "h": 90},
    {"nome": "Cuiabá", "sub": f"{SOMA7['Cuiabá']} mm em 7 dias (previsão)", "lon": -56.1, "lat": -15.6, "ini": em("f9", "Cuiabá"), "fim": ini("f10"), "h": 280},
    {"nome": "Atlântico Sul", "sub": "mar até 3 °C acima da média (11/11)", "lon": -54.5, "lat": -37.9, "ini": em("f10", "oceano") - .6, "fim": ini("f11"), "h": 150},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0


def conta(ate, fid, palavra, cor, unid, dec=0, de=0, k=1, desde=None):
    t = em(fid, palavra, k)
    lead = max(.4, min(LEAD, t - (desde if desde is not None else ini(fid))))   # número logo no começo: o contador cabe no painel
    return {"de": de, "ate": ate, "dec": dec, "ini": t - lead, "dur": lead, "cor": cor, "unid": unid}


GD = max(ini("f8") + 1.0, em("f8", "domingo"))
GS = em("f8", "temporais")
hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o fato da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:76px;color:#FACC15">4.299 CIDADES</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">em alerta de tempestade no domingo, 15/11 (INMET)</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "O QUE MANDA NO TEMPO · PREVISÃO",
     "itens": [{"t": em("f2", "calor"), "txt": "🌡️ Calor + umidade alta"}, {"t": em("f2", "abafamento"), "txt": "🥵 Abafamento acima de 30 °C no país"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f3"), "fim": GRAN - .05, "k": "HOJE, 13/11 · ALERTA DE TEMPESTADE",
     "contador": conta(2653, "f3", "2.653", "#ff8c1a", "CIDADES"),
     "l": "MG 853 · SP 645 · PR 263 · GO 246 · TO 134 · granizo e vento de 40 a 60 km/h (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": GFIM, "fim": ini("f5"), "k": "HOJE À TARDE · PREVISÃO",
     "itens": [{"t": max(GFIM, em("f4", "pancadas")), "txt": "🌦️ Norte e Sudeste: pancadas organizadas"}, {"t": em("f4", "temporal"), "txt": "⛈️ Podem virar temporal"}],
     "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "NORDESTE · CALOR (PREVISÃO)",
     "contador": conta(44, "f5", "44", "#ff2a1f", "°C"),
     "l": f"Teresina: máxima de {TE_TX[0]} °C hoje (Open-Meteo) · ar seco em 381 cidades do NE (INMET)", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "PARAGUAI E NORTE DA ARGENTINA",
     "contador": conta(45, "f6", "45", "#ff2a1f", "°C"),
     "l": "onda de ar quente ao lado do Sul do Brasil (previsão)", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SÁBADO, 14/11 · ALERTA NO SUL",
     "contador": conta(964, "f7", "964", "#ff8c1a", "CIDADES"),
     "l": "RS 497 · SC 295 · PR 157 · tempestade com granizo (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "SUL · PRÓXIMOS 7 DIAS (PREVISÃO)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": GD - 1.0, "dur": GS - GD + 1.0,
                 "linha": {"nome": "Máxima em Porto Alegre", "cor": "#ff8c1a", "v": PA_TX, "unid": "°C"}},
     "l": "domingo, 15/11: pancadas de manhã no RS, temporais à tarde · chuva em mm somados nas capitais do Sul (Open-Meteo)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "CHUVA PREVISTA · 7 DIAS",
     "contador": conta(SOMA7["Cuiabá"], "f9", "109", "#5ec8ff", "MM EM CUIABÁ"),
     "l": f"Palmas {SOMA7['Palmas']} · Belo Horizonte {SOMA7['Belo Horizonte']} · Goiânia {SOMA7['Goiânia']} · Brasília {SOMA7['Brasília']} mm (Open-Meteo)", "borda": "rgba(60,150,255,.85)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "CICLONES · PREVISÃO",
     "itens": [{"t": em("f10", "bomba"), "txt": "❌ Ciclone bomba na costa: não está na previsão"}, {"t": em("f10", "20"), "txt": "🌀 Dias 20 e 25: ciclones no oceano"}],
     "borda": "rgba(255,140,26,.8)"},
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
    {"ini": CAPA, "fim": ini("f2"), "html": "<b>INMET</b>, aviso de tempestade 15/11 (4.299 municípios)"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · {GOES}"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INMET</b>, aviso de tempestade 13/11 (2.653 municípios) · foto do granizo: ilustração"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · {OM}, 13/11 · <b>INMET</b>, aviso de baixa umidade 13/11"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>, aviso de tempestade 14/11 (964 municípios)"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · {OM}, 13/11 a 19/11"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · {OM}, 13/11 a 19/11"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b> · anomalia da temperatura do mar em 11/11: GHRSST MUR via <b>NASA</b> GIBS"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "pancadas": "#5ec8ff", "chove": "#5ec8ff", "milimetros": "#5ec8ff", "umidade": "#5ec8ff", "oceano": "#5ec8ff",
         "granizo": "#ff2a1f", "tempestade": "#ff8c1a", "temporal": "#ff8c1a", "temporais": "#ff8c1a", "ciclone": "#ff8c1a", "ciclones": "#ff8c1a",
         "bomba": "#ff2a1f", "alerta": "#ff2a1f", "atencao": "#ff2a1f", "risco": "#ff2a1f", "dispara": "#ff2a1f",
         "calor": "#ff2a1f", "abafamento": "#ff2a1f", "graus": "#ff2a1f", "sol": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "minas", "norte", "sudeste", "nordeste", "teresina", "paraguai", "argentina", "rio", "grande", "oeste",
         "goias", "bahia", "mato", "grosso", "cuiaba", "pais", "costa", "hoje", "sabado", "domingo", "inemaclub", "onde"}
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
     "camera": camera, "sat": SAT, "imagens": imagens, "colunas": colunas, "rios": rios, "telas": telas, "estados": estados, "pinos": pinos,
     "hero": hero, "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"domingo {DOM} · hoje {HOJE} · sábado {SAB} · 7d {SOMA7} · Teresina {TE_TX} · Sul {SULV} · mar {ANOM_DIA}")
