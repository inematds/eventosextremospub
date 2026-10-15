#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 15/10/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png), infravermelho do GOES-19 sobre o Sudeste e o Centro-Oeste,
foto do temporal com granizo (ilustração), alerta laranja de MG, SP e o total do Brasil, colunas 3D da chuva prevista
hoje nas capitais, foto da geada (ilustração) e gráfico da chuva prevista no Sul em 7 dias.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "15/10/2026"
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
BRA = {"lon": -50.0, "lat": -17.5, "zoom": 3.95}     # f1/f3: o Brasil do alerta
SECO = {"lon": -48.5, "lat": -18.5, "zoom": 4.75}    # f2: Sudeste e Centro-Oeste (IR)
MG = {"lon": -44.6, "lat": -18.6, "zoom": 5.3}       # f3: Minas Gerais
SPE = {"lon": -48.6, "lat": -22.3, "zoom": 5.3}      # f3: estado de São Paulo
COL = {"lon": -51.0, "lat": -21.5, "zoom": 4.75}     # f4: colunas 3D nas capitais
SUL = {"lon": -51.5, "lat": -27.3, "zoom": 5.3}      # f5/f10: Sul
NE = {"lon": -41.5, "lat": -8.0, "zoom": 4.6}        # f6: Nordeste seco
SEX = {"lon": -44.5, "lat": -20.8, "zoom": 5.0}      # f7: de SP ao ES
ES = {"lon": -40.7, "lat": -19.7, "zoom": 6.3}       # f8: Espírito Santo
SERRA = {"lon": -50.0, "lat": -28.1, "zoom": 6.2}    # f9: Serra Catarinense
CWB = {"lon": -49.6, "lat": -25.6, "zoom": 6.0}      # f10: Curitiba
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
ALERTA = em("f1", "alerta")
MINAS, SAO, BRASIL = em("f3", "Minas"), em("f3", "São"), em("f3", "Brasil")
ESP = em("f8", "Espírito")
CUR = em("f10", "Curitiba")
camera = [
    K(0, BR), K(CAPA, BR), K(ALERTA + 1.0, BRA, 0, 0), K(fim("f1") - .2, {**BRA, "zoom": 4.0}, 0, 0),
    K(ini("f2") + 1.0, SECO, 0, 0), K(fim("f2") - .2, {**SECO, "lon": -48.0}, 0, 0),
    K(MINAS + .8, MG, 10, 0), K(SAO - .2, {**MG, "zoom": 5.35}, 10, 0), K(SAO + .9, SPE, 10, 0),
    K(BRASIL - .2, {**SPE, "zoom": 5.2}, 10, 0), K(BRASIL + 1.0, BRA, 0, 0), K(fim("f3") - .2, {**BRA, "zoom": 3.95}, 0, 0),
    K(ini("f4") + 1.2, COL, 52, -20), K(fim("f4") - .2, {**COL, "zoom": 4.8}, 56, 16),
    K(ini("f5") + 1.0, SUL, 0, 0), K(fim("f5") - .2, {**SUL, "lon": -51.0}, 0, 0),
    K(ini("f6") + 1.0, NE, 6, -2), K(fim("f6") - .2, {**NE, "lon": -41.8}, 8, 2),
    K(ini("f7") + 1.0, SEX, 10, 0), K(fim("f7") - .2, {**SEX, "lon": -44.0}, 12, 2),
    K(ini("f8") + .9, {**SEX, "lon": -48.0, "lat": -21.5}, 0, 0), K(ESP - .2, {**SEX, "lon": -47.4, "lat": -21.3}, 0, 0),
    K(ESP + 1.1, ES, 25, -6), K(fim("f8") - .2, {**ES, "zoom": 6.4}, 28, 4),
    K(ini("f9") + 1.0, SERRA, 30, -8), K(fim("f9") - .2, {**SERRA, "zoom": 6.3}, 34, 4),
    K(ini("f10") + 1.0, SUL, 10, 0), K(CUR - .2, {**SUL, "lon": -50.8}, 10, 0), K(CUR + 1.0, CWB, 20, 0), K(fim("f10") - .2, {**CWB, "zoom": 6.1}, 22, 4),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) sobre o Sudeste e o Centro-Oeste (f2)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


GRANIZO = em("f2", "granizo")
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": ini("f2") - .3, "fim": GRANIZO + .3, "dur": GRANIZO - ini("f2") + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

# ---------------------------------------------------------------- previsão Open-Meteo nas capitais (pesquisa/bruto/resumo.json)
OMC = json.loads((B / "resumo.json").read_text())["openmeteo_capitais"]["linhas"]
chuva = lambda cap, dia: next(l["chuva"] for l in OMC if l["cap"] == cap and l["dia"] == dia)
assert round(chuva("Campo Grande", "2026-10-15")) == 38 and round(chuva("Brasília", "2026-10-15")) == 22
assert round(chuva("Curitiba", "2026-10-15")) == 22 and round(chuva("Curitiba", "2026-10-21")) == 41

# colunas 3D: chuva PREVISTA hoje nas capitais do Centro-Sul (altura = mm)
CAPS = [("Campo Grande", -54.65, -20.47), ("Brasília", -47.88, -15.79), ("Curitiba", -49.27, -25.43), ("Vitória", -40.31, -20.32),
        ("Cuiabá", -56.10, -15.60), ("Goiânia", -49.25, -16.68), ("Florianópolis", -48.55, -27.60), ("São Paulo", -46.63, -23.55),
        ("Porto Alegre", -51.23, -30.03), ("Rio de Janeiro", -43.20, -22.91), ("Belo Horizonte", -43.94, -19.92)]
cor_mm = lambda mm: [150, 215, 255] if mm < 10 else [60, 150, 255] if mm < 25 else [120, 90, 255]
col = [{"id": i, "p": [lon, lat], "v": chuva(c, "2026-10-15"), "cor": cor_mm(chuva(c, "2026-10-15"))} for i, (c, lon, lat) in enumerate(CAPS)]
ordem = {c["id"]: i * .15 for i, c in enumerate(col)}
colunas = [{"id": "chuvahoje", "ini": ini("f4") - .2, "fim": ini("f5") + .5, "dados": col, "raio": 32000, "escala": 11000, "ordem": ordem, "varredura": 1}]

# gráfico: chuva prevista no Sul em 7 dias (soma das capitais do Sul)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-15" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qui", "sex", "sáb", "dom", "seg", "ter", "qua"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
assert max(SULV) == SULV[-1] and min(SULV) < 2   # o Sul seca no começo da semana e a chuva volta na quarta
series = [{"nome": "Sul", "cor": "#5ec8ff", "v": SULV}]

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, temporal e geada
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/temporal.png", "ini": GRANIZO - .1, "fim": ini("f3") + .4, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/geada.png", "ini": em("f9", "geada") - .1, "fim": ini("f10") + .4, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
HOJE = sorted(set(ufs_av(56071)) | ({"DF"} if por_uf(56071, "DF") else set()))     # tempestade laranja 15/10: 2.163 (MG 815, SP 645, GO 246, PR 104, MT 103, RJ 92, ES 78, MS 41)
assert len(geo(56071)) == 2163 and por_uf(56071, "MG") == 815 and por_uf(56071, "SP") == 645
assert aviso[56071]["severidade"] == "Perigo" and aviso[56071]["descricao"] == "Tempestade" and aviso[56071]["inicio"].startswith("2026-10-15")
AMANHA = ufs_av(56082)   # tempestade laranja 16/10: 1.161 (MG 619, SP 312, RJ 92, GO 86, ES 51)
assert len(geo(56082)) == 1161 and aviso[56082]["severidade"] == "Perigo" and aviso[56082]["inicio"].startswith("2026-10-16")
assert len(geo(56079)) == 816 and aviso[56079]["descricao"] == "Baixa Umidade"   # ar seco no Nordeste hoje (amarelo)
NORDESTE = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
estados = [
    {"id": "hoje1", "ini": ALERTA - .2, "fim": ini("f2") + .3, "ufs": HOJE, "cor": LAR, "alfa": .5},
    {"id": "seco", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["MG", "SP", "GO", "DF", "MT", "MS", "RJ", "ES"], "cor": LAR, "alfa": .3},
    {"id": "mg", "ini": MINAS - .2, "fim": SAO + .3, "ufs": ["MG"], "cor": LAR, "alfa": .6},
    {"id": "sp", "ini": SAO - .2, "fim": BRASIL + .3, "ufs": ["SP"], "cor": LAR, "alfa": .6},
    {"id": "hoje", "ini": BRASIL - .2, "fim": ini("f4") + .3, "ufs": HOJE, "cor": LAR, "alfa": .55},
    {"id": "sul", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .35},
    {"id": "ne", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": NORDESTE, "cor": [255, 90, 20], "alfa": .35},
    {"id": "amanha", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": AMANHA, "cor": LAR, "alfa": .5},
    {"id": "firma", "ini": em("f8", "firmar") - .2, "fim": ESP + .3, "ufs": ["SP", "MS"], "cor": AMA, "alfa": .3},
    {"id": "es", "ini": ESP - .2, "fim": ini("f9") + .3, "ufs": ["ES"], "cor": LAR, "alfa": .55},
    {"id": "frio", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["SC", "RS", "PR"], "cor": FRIO, "alfa": .4},
    {"id": "temporal", "ini": ini("f10"), "fim": ini("f11") + .3, "ufs": ["PR", "SC", "RS"], "cor": LAR, "alfa": .35},
]

pinos = [
    {"nome": "Campo Grande (MS)", "sub": "38 mm previstos hoje", "lon": -54.65, "lat": -20.47, "ini": em("f4", "Campo"), "fim": ini("f5"), "h": 330},
    {"nome": "Brasília", "sub": "22 mm previstos", "lon": -47.88, "lat": -15.79, "ini": em("f4", "Brasília"), "fim": ini("f5"), "h": 260},
    {"nome": "Curitiba", "sub": "22 mm previstos", "lon": -49.27, "lat": -25.43, "ini": em("f4", "Curitiba"), "fim": ini("f5"), "h": 220},
    {"nome": "Norte gaúcho", "sub": "chuva à tarde", "lon": -52.4, "lat": -28.3, "ini": em("f5", "gaúcho") - .2, "fim": ini("f6"), "h": 150},
    {"nome": "Espírito Santo", "sub": "pancadas fortes no sábado", "lon": -40.5, "lat": -19.6, "ini": ESP, "fim": ini("f9"), "h": 190},
    {"nome": "Serra Catarinense", "sub": "geada isolada · dom, seg e ter", "lon": -49.93, "lat": -28.29, "ini": em("f9", "frio"), "fim": em("f9", "geada"), "h": 180},
    {"nome": "Curitiba", "sub": "41 mm previstos na quarta", "lon": -49.27, "lat": -25.43, "ini": CUR, "fim": ini("f11"), "h": 200},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
conta = lambda ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0: {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra) - lead, "dur": lead, "cor": cor, "unid": unid}
hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o número da capa ficam toda a f1 (o contador do total vem na f3)
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:92px">2.163 CIDADES</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">em alerta laranja de tempestade hoje (INMET)</div>'}]
D_BR = max(BRASIL + .3, em("f3", "2.163") - LEAD)   # o total do Brasil sobe de 645 a 2.163 até a palavra
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "POR QUE · PREVISÃO",
     "itens": [{"t": em("f2", "baixa"), "txt": "🌀 a baixa pressão perde força"},
               {"t": em("f2", "Sudeste"), "txt": "⛈️ temporais no Sudeste e no Centro-Oeste"},
               {"t": GRANIZO, "txt": "🧊 risco de granizo e ventania"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f3"), "fim": SAO - .05, "k": "ALERTA LARANJA · MINAS GERAIS",
     "contador": conta(815, "f3", "815", "#ff8c1a", "CIDADES EM MG", lead=min(LEAD, em("f3", "815") - ini("f3") - .05)),
     "l": "tempestade hoje · INMET, 15/10", "borda": "rgba(255,140,26,.7)"},
    {"ini": SAO - .05, "fim": BRASIL, "k": "ALERTA LARANJA · SÃO PAULO",
     "contador": conta(645, "f3", "645", "#ff8c1a", "CIDADES EM SP", lead=min(LEAD, em("f3", "645") - SAO)),
     "l": "todas as cidades do estado · INMET, 15/10", "borda": "rgba(255,140,26,.7)"},
    {"ini": BRASIL, "fim": ini("f4"), "k": "BRASIL INTEIRO · HOJE",
     "contador": {"de": 645, "ate": 2163, "dec": 0, "ini": D_BR, "dur": max(.4, em("f3", "2.163") - D_BR), "cor": "#ff8c1a", "unid": "CIDADES NO BRASIL"},
     "l": "MG 815 · SP 645 · GO 246 · PR 104 · MT 103 · RJ 92 · ES 78", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "CHUVA PREVISTA HOJE · CAPITAIS",
     "contador": conta(38, "f4", "38", "#5ec8ff", "MM"),
     "l": "Campo Grande (MS) · Brasília 22 · Curitiba 22 · coluna = mm previstos", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "SUL · HOJE (PREVISÃO)",
     "itens": [{"t": em("f5", "sol"), "txt": "🌤️ sol entre nuvens"},
               {"t": em("f5", "Paraná"), "txt": "🌧️ chuva à tarde no PR e em SC"},
               {"t": em("f5", "gaúcho"), "txt": "🌧️ e no norte gaúcho"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "NORDESTE · AR SECO E CALOR",
     "contador": conta(43, "f6", "43", "#ff2a1f", "°C", de=30),
     "l": "pode passar de 43 °C (previsão) · INMET: baixa umidade em 816 cidades", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "AMANHÃ · SEXTA, 16/10",
     "contador": conta(1161, "f7", "1.161", "#ff8c1a", "CIDADES EM ALERTA"),
     "l": "tempestade · MG 619 · SP 312 · RJ 92 · GO 86 · ES 51 (INMET)", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "SÁBADO, 17/10 (PREVISÃO)",
     "itens": [{"t": em("f8", "firmar"), "txt": "🌤️ tempo firma em SP e MS"},
               {"t": ESP, "txt": "⛈️ pancadas fortes no Espírito Santo"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "SUL · DOM, SEG E TER (PREVISÃO)",
     "itens": [{"t": em("f9", "frio"), "txt": "🌡️ frio de manhã"},
               {"t": em("f9", "geada"), "txt": "❄️ geada isolada na Serra Catarinense"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "SUL · CHUVA PREVISTA EM 7 DIAS (MM SOMADOS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f10") + .3, "dur": 1.6},
     "l": "soma nas capitais do Sul · Curitiba: 41 mm na quarta, 21/10", "borda": "rgba(60,150,255,.7)"},
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
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso laranja de tempestade para 15/10 (2.163 municípios)"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE} · <b>{MET}</b> · foto: ilustração"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INMET</b>, aviso laranja de tempestade para 15/10: MG 815, SP 645, Brasil 2.163 municípios"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"{OM} para 15/10 · altura da coluna = milímetros previstos"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · <b>INMET</b>, baixa umidade em 816 municípios"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso laranja de tempestade para 16/10 (1.161 municípios)"},
    {"ini": ini("f8"), "fim": ini("f10"), "html": f"<b>{MET}</b> · foto da geada: ilustração"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": f"<b>{MET}</b> · {OM}, 15 a 21/10"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chover": "#5ec8ff", "milimetros": "#5ec8ff", "temporais": "#ff8c1a", "temporal": "#ff8c1a", "tempestade": "#ff8c1a",
         "alerta": "#ff8c1a", "laranja": "#ff8c1a", "granizo": "#ff8c1a", "ventania": "#ff8c1a", "pancadas": "#ff8c1a", "fortes": "#ff8c1a",
         "seco": "#ff8c1a", "calor": "#ff2a1f", "frio": "#96d2ff", "geada": "#96d2ff", "graus": "#ff2a1f", "comenta": AM,
         "inteligencia": AM, "artificial": AM}
LUGAR = {"sudeste", "centrooeste", "minas", "sao", "paulo", "brasil", "campo", "grande", "brasilia", "curitiba", "sul", "parana", "santa",
         "catarina", "norte", "gaucho", "nordeste", "espirito", "santo", "mato", "grosso", "serra", "catarinense", "inemaclub", "onde"}
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
      f"tempestade hoje {HOJE} · amanhã {AMANHA} · 7 dias {ROTD}")
