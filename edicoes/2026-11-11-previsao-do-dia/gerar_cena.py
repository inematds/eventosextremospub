#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 11/11/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "ATÉ 300 MM DE CHUVA NO SUL ATÉ O DIA 25"),
IR de 24 h no Sul (baixa pressão, temporais irregulares), aviso de tempestade do INMET até amanhã no Sul (472), aviso de hoje
do Paraná ao Pará (1.123, GO 246), colunas 3D da chuva prevista em 7 dias nas capitais do CO/Norte (Palmas 87 mm), aviso de
quinta (2.084, SP 644) com granizo (ilustração), calor no Piauí e no Ceará (até 44 °C), gráfico do Sul (chuva + máxima de
Porto Alegre 27 → 31 °C no sábado), tendência de até 300 mm no Sul até 25/11 e enxurrada (ilustração) no solo encharcado.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "11/11/2026"
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
SULG = {"lon": -51.5, "lat": -27.5, "zoom": 5.0}      # f1: até 300 mm no Sul até o dia 25
SUL2 = {"lon": -52.5, "lat": -28.5, "zoom": 5.3}      # f2: baixa pressão, temporais irregulares RS → PR
SC = {"lon": -51.0, "lat": -27.0, "zoom": 5.5}        # f3: 472 cidades até amanhã, SC 257
CON = {"lon": -50.5, "lat": -14.5, "zoom": 4.3}       # f4: 1.123 cidades hoje, do Paraná ao Pará, GO 246
COL = {"lon": -52.0, "lat": -14.0, "zoom": 4.5}       # f5: colunas 3D (7 dias nas capitais)
SPMG = {"lon": -47.5, "lat": -20.5, "zoom": 4.9}      # f6: quinta, 2.084 cidades, SP 644, granizo
NE = {"lon": -44.3, "lat": -6.5, "zoom": 5.1}         # f7 (lon -41 mostrava a borda leste do geocolor): Piauí e Ceará até 44 °C
POA = {"lon": -51.8, "lat": -28.5, "zoom": 5.0}       # f8: ar quente no Sul, Porto Alegre 31 °C no sábado
SUL3 = {"lon": -51.5, "lat": -27.0, "zoom": 5.1}      # f9–f10: até 300 mm até 25/11, solo encharcado
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
GRAN = em("f6", "risco") - .1      # foto do granizo em "com risco de granizo"
GFIM = ini("f7") + .25
ENX = em("f10", "podem") - .1     # foto da enxurrada em "podem virar alagamento e enxurrada"
EFIM = ini("f11") + .25
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, SULG, 0, 0), K(fim("f1") - .2, {**SULG, "zoom": 5.1}, 0, 0),
    K(ini("f2") + 1.0, SUL2, 30, -8), K(fim("f2") - .2, {**SUL2, "zoom": 5.5}, 40, 6),
    K(ini("f3") + 1.0, SC, 0, 0), K(fim("f3") - .2, {**SC, "zoom": 5.6}, 0, 0),
    K(ini("f4") + 1.0, CON, 0, 0), K(fim("f4") - .2, {**CON, "zoom": 4.4}, 0, 0),
    K(ini("f5") + 1.2, COL, 55, -20), K(fim("f5") - .2, {**COL, "zoom": 4.6}, 56, 15),
    K(ini("f6") + 1.0, SPMG, 0, 0), K(GRAN, {**SPMG, "zoom": 5.0}, 0, 0),
    K(ini("f7") + 1.0, NE, 0, 0), K(fim("f7") - .2, {**NE, "zoom": 5.2}, 0, 0),
    K(ini("f8") + 1.0, POA, 0, 0), K(fim("f8") - .2, {**POA, "zoom": 5.1}, 0, 0),
    K(ini("f9") + 1.0, SUL3, 35, -10), K(fim("f9") - .2, {**SUL3, "zoom": 5.3}, 45, 8),
    K(ENX, {**SUL3, "zoom": 5.4}, 45, 10),
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
CAPS = {"Palmas": (-10.16, -48.32), "Campo Grande": (-20.49, -54.65), "Goiânia": (-16.7, -49.26), "Cuiabá": (-15.64, -56.1),
        "Porto Velho": (-8.75, -63.93), "Brasília": (-15.78, -47.89), "Porto Alegre": (-30.03, -51.23)}


def cap(nome):
    la, lo = CAPS[nome]
    x = min(OMC, key=lambda c: abs(c["latitude"] - la) + abs(c["longitude"] - lo))
    assert abs(x["latitude"] - la) < .15 and abs(x["longitude"] - lo) < .15, (nome, x["latitude"], x["longitude"])
    assert x["daily"]["time"][0] == "2026-11-11", x["daily"]["time"]
    return x


SOMA7 = {nm: round(sum(v or 0 for v in cap(nm)["daily"]["precipitation_sum"])) for nm in CAPS if nm != "Porto Alegre"}
assert SOMA7["Palmas"] == 87 and SOMA7["Campo Grande"] == 77 and SOMA7["Goiânia"] == 76, SOMA7   # f5
PA = cap("Porto Alegre")["daily"]
PA_TX = [round(v) for v in PA["temperature_2m_max"]]
assert PA_TX[0] == 27 and PA_TX[3] == 31 and PA["time"][3] == "2026-11-14", PA_TX   # f8: 31 °C no sábado

# colunas 3D: chuva PREVISTA somada em 7 dias nas capitais do Centro-Oeste e do Norte
col = [{"id": i, "p": [cap(nm)["longitude"], cap(nm)["latitude"]], "v": v, "cor": [60, 150, 255] if v >= 60 else [120, 190, 255]}
       for i, (nm, v) in enumerate(SOMA7.items())]
ordem = {c["id"]: i * .15 for i, c in enumerate(sorted(col, key=lambda c: -c["v"]))}
colunas = [{"id": "chuva7d", "ini": ini("f5") + .3, "fim": ini("f6") + .3, "dados": col, "raio": 45000, "escala": 4200, "ordem": ordem, "varredura": 1}]

P7 = json.loads((B / "previsao7d.json").read_text())
HOJE_D = "2026-11-11"
assert P7["dias"][0] == HOJE_D and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qua", "qui", "sex", "sáb", "dom", "seg", "ter"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
series = [{"nome": "Chuva no Sul (mm)", "cor": "#5ec8ff", "v": SULV}]

rios = []

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, granizo, enxurrada
assert GFIM - GRAN > .8, (GRAN, GFIM)
assert EFIM - ENX > .8, (ENX, EFIM)
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .02},
         {"src": "capa-dia/granizo.png", "ini": GRAN, "fim": GFIM, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/enxurrada.png", "ini": ENX, "fim": EFIM, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
SULA = ufs_av(56378)        # tempestade 11/11 12h → 12/11 12h: 472 (SC 257, PR 183, RS 30, MS 2)
assert len(geo(56378)) == 472 and aviso[56378]["descricao"] == "Tempestade" and aviso[56378]["fim"].startswith("2026-11-12")
assert (por_uf(56378, "SC"), por_uf(56378, "PR"), por_uf(56378, "RS"), por_uf(56378, "MS")) == (257, 183, 30, 2)
HOJE = ufs_av(56376, 20)    # tempestade hoje 11/11: 1.123 (GO 246, SP 217, PR 179, TO 139, MT 139 …, PA 34)
assert len(geo(56376)) == 1123 and aviso[56376]["descricao"] == "Tempestade" and aviso[56376]["inicio"].startswith("2026-11-11")
assert (por_uf(56376, "GO"), por_uf(56376, "SP"), por_uf(56376, "PR"), por_uf(56376, "TO"), por_uf(56376, "MT"), por_uf(56376, "PA")) == (246, 217, 179, 139, 139, 34)
QUINTA = ufs_av(56381, 20)  # tempestade quinta 12/11: 2.084 (SP 644, MG 553, PR 286, GO 246)
assert len(geo(56381)) == 2084 and aviso[56381]["descricao"] == "Tempestade" and aviso[56381]["inicio"].startswith("2026-11-12")
assert (por_uf(56381, "SP"), por_uf(56381, "MG"), por_uf(56381, "PR"), por_uf(56381, "GO")) == (644, 553, 286, 246)
assert "granizo" in aviso[56381]["riscos"][0] and "40-60 km/h" in aviso[56381]["riscos"][0]
estados = [
    {"id": "sul", "ini": CAPA, "fim": ini("f2") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .4},
    {"id": "sul_hoje", "ini": em("f2", "temporais"), "fim": ini("f3") + .3, "ufs": ["PR", "SC", "RS"], "cor": LAR, "alfa": .3},
    {"id": "sul_alerta", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": SULA, "cor": LAR, "alfa": .45},
    {"id": "hoje", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": HOJE, "cor": LAR, "alfa": .45},
    {"id": "quinta", "ini": ini("f6"), "fim": GRAN + .3, "ufs": QUINTA, "cor": LAR, "alfa": .45},
    {"id": "calor_ne", "ini": em("f7", "calor"), "fim": ini("f8") + .3, "ufs": ["PI", "CE"], "cor": VERM, "alfa": .45},
    {"id": "calor_sul", "ini": em("f8", "quente"), "fim": ini("f9") + .3, "ufs": ["PR", "SC", "RS"], "cor": LAR, "alfa": .35},
    {"id": "chuva_sul", "ini": em("f9", "chuva"), "fim": ini("f11") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .45},
]

pinos = [
    {"nome": "Rio Grande do Sul, hoje", "sub": "temporais irregulares (previsão)", "lon": -53.5, "lat": -29.3, "ini": em("f2", "irregulares"), "fim": ini("f3"), "h": 150},
    {"nome": "Santa Catarina", "sub": "257 cidades em alerta até amanhã (INMET)", "lon": -50.5, "lat": -27.2, "ini": em("f3", "Santa"), "fim": ini("f4"), "h": 160},
    {"nome": "Goiás, hoje", "sub": "246 cidades em alerta de tempestade (INMET)", "lon": -49.6, "lat": -15.8, "ini": em("f4", "246"), "fim": ini("f5"), "h": 140},
    {"nome": "Palmas", "sub": f"{SOMA7['Palmas']} mm em 7 dias (previsão)", "lon": -48.32, "lat": -10.16, "ini": em("f5", "Palmas"), "fim": ini("f6"), "h": 260},
    {"nome": "São Paulo, quinta", "sub": "644 cidades em alerta de tempestade (INMET)", "lon": -48.5, "lat": -22.3, "ini": em("f6", "644"), "fim": GRAN, "h": 180},
    {"nome": "Piauí e Ceará", "sub": "máxima de até 44 °C (previsão)", "lon": -41.5, "lat": -6.0, "ini": em("f7", "Piauí"), "fim": ini("f8"), "h": 160},
    {"nome": "Porto Alegre", "sub": f"máxima {PA_TX[0]} °C hoje → {PA_TX[3]} °C sábado (previsão)", "lon": -51.23, "lat": -30.03, "ini": em("f8", "Porto"), "fim": ini("f9"), "h": 160},
    {"nome": "Sul, até 25/11", "sub": "até 300 mm em alguns pontos (tendência)", "lon": -52.0, "lat": -26.8, "ini": em("f9", "300"), "fim": ENX, "h": 160},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0


def conta(ate, fid, palavra, cor, unid, dec=0, de=0, k=1, desde=None):
    t = em(fid, palavra, k)
    lead = max(.4, min(LEAD, t - (desde if desde is not None else ini(fid))))   # número logo no começo: o contador cabe no painel
    return {"de": de, "ate": ate, "dec": dec, "ini": t - lead, "dur": lead, "cor": cor, "unid": unid}


G31 = em("f8", "31")
GQ = em("f8", "quente")
hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o fato da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:76px;color:#FACC15">ATÉ 300 MM</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">de chuva no Sul até o dia 25 · em alguns pontos (tendência)</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "HOJE, 11/11 · PREVISÃO",
     "itens": [{"t": em("f2", "baixa"), "txt": "🌀 Baixa pressão sobre o Sul"}, {"t": em("f2", "irregulares"), "txt": "⛈️ Temporais irregulares, do RS ao PR"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "ATÉ AMANHÃ, 12H · ALERTA DE TEMPESTADE",
     "contador": conta(472, "f3", "472", "#ff8c1a", "CIDADES"),
     "l": "SC 257 · PR 183 · RS 30 · MS 2 · granizo e vento de 40 a 60 km/h (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE, 11/11 · ALERTA DE TEMPESTADE",
     "contador": conta(1123, "f4", "1.123", "#ff8c1a", "CIDADES"),
     "l": "GO 246 · SP 217 · PR 179 · TO 139 · MT 139 · PA 34 (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "CHUVA PREVISTA · 7 DIAS",
     "contador": conta(SOMA7["Palmas"], "f5", "87", "#5ec8ff", "MM EM PALMAS"),
     "l": f"Campo Grande {SOMA7['Campo Grande']} · Goiânia {SOMA7['Goiânia']} · Cuiabá {SOMA7['Cuiabá']} · Porto Velho {SOMA7['Porto Velho']} mm (Open-Meteo)", "borda": "rgba(60,150,255,.85)"},
    {"ini": ini("f6"), "fim": GRAN - .05, "k": "QUINTA, 12/11 · ALERTA DE TEMPESTADE",
     "contador": conta(2084, "f6", "2.084", "#ff8c1a", "CIDADES"),
     "l": "SP 644 · MG 553 · PR 286 · GO 246 · granizo e vento de 40 a 60 km/h (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": GFIM, "fim": ini("f8"), "k": "NORDESTE · CALOR (PREVISÃO)",
     "contador": conta(44, "f7", "44", "#ff2a1f", "°C", desde=GFIM),
     "l": "Piauí e Ceará: máximas acima de 42 °C, chegando a 44 °C", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "SUL · PRÓXIMOS 7 DIAS (PREVISÃO)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": GQ - 1.0, "dur": G31 - GQ + 1.0,
                 "linha": {"nome": "Máxima em Porto Alegre", "cor": "#ff8c1a", "v": PA_TX, "unid": "°C"}},
     "l": f"Porto Alegre: {PA_TX[0]} °C hoje → {PA_TX[3]} °C no sábado · chuva em mm somados nas capitais do Sul (Open-Meteo)", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f9"), "fim": ENX - .05, "k": "SUL · ATÉ 25/11 (TENDÊNCIA)",
     "contador": conta(300, "f9", "300", "#5ec8ff", "MM"),
     "l": "chuva volta na semana que vem · até 300 mm em alguns pontos · solo já encharcado", "borda": "rgba(60,150,255,.85)"},
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
    {"ini": CAPA, "fim": ini("f3"), "html": f"<b>{MET}</b> · {GOES}"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INMET</b>, aviso de tempestade 11/11 12h a 12/11 12h (472 municípios)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso de tempestade 11/11 (1.123 municípios)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"{OM}, 11/11 a 17/11"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso de tempestade 12/11 (2.084 municípios) · foto do granizo: ilustração"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · {OM}, 11/11 a 17/11"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>{MET}</b> · foto da enxurrada: ilustração"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "pancadas": "#5ec8ff", "chove": "#5ec8ff", "encharcado": "#5ec8ff", "milimetros": "#5ec8ff",
         "granizo": "#ff2a1f", "tempestade": "#ff8c1a", "temporais": "#ff8c1a", "alagamento": "#ff2a1f", "enxurrada": "#ff2a1f",
         "alerta": "#ff2a1f", "atencao": "#ff2a1f", "risco": "#ff2a1f", "irregulares": "#ff8c1a", "aumentam": "#ff2a1f",
         "calor": "#ff2a1f", "quente": "#ff2a1f", "insuportavel": "#ff2a1f", "graus": "#ff2a1f",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "rio", "grande", "parana", "para", "santa", "catarina", "goias", "palmas", "sao", "paulo", "nordeste", "piaui", "ceara",
         "porto", "alegre", "hoje", "amanha", "quarta", "sabado", "inemaclub", "onde", "do"}
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
      f"sul {SULA} · hoje {HOJE} · quinta {QUINTA} · 7d {SOMA7} · Porto Alegre {PA_TX}")
