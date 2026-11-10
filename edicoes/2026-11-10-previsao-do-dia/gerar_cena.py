#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 10/11/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "2.574 CIDADES EM ALERTA DE TEMPESTADE · NA QUINTA · 645 EM SÃO PAULO"),
aviso de tempestade do INMET de quinta (2.574) pintado, ar seco no Sul hoje, chuva intensa hoje (655, de Goiás ao Maranhão),
alerta de quarta no RS/SC (224) e nível de perigo no MS/MT/GO (78, vento até 100 km/h), quinta com granizo (ilustração) e
ranking por estado, colunas 3D da chuva prevista em 7 dias nas capitais do CO/Norte, gráfico do Sul (chuva + máxima de
Porto Alegre 27 → 31 °C no sábado), tendência de frente fria e ciclone extratropical nos dias 15 e 16.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "10/11/2026"
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
QUI = {"lon": -49.0, "lat": -22.5, "zoom": 4.5}       # f1: 2.574 cidades na quinta, 645 em SP
SUL = {"lon": -51.0, "lat": -26.5, "zoom": 5.0}       # f2: ar seco no Sul; chuvisco no litoral PR/SP
CON = {"lon": -50.0, "lat": -10.5, "zoom": 4.4}       # f3: chuva intensa hoje, de Goiás ao Maranhão
RSSC = {"lon": -52.5, "lat": -28.5, "zoom": 5.4}      # f4: quarta, 224 cidades RS/SC
MSMT = {"lon": -54.0, "lat": -18.5, "zoom": 5.0}      # f5: nível de perigo MS/MT/GO
SPMG = {"lon": -46.5, "lat": -21.0, "zoom": 5.0}      # f6: quinta em SP/MG/RJ
COL = {"lon": -52.0, "lat": -14.0, "zoom": 4.5}       # f7: colunas 3D (7 dias nas capitais)
POA = {"lon": -51.8, "lat": -28.5, "zoom": 5.0}       # f8: calor no Sul, Porto Alegre 31 °C
CIC = {"lon": -51.5, "lat": -28.0, "zoom": 4.9}       # f9: frente fria e ciclone, dias 15 e 16 (oceano)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
GRAN = em("f6", "pancadas") - .1    # foto do granizo em "pancadas a qualquer hora, com granizo"
GFIM = em("f6", "Minas", 2) - .1
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, QUI, 0, 0), K(fim("f1") - .2, {**QUI, "zoom": 4.6}, 0, 0),
    K(ini("f2") + 1.0, SUL, 0, 0), K(fim("f2") - .2, {**SUL, "zoom": 5.1}, 0, 0),
    K(ini("f3") + 1.0, CON, 0, 0), K(fim("f3") - .2, {**CON, "zoom": 4.5}, 0, 0),
    K(ini("f4") + 1.2, RSSC, 30, -8), K(fim("f4") - .2, {**RSSC, "zoom": 5.6}, 40, 6),
    K(ini("f5") + 1.2, MSMT, 35, -10), K(fim("f5") - .2, {**MSMT, "zoom": 5.1}, 45, 8),
    K(ini("f6") + 1.0, SPMG, 0, 0), K(fim("f6") - .2, {**SPMG, "zoom": 5.1}, 0, 0),
    K(ini("f7") + 1.2, COL, 55, -20), K(fim("f7") - .2, {**COL, "zoom": 4.6}, 56, 15),
    K(ini("f8") + 1.0, POA, 0, 0), K(fim("f8") - .2, {**POA, "zoom": 5.1}, 0, 0),
    K(ini("f9") + 1.0, CIC, 25, -6), K(fim("f9") - .2, {**CIC, "zoom": 5.0}, 32, 6),
    K(ini("f10") + 1.4, {"lon": -50.0, "lat": -16.0, "zoom": 4.4}, 0, 0), K(DUR, {"lon": -50.0, "lat": -16.0, "zoom": 4.5}, 0, 2),
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
CAPS = {"Cuiabá": (-15.64, -56.1), "Palmas": (-10.16, -48.32), "Brasília": (-15.78, -47.89), "Campo Grande": (-20.49, -54.65),
        "Goiânia": (-16.7, -49.26), "Porto Velho": (-8.75, -63.93), "Porto Alegre": (-30.03, -51.23)}


def cap(nome):
    la, lo = CAPS[nome]
    x = min(OMC, key=lambda c: abs(c["latitude"] - la) + abs(c["longitude"] - lo))
    assert abs(x["latitude"] - la) < .15 and abs(x["longitude"] - lo) < .15, (nome, x["latitude"], x["longitude"])
    assert x["daily"]["time"][0] == "2026-11-10", x["daily"]["time"]
    return x


SOMA7 = {nm: round(sum(v or 0 for v in cap(nm)["daily"]["precipitation_sum"])) for nm in CAPS if nm != "Porto Alegre"}
assert SOMA7["Cuiabá"] == 83 and SOMA7["Palmas"] == 82, SOMA7   # f7
PA = cap("Porto Alegre")["daily"]
PA_TX = [round(v) for v in PA["temperature_2m_max"]]
assert PA_TX[0] == 27 and PA_TX[4] == 31 and PA["time"][4] == "2026-11-14", PA_TX   # f8: 31 °C no sábado

# colunas 3D: chuva PREVISTA somada em 7 dias nas capitais do Centro-Oeste e do Norte
col = [{"id": i, "p": [cap(nm)["longitude"], cap(nm)["latitude"]], "v": v, "cor": [60, 150, 255] if v >= 60 else [120, 190, 255]}
       for i, (nm, v) in enumerate(SOMA7.items())]
ordem = {c["id"]: i * .15 for i, c in enumerate(sorted(col, key=lambda c: -c["v"]))}
colunas = [{"id": "chuva7d", "ini": ini("f7") + .3, "fim": ini("f8") + .3, "dados": col, "raio": 45000, "escala": 4200, "ordem": ordem, "varredura": 1}]

P7 = json.loads((B / "previsao7d.json").read_text())
HOJE_D = "2026-11-10"
assert P7["dias"][0] == HOJE_D and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["ter", "qua", "qui", "sex", "sáb", "dom", "seg"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
series = [{"nome": "Chuva no Sul (mm)", "cor": "#5ec8ff", "v": SULV}]

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
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
QUINTA = ufs_av(56370, 50)   # tempestade (perigo potencial) quinta 12/11: 2.574
assert len(geo(56370)) == 2574 and aviso[56370]["descricao"] == "Tempestade" and aviso[56370]["inicio"].startswith("2026-11-12")
assert (por_uf(56370, "SP"), por_uf(56370, "MG"), por_uf(56370, "PR"), por_uf(56370, "SC"), por_uf(56370, "RS")) == (645, 494, 322, 271, 263)
assert "granizo" in aviso[56370]["riscos"][0]
HOJE = ufs_av(56363, 50)     # chuvas intensas hoje 10/11: 655
assert len(geo(56363)) == 655 and aviso[56363]["descricao"] == "Chuvas Intensas" and aviso[56363]["inicio"].startswith("2026-11-10")
assert (por_uf(56363, "GO"), por_uf(56363, "TO"), por_uf(56363, "MA"), por_uf(56363, "PI")) == (181, 139, 110, 97)
QUA_SUL = ufs_av(56366)  # tempestade quarta 11/11 no RS/SC: 224
assert len(geo(56366)) == 224 and aviso[56366]["inicio"].startswith("2026-11-11") and (por_uf(56366, "RS"), por_uf(56366, "SC")) == (184, 40)
PERIGO = ufs_av(56369)   # tempestade nível PERIGO quarta 11/11: 78
assert len(geo(56369)) == 78 and aviso[56369]["severidade"] == "Perigo" and aviso[56369]["inicio"].startswith("2026-11-11")
assert (por_uf(56369, "MS"), por_uf(56369, "MT"), por_uf(56369, "GO")) == (42, 19, 17)
assert "60-100 km/h" in aviso[56369]["riscos"][0] and "50 e 100 mm/dia" in aviso[56369]["riscos"][0]
estados = [
    {"id": "quinta", "ini": CAPA, "fim": ini("f2") + .3, "ufs": QUINTA, "cor": LAR, "alfa": .45},
    {"id": "seco", "ini": em("f2", "seco"), "fim": ini("f3") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .3},
    {"id": "hoje", "ini": em("f3", "pancadas"), "fim": ini("f4") + .3, "ufs": HOJE, "cor": LAR, "alfa": .45},
    {"id": "quarta_sul", "ini": em("f4", "Sul"), "fim": ini("f5") + .3, "ufs": QUA_SUL, "cor": LAR, "alfa": .45},
    {"id": "perigo", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": PERIGO, "cor": VERM, "alfa": .45},
    {"id": "quinta2", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": QUINTA, "cor": LAR, "alfa": .4},
    {"id": "calor", "ini": em("f8", "calor"), "fim": ini("f9") + .3, "ufs": ["PR", "SC", "RS"], "cor": LAR, "alfa": .35},
    {"id": "frente", "ini": em("f9", "frente"), "fim": ini("f10") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .4},
]

pinos = [
    {"nome": "São Paulo, quinta", "sub": "645 cidades em alerta de tempestade (INMET)", "lon": -48.5, "lat": -22.3, "ini": em("f1", "645"), "fim": ini("f2"), "h": 200},
    {"nome": "Sul, hoje", "sub": "sol e calor (previsão)", "lon": -53.0, "lat": -28.5, "ini": em("f2", "seco"), "fim": ini("f3"), "h": 120},
    {"nome": "Litoral de SC, PR e SP", "sub": "nuvens e chuvisco (previsão)", "lon": -48.3, "lat": -25.3, "ini": em("f2", "litoral"), "fim": ini("f3"), "h": 220},
    {"nome": "Goiás, hoje", "sub": "181 cidades em alerta de chuva intensa (INMET)", "lon": -49.6, "lat": -15.8, "ini": em("f3", "655"), "fim": ini("f4"), "h": 120},
    {"nome": "Maranhão, hoje", "sub": "110 cidades em alerta (INMET)", "lon": -45.0, "lat": -5.5, "ini": em("f3", "655"), "fim": ini("f4"), "h": 220},
    {"nome": "Rio Grande do Sul, amanhã", "sub": "184 cidades em alerta de tempestade (INMET)", "lon": -53.5, "lat": -29.5, "ini": em("f4", "224"), "fim": ini("f5"), "h": 150},
    {"nome": "Mato Grosso do Sul", "sub": "42 cidades no nível de perigo amanhã (INMET)", "lon": -54.6, "lat": -20.8, "ini": em("f5", "78"), "fim": ini("f6"), "h": 180},
    {"nome": "Minas Gerais, quinta", "sub": "494 cidades em alerta (INMET)", "lon": -44.0, "lat": -18.6, "ini": GFIM, "fim": ini("f7"), "h": 60},
    {"nome": "Cuiabá", "sub": f"{SOMA7['Cuiabá']} mm em 7 dias (previsão)", "lon": -56.1, "lat": -15.64, "ini": em("f7", "Cuiabá"), "fim": ini("f8"), "h": 260},
    {"nome": "Porto Alegre", "sub": f"máxima {PA_TX[0]} °C hoje → {PA_TX[4]} °C sábado (previsão)", "lon": -51.23, "lat": -30.03, "ini": em("f8", "Porto"), "fim": ini("f9"), "h": 160},
    {"nome": "Sul, dias 15 e 16", "sub": "frente fria e possível ciclone (tendência)", "lon": -50.3, "lat": -30.3, "ini": em("f9", "ciclone"), "fim": ini("f10"), "h": 140},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0


def conta(ate, fid, palavra, cor, unid, dec=0, de=0, k=1, desde=None):
    t = em(fid, palavra, k)
    lead = max(.4, min(LEAD, t - (desde if desde is not None else ini(fid))))   # número logo no começo: o contador cabe no painel
    return {"de": de, "ate": ate, "dec": dec, "ini": t - lead, "dur": lead, "cor": cor, "unid": unid}


R494 = em("f6", "494")
G31 = em("f8", "31")
GCAL = em("f8", "calor")
hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o fato da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:76px;color:#FACC15">2.574 CIDADES</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">em alerta de tempestade na quinta · 645 em São Paulo · INMET</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "HOJE, 10/11 · PREVISÃO",
     "itens": [{"t": em("f2", "seco"), "txt": "☀️ Sol e calor em quase todo o Sul"}, {"t": em("f2", "litoral"), "txt": "🌫️ Nuvens e chuvisco no litoral, de SC a SP"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "HOJE, 10/11 · CHUVA INTENSA",
     "contador": conta(655, "f3", "655", "#ff8c1a", "CIDADES"),
     "l": "GO 181 · TO 139 · MA 110 · PI 97 · até 50 mm no dia (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "QUARTA, 11/11 · ALERTA DE TEMPESTADE",
     "contador": conta(224, "f4", "224", "#ff8c1a", "CIDADES"),
     "l": "RS 184 · SC 40 · pancadas de verão (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "QUARTA, 11/11 · NÍVEL DE PERIGO",
     "contador": conta(78, "f5", "78", "#ff2a1f", "CIDADES"),
     "l": "MS 42 · MT 19 · GO 17 · vento de 60 a 100 km/h e granizo (INMET)", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f6"), "fim": GRAN - .1, "k": "QUINTA, 12/11 · ALERTA DE TEMPESTADE",
     "itens": [{"t": em("f6", "dispara"), "txt": "⛈️ Pancadas a qualquer hora em SP, MG e RJ"}],
     "borda": "rgba(255,140,26,.85)"},
    {"ini": GFIM, "fim": ini("f7"), "k": "QUINTA, 12/11 · CIDADES EM ALERTA",
     "ranking": {"itens": [{"nome": "São Paulo", "v": 645}, {"nome": "Minas", "v": 494}, {"nome": "Paraná", "v": 322},
                           {"nome": "Santa Catarina", "v": 271}, {"nome": "Rio Grande do Sul", "v": 263}],
                 "cor": "#ff8c1a", "cor_top": "#FACC15", "unid": "", "ini": GFIM, "dur": max(.4, R494 - GFIM)},
     "l": "aviso de tempestade · 2.574 cidades no total (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "CHUVA PREVISTA · 7 DIAS",
     "contador": conta(SOMA7["Cuiabá"], "f7", "83", "#5ec8ff", "MM EM CUIABÁ"),
     "l": f"Palmas {SOMA7['Palmas']} · Brasília {SOMA7['Brasília']} · Campo Grande {SOMA7['Campo Grande']} · Goiânia {SOMA7['Goiânia']} mm (Open-Meteo)", "borda": "rgba(60,150,255,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "SUL · PRÓXIMOS 7 DIAS (PREVISÃO)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": GCAL - 1.0, "dur": G31 - GCAL + 1.0,
                 "linha": {"nome": "Máxima em Porto Alegre", "cor": "#ff8c1a", "v": PA_TX, "unid": "°C"}},
     "l": f"Porto Alegre: {PA_TX[0]} °C hoje → {PA_TX[4]} °C no sábado · chuva em mm somados nas capitais do Sul (Open-Meteo)", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "SUL · DIAS 15 E 16 (TENDÊNCIA)",
     "itens": [{"t": em("f9", "frente"), "txt": "🌬️ Frente fria chega ao Sul"}, {"t": em("f9", "ciclone"), "txt": "🌀 Pode se formar um ciclone extratropical"}],
     "borda": "rgba(60,150,255,.85)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "onde"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f10", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
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

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

GOES = f"satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"
fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>INMET</b>, aviso de tempestade 12/11 (2.574 municípios) · {GOES}"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · {GOES}"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso de chuvas intensas 10/11 (655 municípios)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso de tempestade 11/11 (224 municípios)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INMET</b>, aviso de tempestade nível perigo 11/11 (78 municípios)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso de tempestade 12/11 · foto do granizo: ilustração"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"{OM}, 10/11 a 16/11"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · {OM}, 10/11 a 16/11"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "pancadas": "#5ec8ff", "chuvisco": "#5ec8ff", "frente": "#5ec8ff", "fria": "#5ec8ff",
         "granizo": "#ff2a1f", "perigo": "#ff2a1f", "tempestade": "#ff8c1a", "intensa": "#ff8c1a", "ciclone": "#ff2a1f",
         "extratropical": "#ff2a1f", "vento": "#ff8c1a", "alerta": "#ff2a1f", "atencao": "#ff2a1f", "seco": "#5ec8ff",
         "dispara": "#ff2a1f", "disparar": "#ff2a1f", "calor": "#ff2a1f", "quente": "#ff2a1f",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"minas", "florianopolis", "goias", "sao", "paulo", "cuiaba", "porto", "alegre", "rio", "parana", "sul", "norte", "centrooeste", "mato",
         "grosso", "gauchas", "catarinenses", "paraguai", "litoral", "hoje", "amanha", "quinta", "sabado", "terca", "inemaclub",
         "onde", "inmet"}
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
      f"quinta {QUINTA} · hoje {HOJE} · perigo {PERIGO} · 7d {SOMA7} · Porto Alegre {PA_TX}")
