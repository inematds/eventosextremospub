#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 14/11/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "ATÉ 45 °C EM MATO GROSSO DO SUL NESTE FIM DE SEMANA"),
MS pintado, IR de 24 h (massa de ar quente), oeste de SP 42 °C, Nordeste (Teresina 40 °C na sexta), calor + umidade,
aviso de hoje à noite (342) com granizo (ilustração), aviso de domingo (2.633, SP 645), campanha gaúcha,
gráfico de 7 dias + aviso de segunda (2.819) e colunas 3D de 7 dias (Palmas 70 mm, BH 63 mm).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "14/11/2026"
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
MS = {"lon": -54.8, "lat": -20.6, "zoom": 5.1}        # f1: até 45 °C em MS no fim de semana
BR2 = {"lon": -50.0, "lat": -15.0, "zoom": 4.0}       # f2: massa de ar quente sobre quase todo o país (IR)
SP = {"lon": -50.0, "lat": -22.3, "zoom": 5.5}        # f3: oeste de SP, 42 °C
NE = {"lon": -40.5, "lat": -6.8, "zoom": 5.0}         # f4: Nordeste, Teresina 40 °C na sexta
CS = {"lon": -51.0, "lat": -22.0, "zoom": 4.6}        # f5: calor + umidade = temporais de verão (inclinada)
SUL = {"lon": -52.0, "lat": -26.5, "zoom": 5.1}       # f6: hoje à noite, 342 no Sul e MS
SE = {"lon": -48.0, "lat": -21.5, "zoom": 4.8}        # f7: domingo, 2.633, SP 645
RS = {"lon": -54.0, "lat": -30.3, "zoom": 5.7}        # f8: campanha e extremo sul gaúcho
BR = {"lon": -50.0, "lat": -16.0, "zoom": 4.0}        # f9: segunda a quarta, 2.819
COL = {"lon": -48.5, "lat": -16.0, "zoom": 4.6}       # f10: colunas 3D (7 dias)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
GRAN = em("f6", "risco") - .1      # foto do granizo em "com risco de granizo"
GFIM = ini("f7") + .25
camera = [
    K(0, MS), K(CAPA, MS), K(fim("f1") - .2, {**MS, "zoom": 5.2}, 0, 0),
    K(ini("f2") + 1.0, BR2, 30, -8), K(fim("f2") - .2, {**BR2, "zoom": 4.1}, 38, 6),
    K(ini("f3") + 1.0, SP, 0, 0), K(fim("f3") - .2, {**SP, "zoom": 5.6}, 0, 0),
    K(ini("f4") + 1.0, NE, 0, 0), K(fim("f4") - .2, {**NE, "zoom": 5.1}, 0, 0),
    K(ini("f5") + 1.0, CS, 40, -10), K(fim("f5") - .2, {**CS, "zoom": 4.7}, 46, 8),
    K(ini("f6") + 1.0, SUL, 0, 0), K(GRAN, {**SUL, "zoom": 5.2}, 0, 0),
    K(ini("f7") + 1.0, SE, 0, 0), K(fim("f7") - .2, {**SE, "zoom": 4.9}, 0, 0),
    K(ini("f8") + 1.0, RS, 0, 0), K(fim("f8") - .2, {**RS, "zoom": 5.8}, 0, 0),
    K(ini("f9") + 1.0, BR, 0, 0), K(fim("f9") - .2, {**BR, "zoom": 4.1}, 0, 0),
    K(ini("f10") + 1.2, COL, 55, -20), K(fim("f10") - .2, {**COL, "zoom": 4.7}, 56, 15),
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
imagens = []

# ---------------------------------------------------------------- previsão Open-Meteo nas capitais (7 dias)
OMC = json.loads((B / "openmeteo_capitais_3d.json").read_text())
CAPS = {"Palmas": (-10.16, -48.32), "Belo Horizonte": (-19.92, -43.94), "Cuiabá": (-15.64, -56.1), "São Paulo": (-23.55, -46.63),
        "Porto Velho": (-8.75, -63.93), "Vitória": (-20.32, -40.34), "Goiânia": (-16.7, -49.26), "Campo Grande": (-20.49, -54.65),
        "Brasília": (-15.78, -47.89)}
OUTRAS = {"Teresina": (-5.09, -42.8)}


def cap(nome):
    la, lo = {**CAPS, **OUTRAS}[nome]
    x = min(OMC, key=lambda c: abs(c["latitude"] - la) + abs(c["longitude"] - lo))
    assert abs(x["latitude"] - la) < .15 and abs(x["longitude"] - lo) < .15, (nome, x["latitude"], x["longitude"])
    assert x["daily"]["time"][0] == "2026-11-14", x["daily"]["time"]
    return x


SOMA7 = {nm: round(sum(v or 0 for v in cap(nm)["daily"]["precipitation_sum"])) for nm in CAPS}
assert SOMA7["Palmas"] == 70 and SOMA7["Belo Horizonte"] == 63, SOMA7   # f10
assert max(SOMA7.values()) == SOMA7["Palmas"], SOMA7
TE = cap("Teresina")["daily"]
TE_TX = [round(v) for v in TE["temperature_2m_max"]]
assert TE_TX[6] == 40 and TE["time"][6] == "2026-11-20", TE_TX   # f4: Teresina 40 °C na sexta, 20/11

# colunas 3D: chuva PREVISTA somada em 7 dias nas capitais do Norte, Centro-Oeste e Sudeste
col = [{"id": i, "p": [cap(nm)["longitude"], cap(nm)["latitude"]], "v": v, "cor": [60, 150, 255] if v >= 55 else [120, 190, 255]}
       for i, (nm, v) in enumerate(SOMA7.items())]
ordem = {c["id"]: i * .15 for i, c in enumerate(sorted(col, key=lambda c: -c["v"]))}
colunas = [{"id": "chuva7d", "ini": ini("f10") + .3, "fim": ini("f11") + .3, "dados": col, "raio": 45000, "escala": 5500, "ordem": ordem, "varredura": 1}]

P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-11-14" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sáb", "dom", "seg", "ter", "qua", "qui", "sex"], ROTD
SEV = [d["por_regiao_mm"]["SE"] for d in P7["por_dia"]]
COV = [d["por_regiao_mm"]["CO"] for d in P7["por_dia"]]
series = [{"nome": "Chuva no Sudeste (mm)", "cor": "#5ec8ff", "v": SEV}, {"nome": "Chuva no Centro-Oeste (mm)", "cor": "#3c96ff", "v": COV}]

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
NOITE = ufs_av(56405, 10)   # tempestade hoje à noite 14/11: 342 (PR 149, RS 94, SC 87, MS 12)
assert len(geo(56405)) == 342 and aviso[56405]["descricao"] == "Tempestade" and aviso[56405]["inicio"].startswith("2026-11-14 20")
assert (por_uf(56405, "PR"), por_uf(56405, "RS"), por_uf(56405, "SC"), por_uf(56405, "MS")) == (149, 94, 87, 12) and NOITE == ["MS", "PR", "RS", "SC"], NOITE
assert "granizo" in aviso[56405]["riscos"][0] and "40-60 km/h" in aviso[56405]["riscos"][0]
DOM = ufs_av(56408, 20)     # tempestade domingo 15/11: 2.633 (MG 844, SP 645, PR 399, SC 270, GO 129)
assert len(geo(56408)) == 2633 and aviso[56408]["descricao"] == "Tempestade" and aviso[56408]["inicio"].startswith("2026-11-15")
assert (por_uf(56408, "MG"), por_uf(56408, "SP"), por_uf(56408, "PR"), por_uf(56408, "SC"), por_uf(56408, "GO")) == (844, 645, 399, 270, 129)
SEG = ufs_av(56410, 20)     # tempestade segunda 16/11: 2.819 (MG 853, SP 600, BA 326, GO 246)
assert len(geo(56410)) == 2819 and aviso[56410]["descricao"] == "Tempestade" and aviso[56410]["inicio"].startswith("2026-11-16")
assert (por_uf(56410, "MG"), por_uf(56410, "SP"), por_uf(56410, "BA"), por_uf(56410, "GO")) == (853, 600, 326, 246)
estados = [
    {"id": "ms", "ini": CAPA, "fim": ini("f2") + .3, "ufs": ["MS"], "cor": VERM, "alfa": .5},
    {"id": "sp", "ini": em("f3", "oeste"), "fim": ini("f4") + .3, "ufs": ["SP"], "cor": VERM, "alfa": .45},
    {"id": "nordeste", "ini": em("f4", "Piauí"), "fim": ini("f5") + .3, "ufs": ["PI", "CE", "PE"], "cor": VERM, "alfa": .45},
    {"id": "noite", "ini": ini("f6"), "fim": GRAN + .3, "ufs": NOITE, "cor": LAR, "alfa": .45},
    {"id": "domingo", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": DOM, "cor": LAR, "alfa": .45},
    {"id": "segunda", "ini": em("f9", "segunda", 2), "fim": ini("f10") + .3, "ufs": SEG, "cor": LAR, "alfa": .4},
]

pinos = [
    {"nome": "Oeste de São Paulo", "sub": "máxima de até 42 °C (previsão)", "lon": -51.4, "lat": -21.8, "ini": em("f3", "oeste"), "fim": ini("f4"), "h": 150},
    {"nome": "Teresina", "sub": f"{TE_TX[6]} °C na sexta, 20/11 (previsão)", "lon": -42.8, "lat": -5.09, "ini": em("f4", "Teresina"), "fim": ini("f5"), "h": 160},
    {"nome": "Paraná, hoje à noite", "sub": "149 cidades em alerta de tempestade (INMET)", "lon": -51.5, "lat": -24.8, "ini": em("f6", "342"), "fim": GRAN, "h": 150},
    {"nome": "São Paulo, domingo", "sub": "645 cidades em alerta de tempestade (INMET)", "lon": -48.5, "lat": -22.3, "ini": em("f7", "645"), "fim": ini("f8"), "h": 150},
    {"nome": "Campanha gaúcha", "sub": "chuva deve falhar em muitas áreas (previsão)", "lon": -55.0, "lat": -30.8, "ini": em("f8", "campanha"), "fim": ini("f9"), "h": 130},
    {"nome": "Palmas", "sub": f"{SOMA7['Palmas']} mm em 7 dias (previsão)", "lon": -48.32, "lat": -10.16, "ini": em("f10", "Palmas"), "fim": ini("f11"), "h": 300},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0


def conta(ate, fid, palavra, cor, unid, dec=0, de=0, k=1, desde=None):
    t = em(fid, palavra, k)
    lead = max(.4, min(LEAD, t - (desde if desde is not None else ini(fid))))   # número logo no começo: o contador cabe no painel
    return {"de": de, "ate": ate, "dec": dec, "ini": t - lead, "dur": lead, "cor": cor, "unid": unid}


SEG2 = em("f9", "Na") - .05          # gráfico até "Na segunda", depois o contador do aviso de segunda
hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o fato da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:76px;color:#FACC15">ATÉ 45 °C</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">em Mato Grosso do Sul neste fim de semana (previsão)</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "O QUE MANDA NO TEMPO · PREVISÃO",
     "itens": [{"t": em("f2", "massa"), "txt": "🔥 Forte massa de ar quente"}, {"t": em("f2", "Sul"), "txt": "🇧🇷 Do Sul ao Nordeste"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "OESTE DE SÃO PAULO · PREVISÃO",
     "contador": conta(42, "f3", "42", "#ff2a1f", "°C"),
     "l": "máxima no fim de semana; Mato Grosso do Sul até 45 °C", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "NORDESTE · CALOR (PREVISÃO)",
     "contador": conta(TE_TX[6], "f4", "40", "#ff2a1f", "°C EM TERESINA"),
     "l": f"sexta, 20/11 · hoje {TE_TX[0]} °C (Open-Meteo) · Piauí, Ceará e Pernambuco", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "TEMPORAIS DE VERÃO · PREVISÃO",
     "itens": [{"t": em("f5", "Calor"), "txt": "🌡️ Calor + 💧 umidade alta"}, {"t": em("f5", "temporais"), "txt": "⛈️ Temporais de verão na primavera"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f6"), "fim": GRAN - .05, "k": "HOJE À NOITE, 14/11 · ALERTA DE TEMPESTADE",
     "contador": conta(342, "f6", "342", "#ff8c1a", "CIDADES"),
     "l": "PR 149 · RS 94 · SC 87 · MS 12 · granizo e vento de 40 a 60 km/h (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": GFIM, "fim": ini("f8"), "k": "DOMINGO, 15/11 · ALERTA DE TEMPESTADE",
     "contador": conta(2633, "f7", "2.633", "#ff8c1a", "CIDADES", desde=GFIM),
     "l": "MG 844 · SP 645 · PR 399 · SC 270 · GO 129 (INMET) · baixa pressão reforça os temporais", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "RIO GRANDE DO SUL · PREVISÃO",
     "itens": [{"t": em("f8", "campanha"), "txt": "📍 Campanha e extremo sul gaúcho"}, {"t": em("f8", "falhar"), "txt": "🌦️ Chuva deve falhar em muitas áreas"}],
     "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f9"), "fim": SEG2, "k": "PRÓXIMOS 7 DIAS · PREVISÃO",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f9") + .3, "dur": em("f9", "temporais") - ini("f9") - .3,
                 "linha": {"nome": "Máxima em Teresina", "cor": "#ff2a1f", "v": TE_TX, "unid": "°C"}},
     "l": "mini verão: calor forte e temporais todo dia · chuva em mm somados nas capitais (Open-Meteo)", "borda": "rgba(255,42,31,.8)"},
    {"ini": SEG2, "fim": ini("f10"), "k": "SEGUNDA, 16/11 · ALERTA DE TEMPESTADE",
     "contador": conta(2819, "f9", "2.819", "#ff8c1a", "CIDADES", desde=SEG2),
     "l": "MG 853 · SP 600 · BA 326 · GO 246 (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "CHUVA PREVISTA · 7 DIAS",
     "contador": conta(SOMA7["Palmas"], "f10", "70", "#5ec8ff", "MM EM PALMAS"),
     "l": f"Belo Horizonte {SOMA7['Belo Horizonte']} · Cuiabá {SOMA7['Cuiabá']} · São Paulo {SOMA7['São Paulo']} · Porto Velho {SOMA7['Porto Velho']} mm (Open-Meteo)", "borda": "rgba(60,150,255,.85)"},
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
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · {GOES}"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · {OM}, 14/11 a 20/11"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INMET</b>, aviso de tempestade 14/11 à noite (342 municípios) · foto do granizo: ilustração"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>INMET</b>, aviso de tempestade 15/11 (2.633 municípios) · <b>{MET}</b>"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · {OM}, 14/11 a 20/11 · <b>INMET</b>, aviso de tempestade 16/11 (2.819 municípios)"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b> · {OM}, 14/11 a 20/11"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "pancadas": "#5ec8ff", "chove": "#5ec8ff", "milimetros": "#5ec8ff", "umidade": "#5ec8ff", "oceano": "#5ec8ff",
         "granizo": "#ff2a1f", "tempestade": "#ff8c1a", "temporal": "#ff8c1a", "temporais": "#ff8c1a", "ciclone": "#ff8c1a", "ciclones": "#ff8c1a",
         "bomba": "#ff2a1f", "alerta": "#ff2a1f", "atencao": "#ff2a1f", "risco": "#ff2a1f", "dispara": "#ff2a1f",
         "calor": "#ff2a1f", "quente": "#ff2a1f", "verao": "#ff8c1a", "abafamento": "#ff2a1f", "graus": "#ff2a1f", "sol": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "mato", "grosso", "sao", "paulo", "oeste", "nordeste", "piaui", "ceara", "pernambuco", "teresina", "brasil",
         "campanha", "extremo", "gaucho", "palmas", "belo", "horizonte", "hoje", "noite", "sabado", "domingo", "segunda", "terca",
         "quarta", "sexta", "inemaclub", "onde"}
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
      f"noite {NOITE} · domingo {DOM} · segunda {SEG} · 7d {SOMA7} · Teresina {TE_TX} · SE {SEV} · CO {COV}")
