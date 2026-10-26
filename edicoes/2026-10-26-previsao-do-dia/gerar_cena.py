#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 26/10/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png), infravermelho do GOES-19 sobre o Sul (baixa pressão e frente fria saindo),
foto da enchente (ilustração), colunas 3D da chuva que JÁ CAIU no PR, SC e noroeste do RS, Sul pintado de seco hoje, aviso amarelo
de tempestade do INMET hoje (1.608) e na quinta (2.777), foto do temporal (ilustração), gráfico da chuva prevista em 7 dias.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "26/10/2026"
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
OPR = {"lon": -51.6, "lat": -26.4, "zoom": 5.0}      # f1: Paraná e Sul (248 mm já caíram)
SIST = {"lon": -51.5, "lat": -27.0, "zoom": 4.6}     # f2: baixa pressão + frente fria (IR)
COL = {"lon": -51.6, "lat": -26.1, "zoom": 5.5}      # f3: colunas 3D: Guarapuava, Curitiba, Guaraciaba
NORS = {"lon": -54.0, "lat": -27.3, "zoom": 6.3}     # f4: noroeste gaúcho (Porto Mauá)
SULS = {"lon": -51.5, "lat": -27.8, "zoom": 5.0}     # f5: hoje, Sul seco; chuva fraca no litoral, serra e oeste de SC
AVH = {"lon": -47.5, "lat": -17.5, "zoom": 4.8}     # f6: Rio e Minas + aviso amarelo de hoje (MG, BA, GO, TO, ES)
TQ = {"lon": -47.5, "lat": -17.0, "zoom": 4.8}       # f7: ter e qua: litoral de SP, ES, GO, TO, BA
QS = {"lon": -50.0, "lat": -21.5, "zoom": 4.4}      # f8: qui e sex: Sudeste, Centro-Oeste e Sul
AVQ = {"lon": -50.0, "lat": -21.5, "zoom": 4.4}      # f9: aviso amarelo de quinta (2.777)
G7 = {"lon": -50.0, "lat": -22.0, "zoom": 4.45}       # f10: gráfico dos 7 dias
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
ENCH = em("f2", "enchentes")
TEMP = em("f8", "temporais")
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, OPR, 0, 0), K(fim("f1") - .2, {**OPR, "zoom": 5.1}, 0, 0),
    K(ini("f2") + 1.0, SIST, 0, 0), K(fim("f2") - .2, {**SIST, "zoom": 4.7}, 0, 0),
    K(ini("f3") + 1.0, COL, 54, -20), K(fim("f3") - .2, {**COL, "zoom": 5.6}, 58, 16),
    K(ini("f4") + 1.0, NORS, 50, 10), K(fim("f4") - .2, {**NORS, "zoom": 6.4}, 54, 30),
    K(ini("f5") + 1.0, SULS, 0, 0), K(fim("f5") - .2, {**SULS, "zoom": 5.1}, 0, 0),
    K(ini("f6") + 1.0, AVH, 0, 0), K(fim("f6") - .2, {**AVH, "zoom": 4.85}, 0, 0),
    K(ini("f7") + 1.0, TQ, 10, -4), K(fim("f7") - .2, {**TQ, "zoom": 4.85}, 12, 4),
    K(ini("f8") + 1.0, QS, 0, 0), K(fim("f8") - .2, {**QS, "zoom": 4.5}, 0, 0),
    K(ini("f9") + 1.0, AVQ, 0, 0), K(fim("f9") - .2, {**AVQ, "zoom": 4.5}, 0, 0),
    K(ini("f10") + 1.0, G7, 0, 0), K(fim("f10") - .2, {**G7, "zoom": 4.55}, 0, 0),
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

# colunas 3D: chuva que JÁ CAIU nos últimos dias (Meteorologia · 26/10, mapa do CEMADEN) — não é previsão
REG = [("Cantagalo", -52.37, -25.37, 248), ("Guarapuava", -51.46, -25.39, 247), ("Cascavel", -53.46, -24.96, 194),
       ("Curitiba", -49.27, -25.43, 184), ("Morretes", -48.83, -25.48, 178), ("Guaraciaba", -53.52, -26.60, 220),
       ("Iporã do Oeste", -53.54, -26.99, 190), ("Coronel Freitas", -52.77, -26.91, 167), ("Águas de Chapecó", -52.99, -27.07, 165),
       ("Mondaí", -53.40, -27.10, 158), ("Caibi", -53.25, -27.07, 153), ("Chapecó", -52.62, -27.10, 135),
       ("Balneário Camboriú", -48.63, -26.99, 116), ("Porto Mauá", -54.67, -27.58, 225), ("Esperança do Sul", -53.99, -27.36, 211),
       ("Horizontina", -54.31, -27.63, 206)]
cor_mm = lambda mm: [120, 90, 255] if mm < 200 else [255, 42, 31]
col = [{"id": i, "p": [lon, lat], "v": v, "cor": cor_mm(v)} for i, (_, lon, lat, v) in enumerate(REG)]
ordem = {c["id"]: i * .1 for i, c in enumerate(col)}
colunas = [{"id": "jacaiu", "ini": ini("f3") + .3, "fim": ini("f5") + .5, "dados": col, "raio": 13000, "escala": 1200, "ordem": ordem, "varredura": 1}]

# gráfico: chuva prevista no Sul, Sudeste e Centro-Oeste em 7 dias (soma das capitais, Open-Meteo)
P7 = json.loads((B / "previsao7d.json").read_text())
HOJE = "2026-10-26"
assert P7["dias"][0] == HOJE and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
SEV = [d["por_regiao_mm"]["SE"] for d in P7["por_dia"]]
COV = [d["por_regiao_mm"]["CO"] for d in P7["por_dia"]]
assert max(SULV[1:3]) < 5 and SULV[4] > 10 and max(SEV[3:5]) > 40, (SULV, SEV)   # Sul seco ter e qua; chuva volta qui e sex
series = [{"nome": "Sul", "cor": "#5ec8ff", "v": SULV}, {"nome": "Sudeste", "cor": "#ff8c1a", "v": SEV},
          {"nome": "Centro-Oeste", "cor": "#a78bfa", "v": COV}]

rios = []

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, enchente e temporal
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/enchente.png", "ini": ENCH - .1, "fim": fim("f2") - .1, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/temporal.png", "ini": TEMP - .1, "fim": fim("f8") - .1, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
AHOJE = ufs_av(56192)    # tempestade AMARELA (Perigo Potencial) hoje, segunda 26/10: 1.608 (MG 608, BA 263, GO 193, TO 139, ES 78)
assert len(geo(56192)) == 1608 and por_uf(56192, "MG") == 608 and por_uf(56192, "BA") == 263 and por_uf(56192, "GO") == 193
assert aviso[56192]["descricao"] == "Tempestade" and aviso[56192]["severidade"] == "Perigo Potencial" and aviso[56192]["inicio"].startswith("2026-10-26")
AQUI_ = ufs_av(56195)    # tempestade AMARELA (Perigo Potencial) quinta 29/10: 2.777 (SP 645, MG 536, PR 399, SC 295, RS 107)
assert len(geo(56195)) == 2777 and por_uf(56195, "SP") == 645 and por_uf(56195, "MG") == 536 and por_uf(56195, "PR") == 399
assert aviso[56195]["descricao"] == "Tempestade" and aviso[56195]["severidade"] == "Perigo Potencial" and aviso[56195]["inicio"].startswith("2026-10-29")
estados = [
    {"id": "sul0", "ini": CAPA, "fim": ini("f2") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .3},
    {"id": "sul", "ini": em("f2", "baixa"), "fim": ini("f3") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .3},
    {"id": "caiu", "ini": ini("f3"), "fim": ini("f5") + .3, "ufs": ["PR", "SC", "RS"], "cor": LAR, "alfa": .25},
    {"id": "seco", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["RS", "SC", "PR"], "cor": AMA, "alfa": .22},
    {"id": "ahoje", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": AHOJE, "cor": AMA, "alfa": .4},
    {"id": "terqua", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": ["SP", "ES", "GO", "TO", "BA"], "cor": AZUL, "alfa": .3},
    {"id": "quisex", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["SP", "MG", "RJ", "ES", "GO", "MT", "MS", "DF", "PR", "SC", "RS"], "cor": AZUL, "alfa": .3},
    {"id": "aqui", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": AQUI_, "cor": AMA, "alfa": .4},
]

pinos = [
    {"nome": "Cantagalo (PR)", "sub": "248 mm já caíram", "lon": -52.37, "lat": -25.37, "ini": em("f1", "248"), "fim": ini("f2"), "h": 200},
    {"nome": "Sul do Brasil", "sub": "baixa pressão e frente fria", "lon": -52.5, "lat": -27.3, "ini": em("f2", "baixa"), "fim": ENCH - .1, "h": 160},
    {"nome": "Guarapuava", "sub": "247 mm", "lon": -51.46, "lat": -25.39, "ini": em("f3", "Guarapuava"), "fim": ini("f4"), "h": 260},
    {"nome": "Curitiba", "sub": "184 mm", "lon": -49.27, "lat": -25.43, "ini": em("f3", "Curitiba"), "fim": ini("f4"), "h": 200},
    {"nome": "Guaraciaba (SC)", "sub": "220 mm", "lon": -53.52, "lat": -26.60, "ini": em("f3", "Guaraciaba"), "fim": ini("f4"), "h": 240},
    {"nome": "Porto Mauá (RS)", "sub": "225 mm", "lon": -54.67, "lat": -27.58, "ini": em("f4", "Porto"), "fim": ini("f5"), "h": 260},
    {"nome": "Esperança do Sul", "sub": "211 mm", "lon": -53.99, "lat": -27.36, "ini": em("f4", "225") + .3, "fim": ini("f5"), "h": 120},
    {"nome": "Litoral de SC", "sub": "chuva fraca e isolada", "lon": -48.7, "lat": -27.6, "ini": em("f5", "litoral"), "fim": ini("f6"), "h": 60},
    {"nome": "Serra Gaúcha", "sub": "chuva fraca e isolada", "lon": -51.2, "lat": -29.2, "ini": em("f5", "Serra"), "fim": ini("f6"), "h": 60},
    {"nome": "Oeste catarinense", "sub": "chuva fraca e isolada", "lon": -52.9, "lat": -26.9, "ini": em("f5", "oeste"), "fim": ini("f6"), "h": 140},
    {"nome": "Rio de Janeiro", "sub": "chuva mais grossa hoje", "lon": -43.2, "lat": -22.9, "ini": em("f6", "Rio"), "fim": ini("f7"), "h": 60},
    {"nome": "Minas Gerais", "sub": "chuva mais grossa hoje", "lon": -44.5, "lat": -18.5, "ini": em("f6", "Minas"), "fim": ini("f7"), "h": 200},
    {"nome": "Litoral paulista", "sub": "pancadas ter e qua", "lon": -46.3, "lat": -23.9, "ini": em("f7", "litoral"), "fim": ini("f8"), "h": 60},
    {"nome": "Espírito Santo", "sub": "pancadas ter e qua", "lon": -40.6, "lat": -19.6, "ini": em("f7", "Espírito"), "fim": ini("f8"), "h": 120},
    {"nome": "Goiás", "sub": "pancadas ter e qua", "lon": -49.6, "lat": -16.2, "ini": em("f7", "Goiás"), "fim": ini("f8"), "h": 160},
    {"nome": "Tocantins", "sub": "pancadas ter e qua", "lon": -48.3, "lat": -10.2, "ini": em("f7", "Tocantins"), "fim": ini("f8"), "h": 220},
    {"nome": "Bahia", "sub": "pancadas ter e qua", "lon": -41.7, "lat": -12.5, "ini": em("f7", "Bahia"), "fim": ini("f8"), "h": 260},
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
                 '<div class="t1" style="font-size:92px;color:#5ec8ff">ATÉ 248 MM</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">já caíram no Paraná · agora, 2 a 3 dias secos no Sul</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ENCH - .1, "k": "POR QUE CHOVEU TANTO",
     "itens": [{"t": em("f2", "baixa"), "txt": "🌀 Baixa pressão"}, {"t": em("f2", "frente"), "txt": "❄️ Frente fria"}],
     "l": "sobre o Sul do Brasil", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "JÁ CAIU · CHUVA REGISTRADA",
     "contador": conta(247, "f3", "247", "#5ec8ff", "MM EM GUARAPUAVA"),
     "l": "Curitiba 184 mm · Guaraciaba (SC) 220 mm · coluna = mm que caíram", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "JÁ CAIU · NOROESTE GAÚCHO",
     "contador": conta(225, "f4", "225", "#ff2a1f", "MM EM PORTO MAUÁ"),
     "l": "Esperança do Sul 211 mm · Horizontina 206 mm", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "HOJE, 26/10 · SUL (PREVISÃO)",
     "itens": [{"t": em("f5", "firme"), "txt": "☀️ Tempo firme no Sul"}, {"t": em("f5", "fraca"), "txt": "🌦️ Chuva fraca e isolada"}],
     "l": "litoral, Serra Gaúcha e oeste de SC", "borda": "rgba(250,204,21,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "HOJE, 26/10 · AVISO AMARELO",
     "contador": conta(1608, "f6", "1.608", "#FACC15", "CIDADES · TEMPESTADE"),
     "l": "MG 608 · BA 263 · GO 193 · TO 139 · ES 78 (INMET)", "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "TERÇA E QUARTA (PREVISÃO)",
     "itens": [{"t": em("f7", "pancadas"), "txt": "⛈️ Pancadas com trovoadas"}, {"t": em("f7", "litoral"), "txt": "📍 Litoral de SP, ES, GO, TO e BA"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f8"), "fim": TEMP - .1, "k": "QUINTA E SEXTA (PREVISÃO)",
     "itens": [{"t": em("f8", "volta"), "txt": "🌧️ Chuva volta"}, {"t": em("f8", "Sudeste"), "txt": "📍 Sudeste, Centro-Oeste e Sul"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "QUINTA, 29/10 · AVISO AMARELO",
     "contador": conta(2777, "f9", "2.777", "#FACC15", "CIDADES · TEMPESTADE"),
     "l": "SP 645 · MG 536 · PR 399 · SC 295 · solo encharcado (INMET)", "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "PRÓXIMOS 7 DIAS · CHUVA PREVISTA",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f10") + .3, "dur": 1.6},
     "l": "fim de semana: pancadas à tarde · frentes frias: 3 a 4 e 8 de novembro · mm somados nas capitais", "borda": "rgba(250,204,21,.7)"},
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
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>{MET}</b> · {GOES}"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · {GOES} · foto da enchente: ilustração"},
    {"ini": ini("f3"), "fim": ini("f5"), "html": f"<b>{MET}</b> · chuva já registrada (CEMADEN) · altura da coluna = milímetros"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso amarelo de tempestade para 26/10 (1.608 municípios)"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · foto do temporal: ilustração"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>INMET</b>, aviso amarelo de tempestade para 29/10 (2.777 municípios)"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": f"<b>{MET}</b> · {OM}, 26/10 a 01/11"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chuvarada": "#5ec8ff", "milimetros": "#5ec8ff", "pancadas": "#5ec8ff", "seco": AM, "firme": AM,
         "fraca": "#5ec8ff", "grossa": "#5ec8ff", "frente": "#5ec8ff", "fria": "#5ec8ff", "frias": "#5ec8ff", "baixa": "#5ec8ff",
         "enchentes": "#ff2a1f", "enxurradas": "#ff2a1f", "deslizamentos": "#ff2a1f", "encharcado": "#5ec8ff", "transtornos": "#ff2a1f",
         "tempestade": "#ff8c1a", "temporais": "#ff8c1a", "trovoadas": "#ff8c1a", "aviso": "#ff8c1a", "atencao": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"parana", "sul", "sao", "paulo", "guarapuava", "curitiba", "guaraciaba", "catarinense", "noroeste", "gaucho", "porto", "maua",
         "litoral", "serra", "gaucha", "oeste", "rio", "minas", "paulista", "espirito", "santo", "goias", "tocantins", "bahia",
         "sudeste", "centrooeste", "inemaclub", "onde"}
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
      f"amarelo hoje {AHOJE} · amarelo qui {AQUI_} · 7 dias {ROTD} · Sul {SULV} · Sudeste {SEV} · CO {COV}")
