#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 16/10/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png), infravermelho do GOES-19 sobre o Sul e o Atlântico (ciclone),
alerta laranja de MG e o total do Brasil, colunas 3D da chuva prevista hoje nas capitais, foto da ventania na Lagoa dos Patos
(ilustração), foto da geada (ilustração) e gráfico da chuva prevista no Sul em 7 dias.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "16/10/2026"
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
BRA = {"lon": -50.0, "lat": -17.5, "zoom": 3.95}     # f4/f7: o Brasil
CICL = {"lon": -47.0, "lat": -26.8, "zoom": 4.7}    # f1/f2: Sul e Atlântico (ciclone no IR)
SE = {"lon": -45.0, "lat": -21.0, "zoom": 5.0}       # f3/f6: de SP ao RJ e ES
MG = {"lon": -44.6, "lat": -18.6, "zoom": 5.3}       # f3: Minas Gerais
COL = {"lon": -48.5, "lat": -21.5, "zoom": 4.75}     # f4: colunas 3D nas capitais
RSL = {"lon": -51.0, "lat": -30.6, "zoom": 6.0}      # f5: litoral gaúcho e Lagoa dos Patos
SERRA = {"lon": -51.0, "lat": -27.4, "zoom": 6.0}    # f8: Serra e Campos de Palmas
PR = {"lon": -51.8, "lat": -25.0, "zoom": 5.9}       # f9/f10: Paraná
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
MINAS, BRASIL, CAPITAL = em("f3", "Minas"), em("f4", "Brasil"), em("f4", "capital")
VENT = em("f5", "ventania")
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, CICL, 0, 0), K(fim("f1") - .2, {**CICL, "zoom": 4.75}, 0, 0),
    K(ini("f2") + 1.0, {**CICL, "lon": -48.0, "lat": -26.2}, 15, -4), K(fim("f2") - .2, {**CICL, "lon": -48.3, "lat": -26.0}, 18, 4),
    K(ini("f3") + 1.0, SE, 10, 0), K(MINAS - .2, {**SE, "lon": -44.8}, 10, 0), K(MINAS + .9, MG, 10, 0), K(fim("f3") - .2, {**MG, "zoom": 5.35}, 10, 0),
    K(BRASIL + .6, BRA, 0, 0), K(CAPITAL - .2, {**BRA, "zoom": 4.0}, 0, 0),
    K(CAPITAL + 1.2, COL, 52, -20), K(fim("f4") - .2, {**COL, "zoom": 4.8}, 56, 16),
    K(ini("f5") + 1.0, RSL, 20, -6), K(fim("f5") - .2, {**RSL, "zoom": 6.1}, 24, 4),
    K(ini("f6") + 1.0, SE, 10, 0), K(fim("f6") - .2, {**SE, "lon": -43.8}, 12, 2),
    K(ini("f7") + 1.0, BRA, 0, 0), K(fim("f7") - .2, {**BRA, "zoom": 4.0}, 0, 0),
    K(ini("f8") + 1.0, SERRA, 30, -8), K(fim("f8") - .2, {**SERRA, "zoom": 6.1}, 34, 4),
    K(ini("f9") + 1.0, PR, 10, 0), K(fim("f9") - .2, {**PR, "lon": -51.6}, 12, 2),
    K(ini("f10") + 1.0, {**PR, "zoom": 5.7}, 0, 0), K(fim("f10") - .2, {**PR, "zoom": 5.8}, 0, 0),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) sobre o Sul e o Atlântico (f1–f2)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": CAPA - .3, "fim": fim("f2") + .3, "dur": fim("f2") - CAPA + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

# ---------------------------------------------------------------- previsão Open-Meteo nas capitais (pesquisa/bruto/resumo.json)
OMC = json.loads((B / "resumo.json").read_text())["openmeteo_capitais"]["linhas"]
chuva = lambda cap, dia: next(l["chuva"] for l in OMC if l["cap"] == cap and l["dia"] == dia)
tmin = lambda cap, dia: next(l["tmin"] for l in OMC if l["cap"] == cap and l["dia"] == dia)
assert round(chuva("São Paulo", "2026-10-16")) == 32 and round(chuva("Rio de Janeiro", "2026-10-16")) == 13
assert round(tmin("Curitiba", "2026-10-18")) == 9

# colunas 3D: chuva PREVISTA hoje nas capitais do Centro-Sul (altura = mm)
CAPS = [("São Paulo", -46.63, -23.55), ("Rio de Janeiro", -43.20, -22.91), ("Florianópolis", -48.55, -27.60), ("Brasília", -47.88, -15.79),
        ("Belo Horizonte", -43.94, -19.92), ("Campo Grande", -54.65, -20.47), ("Curitiba", -49.27, -25.43), ("Porto Alegre", -51.23, -30.03),
        ("Vitória", -40.31, -20.32), ("Goiânia", -49.25, -16.68), ("Cuiabá", -56.10, -15.60)]
cor_mm = lambda mm: [150, 215, 255] if mm < 10 else [60, 150, 255] if mm < 25 else [120, 90, 255]
col = [{"id": i, "p": [lon, lat], "v": chuva(c, "2026-10-16"), "cor": cor_mm(chuva(c, "2026-10-16"))} for i, (c, lon, lat) in enumerate(CAPS)]
ordem = {c["id"]: i * .15 for i, c in enumerate(col)}
colunas = [{"id": "chuvahoje", "ini": CAPITAL - .2, "fim": ini("f5") + .5, "dados": col, "raio": 32000, "escala": 11000, "ordem": ordem, "varredura": 1}]

# gráfico: chuva prevista no Sul em 7 dias (soma das capitais do Sul)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-16" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sex", "sáb", "dom", "seg", "ter", "qua", "qui"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
assert SULV[3] == 0 and SULV[4] == 0 and SULV[-1] > 10   # o Sul seca no começo da semana e a chuva volta na quinta
series = [{"nome": "Sul", "cor": "#5ec8ff", "v": SULV}]

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, ventania e geada
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/ventania.png", "ini": VENT - .1, "fim": em("f5", "115") - .3, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/geada.png", "ini": em("f8", "geada") - .1, "fim": ini("f9") + .4, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
HOJE = ufs_av(56091)     # tempestade laranja 16/10: 563 (MG 364, RJ 92, SP 55, ES 52)
assert len(geo(56091)) == 563 and por_uf(56091, "MG") == 364
assert aviso[56091]["severidade"] == "Perigo" and aviso[56091]["descricao"] == "Tempestade" and aviso[56091]["inicio"].startswith("2026-10-16")
VENTO = ufs_av(56095)    # ventos costeiros laranja 17/10: 115 (SC 71, RS 43)
assert len(geo(56095)) == 115 and aviso[56095]["descricao"] == "Ventos Costeiros" and aviso[56095]["inicio"].startswith("2026-10-17")
SAB = ufs_av(56096)      # tempestade laranja 17/10: 370 (MG 245, ES 78, RJ 26, BA 21)
assert len(geo(56096)) == 370 and aviso[56096]["severidade"] == "Perigo" and aviso[56096]["inicio"].startswith("2026-10-17")
estados = [
    {"id": "sul0", "ini": CAPA, "fim": ini("f3") + .3, "ufs": ["RS", "SC"], "cor": AZUL, "alfa": .25},
    {"id": "hoje", "ini": ini("f3"), "fim": MINAS + .3, "ufs": HOJE, "cor": LAR, "alfa": .45},
    {"id": "mg", "ini": MINAS - .2, "fim": BRASIL + .3, "ufs": ["MG"], "cor": LAR, "alfa": .6},
    {"id": "hojebr", "ini": BRASIL - .2, "fim": CAPITAL + .3, "ufs": HOJE, "cor": LAR, "alfa": .55},
    {"id": "vento", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": VENTO, "cor": LAR, "alfa": .45},
    {"id": "sab", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": SAB, "cor": LAR, "alfa": .5},
    {"id": "solsul", "ini": em("f7", "sol") - .2, "fim": em("f7", "pancadas") + .3, "ufs": ["PR", "SC", "RS"], "cor": AMA, "alfa": .35},
    {"id": "dom", "ini": em("f7", "pancadas") - .2, "fim": ini("f8") + .3, "ufs": ["SP", "MS", "GO", "BA"], "cor": LAR, "alfa": .35},
    {"id": "frio", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["SC", "RS", "PR"], "cor": FRIO, "alfa": .4},
    {"id": "pr", "ini": ini("f9"), "fim": ini("f11") + .3, "ufs": ["PR"], "cor": LAR, "alfa": .4},
]

pinos = [
    {"nome": "Litoral gaúcho", "sub": "rajadas até 70 km/h · sábado", "lon": -50.4, "lat": -30.4, "ini": em("f1", "litoral"), "fim": ini("f2"), "h": 200},
    {"nome": "Minas Gerais", "sub": "364 cidades em alerta laranja", "lon": -44.6, "lat": -18.6, "ini": MINAS, "fim": BRASIL, "h": 220},
    {"nome": "São Paulo (capital)", "sub": "32 mm previstos hoje", "lon": -46.63, "lat": -23.55, "ini": CAPITAL, "fim": ini("f5"), "h": 330},
    {"nome": "Lagoa dos Patos", "sub": "ventania no sábado · até 70 km/h", "lon": -51.2, "lat": -31.0, "ini": em("f5", "115") - .3, "fim": ini("f6"), "h": 200},
    {"nome": "Espírito Santo", "sub": "pancadas no sábado", "lon": -40.5, "lat": -19.6, "ini": em("f6", "Espírito"), "fim": ini("f7"), "h": 190},
    {"nome": "Campos de Palmas", "sub": "geada fraca · segunda", "lon": -51.99, "lat": -26.48, "ini": em("f8", "frio"), "fim": em("f8", "geada"), "h": 180},
    {"nome": "Sudoeste do Paraná", "sub": "temporais · qua e qui", "lon": -53.05, "lat": -26.08, "ini": em("f9", "sudoeste"), "fim": ini("f10"), "h": 200},
    {"nome": "Oeste do Paraná", "sub": "mais de 400 mm em 15 dias", "lon": -52.9, "lat": -25.0, "ini": em("f10", "Paraná"), "fim": ini("f11"), "h": 200},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
conta = lambda ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0: {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra) - lead, "dur": lead, "cor": cor, "unid": unid}
hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o número da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:92px">70 KM/H</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">rajadas previstas no litoral gaúcho com o ciclone</div>'}]
D_BR = max(BRASIL - LEAD, ini("f4"))   # o total do Brasil sobe de 364 a 563 até a palavra
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "POR QUE · PREVISÃO",
     "itens": [{"t": em("f2", "ciclone"), "txt": "🌀 ciclone extratropical no Atlântico"},
               {"t": em("f2", "frente"), "txt": "🌧️ puxa uma frente fria"},
               {"t": em("f2", "firma"), "txt": "🌤️ depois, tempo firme e frio no Sul"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "ALERTA LARANJA · MINAS GERAIS",
     "contador": conta(364, "f3", "364", "#ff8c1a", "CIDADES EM MG", lead=min(LEAD, em("f3", "364") - ini("f3") - .05)),
     "l": "tempestade hoje · INMET, 16/10", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f4"), "fim": CAPITAL - .05, "k": "BRASIL INTEIRO · HOJE",
     "contador": {"de": 364, "ate": 563, "dec": 0, "ini": D_BR, "dur": max(.4, em("f4", "563") - D_BR), "cor": "#ff8c1a", "unid": "CIDADES NO BRASIL"},
     "l": "MG 364 · RJ 92 · SP 55 · ES 52 · alerta laranja", "borda": "rgba(255,140,26,.7)"},
    {"ini": CAPITAL - .05, "fim": ini("f5"), "k": "CHUVA PREVISTA HOJE · CAPITAIS",
     "contador": conta(32, "f4", "32", "#5ec8ff", "MM", lead=min(LEAD, em("f4", "32") - CAPITAL)),
     "l": "São Paulo · Rio 13 · Florianópolis 11 · coluna = mm previstos", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "SÁBADO, 17/10 · VENTOS COSTEIROS",
     "contador": conta(115, "f5", "115", "#ff8c1a", "CIDADES EM ALERTA"),
     "l": "SC 71 · RS 43 · rajadas até 70 km/h (previsão) · INMET", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SÁBADO, 17/10 · TEMPESTADE",
     "contador": conta(370, "f6", "370", "#ff8c1a", "CIDADES EM ALERTA"),
     "l": "MG 245 · ES 78 · RJ 26 · BA 21 · alerta laranja (INMET)", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "DOMINGO, 18/10 (PREVISÃO)",
     "itens": [{"t": em("f7", "sol"), "txt": "☀️ sol no Sul"},
               {"t": em("f7", "pancadas"), "txt": "⛈️ pancadas em SP, MS, GO e BA"}],
     "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "FRIO · SÁB A TER (PREVISÃO)",
     "contador": conta(8, "f8", "8", "#96d2ff", "°C AO AMANHECER", de=20),
     "l": "8 a 10 °C nas madrugadas · geada fraca na segunda", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "SUL · CHUVA PREVISTA EM 7 DIAS (MM SOMADOS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f9") + .3, "dur": 1.6},
     "l": "soma nas capitais do Sul · seca até terça, chuva volta no meio da semana", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "PARANÁ · 1 A 15 DE OUTUBRO",
     "contador": conta(400, "f10", "400", "#5ec8ff", "MM DE CHUVA", de=100),
     "l": "partes do estado já passaram de 400 mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "onde"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f11", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
     "borda": "rgba(250,204,21,.8)"},
]
for a, b in zip(paineis, paineis[1:]):
    assert a["fim"] <= b["ini"] + 1e-6, (a["k"], b["k"])
for a in paineis:
    if a.get("contador"):
        c = a["contador"]
        assert a["ini"] - .01 <= c["ini"] and c["ini"] + c["dur"] <= a["fim"] + .01, ("contador fora do painel", a["k"], c, a["ini"], a["fim"])

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f3"), "html": f"<b>{MET}</b> · satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f3"), "fim": CAPITAL, "html": "<b>INMET</b>, aviso laranja de tempestade para 16/10: MG 364, Brasil 563 municípios"},
    {"ini": CAPITAL, "fim": ini("f5"), "html": f"{OM} para 16/10 · altura da coluna = milímetros previstos"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · <b>INMET</b>, ventos costeiros para 17/10 (115 municípios) · foto: ilustração"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso laranja de tempestade para 17/10 (370 municípios)"},
    {"ini": ini("f7"), "fim": ini("f9"), "html": f"<b>{MET}</b> · foto da geada: ilustração"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · {OM}, 16 a 22/10"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chover": "#5ec8ff", "milimetros": "#5ec8ff", "temporais": "#ff8c1a", "temporal": "#ff8c1a", "tempestade": "#ff8c1a",
         "alerta": "#ff8c1a", "laranja": "#ff8c1a", "ciclone": "#ff8c1a", "ventania": "#ff8c1a", "rajadas": "#ff8c1a", "pancadas": "#ff8c1a",
         "ventos": "#ff8c1a", "costeiros": "#ff8c1a", "frio": "#96d2ff", "geada": "#96d2ff", "graus": "#96d2ff", "sol": AM, "comenta": AM,
         "inteligencia": AM, "artificial": AM}
LUGAR = {"sudeste", "minas", "sao", "paulo", "rio", "brasil", "sul", "parana", "santa", "catarina", "gaucho", "litoral", "lagoa", "patos",
         "espirito", "santo", "mato", "grosso", "goias", "bahia", "serra", "campos", "palmas", "sudoeste", "centrooeste", "inemaclub", "onde"}
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
     "camera": camera, "sat": SAT, "colunas": colunas, "telas": telas, "estados": estados, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"tempestade hoje {HOJE} · vento sáb {VENTO} · tempestade sáb {SAB} · 7 dias {ROTD}")
