#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 27/10/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png), infravermelho do GOES-19 sobre o Sul (alta pressão com ar seco),
garoa no litoral do PR, SP, RJ e ES, pancadas em MS e calor no oeste do Sul, pancadas de quarta, foto do temporal (ilustração)
de quinta e sexta, aviso amarelo de tempestade do INMET na quinta (2.777), 30 a 50 mm previstos no Sul com o solo encharcado,
calor de até 44 °C no domingo no PI, CE, MA e PA, gráfico da chuva prevista em 7 dias e frentes frias de novembro.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "27/10/2026"
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
ABRE = {"lon": -50.0, "lat": -16.0, "zoom": 3.9}     # f1: Brasil (temporais qui/sex e calor de domingo)
SIST = {"lon": -52.0, "lat": -27.5, "zoom": 4.7}     # f2: alta pressão com ar seco sobre o Sul (IR)
LIT = {"lon": -45.0, "lat": -23.2, "zoom": 5.0}      # f3: garoa no litoral do PR, SP, RJ e ES
MSO = {"lon": -54.0, "lat": -24.0, "zoom": 4.9}      # f4: pancadas em MS; oeste do Sul mais quente
QUA = {"lon": -49.0, "lat": -20.0, "zoom": 4.2}      # f5: quarta, pancadas no SE, CO e Sul
QS = {"lon": -49.5, "lat": -21.0, "zoom": 4.4}       # f6: quinta e sexta, baixa pressão e temporais
AVQ = {"lon": -50.0, "lat": -21.5, "zoom": 4.3}      # f7: aviso amarelo de quinta (2.777)
SUL = {"lon": -52.3, "lat": -27.3, "zoom": 5.3}      # f8: 30 a 50 mm no Sul, solo encharcado
NE = {"lon": -44.0, "lat": -5.5, "zoom": 4.7}        # f9: domingo, até 44 °C no PI, CE, MA e PA
G7 = {"lon": -50.0, "lat": -22.0, "zoom": 4.45}      # f10: gráfico dos 7 dias
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
TEMP = em("f6", "temporais")
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, ABRE, 0, 0), K(fim("f1") - .2, {**ABRE, "zoom": 4.0}, 0, 0),
    K(ini("f2") + 1.0, SIST, 0, 0), K(fim("f2") - .2, {**SIST, "zoom": 4.8}, 0, 0),
    K(ini("f3") + 1.0, LIT, 0, 0), K(fim("f3") - .2, {**LIT, "zoom": 5.1}, 0, 0),
    K(ini("f4") + 1.0, MSO, 0, 0), K(fim("f4") - .2, {**MSO, "zoom": 5.0}, 0, 0),
    K(ini("f5") + 1.0, QUA, 0, 0), K(fim("f5") - .2, {**QUA, "zoom": 4.3}, 0, 0),
    K(ini("f6") + 1.0, QS, 10, -4), K(fim("f6") - .2, {**QS, "zoom": 4.5}, 12, 4),
    K(ini("f7") + 1.0, AVQ, 0, 0), K(fim("f7") - .2, {**AVQ, "zoom": 4.4}, 0, 0),
    K(ini("f8") + 1.0, SUL, 50, -20), K(fim("f8") - .2, {**SUL, "zoom": 5.4}, 56, 16),
    K(ini("f9") + 1.0, NE, 0, 0), K(fim("f9") - .2, {**NE, "zoom": 4.8}, 0, 0),
    K(ini("f10") + 1.0, G7, 0, 0), K(fim("f10") - .2, {**G7, "zoom": 4.55}, 0, 0),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) (f1–f2)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
assert len(BONS) >= 40, BONS
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": CAPA - .3, "fim": ini("f3") + .3, "dur": ini("f3") - CAPA + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

colunas = []

# gráfico: chuva prevista no Sul, Sudeste e Centro-Oeste em 7 dias (soma das capitais, Open-Meteo)
P7 = json.loads((B / "previsao7d.json").read_text())
HOJE = "2026-10-27"
assert P7["dias"][0] == HOJE and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["ter", "qua", "qui", "sex", "sáb", "dom", "seg"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
SEV = [d["por_regiao_mm"]["SE"] for d in P7["por_dia"]]
COV = [d["por_regiao_mm"]["CO"] for d in P7["por_dia"]]
assert max(SULV[0:2]) < 5 and SULV[3] > 30 and max(SEV[2:4]) > 50, (SULV, SEV)   # Sul seco ter e qua; chuva forte qui e sex
series = [{"nome": "Sul", "cor": "#5ec8ff", "v": SULV}, {"nome": "Sudeste", "cor": "#ff8c1a", "v": SEV},
          {"nome": "Centro-Oeste", "cor": "#a78bfa", "v": COV}]

rios = []

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e temporal
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/temporal.png", "ini": TEMP - .1, "fim": fim("f6") - .1, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
AQUI_ = ufs_av(56195)    # tempestade AMARELA (Perigo Potencial) quinta 29/10: 2.777 (SP 645, MG 536, PR 399, SC 295, GO 246)
assert len(geo(56195)) == 2777 and por_uf(56195, "SP") == 645 and por_uf(56195, "MG") == 536 and por_uf(56195, "PR") == 399
assert por_uf(56195, "SC") == 295 and por_uf(56195, "GO") == 246
assert aviso[56195]["descricao"] == "Tempestade" and aviso[56195]["severidade"] == "Perigo Potencial" and aviso[56195]["inicio"].startswith("2026-10-29")
estados = [
    {"id": "sul0", "ini": CAPA, "fim": ini("f2") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .22},
    {"id": "seco", "ini": em("f2", "alta"), "fim": ini("f3") + .3, "ufs": ["RS", "SC", "PR"], "cor": AMA, "alfa": .25},
    {"id": "garoa", "ini": em("f3", "litoral"), "fim": ini("f4") + .3, "ufs": ["PR", "SP", "RJ", "ES"], "cor": FRIO, "alfa": .25},
    {"id": "ms", "ini": em("f4", "Mato"), "fim": ini("f5") + .3, "ufs": ["MS"], "cor": AZUL, "alfa": .3},
    {"id": "quente", "ini": em("f4", "oeste"), "fim": ini("f5") + .3, "ufs": ["PR", "SC", "RS"], "cor": LAR, "alfa": .22},
    {"id": "quarta", "ini": em("f5", "pancadas"), "fim": ini("f6") + .3, "ufs": ["SP", "MG", "RJ", "ES", "GO", "MT", "MS", "DF", "PR", "SC", "RS"], "cor": AZUL, "alfa": .22},
    {"id": "quisex", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["SP", "MG", "RJ", "ES", "GO", "MT", "MS", "DF"], "cor": AZUL, "alfa": .35},
    {"id": "aqui", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": AQUI_, "cor": AMA, "alfa": .4},
    {"id": "sulchuva", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .35},
    {"id": "calor", "ini": em("f9", "Piauí"), "fim": ini("f10") + .3, "ufs": ["PI", "CE", "MA", "PA"], "cor": VERM, "alfa": .4},
]

pinos = [
    {"nome": "Sul do Brasil", "sub": "alta pressão · ar seco", "lon": -52.5, "lat": -27.8, "ini": em("f2", "alta"), "fim": ini("f3"), "h": 160},
    {"nome": "Litoral do PR", "sub": "garoa", "lon": -48.5, "lat": -25.5, "ini": em("f3", "Paraná"), "fim": ini("f4"), "h": 50},
    {"nome": "Litoral de SP", "sub": "garoa", "lon": -46.3, "lat": -23.95, "ini": em("f3", "Paulo"), "fim": ini("f4"), "h": 230},
    {"nome": "Rio de Janeiro", "sub": "garoa", "lon": -43.2, "lat": -22.9, "ini": em("f3", "Rio"), "fim": ini("f4"), "h": 50},
    {"nome": "Espírito Santo", "sub": "garoa", "lon": -40.3, "lat": -20.3, "ini": em("f3", "Espírito"), "fim": ini("f4"), "h": 160},
    {"nome": "Mato Grosso do Sul", "sub": "algumas pancadas", "lon": -54.6, "lat": -20.5, "ini": em("f4", "Mato"), "fim": ini("f5"), "h": 120},
    {"nome": "Oeste do Sul", "sub": "mais quente hoje e amanhã", "lon": -53.3, "lat": -26.5, "ini": em("f4", "oeste"), "fim": ini("f5"), "h": 200},
    {"nome": "Sul do Brasil", "sub": "30 a 50 mm previstos", "lon": -52.4, "lat": -27.2, "ini": em("f8", "Sul"), "fim": ini("f9"), "h": 220},
    {"nome": "Piauí", "sub": "até 44 °C domingo", "lon": -42.8, "lat": -5.1, "ini": em("f9", "Piauí"), "fim": ini("f10"), "h": 300},
    {"nome": "Ceará", "sub": "até 44 °C", "lon": -39.5, "lat": -5.2, "ini": em("f9", "Ceará"), "fim": ini("f10"), "h": 160},
    {"nome": "Maranhão", "sub": "até 44 °C", "lon": -45.3, "lat": -5.0, "ini": em("f9", "Maranhão"), "fim": ini("f10"), "h": 40},
    {"nome": "Pará", "sub": "até 44 °C", "lon": -50.5, "lat": -4.0, "ini": em("f9", "Pará"), "fim": ini("f10"), "h": 160},
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
                 '<div class="t1" style="font-size:92px;color:#ff2a1f">ATÉ 44°C</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">no domingo · temporais na quinta e na sexta</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "HOJE, 27/10 · O QUE MANDA NO TEMPO",
     "itens": [{"t": em("f2", "alta"), "txt": "🌀 Alta pressão"}, {"t": em("f2", "seco"), "txt": "☀️ Ar seco segura a chuva"}],
     "l": "sobre o Sul · vai perdendo força", "borda": "rgba(250,204,21,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "HOJE, 27/10 (PREVISÃO)",
     "itens": [{"t": em("f3", "garoa"), "txt": "🌦️ Garoa no litoral"}, {"t": em("f3", "firme"), "txt": "☀️ No resto, tempo firme"}],
     "l": "PR, SP, RJ e ES", "borda": "rgba(150,210,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE E AMANHÃ (PREVISÃO)",
     "itens": [{"t": em("f4", "pancadas"), "txt": "⛈️ Pancadas em MS"}, {"t": em("f4", "quente"), "txt": "🌡️ Oeste do Sul mais quente"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "QUARTA, 28/10 (PREVISÃO)",
     "itens": [{"t": em("f5", "nuvens"), "txt": "☁️ Nuvens aumentam"}, {"t": em("f5", "pancadas"), "txt": "🌧️ Pancadas isoladas"}],
     "l": "mais no Sudeste e no Centro-Oeste, e no Sul", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": TEMP - .1, "k": "QUINTA E SEXTA (PREVISÃO)",
     "itens": [{"t": em("f6", "baixa"), "txt": "🌀 Baixa pressão"}, {"t": em("f6", "carregadas"), "txt": "⛈️ Nuvens carregadas"}],
     "l": "Sudeste e Centro-Oeste", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "QUINTA, 29/10 · AVISO AMARELO",
     "contador": conta(2777, "f7", "2.777", "#FACC15", "CIDADES · TEMPESTADE"),
     "l": "SP 645 · MG 536 · PR 399 · SC 295 · GO 246 (INMET)", "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "SUL · QUINTA E SEXTA (PREVISÃO)",
     "contador": conta(50, "f8", "50", "#5ec8ff", "MM PREVISTOS", de=30),
     "l": "de 30 a 50 mm · solo encharcado: alagamento pontual", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "DOMINGO, 01/11 (PREVISÃO)",
     "contador": conta(44, "f9", "44", "#ff2a1f", "°C · PI, CE, MA E PA", de=30),
     "l": "fim de semana: o sol volta ao Sul", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "PRÓXIMOS 7 DIAS · CHUVA PREVISTA",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f10") + .3, "dur": 1.6},
     "l": "frentes frias por volta de 3, 6 e 8 de novembro (projeção) · mm somados nas capitais", "borda": "rgba(250,204,21,.7)"},
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
    {"ini": CAPA, "fim": ini("f3"), "html": f"<b>{MET}</b> · {GOES}"},
    {"ini": ini("f3"), "fim": ini("f6"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · foto do temporal: ilustração"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>INMET</b>, aviso amarelo de tempestade para 29/10 (2.777 municípios)"},
    {"ini": ini("f8"), "fim": ini("f10"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": f"<b>{MET}</b> · {OM}, 27/10 a 02/11"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "pancadas": "#5ec8ff", "garoa": "#5ec8ff", "seco": AM, "firme": AM, "sol": AM,
         "nuvens": "#5ec8ff", "carregadas": "#5ec8ff", "frente": "#5ec8ff", "frentes": "#5ec8ff", "frias": "#5ec8ff", "baixa": "#5ec8ff",
         "alta": AM, "pressao": AM, "encharcado": "#5ec8ff", "alagamento": "#ff2a1f", "quente": "#ff2a1f", "calor": "#ff2a1f",
         "graus": "#ff2a1f", "tempestade": "#ff8c1a", "temporais": "#ff8c1a", "aviso": "#ff8c1a", "instavel": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"parana", "sul", "sao", "paulo", "rio", "espirito", "santo", "litoral", "mato", "grosso", "oeste", "sudeste", "centrooeste",
         "piaui", "ceara", "maranhao", "inemaclub", "onde"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR or w.startswith("Pará") else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        prox = t["palavras"][i + 1]["w"] if i + 1 < len(t["palavras"]) else ""
        longo = sum(len(b["w"]) + 1 for b in bloco) + len(prox) > 20   # "marcaram 500 milímetros" passava da borda
        if len(bloco) == 3 or longo or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · PREVISÃO DO DIA", "selo": DATA[:5] + " · INMET · NOAA",
     "camera": camera, "sat": SAT, "imagens": [], "colunas": colunas, "rios": rios, "telas": telas, "estados": estados, "pinos": pinos,
     "hero": hero, "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"amarelo qui {AQUI_} · 7 dias {ROTD} · Sul {SULV} · Sudeste {SEV} · CO {COV}")
