#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 05/11/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "2.595 CIDADES EM ALERTA DE TEMPESTADE NO SÁBADO"),
aviso de tempestade do INMET para sábado (2.595) pintado, foto do granizo (ilustração) na frente fria,
infravermelho do GOES-19 das últimas 24 h (tornados no oeste de SC), pinos em Chapecó/Guatambu/Xanxerê,
Paraná hoje (30 °C), aviso de tempestade de hoje (2.308), sexta no PR/SP, oeste do Sul, Vale do Itajaí,
SC inteira no aviso de sábado (295) → declínio de temperatura no domingo (2.060), gráfico dos 7 dias.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "05/11/2026"
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
SABP = {"lon": -50.0, "lat": -23.0, "zoom": 4.2}     # f1: 2.595 cidades em aviso no sábado (SP, MG, PR, RS, SC, GO)
SUL = {"lon": -51.5, "lat": -27.5, "zoom": 4.8}      # f2: frente fria no Sul
OESTE = {"lon": -52.6, "lat": -27.0, "zoom": 6.6}    # f3: Chapecó, Guatambu, Xanxerê
PR = {"lon": -51.5, "lat": -24.9, "zoom": 5.4}       # f4: Paraná hoje
HOJEP = {"lon": -48.5, "lat": -19.5, "zoom": 4.3}    # f5: aviso de hoje (MG, SP, PR, GO)
SEX = {"lon": -49.5, "lat": -23.6, "zoom": 5.0}      # f6: sexta no PR e SP
OSUL = {"lon": -53.2, "lat": -26.8, "zoom": 5.6}     # f7: sudoeste do PR, oeste de SC, noroeste gaúcho
VALE = {"lon": -49.2, "lat": -26.9, "zoom": 6.6}     # f8: Vale do Itajaí
SC = {"lon": -50.6, "lat": -27.3, "zoom": 5.7}       # f9: SC inteira no aviso de sábado
DOM = {"lon": -50.5, "lat": -25.5, "zoom": 4.5}      # f9: domingo, temperatura cai (SP, RS, PR, SC, MG)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
GRAN = em("f2", "trovoada")  # avatar 05/11 fala rápido: granizo→fim < 1 s
DOMT = em("f9", "domingo")
P9 = min(ini("f9"), em("f9", "295") - 1.0)   # "295" é a 2ª palavra da f9: o painel entra 1 s antes para o contador chegar no número
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, SABP, 0, 0), K(fim("f1") - .2, {**SABP, "zoom": 4.3}, 0, 0),
    K(ini("f2") + 1.0, SUL, 0, 0), K(fim("f2") - .2, {**SUL, "zoom": 4.9}, 0, 0),
    K(ini("f3") + 1.2, OESTE, 35, -10), K(fim("f3") - .2, {**OESTE, "zoom": 6.9}, 45, 10),
    K(ini("f4") + 1.0, PR, 0, 0), K(fim("f4") - .2, {**PR, "zoom": 5.5}, 0, 0),
    K(ini("f5") + 1.0, HOJEP, 0, 0), K(fim("f5") - .2, {**HOJEP, "zoom": 4.4}, 0, 0),
    K(ini("f6") + 1.0, SEX, 0, 0), K(fim("f6") - .2, {**SEX, "zoom": 5.1}, 0, 0),
    K(ini("f7") + 1.0, OSUL, 20, -6), K(fim("f7") - .2, {**OSUL, "zoom": 5.8}, 30, 6),
    K(ini("f8") + 1.2, VALE, 40, -8), K(fim("f8") - .2, {**VALE, "zoom": 6.9}, 50, 12),
    K(ini("f9") + 1.0, SC, 0, 0), K(DOMT - .2, {**SC, "zoom": 5.8}, 0, 0),
    K(DOMT + 1.2, DOM, 0, 0), K(fim("f9") - .2, {**DOM, "zoom": 4.6}, 0, 0),
    K(ini("f10") + 1.0, SUL, 0, 0), K(fim("f10") - .2, {**SUL, "zoom": 4.9}, 0, 0),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) (f1–f3: tornados no oeste de SC)
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

colunas = []   # a previsão de hoje não dá volume de chuva em mm: sem colunas 3D

# ---------------------------------------------------------------- previsão Open-Meteo (7 dias): gráfico
P7 = json.loads((B / "previsao7d.json").read_text())
HOJE_D = "2026-11-05"
assert P7["dias"][0] == HOJE_D and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qui", "sex", "sáb", "dom", "seg", "ter", "qua"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
SEV = [d["por_regiao_mm"]["SE"] for d in P7["por_dia"]]
COV = [d["por_regiao_mm"]["CO"] for d in P7["por_dia"]]
assert SULV[2] == max(SULV) and round(SULV[2]) == 63 and round(SULV[1]) == 1, SULV  # Sul: pico no sábado (63 mm), sexta seca
series = [{"nome": "Sudeste", "cor": "#ff8c1a", "v": SEV}, {"nome": "Centro-Oeste", "cor": "#a78bfa", "v": COV},
          {"nome": "Sul", "cor": "#5ec8ff", "v": SULV}]

rios = []

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e granizo
GFIM = fim("f2") - .15
assert GFIM - GRAN > 1.0, (GRAN, GFIM)
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .02},
         {"src": "capa-dia/granizo.png", "ini": GRAN - .1, "fim": GFIM, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
SAB = ufs_av(56295)   # tempestade (amarelo) sábado 7/11: 2.595 (SP 645, MG 442, PR 399, RS 351, SC 295 = todas, GO 246)
assert len(geo(56295)) == 2595 and por_uf(56295, "SC") == 295 and aviso[56295]["descricao"] == "Tempestade"
assert aviso[56295]["inicio"].startswith("2026-11-07")
HOJE_T = geo(56290) | geo(56273)   # tempestade hoje 5/11: amarelo 2.308 (laranja 502 já dentro)
assert len(HOJE_T) == 2308 and aviso[56290]["inicio"].startswith("2026-11-05") and aviso[56273]["inicio"].startswith("2026-11-05")
HOJE_UF = sorted({UF[c[:2]] for c in HOJE_T if sum(x[:2] == c[:2] for x in HOJE_T) >= 5})
LARANJA = ufs_av(56273)   # laranja hoje: PR 251, SP 221, MS 30
assert por_uf(56273, "PR") == 251
SEXT = ufs_av(56293)      # tempestade sexta 6/11: 1.568 (MG 693, SP 404, PR 243…)
assert aviso[56293]["inicio"].startswith("2026-11-06") and len(geo(56293)) == 1568
DOM_ = ufs_av(56281)      # declínio de temperatura domingo 8/11: 2.060
assert len(geo(56281)) == 2060 and aviso[56281]["descricao"] == "Declínio de Temperatura" and aviso[56281]["inicio"].startswith("2026-11-08")
estados = [
    {"id": "sabado", "ini": CAPA, "fim": ini("f2") + .3, "ufs": SAB, "cor": LAR, "alfa": .4},
    {"id": "frente", "ini": em("f2", "Sul"), "fim": ini("f3") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .35},
    {"id": "pr", "ini": em("f4", "Paraná"), "fim": ini("f5") + .3, "ufs": ["PR"], "cor": LAR, "alfa": .4},
    {"id": "hoje", "ini": em("f5", "aviso"), "fim": ini("f6") + .3, "ufs": HOJE_UF, "cor": LAR, "alfa": .4},
    {"id": "sexta", "ini": em("f6", "Paraná"), "fim": ini("f7") + .3, "ufs": ["PR", "SP"], "cor": LAR, "alfa": .35},
    {"id": "sc", "ini": em("f9", "Santa"), "fim": DOMT + .3, "ufs": ["SC"], "cor": VERM, "alfa": .45},
    {"id": "domingo", "ini": DOMT, "fim": ini("f10") + .3, "ufs": DOM_, "cor": AZUL, "alfa": .4},
]

pinos = [
    {"nome": "Sábado, 7/11", "sub": "2.595 cidades em alerta de tempestade (INMET)", "lon": -49.0, "lat": -22.0, "ini": em("f1", "sábado"), "fim": ini("f2"), "h": 200},
    {"nome": "Frente fria", "sub": "chuva, trovoada, granizo e vendaval no sábado (previsão)", "lon": -52.0, "lat": -29.5, "ini": em("f2", "frente"), "fim": GRAN - .1, "h": 160},
    {"nome": "Chapecó", "sub": "tornado em 4/11", "lon": -52.62, "lat": -27.10, "ini": em("f3", "Chapecó"), "fim": ini("f4"), "h": 120},
    {"nome": "Xanxerê", "sub": "tornado em 4/11", "lon": -52.40, "lat": -26.88, "ini": em("f3", "Xanxerê"), "fim": ini("f4"), "h": 220},
    {"nome": "Guatambu", "sub": "sem energia elétrica", "lon": -52.79, "lat": -27.13, "ini": em("f3", "Guatambu", 2), "fim": ini("f4"), "h": 60},
    {"nome": "Paraná", "sub": "temporal localizado pela manhã (previsão)", "lon": -51.5, "lat": -24.6, "ini": em("f4", "Paraná"), "fim": ini("f5"), "h": 140},
    {"nome": "Minas Gerais", "sub": "744 cidades em aviso hoje", "lon": -44.5, "lat": -18.5, "ini": em("f5", "Minas"), "fim": ini("f6"), "h": 140},
    {"nome": "São Paulo", "sub": "645 cidades em aviso hoje", "lon": -48.5, "lat": -22.3, "ini": em("f5", "Paulo"), "fim": ini("f6"), "h": 220},
    {"nome": "Paraná", "sub": "sexta quente e abafada (previsão)", "lon": -51.5, "lat": -24.6, "ini": em("f6", "Paraná"), "fim": ini("f7"), "h": 120},
    {"nome": "São Paulo", "sub": "pancadas já de manhã na sexta (previsão)", "lon": -48.0, "lat": -22.3, "ini": em("f6", "Paulo"), "fim": ini("f7"), "h": 220},
    {"nome": "Sudoeste do PR", "sub": "chuva na sexta à tarde e à noite (previsão)", "lon": -53.0, "lat": -25.9, "ini": em("f7", "sudoeste"), "fim": ini("f8"), "h": 220},
    {"nome": "Oeste de SC", "sub": "chuva na sexta à noite (previsão)", "lon": -52.6, "lat": -27.0, "ini": em("f7", "Santa"), "fim": ini("f8"), "h": 120},
    {"nome": "Noroeste gaúcho", "sub": "chuva na sexta à noite (previsão)", "lon": -54.0, "lat": -27.9, "ini": em("f7", "gaúcho"), "fim": ini("f8"), "h": 60},
    {"nome": "Vale do Itajaí", "sub": "chuva mais volumosa no sábado (previsão)", "lon": -49.07, "lat": -26.92, "ini": em("f8", "Vale"), "fim": ini("f9"), "h": 200},
    {"nome": "Santa Catarina", "sub": "todas as 295 cidades no aviso de sábado", "lon": -50.5, "lat": -27.2, "ini": em("f9", "Santa"), "fim": DOMT, "h": 200},
    {"nome": "Domingo, 8/11", "sub": "temperatura cai em 2.060 cidades (INMET)", "lon": -50.0, "lat": -24.0, "ini": DOMT, "fim": ini("f10"), "h": 260},
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
                 '<div class="t1" style="font-size:76px;color:#FACC15">2.595 CIDADES</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">em alerta de tempestade no sábado · INMET</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": GRAN - .1, "k": "SÁBADO, 7/11 · PREVISÃO",
     "itens": [{"t": em("f2", "frente"), "txt": "❄️ Nova frente fria no Sul"}, {"t": em("f2", "chuva"), "txt": "⛈️ Chuva e trovoada"}],
     "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "OESTE DE SC · DEPOIS DOS TORNADOS",
     "itens": [{"t": em("f3", "tornados"), "txt": "🌪️ Chapecó, Guatambu e Xanxerê"}, {"t": em("f3", "firma"), "txt": "☀️ Tempo firma hoje"},
               {"t": em("f3", "energia"), "txt": "⚡ Guatambu sem energia"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "PARANÁ · HOJE, 5/11",
     "contador": conta(30, "f4", "30", "#ff8c1a", "°C MÁXIMA (PREVISÃO)", de=20),
     "l": "temporal localizado pela manhã · depois esquenta", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "HOJE, 5/11 · AVISO DE TEMPESTADE",
     "contador": conta(2308, "f5", "2.308", "#ff8c1a", "CIDADES"),
     "l": "MG 744 · SP 645 · PR 399 · GO 226 (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SEXTA, 6/11 · PREVISÃO",
     "itens": [{"t": em("f6", "quente"), "txt": "🥵 Quente e abafado no Paraná"}, {"t": em("f6", "pancadas"), "txt": "🌧️ Pancadas em SP de manhã"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SEXTA · TARDE E NOITE",
     "itens": [{"t": em("f7", "sudoeste"), "txt": "🌧️ Sudoeste do Paraná"}, {"t": em("f7", "Santa"), "txt": "🌧️ Oeste de Santa Catarina"},
               {"t": em("f7", "gaúcho"), "txt": "🌧️ Noroeste gaúcho"}],
     "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f8"), "fim": P9, "k": "SÁBADO · VALE DO ITAJAÍ",
     "itens": [{"t": em("f8", "atento"), "txt": "⚠️ Fique atento"}, {"t": em("f8", "volumosa"), "txt": "🌧️ Chuva mais volumosa (previsão)"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": P9, "fim": DOMT, "k": "SÁBADO · SANTA CATARINA INTEIRA",
     "contador": conta(295, "f9", "295", "#ff2a1f", "CIDADES EM AVISO", desde=P9),
     "l": "aviso de tempestade para 07/11 (INMET)", "borda": "rgba(255,42,31,.85)"},
    {"ini": DOMT, "fim": ini("f10"), "k": "DOMINGO, 8/11 · TEMPERATURA CAI",
     "contador": conta(2060, "f9", "2.060", "#5ec8ff", "CIDADES", desde=DOMT),
     "l": "aviso de declínio de temperatura (INMET)", "borda": "rgba(60,150,255,.85)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "SUL · PRÓXIMOS 7 DIAS (CHUVA PREVISTA)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f10") + .3, "dur": 1.6},
     "l": f"Sul: pico no sábado ({round(SULV[2])} mm) · mm somados nas capitais", "borda": "rgba(94,200,255,.7)"},
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
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>INMET</b>, aviso de tempestade para 07/11 (2.595 municípios) · {GOES}"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · foto do granizo: ilustração"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b> · {GOES}"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INMET</b>, avisos de tempestade para 05/11 (2.308 municípios)"},
    {"ini": ini("f6"), "fim": ini("f9"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": "<b>INMET</b>, tempestade 07/11 (SC: 295) · declínio de temperatura 08/11 (2.060)"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": f"<b>{MET}</b> · {OM}, 05/11 a 11/11"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chuvas": "#5ec8ff", "pancadas": "#5ec8ff", "trovoada": "#5ec8ff", "volumosa": "#5ec8ff",
         "enchente": "#ff2a1f", "frente": "#5ec8ff", "fria": "#5ec8ff", "granizo": "#ff2a1f", "tornados": "#ff2a1f",
         "quente": "#ff8c1a", "abafado": "#ff8c1a", "graus": "#ff8c1a", "tempestade": "#ff8c1a", "temporal": "#ff8c1a",
         "vendaval": "#ff8c1a", "alerta": "#ff2a1f", "aviso": "#ff8c1a", "atento": "#ff2a1f", "cai": "#5ec8ff",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"parana", "sul", "sao", "paulo", "minas", "catarina", "santa", "chapeco", "guatambu", "xanxere", "oeste", "sudoeste",
         "noroeste", "gaucho", "catarinense", "vale", "itajai", "sabado", "domingo", "sexta", "inemaclub", "onde"}
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
      f"sábado {SAB} · hoje {HOJE_UF} · sexta {SEXT} · domingo {DOM_} · Sul {SULV}")
