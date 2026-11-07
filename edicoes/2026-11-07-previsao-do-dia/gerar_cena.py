#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 07/11/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "MAIS DE 100 MM NUM SÓ DIA NO PARANÁ HOJE"),
aviso de grande perigo do INMET de hoje (233: PR 223, SC 10) pintado, foto do granizo (ilustração) na frente fria,
contador 233 + critério de 100 km/h, solo encharcado → foto de enchente (ilustração), oeste/meio-oeste de SC,
sudoeste do PR e noroeste gaúcho (câmera inclinada), Vale do Itajaí / Rio do Sul, aviso de tempestade de hoje (2.980),
declínio de temperatura no domingo (2.060), gráfico dos 7 dias.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "07/11/2026"
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
PR = {"lon": -51.6, "lat": -25.0, "zoom": 5.5}       # f1: mais de 100 mm hoje no Paraná
SUL = {"lon": -51.5, "lat": -27.5, "zoom": 4.8}      # f2: baixa pressão → frente fria; f9
GPZ = {"lon": -52.2, "lat": -24.9, "zoom": 6.0}      # f3: área do grande perigo (PR centro/oeste + oeste de SC)
SOLO = {"lon": -52.4, "lat": -26.4, "zoom": 5.8}     # f4: solo encharcado
CORR = {"lon": -52.6, "lat": -26.9, "zoom": 6.2}     # f5: oeste/meio-oeste SC, sudoeste PR, noroeste RS
VALE = {"lon": -49.4, "lat": -27.1, "zoom": 6.8}     # f6: Vale do Itajaí, Rio do Sul
HOJEP = {"lon": -49.0, "lat": -21.0, "zoom": 4.1}    # f7: aviso de hoje (MG, SP, PR, RS, SC, GO)
DOM = {"lon": -50.5, "lat": -25.5, "zoom": 4.5}      # f8: domingo, temperatura cai
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
GRAN = em("f2", "temporais") - .1   # foto do granizo em "Os temporais podem vir com raios, granizo e vendaval"
GFIM = fim("f2") - .15
ENCH = em("f4", "Essa") - .1        # foto da enchente em "Essa chuva pode virar alagamento, enxurrada..."
EFIM = fim("f4") - .15
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, PR, 0, 0), K(fim("f1") - .2, {**PR, "zoom": 5.6}, 0, 0),
    K(ini("f2") + 1.0, SUL, 0, 0), K(fim("f2") - .2, {**SUL, "zoom": 4.9}, 0, 0),
    K(ini("f3") + 1.2, GPZ, 35, -10), K(fim("f3") - .2, {**GPZ, "zoom": 6.2}, 45, 8),
    K(ini("f4") + 1.0, SOLO, 0, 0), K(fim("f4") - .2, {**SOLO, "zoom": 5.9}, 0, 0),
    K(ini("f5") + 1.2, CORR, 45, -12), K(fim("f5") - .2, {**CORR, "zoom": 6.5}, 55, 14),
    K(ini("f6") + 1.0, VALE, 30, 0), K(fim("f6") - .2, {**VALE, "zoom": 7.0}, 40, 10),
    K(ini("f7") + 1.0, HOJEP, 0, 0), K(fim("f7") - .2, {**HOJEP, "zoom": 4.2}, 0, 0),
    K(ini("f8") + 1.0, DOM, 0, 0), K(fim("f8") - .2, {**DOM, "zoom": 4.6}, 0, 0),
    K(ini("f9") + 1.0, SUL, 0, 0), K(fim("f9") - .2, {**SUL, "zoom": 4.9}, 0, 0),
    K(ini("f10") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
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
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": CAPA - .3, "fim": IRF, "dur": IRF - CAPA, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

colunas = []   # a previsão de hoje não dá volume de chuva em mm por cidade (o 100 mm é o critério do INMET): sem colunas 3D

# ---------------------------------------------------------------- previsão Open-Meteo (7 dias): gráfico
P7 = json.loads((B / "previsao7d.json").read_text())
HOJE_D = "2026-11-07"
assert P7["dias"][0] == HOJE_D and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sáb", "dom", "seg", "ter", "qua", "qui", "sex"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
SEV = [d["por_regiao_mm"]["SE"] for d in P7["por_dia"]]
COV = [d["por_regiao_mm"]["CO"] for d in P7["por_dia"]]
assert SULV[0] == max(SULV) and round(SULV[0]) == 33 and round(SULV[1]) == 5, SULV  # Sul: pico hoje (33 mm), domingo 5 mm
series = [{"nome": "Sudeste", "cor": "#ff8c1a", "v": SEV}, {"nome": "Centro-Oeste", "cor": "#a78bfa", "v": COV},
          {"nome": "Sul", "cor": "#5ec8ff", "v": SULV}]

rios = []

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, granizo, enchente
assert GFIM - GRAN > 1.0, (GRAN, GFIM)
assert EFIM - ENCH > 1.0, (ENCH, EFIM)
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .02},
         {"src": "capa-dia/granizo.png", "ini": GRAN, "fim": GFIM, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/enchente.png", "ini": ENCH, "fim": EFIM, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
GP = ufs_av(56337)   # tempestade GRANDE PERIGO hoje 7/11, 11h45–23h59: 233 (PR 223, SC 10)
assert len(geo(56337)) == 233 and aviso[56337]["descricao"] == "Tempestade" and aviso[56337]["severidade"] == "Grande Perigo"
assert aviso[56337]["inicio"].startswith("2026-11-07") and GP == ["PR", "SC"]
assert (por_uf(56337, "PR"), por_uf(56337, "SC")) == (223, 10)
HOJE_T = geo(56318) | geo(56322) | geo(56337)   # tempestade hoje 7/11: 2.980
assert len(HOJE_T) == 2980 and all(aviso[i]["inicio"].startswith("2026-11-07") and aviso[i]["descricao"] == "Tempestade" for i in (56318, 56322, 56337))
HOJE_UF = sorted({UF[c[:2]] for c in HOJE_T if sum(x[:2] == c[:2] for x in HOJE_T) >= 5})
hoje_uf = lambda uf: sum(UF[c[:2]] == uf for c in HOJE_T)
assert (hoje_uf("MG"), hoje_uf("SP"), hoje_uf("PR"), hoje_uf("RS"), hoje_uf("SC")) == (734, 645, 399, 385, 295)
DOM_ = ufs_av(56281)      # declínio de temperatura domingo 8/11: 2.060
assert len(geo(56281)) == 2060 and aviso[56281]["descricao"] == "Declínio de Temperatura" and aviso[56281]["inicio"].startswith("2026-11-08")
estados = [
    {"id": "gp", "ini": CAPA, "fim": ini("f2") + .3, "ufs": ["PR"], "cor": VERM, "alfa": .45},
    {"id": "frente", "ini": em("f2", "frente"), "fim": ini("f3") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .35},
    {"id": "gp2", "ini": em("f3", "perigo"), "fim": ini("f4") + .3, "ufs": GP, "cor": VERM, "alfa": .45},
    {"id": "solo", "ini": em("f4", "solo"), "fim": ini("f5") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .4},
    {"id": "corredor", "ini": em("f5", "oeste"), "fim": ini("f6") + .3, "ufs": ["PR", "SC", "RS"], "cor": VERM, "alfa": .35},
    {"id": "vale", "ini": em("f6", "Vale"), "fim": ini("f7") + .3, "ufs": ["SC"], "cor": LAR, "alfa": .4},
    {"id": "hoje", "ini": em("f7", "aviso"), "fim": ini("f8") + .3, "ufs": HOJE_UF, "cor": LAR, "alfa": .4},
    {"id": "domingo", "ini": em("f8", "temperatura"), "fim": ini("f9") + .3, "ufs": DOM_, "cor": AZUL, "alfa": .4},
]

pinos = [
    {"nome": "Paraná, hoje", "sub": "risco de mais de 100 mm no dia (INMET)", "lon": -51.8, "lat": -24.6, "ini": em("f1", "Paraná"), "fim": ini("f2"), "h": 200},
    {"nome": "Frente fria", "sub": "raios, granizo e vendaval (previsão)", "lon": -53.0, "lat": -30.0, "ini": em("f2", "frente"), "fim": GRAN - .1, "h": 160},
    {"nome": "Paraná", "sub": "223 cidades em grande perigo (INMET)", "lon": -52.0, "lat": -24.4, "ini": em("f3", "Paraná"), "fim": ini("f4"), "h": 220},
    {"nome": "Oeste de SC", "sub": "10 cidades em grande perigo (INMET)", "lon": -52.33, "lat": -26.56, "ini": em("f3", "Paraná"), "fim": ini("f4"), "h": 80},
    {"nome": "Oeste de SC", "sub": "Chapecó · temporais hoje (previsão)", "lon": -52.62, "lat": -27.10, "ini": em("f5", "Santa"), "fim": ini("f6"), "h": 50},
    {"nome": "Meio-oeste de SC", "sub": "Joaçaba · temporais (previsão)", "lon": -51.50, "lat": -27.17, "ini": em("f5", "meio"), "fim": ini("f6"), "h": 150},
    {"nome": "Sudoeste do PR", "sub": "risco alto de tempo severo (previsão)", "lon": -53.0, "lat": -25.9, "ini": em("f5", "sudoeste"), "fim": ini("f6"), "h": 280},
    {"nome": "Noroeste gaúcho", "sub": "temporais (previsão)", "lon": -54.0, "lat": -28.0, "ini": em("f5", "gaúcho"), "fim": ini("f6"), "h": 60},
    {"nome": "Rio do Sul", "sub": "Vale do Itajaí em alerta (previsão)", "lon": -49.64, "lat": -27.21, "ini": em("f6", "Rio"), "fim": ini("f7"), "h": 140},
    {"nome": "Domingo, 8/11", "sub": "temperatura cai em 2.060 cidades (INMET)", "lon": -50.0, "lat": -24.0, "ini": em("f8", "temperatura"), "fim": ini("f9"), "h": 260},
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
                 '<div class="t1" style="font-size:76px;color:#FACC15">MAIS DE 100 MM</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">de chuva num só dia · risco de hoje no Paraná · INMET</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": GRAN - .1, "k": "HOJE, 7/11 · PREVISÃO",
     "itens": [{"t": em("f2", "baixa"), "txt": "🌀 Baixa pressão se forma"}, {"t": em("f2", "frente"), "txt": "❄️ Dá origem a uma frente fria"}],
     "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "GRANDE PERIGO · HOJE ATÉ 23H59",
     "contador": conta(233, "f3", "233", "#ff2a1f", "CIDADES"),
     "l": "PR 223 · SC 10 · vento acima de 100 km/h, mais de 100 mm no dia, granizo (INMET)", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f4"), "fim": ENCH - .05, "k": "HOJE · ATENÇÃO",
     "itens": [{"t": em("f4", "solo"), "txt": "💧 Solo já encharcado"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "HOJE · ATENÇÃO REDOBRADA",
     "itens": [{"t": em("f5", "Santa"), "txt": "⛈️ Oeste e meio-oeste de SC"}, {"t": em("f5", "sudoeste"), "txt": "⛈️ Sudoeste do Paraná"},
               {"t": em("f5", "gaúcho"), "txt": "⛈️ Noroeste gaúcho"}],
     "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "VALE DO ITAJAÍ · ALERTA",
     "itens": [{"t": em("f6", "Rio"), "txt": "📍 Região de Rio do Sul"}, {"t": em("f6", "rios"), "txt": "🌊 Rios dão sinais de cheia"}],
     "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE, 7/11 · AVISO DE TEMPESTADE",
     "contador": conta(2980, "f7", "2.980", "#ff8c1a", "CIDADES"),
     "l": "MG 734 · SP 645 · PR 399 · RS 385 · SC 295 (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "DOMINGO, 8/11 · TEMPERATURA CAI",
     "contador": conta(2060, "f8", "2.060", "#5ec8ff", "CIDADES"),
     "l": "aviso de declínio de temperatura (INMET)", "borda": "rgba(60,150,255,.85)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "PRÓXIMOS 7 DIAS (CHUVA PREVISTA)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f9") + .3, "dur": 1.6},
     "l": f"Sul: {round(SULV[0])} mm hoje → {round(SULV[1])} mm no domingo · mm somados nas capitais", "borda": "rgba(94,200,255,.7)"},
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

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

GOES = f"satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"
fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>INMET</b>, critério do aviso de grande perigo de 07/11 · {GOES}"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · foto do granizo: ilustração"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>INMET</b>, tempestade grande perigo 07/11 (233 municípios) · {GOES}"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · foto da enchente: ilustração"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>, avisos de tempestade para 07/11 (2.980 municípios)"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · <b>INMET</b>, declínio de temperatura 08/11 (2.060 municípios)"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · {OM}, 07/11 a 13/11"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "pancadas": "#5ec8ff", "frente": "#5ec8ff", "fria": "#5ec8ff", "garoa": "#5ec8ff", "frio": "#5ec8ff",
         "encharcado": "#ff2a1f", "alagamento": "#ff2a1f", "enxurrada": "#ff2a1f", "deslizamento": "#ff2a1f", "cheia": "#ff2a1f",
         "granizo": "#ff2a1f", "perigo": "#ff2a1f", "grande": "#ff2a1f", "raios": "#ff8c1a", "tempestade": "#ff8c1a",
         "temporais": "#ff8c1a", "vendaval": "#ff8c1a", "vento": "#ff8c1a", "aviso": "#ff8c1a", "alerta": "#ff2a1f",
         "atencao": "#ff2a1f", "redobrada": "#ff2a1f", "cair": "#5ec8ff", "seco": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"parana", "sul", "catarina", "santa", "oeste", "sudoeste", "noroeste", "gaucho", "meiooeste", "centroleste", "vale", "itajai",
         "rio", "sabado", "domingo", "hoje", "segunda", "terca", "quarta", "inemaclub", "onde", "inmet"}
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
      f"grande perigo {GP} · hoje {HOJE_UF} · domingo {DOM_} · Sul {SULV}")
