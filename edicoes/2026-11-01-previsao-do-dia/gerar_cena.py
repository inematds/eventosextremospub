#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 01/11/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "ATÉ 40°C HOJE · VENDAVAL E GRANIZO NO SUL NA QUARTA, 4/11"),
infravermelho do GOES-19 (calor + umidade, baixa pressão → frente fria), calor de hoje (contador 40 °C no oeste de SP e MS),
temporais à tarde no PR/SC/sul do MS, aviso de chuvas intensas de hoje (546, MG 238, GO 116), Finados com aviso laranja
no PR (337), quarta com foto do granizo (ilustração) + aviso de tempestade (1.631), gráfico dos 7 dias (frente fria 6–7/11),
colunas 3D de 80–100 mm previstos no oeste do Sul com câmera inclinada girando.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "01/11/2026"
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
ABRE = {"lon": -52.0, "lat": -24.5, "zoom": 4.5}     # f1: 40 °C hoje, vendaval e granizo no Sul na quarta
NOVE = {"lon": -52.0, "lat": -22.0, "zoom": 4.1}     # f2: calor + umidade, baixa pressão → frente fria (IR GOES-19)
CAL = {"lon": -52.5, "lat": -21.5, "zoom": 4.7}      # f3: 30 °C em S/SE/CO, 40 °C no oeste de SP e MS
TAR = {"lon": -52.5, "lat": -25.5, "zoom": 5.0}      # f4: temporais à tarde no PR, SC e sul do MS; RS mais seco
MGGO = {"lon": -47.5, "lat": -17.0, "zoom": 4.7}     # f5: aviso de chuvas intensas 546 (MG 238, GO 116)
FIN = {"lon": -54.0, "lat": -25.0, "zoom": 4.9}      # f6: Finados e terça, Paraguai/oeste do Sul, PR 337 em laranja
QUA = {"lon": -52.5, "lat": -28.0, "zoom": 5.0}      # f7: quarta, RS → oeste de SC, aviso 1.631
SUL = {"lon": -51.5, "lat": -26.0, "zoom": 4.6}      # f8: frente fria 6–7/11 + gráfico dos 7 dias
TEND = {"lon": -52.6, "lat": -26.4, "zoom": 5.4}     # f9: colunas 3D de 80–100 mm no oeste do Sul
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
GRANIZO = em("f7", "granizo")
C1631 = em("f7", "1.631")
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, ABRE, 0, 0), K(fim("f1") - .2, {**ABRE, "zoom": 4.6}, 0, 0),
    K(ini("f2") + 1.0, NOVE, 0, 0), K(fim("f2") - .2, {**NOVE, "zoom": 4.2}, 0, 0),
    K(ini("f3") + 1.0, CAL, 0, 0), K(fim("f3") - .2, {**CAL, "zoom": 4.8}, 0, 0),
    K(ini("f4") + 1.0, TAR, 0, 0), K(fim("f4") - .2, {**TAR, "zoom": 5.1}, 0, 0),
    K(ini("f5") + 1.0, MGGO, 0, 0), K(fim("f5") - .2, {**MGGO, "zoom": 4.8}, 0, 0),
    K(ini("f6") + 1.0, FIN, 0, 0), K(fim("f6") - .2, {**FIN, "zoom": 5.0}, 0, 0),
    K(ini("f7") + 1.0, QUA, 20, -6), K(fim("f7") - .2, {**QUA, "zoom": 5.1}, 28, 6),
    K(ini("f8") + 1.0, SUL, 0, 0), K(fim("f8") - .2, {**SUL, "zoom": 4.7}, 0, 0),
    K(ini("f9") + 1.0, {**TEND, "zoom": 5.2}, 45, -16), K(fim("f9") - .2, {**TEND, "zoom": 5.5}, 58, 18),
    K(ini("f10") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
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
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": CAPA - .3, "fim": IRF, "dur": IRF - CAPA, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

# ---------------------------------------------------------------- colunas 3D: 80 a 100 mm previstos no oeste do Sul nos próximos dias (f9)
# a previsão disse "perto dos 80 a 100 milímetros, principalmente no oeste da região Sul": 100 no núcleo, 80 nas bordas
PROJ = {"Oeste do PR": ((-53.6, -24.9), 100), "Sudoeste do PR": ((-52.9, -25.9), 100), "Oeste de SC": ((-52.7, -26.9), 100),
        "Meio-oeste de SC": ((-51.5, -27.1), 80), "Noroeste gaúcho": ((-54.0, -27.8), 90), "Missões (RS)": ((-55.0, -28.4), 80)}
proj = [{"id": i, "p": list(p), "v": v, "cor": VERM if v >= 100 else LAR} for i, (c, (p, v)) in enumerate(PROJ.items())]
COL0 = em("f9", "chuva") - .3
colunas = [{"id": "proj", "ini": COL0, "fim": ini("f10") + .4, "dados": proj, "raio": 22000, "escala": 4500,
            "ordem": {c["id"]: i * .12 for i, c in enumerate(proj)}, "varredura": 1}]

# ---------------------------------------------------------------- previsão Open-Meteo (7 dias): gráfico
P7 = json.loads((B / "previsao7d.json").read_text())
HOJE = "2026-11-01"
assert P7["dias"][0] == HOJE and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
SEV = [d["por_regiao_mm"]["SE"] for d in P7["por_dia"]]
COV = [d["por_regiao_mm"]["CO"] for d in P7["por_dia"]]
assert SULV[3] == max(SULV) and round(SULV[3]) == 46 and round(SULV[6]) == 38, SULV   # Sul: 46 mm na quarta 4/11, 38 mm no sábado 7/11
series = [{"nome": "Sudeste", "cor": "#ff8c1a", "v": SEV}, {"nome": "Centro-Oeste", "cor": "#a78bfa", "v": COV},
          {"nome": "Sul", "cor": "#5ec8ff", "v": SULV}]

rios = []

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e granizo
# granizo entra na palavra e sai antes do contador de 1.631 cidades começar
GFIM = C1631 - 1.1
assert GFIM - GRANIZO > 1.0, (GRANIZO, C1631)
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": GRANIZO - .1, "fim": GFIM, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
HOJE_ = ufs_av(56239)    # chuvas intensas AMARELO hoje 1/11: 546 (MG 238, GO 116, TO 84, ES 48)
assert len(geo(56239)) == 546 and por_uf(56239, "MG") == 238 and por_uf(56239, "GO") == 116 and por_uf(56239, "TO") == 84
assert aviso[56239]["descricao"] == "Chuvas Intensas" and aviso[56239]["inicio"].startswith("2026-11-01")
FIN_ = ufs_av(56227)     # tempestade LARANJA (Perigo) Finados 2/11: 366 (PR 337, SP 16, MS 13)
assert len(geo(56227)) == 366 and por_uf(56227, "PR") == 337 and aviso[56227]["severidade"] == "Perigo"
assert aviso[56227]["descricao"] == "Tempestade" and aviso[56227]["inicio"].startswith("2026-11-02")
QUA_ = ufs_av(56237)     # tempestade AMARELO quarta 4/11: 1.631 (RS 448, SP 375, PR 309, SC 295)
assert len(geo(56237)) == 1631 and por_uf(56237, "RS") == 448 and por_uf(56237, "SC") == 295
assert aviso[56237]["descricao"] == "Tempestade" and aviso[56237]["inicio"].startswith("2026-11-04")
estados = [
    {"id": "abre", "ini": CAPA, "fim": ini("f2") + .3, "ufs": ["SP", "MS", "PR", "SC", "RS"], "cor": VERM, "alfa": .3},
    {"id": "calor", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["SP", "MS"], "cor": VERM, "alfa": .35},
    {"id": "tarde", "ini": em("f4", "Paraná"), "fim": ini("f5") + .3, "ufs": ["PR", "SC", "MS"], "cor": LAR, "alfa": .35},
    {"id": "hoje", "ini": em("f5", "aviso"), "fim": ini("f6") + .3, "ufs": HOJE_, "cor": AMA, "alfa": .35},
    {"id": "finados", "ini": em("f6", "Paraná"), "fim": ini("f7") + .3, "ufs": FIN_, "cor": LAR, "alfa": .45},
    {"id": "quarta", "ini": em("f7", "Rio"), "fim": ini("f8") + .3, "ufs": QUA_, "cor": VERM, "alfa": .4},
    {"id": "frente", "ini": em("f8", "frente"), "fim": ini("f9") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .35},
]

pinos = [
    {"nome": "Oeste de SP e MS", "sub": "até 40 °C hoje (previsão)", "lon": -52.5, "lat": -21.5, "ini": em("f1", "40"), "fim": em("f1", "Sul"), "h": 160},
    {"nome": "Sul do Brasil", "sub": "vendaval e granizo na quarta, 4/11 (previsão)", "lon": -52.0, "lat": -27.5, "ini": em("f1", "Sul"), "fim": ini("f2"), "h": 200},
    {"nome": "Oeste paulista", "sub": "perto de 40 °C hoje", "lon": -51.0, "lat": -21.8, "ini": em("f3", "paulista"), "fim": ini("f4"), "h": 120},
    {"nome": "Mato Grosso do Sul", "sub": "perto de 40 °C hoje", "lon": -54.6, "lat": -20.6, "ini": em("f3", "Mato"), "fim": ini("f4"), "h": 220},
    {"nome": "Paraná", "sub": "temporais à tarde e à noite", "lon": -51.5, "lat": -24.6, "ini": em("f4", "Paraná"), "fim": ini("f5"), "h": 120},
    {"nome": "Santa Catarina", "sub": "temporais à tarde e à noite", "lon": -50.5, "lat": -27.2, "ini": em("f4", "Santa"), "fim": ini("f5"), "h": 60},
    {"nome": "Sul do MS", "sub": "temporais à tarde e à noite", "lon": -54.8, "lat": -22.6, "ini": em("f4", "Mato"), "fim": ini("f5"), "h": 220},
    {"nome": "Rio Grande do Sul", "sub": "tempo mais seco hoje", "lon": -53.5, "lat": -29.8, "ini": em("f4", "Rio"), "fim": ini("f5"), "h": 80},
    {"nome": "Minas Gerais", "sub": "238 cidades em aviso hoje", "lon": -43.8, "lat": -19.6, "ini": em("f5", "Minas"), "fim": ini("f6"), "h": 60},
    {"nome": "Goiás", "sub": "116 cidades em aviso hoje", "lon": -49.6, "lat": -16.0, "ini": em("f5", "Goiás"), "fim": ini("f6"), "h": 260},
    {"nome": "Paraguai", "sub": "pancadas em Finados e na terça (previsão)", "lon": -56.5, "lat": -24.0, "ini": em("f6", "Paraguai"), "fim": ini("f7"), "h": 160},
    {"nome": "Oeste do Sul", "sub": "pancadas irregulares (previsão)", "lon": -53.4, "lat": -27.0, "ini": em("f6", "oeste"), "fim": ini("f7"), "h": 60},
    {"nome": "Rio Grande do Sul", "sub": "temporais na quarta (previsão)", "lon": -53.5, "lat": -29.5, "ini": em("f7", "Rio"), "fim": C1631 - 1.0, "h": 120},
    {"nome": "Oeste catarinense", "sub": "vendaval e granizo na quarta (previsão)", "lon": -52.7, "lat": -26.9, "ini": em("f7", "catarinense"), "fim": ini("f8"), "h": 220},
    {"nome": "Sul do Brasil", "sub": "nova frente fria em 6 e 7/11 (previsão)", "lon": -52.0, "lat": -27.5, "ini": em("f8", "frente"), "fim": ini("f9"), "h": 260},
    {"nome": "Oeste do Sul", "sub": "80 a 100 mm nos próximos dias (previsão)", "lon": -53.0, "lat": -25.9, "ini": em("f9", "80"), "fim": ini("f10"), "h": 340},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0


def conta(ate, fid, palavra, cor, unid, dec=0, de=0, k=1):
    t = em(fid, palavra, k)
    lead = max(.4, min(LEAD, t - ini(fid)))   # número logo no começo da fala: o contador cabe no painel
    return {"de": de, "ate": ate, "dec": dec, "ini": t - lead, "dur": lead, "cor": cor, "unid": unid}


hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o fato da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:80px;color:#FACC15">ATÉ 40 °C HOJE</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">vendaval e granizo no Sul na quarta, 4/11 · previsão</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "POR QUE (PREVISÃO)",
     "itens": [{"t": em("f2", "umidade"), "txt": "🌡️ Calor + umidade alta"}, {"t": em("f2", "pressão"), "txt": "🌀 Baixa pressão"},
               {"t": em("f2", "frente"), "txt": "⛈️ Frente fria numa área grande"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "HOJE, 1/11 · MÁXIMA (PREVISÃO)",
     "contador": conta(40, "f3", "40", "#ff2a1f", "°C"),
     "l": "oeste de SP e MS · 30 °C no Sul, Sudeste e Centro-Oeste", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE, 1/11 · TARDE E NOITE",
     "itens": [{"t": em("f4", "Paraná"), "txt": "⛈️ Temporais no PR, SC e sul do MS"}, {"t": em("f4", "Rio"), "txt": "☀️ RS mais seco"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "HOJE, 1/11 · CHUVAS INTENSAS",
     "contador": conta(546, "f5", "546", "#FACC15", "CIDADES EM AVISO"),
     "l": "MG 238 · GO 116 · TO 84 · ES 48 (INMET)", "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "FINADOS, 2/11 · AVISO LARANJA",
     "contador": conta(337, "f6", "337", "#ff8c1a", "CIDADES NO PARANÁ"),
     "l": "tempestade · 366 cidades no total (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": GFIM, "fim": ini("f8"), "k": "QUARTA, 4/11 · TEMPESTADE",   # entra depois da foto do granizo
     "contador": conta(1631, "f7", "1.631", "#ff2a1f", "CIDADES EM AVISO"),
     "l": "RS 448 · SP 375 · PR 309 · SC 295 (INMET)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "PRÓXIMOS 7 DIAS · CHUVA PREVISTA",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f8") + .3, "dur": 1.6},
     "l": "Sul: 46 mm na quarta · 38 mm no sábado, 7/11 · mm somados nas capitais", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "OESTE DO SUL · PRÓXIMOS DIAS",
     "contador": conta(100, "f9", "100", "#5ec8ff", "MM (PREVISÃO)"),
     "l": "chuva somada entre 80 e 100 mm", "borda": "rgba(60,150,255,.8)"},
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
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>{MET}</b> · {GOES}"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · {GOES}"},
    {"ini": ini("f3"), "fim": ini("f5"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso amarelo de chuvas intensas para 01/11 (546 municípios)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso laranja de tempestade para 02/11 (366 municípios, 337 no PR)"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso de tempestade para 04/11 (1.631 municípios) · foto do granizo: ilustração"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · {OM}, 01/11 a 07/11"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b>, chuva somada prevista para os próximos dias"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chuvas": "#5ec8ff", "milimetros": "#5ec8ff", "pancadas": "#5ec8ff", "sol": AM, "seco": AM,
         "frente": "#5ec8ff", "fria": "#5ec8ff", "frentes": "#5ec8ff", "frias": "#5ec8ff", "volumosa": "#5ec8ff",
         "calor": "#ff2a1f", "calorao": "#ff2a1f", "laranja": "#ff8c1a", "umidade": "#5ec8ff", "seco": AM, "graus": "#ff2a1f", "intensas": "#ff8c1a", "intensa": "#ff8c1a", "tempestade": "#ff8c1a",
         "tempestades": "#ff8c1a", "severas": "#ff2a1f", "temporais": "#ff8c1a", "granizo": "#ff8c1a", "vendaval": "#ff8c1a",
         "tornado": "#ff2a1f", "risco": "#ff2a1f", "aviso": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"parana", "sul", "sao", "paulo", "goias", "minas", "paraguai", "catarinense", "santa", "catarina", "mato", "grosso", "rio", "grande", "paulista", "sudeste", "centrooeste",
         "oeste", "finados", "inemaclub", "onde"}
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
      f"hoje {HOJE_} · finados {FIN_} · quarta {QUA_} · Sul {SULV}")
