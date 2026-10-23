#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 23/10/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS),
dos avisos do INMET e da chuva prevista para sábado nas cidades das áreas de risco do Sul (Open-Meteo, pesquisa/bruto/openmeteo_sul_4d.json,
gravado por coleta_sul.py).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, aviso vermelho no Sul em 325 cidades no sábado), aviso vermelho do INMET
pintando PR, SC e RS, foto do granizo (ilustração) e 50 mm já somados, infravermelho do GOES-19 com câmera inclinada na linha de
instabilidade do Paraguai a SP, avisos de tempestade de hoje (741 em MG → 2.911 no país), Norte e Nordeste quase sem chuva,
calor de 34 a 38 °C e 40 °C em Teresina, colunas 3D da chuva prevista no sábado, vales de risco com foto de alagamento (ilustração),
domingo de eleição com chuva em SP, frio de segunda (4 °C em São Joaquim) e foto da geada (ilustração).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "23/10/2026"
MET = "Meteorologia · " + DATA
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
SUL1 = {"lon": -51.5, "lat": -26.8, "zoom": 4.8}       # f1: aviso vermelho no PR, SC e RS
SUDO = {"lon": -52.8, "lat": -26.0, "zoom": 6.0}       # f2: granizo no sudoeste do PR
CHUVA = {"lon": -51.0, "lat": -25.0, "zoom": 4.6}      # f3: linha de instabilidade do Paraguai a SP (IR)
MG = {"lon": -44.8, "lat": -19.0, "zoom": 5.1}         # f4: aviso em 741 cidades de MG
PAIS = {"lon": -51.0, "lat": -17.0, "zoom": 3.9}       # f4: total do país
NNE = {"lon": -52.0, "lat": -7.5, "zoom": 3.9}         # f5: Norte e Nordeste
CALOR = {"lon": -48.0, "lat": -11.5, "zoom": 4.2}      # f6: Centro-Oeste e Teresina
COL = {"lon": -51.0, "lat": -26.8, "zoom": 6.0}        # f7: colunas 3D do sábado
VALES = {"lon": -50.8, "lat": -26.7, "zoom": 6.1}      # f8: vales do Iguaçu, Itajaí, Rio do Peixe e Uruguai
DOM = {"lon": -47.5, "lat": -23.0, "zoom": 5.8}        # f9: SP no domingo
FRIA = {"lon": -50.0, "lat": -28.0, "zoom": 6.0}       # f10: São Joaquim 4 °C e geada
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
TOT4 = em("f4", "2.911")
camera = [
    K(0, BR), K(CAPA, BR), K(em("f1", "aviso") + .4, SUL1, 0, 0),
    K(fim("f1") - .2, {**SUL1, "zoom": 4.9}, 0, 0),
    K(ini("f2") + 1.2, SUDO, 0, 0), K(fim("f2") - .2, {**SUDO, "zoom": 6.1}, 4, 0),
    K(ini("f3") + 1.3, CHUVA, 45, -18), K(fim("f3") - .2, {**CHUVA, "lon": -49.5, "zoom": 4.7}, 48, -4),
    K(ini("f4") + 1.0, MG, 0, 0), K(TOT4 - 1.2, {**MG, "zoom": 5.2}, 0, 0), K(TOT4 + .4, PAIS, 0, 0), K(fim("f4") - .2, {**PAIS, "zoom": 3.95}, 0, 0),
    K(ini("f5") + 1.0, NNE, 0, 0), K(fim("f5") - .2, {**NNE, "zoom": 3.95}, 0, 0),
    K(ini("f6") + 1.2, CALOR, 0, 0), K(fim("f6") - .2, {**CALOR, "zoom": 4.3}, 4, 0),
    K(ini("f7") + 1.0, COL, 55, -20), K(em("f7", "Santa"), {**COL, "zoom": 6.05}, 56, 0), K(fim("f7") - .2, {**COL, "zoom": 6.1}, 56, 18),
    K(ini("f8") + 1.0, VALES, 0, 0), K(fim("f8") - .2, {**VALES, "zoom": 6.2}, 4, 0),
    K(ini("f9") + 1.0, DOM, 0, 0), K(fim("f9") - .2, {**DOM, "zoom": 5.9}, 4, 0),
    K(ini("f10") + 1.0, FRIA, 30, -10), K(fim("f10") - .2, {**FRIA, "zoom": 6.1}, 34, 6),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na linha de instabilidade (f3)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# câmera inclinada: o Blue Marble do mundo por baixo do geocolor (sem borda preta)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": ini("f3") - .3, "fim": ini("f4") + .4, "dur": fim("f3") - ini("f3") + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])
assert len(BONS) >= 20, f"poucos quadros bons de infravermelho: {len(BONS)}"

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA para sábado (24/10), Open-Meteo
S4 = json.loads((B / "openmeteo_sul_4d.json").read_text())
assert S4["dias"] == ["2026-10-23", "2026-10-24", "2026-10-25", "2026-10-26"], S4["dias"]
CID = {k: v for k, v in S4["cidades"].items() if k != "São Paulo"}
MM = {k: v["por_dia"][1] for k, v in CID.items()}   # só o sábado
assert MM["Rio do Sul"] > 100 and MM["Chapecó"] > 100 and min(MM.values()) >= 10, MM   # a fala diz "de cinquenta a cem"
col = [{"id": i, "p": [v["lon"], v["lat"]], "v": MM[c], "cor": [60, 150, 255] if MM[c] >= 70 else [120, 190, 255]} for i, (c, v) in enumerate(CID.items())]
ordem = {c["id"]: i * .15 for i, c in enumerate(col)}
colunas = [{"id": "chuva3d", "ini": ini("f7") + .2, "fim": ini("f8") + .2, "dados": col, "raio": 19000, "escala": 3000, "ordem": ordem, "varredura": 1}]
fmm = lambda v: f"{v:.0f}"
P = lambda c: (CID[c]["lon"], CID[c]["lat"])

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, granizo, alagamento e geada
GRANIZO = em("f2", "granizo")
FIMGRAN = em("f2", "pontos") - .2
ALAGA = em("f8", "alagamento")
GEAR = em("f10", "gear")
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": GRANIZO - .1, "fim": FIMGRAN, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/alagamento.png", "ini": ALAGA - .1, "fim": ini("f9") + .3, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/geada.png", "ini": GEAR - .1, "fim": ini("f11") + .3, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_geo = lambda g, minimo=5: sorted({UF[c[:2]] for c in g if sum(x[:2] == c[:2] for x in g) >= minimo})
VERMELHO = geo(56168)   # tempestade vermelha (Grande Perigo) sábado 24/10, 06h-21h: 325 (SC 146, PR 99, RS 80)
assert aviso[56168]["severidade"] == "Grande Perigo" and aviso[56168]["descricao"] == "Tempestade" and aviso[56168]["inicio"].startswith("2026-10-24")
assert len(VERMELHO) == 325 and ufs_geo(VERMELHO) == ["PR", "RS", "SC"], len(VERMELHO)
TEMP_HOJE = geo(56159) | geo(56144)   # tempestade amarela 23/10: 2.911 (MG 741, SP 645, RS 497, PR 399, SC 295...); a laranja (590) está dentro
assert all(aviso[i]["descricao"] == "Tempestade" and aviso[i]["inicio"].startswith("2026-10-23") for i in (56159, 56144))
assert len(TEMP_HOJE) == 2911 and sum(c[:2] == "31" for c in TEMP_HOJE) == 741, len(TEMP_HOJE)
HOJE = ufs_geo(TEMP_HOJE)
assert len(geo(56156)) == 684 and aviso[56156]["descricao"] == "Baixa Umidade"   # baixa umidade 22 e 23/10: 684 cidades
NORDESTE = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
estados = [
    {"id": "verm", "ini": em("f1", "aviso"), "fim": ini("f2") + .3, "ufs": ["PR", "SC", "RS"], "cor": VERM, "alfa": .45},
    {"id": "gran", "ini": FIMGRAN, "fim": ini("f3") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .3},
    {"id": "linha", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["RS", "SC", "PR", "SP"], "cor": AZUL, "alfa": .25},
    {"id": "mg", "ini": ini("f4"), "fim": TOT4 - .9, "ufs": ["MG"], "cor": LAR, "alfa": .6},
    {"id": "hoje", "ini": TOT4 - 1.0, "fim": ini("f5") + .3, "ufs": HOJE, "cor": LAR, "alfa": .5},
    {"id": "nchuva", "ini": em("f5", "Amazonas"), "fim": ini("f6") + .3, "ufs": ["AM", "RO"], "cor": AZUL, "alfa": .4},
    {"id": "seco", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": NORDESTE, "cor": LAR, "alfa": .35},
    {"id": "calor", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["MT", "MS", "GO", "PI"], "cor": VERM, "alfa": .4},
    {"id": "sabado", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .3},
    {"id": "dom", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["SP"], "cor": AZUL, "alfa": .45},
    {"id": "frio", "ini": ini("f10"), "fim": ini("f11") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .4},
]

pinos = [
    {"nome": "Sudoeste do Paraná", "sub": "granizo hoje cedo", "lon": -53.4, "lat": -25.9, "ini": FIMGRAN, "fim": ini("f3"), "h": 160},
    {"nome": "Teresina (PI)", "sub": "até 40 °C hoje", "lon": -42.80, "lat": -5.09, "ini": em("f6", "Teresina"), "fim": ini("f7"), "h": 160},
    {"nome": "Rio do Sul (SC)", "sub": f"{fmm(MM['Rio do Sul'])} mm no sábado (previsão)", "lon": P("Rio do Sul")[0], "lat": P("Rio do Sul")[1],
     "ini": em("f7", "Santa"), "fim": ini("f8"), "h": 140},
    {"nome": "Chapecó (SC)", "sub": f"{fmm(MM['Chapecó'])} mm no sábado (previsão)", "lon": P("Chapecó")[0], "lat": P("Chapecó")[1],
     "ini": em("f7", "Rio", 1), "fim": ini("f8"), "h": 200},
    {"nome": "Vale do Iguaçu", "sub": "União da Vitória (PR)", "lon": P("União da Vitória")[0], "lat": P("União da Vitória")[1],
     "ini": em("f8", "Iguaçu"), "fim": ALAGA, "h": 200},
    {"nome": "Vale do Itajaí", "sub": "Blumenau (SC)", "lon": P("Blumenau")[0], "lat": P("Blumenau")[1], "ini": em("f8", "Itajaí"), "fim": ALAGA, "h": 120},
    {"nome": "Vale do Rio do Peixe", "sub": "Joaçaba (SC)", "lon": P("Joaçaba")[0], "lat": P("Joaçaba")[1], "ini": em("f8", "Peixe"), "fim": ALAGA, "h": 60},
    {"nome": "Rio Uruguai", "sub": "Chapecó (SC)", "lon": P("Chapecó")[0], "lat": P("Chapecó")[1], "ini": em("f8", "Uruguai"), "fim": ALAGA, "h": 160},
    {"nome": "São Paulo (capital)", "sub": "chuva forte possível no domingo", "lon": -46.63, "lat": -23.55, "ini": em("f9", "capital"), "fim": ini("f10"), "h": 160},
    {"nome": "São Joaquim (SC)", "sub": "4 °C na segunda (previsão)", "lon": -49.93, "lat": -28.29, "ini": em("f10", "Joaquim"), "fim": GEAR, "h": 160},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)   # número dito logo no começo da fala: o contador começa com a fala
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
H = em("f1", "325") - 1.25   # o hero (data grande) sai 1,25 s antes do "325" (o contador chega no número)
TOTAL = TOT4 - 1.1   # o painel do total do país entra 1,1 s antes do número
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:96px">AVISO VERMELHO</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">de tempestade no Sul, sábado</div>'}]
paineis = [
    {"ini": H + .1, "fim": GRANIZO - .1, "k": "AVISO VERMELHO · SÁBADO, 24/10",
     "contador": conta(325, "f1", "325", "#ff2a1f", "CIDADES DO SUL"),
     "l": "PR, SC e RS · vento acima de 100 km/h · INMET", "borda": "rgba(255,42,31,.85)"},
    {"ini": FIMGRAN, "fim": ini("f3"), "k": "JÁ CHOVEU HOJE",
     "contador": conta(50, "f2", "50", "#5ec8ff", "MM EM PONTOS DO SUL"),
     "l": "e granizo no sudoeste do Paraná", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "LINHA DE INSTABILIDADE",
     "itens": [{"t": em("f3", "Paraguai"), "txt": "⛈️ do Paraguai até São Paulo"},
               {"t": em("f3", "trovoada"), "txt": "⚡ trovoada, granizo e vento"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": TOTAL, "k": "AVISO DE TEMPESTADE · HOJE",
     "contador": conta(741, "f4", "741", "#ff8c1a", "CIDADES DE MINAS"),
     "l": "INMET", "borda": "rgba(255,140,26,.8)"},
    {"ini": TOTAL, "fim": ini("f5"), "k": "AVISO DE TEMPESTADE · HOJE",
     "contador": conta(2911, "f4", "2.911", "#ff8c1a", "CIDADES NO PAÍS"),
     "l": "do Sul ao Sudeste e Centro-Oeste · INMET", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "HOJE NO NORTE E NO NORDESTE",
     "itens": [{"t": em("f5", "chove"), "txt": "☀️ quase não chove"},
               {"t": em("f5", "Amazonas"), "txt": "🌦️ pancadas no AM e em RO"},
               {"t": em("f5", "litoral"), "txt": "🌦️ e no litoral nordestino"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "MÁXIMA PREVISTA HOJE",
     "contador": conta(40, "f6", "40", "#ff2a1f", "°C EM TERESINA"),
     "l": "34 a 38 °C no Centro-Oeste", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SÁBADO, 24/10 (PREVISÃO)",
     "contador": conta(100, "f7", "100", "#5ec8ff", "MM NO SUL"),
     "l": f"Rio do Sul {fmm(MM['Rio do Sul'])} mm · Chapecó {fmm(MM['Chapecó'])} mm (Open-Meteo)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f8"), "fim": ALAGA - .1, "k": "ÁREAS DE RISCO",
     "itens": [{"t": em("f8", "Iguaçu"), "txt": "🌊 vale do Iguaçu"},
               {"t": em("f8", "Itajaí"), "txt": "🌊 vale do Itajaí"},
               {"t": em("f8", "Peixe"), "txt": "🌊 vale do Rio do Peixe"},
               {"t": em("f8", "Uruguai"), "txt": "🌊 Rio Uruguai"}],
     "borda": "rgba(255,90,20,.85)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "DOMINGO, 25/10 · ELEIÇÃO",
     "itens": [{"t": em("f9", "diminui"), "txt": "🌥️ chuva diminui no Sul"},
               {"t": em("f9", "forte"), "txt": "⛈️ chuva forte em São Paulo"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "SEGUNDA E TERÇA (PREVISÃO)",
     "itens": [{"t": em("f10", "4"), "txt": "🌡️ São Joaquim com 4 °C"},
               {"t": GEAR, "txt": "❄️ geada na serra na terça"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "onde"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f11", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
     "borda": "rgba(250,204,21,.8)"},
]
for a, b in zip(paineis, paineis[1:]):
    assert a["fim"] <= b["ini"] + 1e-6, (a["k"], b["k"])
for a in paineis:
    if a.get("contador"):
        c = a["contador"]
        assert a["ini"] - .01 <= c["ini"] and c["ini"] + c["dur"] <= a["fim"], ("contador fora do painel", a["k"])

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "<b>INMET</b>, aviso vermelho de tempestade para 24/10 (325 municípios)"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · foto do granizo: ilustração"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE} · <b>{MET}</b>"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INMET</b>, aviso de tempestade para 23/10 (2.911 municípios)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · <b>INMET</b>: baixa umidade em 684 cidades"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>Open-Meteo</b>, chuva prevista para 24/10 · <b>{MET}</b>"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · foto do alagamento: ilustração"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": f"<b>{MET}</b> · previsão · foto da geada: ilustração"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "chover": "#5ec8ff", "chuvas": "#5ec8ff", "tempestade": "#ff8c1a", "alerta": "#ff8c1a",
         "seco": "#ff8c1a", "frio": "#96d2ff", "esfria": "#96d2ff", "geada": "#96d2ff", "gear": "#96d2ff", "milimetros": "#5ec8ff",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "quente": "#ff2a1f", "granizo": "#96d2ff", "trovoada": "#ff8c1a", "vermelho": "#ff2a1f",
         "forte": "#ff8c1a", "aviso": "#ff8c1a", "vento": "#ff8c1a", "alagamento": "#5ec8ff", "instabilidade": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "parana", "santa", "catarina", "paraguai", "sao", "paulo", "minas", "rio", "amazonas", "rondonia", "nordeste",
         "norte", "teresina", "centrooeste", "iguacu", "itajai", "peixe", "uruguai", "joaquim", "serra", "litoral", "nordestino",
         "capital", "pais", "inemaclub", "onde", "grande"}
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
     "marca": "INEMA · CLIMA DO DIA", "selo": DATA[:5] + " · INMET · NOAA",
     "camera": camera, "sat": SAT, "colunas": colunas, "telas": telas, "estados": estados, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · colunas {MM}")
