#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 23/10/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png), infravermelho do GOES-19 sobre a Argentina, o Paraguai e o oeste do Sul
(baixa pressão), foto do granizo (ilustração), alerta laranja do INMET hoje e no sábado, gráfico da chuva prevista no Sul e no Sudeste
em 7 dias, colunas 3D da chuva prevista até o fim de semana no oeste de SC, foto da enchente (ilustração).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "23/10/2026"
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
OSC = {"lon": -52.4, "lat": -27.0, "zoom": 5.4}      # f1: oeste de Santa Catarina
SIST = {"lon": -57.0, "lat": -26.5, "zoom": 4.6}     # f2: Argentina, Paraguai e oeste do Sul (baixa pressão no IR)
OESTE = {"lon": -53.0, "lat": -26.9, "zoom": 5.6}    # f3: oeste de SC, sudoeste do PR e noroeste do RS
SUL = {"lon": -51.8, "lat": -27.0, "zoom": 4.9}      # f4: laranja hoje, quase todo no Sul
SE = {"lon": -44.5, "lat": -20.6, "zoom": 4.8}       # f5: RJ, ES, MG e leste de SP
SULG = {"lon": -52.0, "lat": -27.5, "zoom": 4.6}     # f6: a baixa passa sobre o Sul (gráfico)
SULSP = {"lon": -50.8, "lat": -26.0, "zoom": 4.7}    # f7: laranja no sábado (PR, SC, SP, RS)
COL = {"lon": -52.6, "lat": -26.9, "zoom": 6.0}      # f8: colunas 3D no oeste de SC
VALE = {"lon": -49.6, "lat": -27.0, "zoom": 5.8}     # f9: Vale do Itajaí
SULF = {"lon": -51.5, "lat": -28.0, "zoom": 5.0}     # f10: domingo melhora no oeste; frio e geada na serra
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
GRAN = em("f3", "granizo")
ENCH = em("f9", "enchentes")
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, OSC, 0, 0), K(fim("f1") - .2, {**OSC, "zoom": 5.5}, 0, 0),
    K(ini("f2") + 1.0, SIST, 0, 0), K(fim("f2") - .2, {**SIST, "zoom": 4.7}, 0, 0),
    K(ini("f3") + 1.0, OESTE, 30, -8), K(fim("f3") - .2, {**OESTE, "zoom": 5.7}, 34, 6),
    K(ini("f4") + 1.0, SUL, 0, 0), K(fim("f4") - .2, {**SUL, "zoom": 5.0}, 0, 0),
    K(ini("f5") + 1.0, SE, 15, -4), K(fim("f5") - .2, {**SE, "zoom": 4.9}, 18, 4),
    K(ini("f6") + 1.0, SULG, 0, 0), K(fim("f6") - .2, {**SULG, "zoom": 4.7}, 0, 0),
    K(ini("f7") + 1.0, SULSP, 0, 0), K(fim("f7") - .2, {**SULSP, "zoom": 4.8}, 0, 0),
    K(ini("f8") + 1.0, COL, 54, -20), K(fim("f8") - .2, {**COL, "zoom": 6.1}, 58, 16),
    K(ini("f9") + 1.0, VALE, 25, -6), K(fim("f9") - .2, {**VALE, "zoom": 5.9}, 28, 6),
    K(ini("f10") + 1.0, SULF, 0, 0), K(fim("f10") - .2, {**SULF, "zoom": 5.1}, 0, 0),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) sobre o Sul e a Argentina (f1–f2)
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

# colunas 3D: chuva PREVISTA até o fim de semana (mapa válido até dom 25/10), Meteorologia · 23/10:
# faixa comum de 100 a 150 mm; o modelo mais agressivo dá 300 a 350 mm no extremo oeste de SC
REG = [("São Miguel do Oeste", -53.52, -26.73, 350), ("Dionísio Cerqueira", -53.64, -26.26, 350), ("Itapiranga", -53.71, -27.17, 350),
       ("Maravilha", -53.17, -26.77, 300), ("Chapecó", -52.62, -27.10, 300), ("Xanxerê", -52.40, -26.88, 150),
       ("Concórdia", -52.03, -27.23, 150), ("Francisco Beltrão", -53.06, -26.08, 150), ("Pato Branco", -52.67, -26.23, 150),
       ("Frederico Westphalen", -53.39, -27.36, 150), ("Erechim", -52.27, -27.63, 100), ("Joaçaba", -51.50, -27.18, 100)]
cor_mm = lambda mm: [120, 90, 255] if mm < 300 else [255, 42, 31]
col = [{"id": i, "p": [lon, lat], "v": v, "cor": cor_mm(v)} for i, (_, lon, lat, v) in enumerate(REG)]
ordem = {c["id"]: i * .12 for i, c in enumerate(col)}
colunas = [{"id": "chuvafds", "ini": ini("f8") + .3, "fim": ini("f9") + .5, "dados": col, "raio": 13000, "escala": 900, "ordem": ordem, "varredura": 1}]

# gráfico: chuva prevista no Sul e no Sudeste em 7 dias (soma das capitais, Open-Meteo)
P7 = json.loads((B / "previsao7d.json").read_text())
HOJE = "2026-10-23"
assert P7["dias"][0] == HOJE and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sex", "sáb", "dom", "seg", "ter", "qua", "qui"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
SEV = [d["por_regiao_mm"]["SE"] for d in P7["por_dia"]]
assert max(SULV) == SULV[1] and SULV[1] > 60 and max(SULV[3:]) < 10, SULV   # nas capitais do Sul, o pico é no sábado
series = [{"nome": "Sul", "cor": "#5ec8ff", "v": SULV}, {"nome": "Sudeste", "cor": "#ff8c1a", "v": SEV}]

rios = []

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, granizo e enchente
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": GRAN - .1, "fim": fim("f3") - .1, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/enchente.png", "ini": ENCH - .1, "fim": em("f9", "Vale") - .1, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
LHOJE = ufs_av(56144)    # tempestade LARANJA (Perigo) hoje, sexta 23/10: 590 (PR 277, RS 184, SC 109, MS 19, SP 1)
assert len(geo(56144)) == 590 and por_uf(56144, "PR") == 277 and por_uf(56144, "RS") == 184 and por_uf(56144, "SC") == 109
assert aviso[56144]["descricao"] == "Tempestade" and aviso[56144]["severidade"] == "Perigo" and aviso[56144]["inicio"].startswith("2026-10-23")
LSAB = ufs_av(56164)     # tempestade LARANJA (Perigo) sábado 24/10: 934 (PR 351, SC 273, SP 187, RS 123)
assert len(geo(56164)) == 934 and por_uf(56164, "PR") == 351 and por_uf(56164, "SC") == 273 and por_uf(56164, "SP") == 187 and por_uf(56164, "RS") == 123
assert aviso[56164]["descricao"] == "Tempestade" and aviso[56164]["severidade"] == "Perigo" and aviso[56164]["inicio"].startswith("2026-10-24")
estados = [
    {"id": "sc0", "ini": CAPA, "fim": ini("f2") + .3, "ufs": ["SC"], "cor": AZUL, "alfa": .3},
    {"id": "sul", "ini": em("f2", "baixa"), "fim": ini("f3") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .3},
    {"id": "oeste", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["PR", "SC", "RS"], "cor": LAR, "alfa": .35},
    {"id": "lhoje", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": LHOJE, "cor": LAR, "alfa": .45},
    {"id": "se", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["RJ", "ES", "MG", "SP"], "cor": AZUL, "alfa": .35},
    {"id": "sul2", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .35},
    {"id": "lsab", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": LSAB, "cor": VERM, "alfa": .4},
    {"id": "sc", "ini": ini("f8"), "fim": fim("f9"), "ufs": ["SC"], "cor": VERM, "alfa": .3},
    {"id": "sul3", "ini": ini("f10"), "fim": ini("f11") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .3},
]

pinos = [
    {"nome": "Oeste de Santa Catarina", "sub": "até 350 mm até o fim de semana · previsão", "lon": -52.9, "lat": -26.9, "ini": em("f1", "Catarina"), "fim": ini("f2"), "h": 200},
    {"nome": "Argentina e Paraguai", "sub": "baixa pressão", "lon": -59.0, "lat": -27.0, "ini": em("f2", "Argentina"), "fim": ini("f3"), "h": 60},
    {"nome": "Amazônia", "sub": "umidade que alimenta a chuva", "lon": -58.0, "lat": -12.0, "ini": em("f2", "Amazônia"), "fim": ini("f3"), "h": 160},
    {"nome": "Oeste catarinense", "sub": "tempestades hoje", "lon": -52.9, "lat": -27.0, "ini": em("f3", "oeste"), "fim": GRAN - .1, "h": 60},
    {"nome": "Sudoeste do Paraná", "sub": "tempestades hoje", "lon": -53.0, "lat": -25.9, "ini": em("f3", "sudoeste"), "fim": GRAN - .1, "h": 180},
    {"nome": "Rio de Janeiro", "sub": "chuva hoje", "lon": -43.2, "lat": -22.9, "ini": em("f5", "Rio"), "fim": ini("f6"), "h": 30},
    {"nome": "Espírito Santo", "sub": "chuva hoje", "lon": -40.6, "lat": -19.8, "ini": em("f5", "Espírito"), "fim": ini("f6"), "h": 110},
    {"nome": "Minas Gerais", "sub": "chuva hoje", "lon": -45.5, "lat": -18.0, "ini": em("f5", "Minas"), "fim": ini("f6"), "h": 240},
    {"nome": "Leste de São Paulo", "sub": "chuva hoje", "lon": -46.6, "lat": -23.5, "ini": em("f5", "leste"), "fim": ini("f6"), "h": 170},
    {"nome": "Vale do Itajaí", "sub": "em atenção", "lon": -49.1, "lat": -26.9, "ini": em("f9", "Vale"), "fim": ini("f10"), "h": 160},
    {"nome": "Oeste do Sul", "sub": "o tempo melhora no domingo", "lon": -53.6, "lat": -27.8, "ini": em("f10", "oeste"), "fim": ini("f11"), "h": 60},
    {"nome": "Alto da serra", "sub": "geada isolada seg e ter", "lon": -50.0, "lat": -28.3, "ini": em("f10", "geada"), "fim": ini("f11"), "h": 200},
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
                 '<div class="t1" style="font-size:92px;color:#5ec8ff">ATÉ 350 MM</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">de chuva no oeste de SC até o fim de semana</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "POR QUE (PREVISÃO)",
     "itens": [{"t": em("f2", "baixa"), "txt": "🌀 Baixa pressão"}, {"t": em("f2", "Amazônia"), "txt": "💨 Umidade da Amazônia"}],
     "l": "sobre a Argentina e o Paraguai, rumo ao Sul", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": GRAN - .1, "k": "HOJE, 23/10 (PREVISÃO)",
     "itens": [{"t": em("f3", "tempestades"), "txt": "⛈️ Tempestades"}, {"t": em("f3", "raios"), "txt": "⚡ Raios"}],
     "l": "oeste de SC, sudoeste do PR e noroeste do RS", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE, 23/10 · ALERTA LARANJA",
     "contador": conta(590, "f4", "590", "#ff8c1a", "CIDADES EM ALERTA"),
     "l": "PR 277 · RS 184 · SC 109 · MS 19 · tempestade (INMET)", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "HOJE · SUDESTE (PREVISÃO)",
     "itens": [{"t": em("f5", "Rio"), "txt": "🌧️ RJ e ES: chuva"}, {"t": em("f5", "Minas"), "txt": "🌧️ MG e leste de SP: chuva"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SÁBADO, 24/10 · CHUVA PREVISTA EM 7 DIAS",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f6") + .3, "dur": 1.6},
     "l": "a baixa pressão passa devagar sobre o Sul · mm somados nas capitais", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SÁBADO, 24/10 · ALERTA LARANJA",
     "contador": conta(934, "f7", "934", "#ff2a1f", "CIDADES EM ALERTA"),
     "l": "PR 351 · SC 273 · SP 187 · RS 123 · tempestade (INMET)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "ATÉ O FIM DE SEMANA · CHUVA PREVISTA",
     "contador": conta(350, "f8", "350", "#ff2a1f", "MM NO EXTREMO OESTE DE SC", de=100),
     "l": "100 a 150 mm na maioria · até 350 mm num modelo · coluna = mm previstos", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f9"), "fim": ENCH - .1, "k": "RISCOS NO FIM DE SEMANA (PREVISÃO)",
     "itens": [{"t": em("f9", "alagamentos"), "txt": "🌊 Alagamentos e enxurradas"}, {"t": em("f9", "deslizamentos"), "txt": "⛰️ Deslizamentos de terra"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "PRÓXIMOS DIAS (TENDÊNCIA)",
     "itens": [{"t": em("f10", "melhorar"), "txt": "🌤️ Domingo: melhora no oeste do Sul"},
               {"t": em("f10", "geada"), "txt": "❄️ Seg e ter: frio e geada isolada na serra"}],
     "borda": "rgba(150,210,255,.7)"},
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
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b> · foto do granizo: ilustração"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>INMET</b>, aviso laranja de tempestade para 23/10 (590 municípios)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · {OM}, 23 a 29/10"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>INMET</b>, aviso laranja de tempestade para 24/10 (934 municípios)"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · chuva prevista até 25/10 · altura da coluna = milímetros"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · foto da enchente: ilustração"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chover": "#5ec8ff", "milimetros": "#5ec8ff", "umidade": "#5ec8ff", "enchentes": "#ff2a1f", "laranja": "#ff2a1f",
         "tempestade": "#ff8c1a", "tempestades": "#ff8c1a", "alerta": "#ff8c1a", "raios": "#ff8c1a", "granizo": "#ff8c1a",
         "alagamentos": "#ff2a1f", "enxurradas": "#ff2a1f", "deslizamentos": "#ff2a1f", "forte": "#ff8c1a", "atencao": "#ff8c1a",
         "frio": "#96d2ff", "geada": "#96d2ff",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"parana", "sul", "sudeste", "paraguai", "argentina", "amazonia", "brasil", "oeste", "sudoeste", "noroeste", "catarinense", "gaucho",
         "santa", "catarina", "sao", "paulo", "minas", "rio", "janeiro", "espirito", "grande", "vale", "itajai", "serra", "inemaclub", "onde"}
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
      f"laranja hoje {LHOJE} · laranja sáb {LSAB} · 7 dias {ROTD} · Sul {SULV} · Sudeste {SEV}")
