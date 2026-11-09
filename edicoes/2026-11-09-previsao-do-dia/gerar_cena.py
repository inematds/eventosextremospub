#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 09/11/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "1.273 CIDADES EM ALERTA DE TEMPESTADE · HOJE · DA BAHIA A GOIÁS"),
aviso de tempestade do INMET de hoje (1.273: BA 299, MG 281, GO 244) pintado, ar seco no Sul/SP × pancadas no CO/SE, foto do
granizo (ilustração) no critério do aviso, ranking por estado, colunas 3D da chuva prevista em 7 dias nas capitais do CO/SE/TO,
aviso de amanhã (654, de Goiás ao Piauí), Sul firme depois dos tornados, gráfico do Sul (chuva + máxima de Curitiba 17 → 28 °C),
tendência de 100 a 150 mm no Sul depois do dia 19.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "09/11/2026"
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
BAGO = {"lon": -45.5, "lat": -14.0, "zoom": 4.6}      # f1: 1.273 cidades, da Bahia a Goiás
SULSE = {"lon": -48.5, "lat": -20.0, "zoom": 4.2}     # f2: ar seco no Sul/SP × pancadas no CO/SE
CRIT = {"lon": -44.0, "lat": -13.5, "zoom": 5.4}      # f3: critério do aviso
EST = {"lon": -45.0, "lat": -14.5, "zoom": 4.8}       # f4: Bahia, Minas, Goiás
COL = {"lon": -48.0, "lat": -15.0, "zoom": 4.6}       # f5: colunas 3D (7 dias nas capitais)
GOPI = {"lon": -46.0, "lat": -10.0, "zoom": 4.6}      # f6: amanhã, de Goiás ao Piauí
SUL = {"lon": -51.0, "lat": -26.8, "zoom": 5.4}       # f7: Sul firme; garoa leste PR, pancadas oeste SC
CWB = {"lon": -50.0, "lat": -26.0, "zoom": 5.0}       # f8: quarta/quinta pancadas; calor em Curitiba
SUL19 = {"lon": -51.5, "lat": -27.5, "zoom": 4.9}     # f9: tendência depois do dia 19
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
GRAN = em("f3", "vento") - .1       # foto do granizo em "vento de até 60 quilômetros por hora e granizo"
GFIM = fim("f3") - .15
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, BAGO, 0, 0), K(fim("f1") - .2, {**BAGO, "zoom": 4.7}, 0, 0),
    K(ini("f2") + 1.0, SULSE, 0, 0), K(fim("f2") - .2, {**SULSE, "zoom": 4.3}, 0, 0),
    K(ini("f3") + 1.0, CRIT, 30, -8), K(fim("f3") - .2, {**CRIT, "zoom": 5.6}, 40, 6),
    K(ini("f4") + 1.2, EST, 35, -10), K(fim("f4") - .2, {**EST, "zoom": 4.9}, 45, 8),
    K(ini("f5") + 1.2, COL, 55, -20), K(fim("f5") - .2, {**COL, "zoom": 4.7}, 56, 15),
    K(ini("f6") + 1.0, GOPI, 0, 0), K(fim("f6") - .2, {**GOPI, "zoom": 4.7}, 0, 0),
    K(ini("f7") + 1.0, SUL, 30, 0), K(fim("f7") - .2, {**SUL, "zoom": 5.6}, 40, 10),
    K(ini("f8") + 1.0, CWB, 0, 0), K(fim("f8") - .2, {**CWB, "zoom": 5.1}, 0, 0),
    K(ini("f9") + 1.0, SUL19, 35, -8), K(fim("f9") - .2, {**SUL19, "zoom": 5.0}, 45, 8),
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
CAPS = {"Palmas": (-10.16, -48.32), "Goiânia": (-16.7, -49.26), "Brasília": (-15.78, -47.89), "Vitória": (-20.35, -40.34),
        "Belo Horizonte": (-19.93, -43.97), "Cuiabá": (-15.64, -56.1), "Curitiba": (-25.41, -49.24)}


def cap(nome):
    la, lo = CAPS[nome]
    x = min(OMC, key=lambda c: abs(c["latitude"] - la) + abs(c["longitude"] - lo))
    assert abs(x["latitude"] - la) < .1 and abs(x["longitude"] - lo) < .1, nome
    assert x["daily"]["time"][0] == "2026-11-09", x["daily"]["time"]
    return x


SOMA7 = {nm: round(sum(v or 0 for v in cap(nm)["daily"]["precipitation_sum"])) for nm in CAPS if nm != "Curitiba"}
assert SOMA7["Palmas"] == 92 and SOMA7["Goiânia"] > 70 and SOMA7["Brasília"] > 70, SOMA7   # f5
CW = cap("Curitiba")["daily"]
CW_TX = [round(v) for v in CW["temperature_2m_max"]]
assert CW_TX[0] == 17 and CW_TX[6] == 28 and CW["time"][6] == "2026-11-15", CW_TX   # f8: 17 → 28 no domingo

# colunas 3D: chuva PREVISTA somada em 7 dias nas capitais do Centro-Oeste, Sudeste e Tocantins
col = [{"id": i, "p": [cap(nm)["longitude"], cap(nm)["latitude"]], "v": v, "cor": [60, 150, 255] if v >= 60 else [120, 190, 255]}
       for i, (nm, v) in enumerate(SOMA7.items())]
ordem = {c["id"]: i * .15 for i, c in enumerate(sorted(col, key=lambda c: -c["v"]))}
colunas = [{"id": "chuva7d", "ini": ini("f5") + .3, "fim": ini("f6") + .3, "dados": col, "raio": 45000, "escala": 4200, "ordem": ordem, "varredura": 1}]

P7 = json.loads((B / "previsao7d.json").read_text())
HOJE_D = "2026-11-09"
assert P7["dias"][0] == HOJE_D and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
assert SULV[2] > SULV[0] and SULV[3] > SULV[0], SULV   # quarta e quinta: pancadas voltam ao Sul
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
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
HOJE = ufs_av(56358)   # tempestade (perigo potencial) hoje 9/11, 09h27–23h59: 1.273
assert len(geo(56358)) == 1273 and aviso[56358]["descricao"] == "Tempestade" and aviso[56358]["inicio"].startswith("2026-11-09")
assert (por_uf(56358, "BA"), por_uf(56358, "MG"), por_uf(56358, "GO"), por_uf(56358, "PI"), por_uf(56358, "TO")) == (299, 281, 244, 146, 139)
assert "50 mm/dia" in aviso[56358]["riscos"][0] and "40-60 km/h" in aviso[56358]["riscos"][0] and "granizo" in aviso[56358]["riscos"][0]
HOJE_T = set()
for a in AV["hoje"]:
    if a["descricao"] == "Tempestade" and a["inicio"].startswith("2026-11-09"):
        HOJE_T |= set(a["geocodes"].split(","))
assert len(HOJE_T) == 1273, len(HOJE_T)   # só um aviso de tempestade hoje
TER = ufs_av(56361)   # tempestade terça 10/11: 654
assert len(geo(56361)) == 654 and aviso[56361]["descricao"] == "Tempestade" and aviso[56361]["inicio"].startswith("2026-11-10")
assert (por_uf(56361, "GO"), por_uf(56361, "PI"), por_uf(56361, "TO"), por_uf(56361, "MA")) == (171, 165, 139, 94)
estados = [
    {"id": "hoje", "ini": CAPA, "fim": ini("f2") + .3, "ufs": HOJE, "cor": LAR, "alfa": .45},
    {"id": "seco", "ini": em("f2", "seco"), "fim": em("f2", "pancadas") + .3, "ufs": ["PR", "SC", "RS", "SP"], "cor": AZUL, "alfa": .35},
    {"id": "pancadas", "ini": em("f2", "pancadas"), "fim": ini("f3") + .3, "ufs": ["MG", "GO", "DF", "TO", "MT", "RJ", "ES", "BA"], "cor": LAR, "alfa": .35},
    {"id": "hoje2", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": HOJE, "cor": LAR, "alfa": .45},
    {"id": "top3", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["BA", "MG", "GO"], "cor": LAR, "alfa": .5},
    {"id": "terca", "ini": em("f6", "alerta"), "fim": ini("f7") + .3, "ufs": TER, "cor": LAR, "alfa": .4},
    {"id": "sul", "ini": em("f7", "Sul"), "fim": ini("f8") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .3},
    {"id": "calor", "ini": em("f8", "calor"), "fim": ini("f9") + .3, "ufs": ["PR", "SC", "RS"], "cor": LAR, "alfa": .3},
    {"id": "sul19", "ini": em("f9", "chuva"), "fim": ini("f10") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .45},
]

pinos = [
    {"nome": "Bahia, hoje", "sub": "299 cidades em alerta de tempestade (INMET)", "lon": -41.5, "lat": -12.5, "ini": em("f1", "Bahia"), "fim": ini("f2"), "h": 200},
    {"nome": "Sul e São Paulo", "sub": "ar seco segura o tempo (previsão)", "lon": -51.0, "lat": -27.5, "ini": em("f2", "seco"), "fim": ini("f3"), "h": 120},
    {"nome": "Centro-Oeste e Sudeste", "sub": "pancadas com trovoada (previsão)", "lon": -47.0, "lat": -16.5, "ini": em("f2", "Centro-Oeste"), "fim": ini("f3"), "h": 220},
    {"nome": "Bahia", "sub": "299 cidades em alerta (INMET)", "lon": -40.5, "lat": -12.0, "ini": em("f4", "Bahia"), "fim": ini("f5"), "h": 110},
    {"nome": "Minas Gerais", "sub": "281 cidades em alerta (INMET)", "lon": -44.0, "lat": -18.6, "ini": em("f4", "Minas"), "fim": ini("f5"), "h": 30},
    {"nome": "Goiás", "sub": "244 cidades em alerta (INMET)", "lon": -49.6, "lat": -15.8, "ini": em("f4", "Goiás"), "fim": ini("f5"), "h": 190},
    {"nome": "Palmas", "sub": f"{SOMA7['Palmas']} mm em 7 dias (previsão)", "lon": -48.32, "lat": -10.16, "ini": em("f5", "Palmas"), "fim": ini("f6"), "h": 260},
    {"nome": "Goiás, amanhã", "sub": "171 cidades em alerta (INMET)", "lon": -49.6, "lat": -15.8, "ini": em("f6", "Goiás"), "fim": ini("f7"), "h": 120},
    {"nome": "Piauí, amanhã", "sub": "165 cidades em alerta (INMET)", "lon": -42.8, "lat": -7.5, "ini": em("f6", "Piauí"), "fim": ini("f7"), "h": 200},
    {"nome": "Leste do Paraná", "sub": "garoa hoje (previsão)", "lon": -49.3, "lat": -25.4, "ini": em("f7", "garoa"), "fim": ini("f8"), "h": 160},
    {"nome": "Oeste catarinense", "sub": "pancadas à tarde (previsão)", "lon": -52.6, "lat": -27.1, "ini": em("f7", "oeste"), "fim": ini("f8"), "h": 60},
    {"nome": "Curitiba", "sub": "máxima 17 °C hoje → 28 °C domingo (previsão)", "lon": -49.27, "lat": -25.43, "ini": em("f8", "Curitiba"), "fim": ini("f9"), "h": 160},
    {"nome": "Sul, depois do dia 19", "sub": "100 a 150 mm (tendência)", "lon": -52.5, "lat": -28.5, "ini": em("f9", "Sul"), "fim": ini("f10"), "h": 140},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0


def conta(ate, fid, palavra, cor, unid, dec=0, de=0, k=1, desde=None):
    t = em(fid, palavra, k)
    lead = max(.4, min(LEAD, t - (desde if desde is not None else ini(fid))))   # número logo no começo: o contador cabe no painel
    return {"de": de, "ate": ate, "dec": dec, "ini": t - lead, "dur": lead, "cor": cor, "unid": unid}


R299 = em("f4", "299")
G17, G28 = em("f8", "17"), em("f8", "28")
hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o fato da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:76px;color:#FACC15">1.273 CIDADES</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">em alerta de tempestade hoje · da Bahia a Goiás · INMET</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "HOJE, 9/11 · PREVISÃO",
     "itens": [{"t": em("f2", "seco"), "txt": "☀️ Ar seco no Sul e em São Paulo"}, {"t": em("f2", "pancadas"), "txt": "⛈️ Pancadas com trovoada no Centro-Oeste e Sudeste"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f3"), "fim": GRAN - .1, "k": "ALERTA · CRITÉRIO DO INMET",
     "itens": [{"t": em("f3", "50"), "txt": "🌧️ Até 50 mm no dia"}],
     "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE, 9/11 · CIDADES EM ALERTA",
     "ranking": {"itens": [{"nome": "Bahia", "v": 299}, {"nome": "Minas", "v": 281}, {"nome": "Goiás", "v": 244},
                           {"nome": "Piauí", "v": 146}, {"nome": "Tocantins", "v": 139}],
                 "cor": "#ff8c1a", "cor_top": "#FACC15", "unid": "", "ini": R299 - 1.0, "dur": 1.0},
     "l": "aviso de tempestade · 1.273 cidades no total (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "CHUVA PREVISTA · 7 DIAS",
     "contador": conta(SOMA7["Palmas"], "f5", "92", "#5ec8ff", "MM EM PALMAS"),
     "l": f"Goiânia {SOMA7['Goiânia']} · Brasília {SOMA7['Brasília']} · Vitória {SOMA7['Vitória']} mm (Open-Meteo)", "borda": "rgba(60,150,255,.85)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "TERÇA, 10/11 · ALERTA DE TEMPESTADE",
     "contador": conta(654, "f6", "654", "#ff8c1a", "CIDADES"),
     "l": "GO 171 · PI 165 · TO 139 · MA 94 (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SUL · HOJE (PREVISÃO)",
     "itens": [{"t": em("f7", "firme"), "txt": "🌤️ Semana começa firme"}, {"t": em("f7", "garoa"), "txt": "🌫️ Garoa no leste do Paraná"},
               {"t": em("f7", "pancadas"), "txt": "⛈️ Pancadas à tarde no oeste catarinense"}],
     "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "SUL · PRÓXIMOS 7 DIAS (PREVISÃO)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": G17 - 1.0, "dur": G28 - G17 + 1.0,
                 "linha": {"nome": "Máxima em Curitiba", "cor": "#ff8c1a", "v": CW_TX, "unid": "°C"}},
     "l": f"Curitiba: {CW_TX[0]} °C hoje → {CW_TX[6]} °C no domingo · chuva em mm somados nas capitais do Sul (Open-Meteo)", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "SUL · DEPOIS DO DIA 19 (TENDÊNCIA)",
     "contador": conta(150, "f9", "150", "#5ec8ff", "MM", de=100),
     "l": "100 a 150 mm sobre solo encharcado e rios cheios", "borda": "rgba(60,150,255,.85)"},
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
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>INMET</b>, aviso de tempestade 09/11 (1.273 municípios) · {GOES}"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · {GOES}"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INMET</b>, critério do aviso de tempestade · foto do granizo: ilustração"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INMET</b>, aviso de tempestade para 09/11 (1.273 municípios)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"{OM}, 09/11 a 15/11"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INMET</b>, aviso de tempestade para 10/11 (654 municípios)"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · {OM}, 09/11 a 15/11"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "pancadas": "#5ec8ff", "garoa": "#5ec8ff", "frias": "#5ec8ff", "despenca": "#5ec8ff", "cair": "#5ec8ff",
         "rios": "#ff2a1f", "granizo": "#ff2a1f", "perigo": "#ff2a1f", "laranja": "#ff8c1a", "tempestade": "#ff8c1a",
         "vento": "#ff8c1a", "aviso": "#ff8c1a", "alerta": "#ff2a1f", "atencao": "#ff2a1f", "fortes": "#ff8c1a",
         "seco": "#5ec8ff", "trovoada": "#ff8c1a", "dispara": "#ff2a1f", "calor": "#ff2a1f", "tornados": "#ff2a1f", "atencao": "#ff2a1f", "encharcado": "#ff2a1f", "cheios": "#ff2a1f", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"minas", "goias", "sao", "paulo", "palmas", "goiania", "brasilia", "bahia", "sudeste", "piaui", "parana", "catarinense",
         "centrooeste", "curitiba", "sul", "hoje", "amanha", "domingo", "segunda", "quarta", "quinta", "inemaclub", "onde", "inmet"}
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
      f"hoje {HOJE} · terça {TER} · 7d {SOMA7} · Curitiba {CW_TX}")
