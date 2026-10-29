#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 29/10/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png), aviso amarelo de chuvas intensas de hoje (2.804 cidades), infravermelho
do GOES-19 (baixa pressão fraca no Sul), chuva em SC, PR e norte gaúcho, pancadas no CO e SE, aviso laranja de tempestade (397, MG 273),
temperaturas (Chapecó, Campo Grande, litoral paulista), aviso de sexta (3.226), gráfico dos 7 dias (Sul sobe na quarta 4/11),
frente fria de 3 e 4/11 com foto da tempestade (ilustração) e colunas 3D da chuva prevista em 7 dias nas capitais (Curitiba 66, BH 76).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "29/10/2026"
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
ABRE = {"lon": -50.0, "lat": -18.0, "zoom": 3.95}    # f1: aviso de chuvas intensas de hoje (2.804)
BAIXA = {"lon": -51.5, "lat": -26.0, "zoom": 4.5}    # f2: baixa pressão fraca no Sul (IR)
SUL = {"lon": -51.8, "lat": -28.0, "zoom": 5.2}      # f3: chuva em SC, PR e norte gaúcho; centro-sul gaúcho seco
CSE = {"lon": -49.0, "lat": -18.5, "zoom": 4.55}     # f4: pancadas em MT, GO, SP, MG e RJ
MG = {"lon": -45.5, "lat": -20.0, "zoom": 5.0}       # f5: aviso laranja de tempestade (MG 273)
TMP = {"lon": -51.0, "lat": -24.0, "zoom": 4.7}      # f6: temperaturas
AVS = {"lon": -49.0, "lat": -21.5, "zoom": 4.4}      # f7: aviso de chuvas intensas de sexta (3.226)
G7 = {"lon": -51.0, "lat": -24.0, "zoom": 4.5}       # f8: fim de semana, segunda e gráfico dos 7 dias
FF = {"lon": -52.5, "lat": -28.0, "zoom": 5.0}       # f9: frente fria de 3 e 4/11
COL = {"lon": -46.5, "lat": -23.0, "zoom": 4.9}      # f10: colunas 3D da chuva prevista nas capitais
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
TEMP = em("f9", "tempestades")
SETE = em("f10", "sete")
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, ABRE, 0, 0), K(fim("f1") - .2, {**ABRE, "zoom": 4.05}, 0, 0),
    K(ini("f2") + 1.0, BAIXA, 10, -4), K(fim("f2") - .2, {**BAIXA, "zoom": 4.6}, 12, 4),
    K(ini("f3") + 1.0, SUL, 0, 0), K(fim("f3") - .2, {**SUL, "zoom": 5.3}, 0, 0),
    K(ini("f4") + 1.0, CSE, 0, 0), K(fim("f4") - .2, {**CSE, "zoom": 4.65}, 0, 0),
    K(ini("f5") + 1.0, MG, 0, 0), K(fim("f5") - .2, {**MG, "zoom": 5.1}, 0, 0),
    K(ini("f6") + 1.0, TMP, 0, 0), K(fim("f6") - .2, {**TMP, "zoom": 4.8}, 0, 0),
    K(ini("f7") + 1.0, AVS, 0, 0), K(fim("f7") - .2, {**AVS, "zoom": 4.5}, 0, 0),
    K(ini("f8") + 1.0, G7, 0, 0), K(fim("f8") - .2, {**G7, "zoom": 4.6}, 0, 0),
    K(ini("f9") + 1.0, FF, 20, -6), K(fim("f9") - .2, {**FF, "zoom": 5.1}, 24, 6),
    K(SETE - .3, {**COL, "zoom": 4.7}, 30, -10), K(SETE + 1.0, COL, 55, -20), K(fim("f10") - .2, {**COL, "zoom": 5.0}, 58, 16),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
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


SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": CAPA - .3, "fim": ini("f3") + .3, "dur": ini("f3") - CAPA + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

# ---------------------------------------------------------------- previsão Open-Meteo (7 dias): colunas 3D e gráfico
P7 = json.loads((B / "previsao7d.json").read_text())
HOJE = "2026-10-29"
assert P7["dias"][0] == HOJE and len(P7["dias"]) == 7
TOP = dict(P7["acumulado_7d_top"])
assert round(TOP["Curitiba"]) == 66 and round(TOP["Belo Horizonte"]) == 76, TOP
CAP = {"Belo Horizonte": (-43.94, -19.92), "Brasília": (-47.88, -15.79), "Curitiba": (-49.27, -25.43), "Campo Grande": (-54.62, -20.47),
       "Florianópolis": (-48.55, -27.59), "Goiânia": (-49.25, -16.68), "São Paulo": (-46.63, -23.55), "Porto Alegre": (-51.23, -30.03)}
cor_mm = lambda mm: [255, 42, 31] if mm >= 60 else [120, 90, 255]
col = [{"id": i, "p": list(CAP[c]), "v": TOP[c], "cor": cor_mm(TOP[c])} for i, c in enumerate(CAP)]
ordem = {c["id"]: i * .12 for i, c in enumerate(col)}
colunas = [{"id": "prev7d", "ini": SETE - .4, "fim": ini("f11") + .4, "dados": col, "raio": 26000, "escala": 5500, "ordem": ordem, "varredura": 1}]

ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qui", "sex", "sáb", "dom", "seg", "ter", "qua"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
SEV = [d["por_regiao_mm"]["SE"] for d in P7["por_dia"]]
COV = [d["por_regiao_mm"]["CO"] for d in P7["por_dia"]]
assert SULV[6] == max(SULV) and SULV[6] > 70 and max(SULV[2:5]) < 10, SULV   # Sul seco no fim de semana, pico na quarta 4/11 (frente fria)
series = [{"nome": "Sudeste", "cor": "#ff8c1a", "v": SEV}, {"nome": "Centro-Oeste", "cor": "#a78bfa", "v": COV},
          {"nome": "Sul", "cor": "#5ec8ff", "v": SULV}]

rios = []

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e tempestade
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/temporal.png", "ini": TEMP - .1, "fim": SETE - .2, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
HOJE_ = ufs_av(56211)    # chuvas intensas AMARELO hoje 29/10: 2.804 (SP 645, MG 511, PR 399, SC 295, GO 246)
assert len(geo(56211)) == 2804 and por_uf(56211, "SP") == 645 and por_uf(56211, "MG") == 511 and por_uf(56211, "PR") == 399
assert aviso[56211]["descricao"] == "Chuvas Intensas" and aviso[56211]["severidade"] == "Perigo Potencial" and aviso[56211]["inicio"].startswith("2026-10-29")
TEMPEST = ufs_av(56213)  # tempestade LARANJA (Perigo) hoje 29/10: 397 (MG 273, SP 95, RJ 16, GO 13)
assert len(geo(56213)) == 397 and por_uf(56213, "MG") == 273 and por_uf(56213, "SP") == 95 and por_uf(56213, "RJ") == 16
assert aviso[56213]["descricao"] == "Tempestade" and aviso[56213]["severidade"] == "Perigo" and aviso[56213]["inicio"].startswith("2026-10-29")
SEX_ = ufs_av(56215)     # chuvas intensas AMARELO sexta 30/10: 3.226 (MG 853, SP 645, PR 399, SC 283, GO 246)
assert len(geo(56215)) == 3226 and por_uf(56215, "MG") == 853 and por_uf(56215, "SP") == 645
assert aviso[56215]["descricao"] == "Chuvas Intensas" and aviso[56215]["inicio"].startswith("2026-10-30")
estados = [
    {"id": "hoje", "ini": CAPA, "fim": ini("f2") + .3, "ufs": HOJE_, "cor": AMA, "alfa": .35},
    {"id": "baixa", "ini": em("f2", "baixa"), "fim": ini("f3") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .3},
    {"id": "sulhoje", "ini": em("f3", "Santa"), "fim": ini("f4") + .3, "ufs": ["SC", "PR"], "cor": AZUL, "alfa": .35},
    {"id": "cse", "ini": em("f4", "Mato"), "fim": ini("f5") + .3, "ufs": ["MT", "GO", "SP", "MG", "RJ"], "cor": AZUL, "alfa": .35},
    {"id": "tempest", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": TEMPEST, "cor": LAR, "alfa": .45},
    {"id": "sex", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": SEX_, "cor": AMA, "alfa": .4},
    {"id": "rsseco", "ini": em("f8", "Rio"), "fim": ini("f9") + .3, "ufs": ["RS"], "cor": AMA, "alfa": .25},
    {"id": "frente", "ini": em("f9", "frente"), "fim": ini("f10") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .35},
]

pinos = [
    {"nome": "Baixa pressão", "sub": "fraca · chuva com pouco volume", "lon": -51.5, "lat": -26.5, "ini": em("f2", "baixa"), "fim": ini("f3"), "h": 200},
    {"nome": "Santa Catarina", "sub": "chuva à tarde e à noite", "lon": -50.5, "lat": -27.2, "ini": em("f3", "Santa"), "fim": ini("f4"), "h": 60},
    {"nome": "Paraná", "sub": "chuva à tarde e à noite", "lon": -51.5, "lat": -24.8, "ini": em("f3", "Paraná"), "fim": ini("f4"), "h": 180},
    {"nome": "Norte gaúcho", "sub": "chuva", "lon": -52.5, "lat": -28.3, "ini": em("f3", "norte"), "fim": ini("f4"), "h": 120},
    {"nome": "Centro-sul gaúcho", "sub": "tempo seco", "lon": -53.5, "lat": -30.8, "ini": em("f3", "centro-sul"), "fim": ini("f4"), "h": 80},
    {"nome": "Mato Grosso", "sub": "pancadas", "lon": -55.5, "lat": -13.0, "ini": em("f4", "Mato"), "fim": ini("f5"), "h": 120},
    {"nome": "Goiás", "sub": "pancadas", "lon": -49.6, "lat": -16.2, "ini": em("f4", "Goiás"), "fim": ini("f5"), "h": 200},
    {"nome": "São Paulo", "sub": "pancadas", "lon": -48.5, "lat": -22.3, "ini": em("f4", "São"), "fim": ini("f5"), "h": 100},
    {"nome": "Minas Gerais", "sub": "pancadas", "lon": -44.5, "lat": -18.5, "ini": em("f4", "Minas"), "fim": ini("f5"), "h": 160},
    {"nome": "Rio de Janeiro", "sub": "pancadas", "lon": -42.8, "lat": -22.4, "ini": em("f4", "Janeiro"), "fim": ini("f5"), "h": 60},
    {"nome": "Minas Gerais", "sub": "273 cidades · tempestade", "lon": -44.5, "lat": -19.0, "ini": em("f5", "273"), "fim": ini("f6"), "h": 220},
    {"nome": "Chapecó", "sub": "28 °C (previsão)", "lon": -52.62, "lat": -27.10, "ini": em("f6", "Chapecó"), "fim": ini("f7"), "h": 120},
    {"nome": "Campo Grande", "sub": "28 °C (previsão)", "lon": -54.62, "lat": -20.47, "ini": em("f6", "Campo"), "fim": ini("f7"), "h": 160},
    {"nome": "Litoral paulista", "sub": "20 °C (previsão)", "lon": -46.33, "lat": -23.96, "ini": em("f6", "litoral"), "fim": ini("f7"), "h": 80},
    {"nome": "Rio Grande do Sul", "sub": "dias secos", "lon": -53.5, "lat": -30.0, "ini": em("f8", "Rio"), "fim": ini("f9"), "h": 100},
    {"nome": "Oeste do PR e SC", "sub": "chuva na segunda", "lon": -53.0, "lat": -25.8, "ini": em("f8", "oeste"), "fim": ini("f9"), "h": 200},
    {"nome": "Sul do Brasil", "sub": "frente fria 3 e 4/11 (projeção)", "lon": -52.5, "lat": -28.5, "ini": em("f9", "frente"), "fim": TEMP, "h": 220},
    {"nome": "Curitiba", "sub": "66 mm em 7 dias (previsão)", "lon": -49.27, "lat": -25.43, "ini": em("f10", "66"), "fim": ini("f11"), "h": 300},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0


def conta(ate, fid, palavra, cor, unid, dec=0, de=0, k=1):
    t = em(fid, palavra, k)
    lead = max(.4, min(LEAD, t - ini(fid)))   # número logo no começo da fala: o contador cabe no painel
    return {"de": de, "ate": ate, "dec": dec, "ini": t - lead, "dur": lead, "cor": cor, "unid": unid}


hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o número da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:92px;color:#FACC15">2.804 CIDADES</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">em alerta de chuvas intensas hoje · aviso do INMET</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "QUEM MANDA NO TEMPO",
     "itens": [{"t": em("f2", "baixa"), "txt": "🌀 Baixa pressão fraca no Sul"}, {"t": em("f2", "temporais"), "txt": "🌦️ Chuva e temporais isolados"}],
     "l": "pouco volume de chuva", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "HOJE NO SUL (PREVISÃO)",
     "itens": [{"t": em("f3", "Santa"), "txt": "🌧️ SC, PR e norte gaúcho"}, {"t": em("f3", "centro-sul"), "txt": "☀️ Centro-sul gaúcho seco"}],
     "l": "chuva à tarde e à noite", "borda": "rgba(150,210,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE · CENTRO-OESTE E SUDESTE",
     "itens": [{"t": em("f4", "Mato"), "txt": "⛈️ Mato Grosso e Goiás"}, {"t": em("f4", "São"), "txt": "⛈️ SP, MG e RJ"}],
     "l": "pancadas (previsão)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "HOJE, 29/10 · AVISO LARANJA",
     "contador": conta(397, "f5", "397", "#ff8c1a", "CIDADES · TEMPESTADE"),
     "l": "MG 273 · SP 95 · RJ 16 · GO 13 (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "TEMPERATURA MÁXIMA (PREVISÃO)",
     "itens": [{"t": em("f6", "Chapecó"), "txt": "🌡️ Chapecó e C. Grande 28 °C"}, {"t": em("f6", "litoral"), "txt": "🌊 Litoral paulista 20 °C"}],
     "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SEXTA, 30/10 · AVISO AMARELO",
     "contador": conta(3226, "f7", "3.226", "#FACC15", "CIDADES · CHUVAS INTENSAS"),
     "l": "MG 853 · SP 645 · PR 399 · SC 283 · GO 246 (INMET)", "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "PRÓXIMOS 7 DIAS · CHUVA PREVISTA",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f8") + .3, "dur": 1.6},
     "l": "fim de semana com calor · RS seco · mm somados nas capitais", "borda": "rgba(250,204,21,.7)"},
    {"ini": ini("f9"), "fim": TEMP - .1, "k": "3 E 4 DE NOVEMBRO (PROJEÇÃO)",
     "itens": [{"t": em("f9", "frente"), "txt": "🌀 Frente fria organizada no Sul"}],
     "borda": "rgba(60,150,255,.8)"},
    {"ini": SETE - .2, "fim": ini("f11"), "k": "PRÓXIMOS 7 DIAS · CHUVA PREVISTA",
     "contador": conta(66, "f10", "66", "#ff2a1f", "MM EM CURITIBA"),
     "l": "BH 76 · Brasília 69 · Campo Grande 59 · Florianópolis 52 mm", "borda": "rgba(255,42,31,.8)"},
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
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>INMET</b>, aviso amarelo de chuvas intensas para 29/10 (2.804 municípios) · {GOES}"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · {GOES}"},
    {"ini": ini("f3"), "fim": ini("f5"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INMET</b>, aviso laranja de tempestade para 29/10 (397 municípios)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>, aviso amarelo de chuvas intensas para 30/10 (3.226 municípios)"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · {OM}, 29/10 a 04/11"},
    {"ini": ini("f9"), "fim": SETE - .2, "html": f"<b>{MET}</b> · foto da tempestade: ilustração"},
    {"ini": SETE - .2, "fim": ini("f11"), "html": f"<b>{MET}</b> · {OM}, 29/10 a 04/11"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chover": "#5ec8ff", "chove": "#5ec8ff", "milimetros": "#5ec8ff", "pancadas": "#5ec8ff", "sol": AM,
         "frente": "#5ec8ff", "fria": "#5ec8ff", "baixa": "#5ec8ff", "pressao": "#5ec8ff", "seco": AM, "calor": "#ff2a1f",
         "graus": "#ff2a1f", "laranja": "#ff8c1a", "intensas": "#ff8c1a", "tempestade": "#ff8c1a", "tempestades": "#ff8c1a",
         "temporais": "#ff8c1a", "aviso": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"parana", "sul", "sao", "paulo", "mato", "grosso", "sudeste", "centrooeste", "goias", "minas", "rio", "janeiro",
         "santa", "catarina", "gaucho", "centrosul", "chapeco", "campo", "grande", "litoral", "paulista", "curitiba",
         "belo", "horizonte", "oeste", "inemaclub", "onde"}
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
      f"hoje {HOJE_} · tempestade {TEMPEST} · sex {SEX_} · 7 dias {ROTD} · Sul {SULV} · Sudeste {SEV} · CO {COV}")
