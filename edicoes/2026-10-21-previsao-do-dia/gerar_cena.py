#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 21/10/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png), infravermelho do GOES-19 sobre o Sul (baixa pressão),
gráfico da chuva prevista no Sul em 7 dias, alertas do INMET (tempestade hoje, quinta e laranja na sexta; baixa umidade no Nordeste),
calor em Teresina, foto do granizo (ilustração), colunas 3D da chuva prevista até domingo, foto do alagamento (ilustração), tendência.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "21/10/2026"
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
SULIR = {"lon": -51.0, "lat": -26.0, "zoom": 4.9}    # f1: o Sul no IR (nuvens da baixa pressão)
AMZSUL = {"lon": -56.0, "lat": -17.0, "zoom": 3.9}   # f2: da Amazônia ao Sul
OESTE = {"lon": -53.2, "lat": -26.3, "zoom": 5.6}    # f3: oeste do RS, oeste de SC, sudoeste do PR
NE = {"lon": -41.5, "lat": -8.0, "zoom": 4.6}        # f4: calor no Nordeste, Teresina
PR = {"lon": -51.5, "lat": -24.8, "zoom": 5.5}       # f5: centro do Paraná na quinta
SUL = {"lon": -51.5, "lat": -26.5, "zoom": 5.0}      # f6/f7: sexta a domingo no Sul
COL = {"lon": -51.6, "lat": -26.2, "zoom": 5.6}      # f8: colunas 3D até domingo
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
GRAN = em("f6", "granizo")
ALAG = em("f9", "alagamento")
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, SULIR, 0, 0), K(fim("f1") - .2, {**SULIR, "zoom": 5.0}, 0, 0),
    K(ini("f2") + 1.0, AMZSUL, 0, 0), K(fim("f2") - .2, {**AMZSUL, "zoom": 4.0}, 0, 0),
    K(ini("f3") + 1.0, OESTE, 30, -8), K(fim("f3") - .2, {**OESTE, "zoom": 5.7}, 34, 6),
    K(ini("f4") + 1.0, NE, 0, 0), K(fim("f4") - .2, {**NE, "zoom": 4.7}, 0, 0),
    K(ini("f5") + 1.0, PR, 20, -6), K(fim("f5") - .2, {**PR, "zoom": 5.6}, 24, 6),
    K(ini("f6") + 1.0, SUL, 15, -4), K(fim("f6") - .2, {**SUL, "zoom": 5.1}, 18, 4),
    K(ini("f7") + 1.0, {**SUL, "lat": -26.0}, 0, 0), K(fim("f7") - .2, {**SUL, "lat": -26.0, "zoom": 5.1}, 0, 0),
    K(ini("f8") + 1.0, COL, 52, -20), K(fim("f8") - .2, {**COL, "zoom": 5.7}, 56, 16),
    K(ini("f9") + 1.0, {**SUL, "zoom": 5.3}, 25, -6), K(fim("f9") - .2, {**SUL, "zoom": 5.4}, 28, 6),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -20.0, "zoom": 4.2}, 0, 0), K(fim("f10") - .2, {"lon": -51.0, "lat": -20.0, "zoom": 4.3}, 0, 0),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) sobre o Sul (f1–f2)
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

# ---------------------------------------------------------------- previsão Open-Meteo nas capitais (pesquisa/bruto/resumo.json)
OMC = json.loads((B / "resumo.json").read_text())["openmeteo_capitais"]["linhas"]
linha = lambda cap, dia: next(l for l in OMC if l["cap"] == cap and l["dia"] == dia)
HOJE, SAB = "2026-10-21", "2026-10-24"
assert linha("Teresina", HOJE)["tmax"] == 39.3 and linha("Teresina", SAB)["tmax"] == 40.1

# colunas 3D: faixa de chuva PREVISTA até domingo, 25/10 (Meteorologia · 21/10: 150 a 200 mm no PR e Grande Curitiba,
# 100 a 150 mm no oeste, meio-oeste e Planalto Norte de SC e no noroeste do RS)
REG = [("Grande Curitiba", -49.3, -25.45, 200), ("Centro do PR", -51.5, -25.0, 200), ("Sudoeste do PR", -52.9, -25.9, 200),
       ("Oeste do PR", -53.5, -24.9, 150), ("Oeste de SC", -52.7, -26.9, 150), ("Planalto Norte de SC", -50.0, -26.4, 150),
       ("Meio-oeste de SC", -51.4, -27.1, 120), ("Noroeste do RS", -54.0, -28.0, 100)]
cor_mm = lambda mm: [60, 150, 255] if mm < 150 else [120, 90, 255] if mm < 200 else [255, 42, 31]
col = [{"id": i, "p": [lon, lat], "v": v, "cor": cor_mm(v)} for i, (_, lon, lat, v) in enumerate(REG)]
ordem = {c["id"]: i * .15 for i, c in enumerate(col)}
colunas = [{"id": "chuvadom", "ini": ini("f8") + .3, "fim": ini("f9") + .5, "dados": col, "raio": 26000, "escala": 1500, "ordem": ordem, "varredura": 1}]

# gráfico: chuva prevista no Sul em 7 dias (soma das capitais do Sul)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == HOJE and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qua", "qui", "sex", "sáb", "dom", "seg", "ter"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
assert max(SULV[:2]) < 10 and min(SULV[2:5]) > 30 and max(SULV[5:]) < 10   # pancadas hoje e quinta; forte de sexta a domingo; seca seg/ter
series = [{"nome": "Sul", "cor": "#5ec8ff", "v": SULV}]

rios = []

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, granizo e alagamento
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": GRAN - .1, "fim": fim("f6") - .1, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/enchente.png", "ini": ALAG - .1, "fim": fim("f9") - .1, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
TQUA = ufs_av(56127)     # tempestade amarelo hoje, quarta 21/10, a partir das 15 h: 623 (PR 323, RS 147, SC 121, MS 28)
assert len(geo(56127)) == 623 and por_uf(56127, "PR") == 323 and por_uf(56127, "RS") == 147 and por_uf(56127, "SC") == 121
assert aviso[56127]["descricao"] == "Tempestade" and aviso[56127]["inicio"].startswith("2026-10-21")
SECO = ufs_av(56135, 50)  # baixa umidade hoje: 1489 (MG 236, PI 220, GO 205, BA 202, CE 135)
assert len(geo(56135)) == 1489 and por_uf(56135, "PI") == 220 and aviso[56135]["descricao"] == "Baixa Umidade"
TQUI = ufs_av(56137)     # tempestade amarelo quinta 22/10: 2883 (MG 646, SP 645, RS 497, PR 399, SC 295)
assert len(geo(56137)) == 2883 and por_uf(56137, "PR") == 399 and por_uf(56137, "SP") == 645
assert aviso[56137]["descricao"] == "Tempestade" and aviso[56137]["inicio"].startswith("2026-10-22")
LSEX = ufs_av(56139)     # tempestade LARANJA (Perigo) sexta 23/10: 678 (PR 342, RS 189, SC 132, MS 14)
assert len(geo(56139)) == 678 and por_uf(56139, "PR") == 342 and por_uf(56139, "RS") == 189 and por_uf(56139, "SC") == 132
assert aviso[56139]["descricao"] == "Tempestade" and aviso[56139]["severidade"] == "Perigo" and aviso[56139]["inicio"].startswith("2026-10-23")
estados = [
    {"id": "sul0", "ini": CAPA, "fim": ini("f2") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .2},
    {"id": "baixa", "ini": em("f2", "baixa"), "fim": ini("f3") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .35},
    {"id": "tqua", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": TQUA, "cor": LAR, "alfa": .45},
    {"id": "seco", "ini": em("f4", "Nordeste"), "fim": ini("f5") + .3, "ufs": SECO, "cor": LAR, "alfa": .4},
    {"id": "tqui", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": TQUI, "cor": LAR, "alfa": .45},
    {"id": "sul3", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .35},
    {"id": "lsex", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": LSEX, "cor": VERM, "alfa": .4},
    {"id": "pr", "ini": ini("f8"), "fim": fim("f9"), "ufs": ["PR"], "cor": VERM, "alfa": .3},
]

pinos = [
    {"nome": "Paraná", "sub": "até 200 mm até domingo · previsão", "lon": -51.6, "lat": -24.9, "ini": em("f1", "Paraná"), "fim": ini("f2"), "h": 200},
    {"nome": "Amazônia", "sub": "ar quente e úmido", "lon": -62.0, "lat": -6.0, "ini": em("f2", "Amazônia"), "fim": ini("f3"), "h": 200},
    {"nome": "Oeste gaúcho", "sub": "pancadas hoje", "lon": -55.8, "lat": -29.5, "ini": em("f3", "oeste"), "fim": ini("f4"), "h": 110},
    {"nome": "Oeste catarinense", "sub": "pancadas hoje", "lon": -52.3, "lat": -27.0, "ini": em("f3", "catarinense"), "fim": ini("f4"), "h": 30},
    {"nome": "Sudoeste do Paraná", "sub": "pancadas hoje", "lon": -52.9, "lat": -25.9, "ini": em("f3", "sudoeste"), "fim": ini("f4"), "h": 170},
    {"nome": "Teresina", "sub": "39,3 °C hoje · 40,1 °C sábado", "lon": -42.80, "lat": -5.09, "ini": em("f4", "Teresina"), "fim": ini("f5"), "h": 260},
    {"nome": "Centro do Paraná", "sub": "chuva concentrada na quinta", "lon": -51.5, "lat": -25.0, "ini": em("f5", "centro"), "fim": ini("f6"), "h": 260},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
conta = lambda ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1: {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o número da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:92px;color:#5ec8ff">200 MM</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">de chuva no Paraná até domingo</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "POR QUE · SUL · CHUVA PREVISTA EM 7 DIAS",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f2") + .3, "dur": 1.6},
     "l": "baixa pressão + umidade da Amazônia · mm somados nas capitais do Sul", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "HOJE, 21/10 · TEMPESTADE À TARDE",
     "contador": conta(623, "f3", "623", "#ff8c1a", "CIDADES EM ALERTA"),
     "l": "PR 323 · RS 147 · SC 121 · MS 28 · a partir das 15 h (INMET)", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE · CALOR EM TERESINA (PREVISÃO)",
     "contador": conta(39.3, "f4", "39", "#ff8c1a", "°C DE MÁXIMA", dec=1),
     "l": "baixa umidade em 1.489 cidades (INMET) · 40,1 °C no sábado (Open-Meteo)", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "QUINTA, 22/10 · TEMPESTADE",
     "contador": conta(2883, "f5", "2883", "#ff8c1a", "CIDADES EM ALERTA", de=623),
     "l": "MG 646 · SP 645 · RS 497 · PR 399 · SC 295 (INMET)", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f6"), "fim": GRAN - .1, "k": "SEXTA A DOMINGO (PREVISÃO)",
     "itens": [{"t": em("f6", "grossa"), "txt": "🌧️ Chuva mais grossa"}, {"t": em("f6", "trovoada"), "txt": "⛈️ Trovoada"}],
     "l": "granizo e ventania no PR, SC e noroeste do RS", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SEXTA, 23/10 · ALERTA LARANJA",
     "contador": conta(678, "f7", "678", "#ff2a1f", "CIDADES EM ALERTA", lead=max(.4, min(LEAD, em("f7", "678") - ini("f7")))),
     "l": "PR 342 · RS 189 · SC 132 · tempestade · sábado deve ser o pior dia (INMET)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "ATÉ DOMINGO, 25/10 · CHUVA PREVISTA",
     "contador": conta(200, "f8", "200", "#ff2a1f", "MM NO PARANÁ"),
     "l": "100 a 150 mm no oeste de SC e no noroeste do RS · coluna = mm previstos", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f9"), "fim": ALAG - .1, "k": "O SOLO JÁ ESTÁ ENCHARCADO",
     "contador": conta(500, "f9", "500", "#5ec8ff", "MM JÁ EM ALGUMAS ESTAÇÕES"),
     "l": "alagamento · enxurrada · deslizamento · queda de barreira", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "PRÓXIMOS DIAS (TENDÊNCIA)",
     "itens": [{"t": em("f10", "segunda"), "txt": "🌤️ Seg e ter, 26 e 27/10: mais seco"},
               {"t": em("f10", "fim"), "txt": "🌧️ Fim da próxima semana: chuva forte"}],
     "l": "início de novembro: seco; chuva de novo por volta de 4 e 5/11", "borda": "rgba(60,150,255,.7)"},
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

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>{MET}</b> · satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · {OM}, 21 a 27/10"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso amarelo de tempestade para 21/10 (623 municípios)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · {OM} · <b>INMET</b>, aviso de baixa umidade em 21/10 (1.489 municípios)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso amarelo de tempestade para 22/10 (2.883 municípios)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · foto do granizo: ilustração"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso laranja de tempestade para 23/10 (678 municípios)"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · faixa de chuva prevista até 25/10 · altura da coluna = milímetros"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · foto do alagamento: ilustração"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "umido": "#5ec8ff", "pancadas": "#5ec8ff",
         "alagamento": "#ff2a1f", "enxurrada": "#ff2a1f", "deslizamento": "#ff2a1f", "barreira": "#ff2a1f", "laranja": "#ff2a1f",
         "tempestade": "#ff8c1a", "alerta": "#ff8c1a", "trovoada": "#ff8c1a", "granizo": "#ff8c1a", "ventania": "#ff8c1a",
         "baixa": "#ff8c1a", "pressao": "#ff8c1a", "calor": "#ff8c1a", "graus": "#ff8c1a", "seco": "#ff8c1a", "pior": "#ff2a1f",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"parana", "sul", "amazonia", "oeste", "gaucho", "catarinense", "sudoeste", "nordeste", "teresina", "centro",
         "santa", "catarina", "noroeste", "curitiba", "pais", "inemaclub", "onde"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
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
      f"tempestade qua {TQUA} · seco {SECO} · qui {TQUI} · laranja sex {LSEX} · 7 dias {ROTD} · Sul {SULV}")
