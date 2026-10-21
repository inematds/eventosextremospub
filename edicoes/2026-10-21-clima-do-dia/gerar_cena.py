#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 21/10/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS),
dos avisos do INMET e da chuva prevista para 7 dias (Open-Meteo, pesquisa/bruto/previsao7d.json).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, granizo no Sul e 40 °C), infravermelho do GOES-19 com câmera inclinada
no oeste do Sul, pinos do granizo da manhã e foto do granizo (ilustração), avisos de tempestade do INMET (323 no PR → 623 no total;
laranja em 678 na sexta), calor de 40 °C em MT/MS e Teresina, colunas 3D da chuva prevista em 7 dias (Curitiba, São Paulo,
Florianópolis, Open-Meteo), domingo de eleição instável no Sul, foto da geada (ilustração).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "21/10/2026"
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
OESTE = {"lon": -55.0, "lat": -27.0, "zoom": 5.0}      # f2: chuva vem do Paraguai e da Argentina
GRAN = {"lon": -53.9, "lat": -27.9, "zoom": 6.5}      # f3: granizo da manhã no noroeste gaúcho
SUL = {"lon": -51.5, "lat": -25.5, "zoom": 4.9}        # f4 e f7: avisos de tempestade do INMET
CALOR = {"lon": -50.0, "lat": -12.0, "zoom": 3.85}     # f5: 40 °C em MT/MS e Teresina
NORTE = {"lon": -55.0, "lat": -7.0, "zoom": 3.75}      # f6: pancadas na Amazônia, Nordeste seco
COL = {"lon": -48.4, "lat": -25.6, "zoom": 5.7}        # f8: colunas 3D Curitiba, São Paulo, Florianópolis
DOM = {"lon": -50.0, "lat": -25.0, "zoom": 4.7}        # f9: domingo de eleição
SERRA = {"lon": -50.5, "lat": -27.5, "zoom": 5.6}      # f10: geada na Serra Catarinense
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
GRANIZO1 = em("f1", "granizo")
camera = [
    K(0, BR), K(CAPA, BR), K(GRANIZO1 + .4, {**BR, "lon": -52.0, "lat": -20.0, "zoom": 4.2}, 0, 0),
    K(fim("f1") - .2, {**BR, "lon": -52.5, "lat": -19.0, "zoom": 4.0}, 0, 0),
    K(ini("f2") + 1.3, OESTE, 45, -18), K(fim("f2") - .2, {**OESTE, "lon": -54.0, "zoom": 5.1}, 48, -4),
    K(ini("f3") + 1.2, GRAN, 30, -8), K(fim("f3") - .2, {**GRAN, "zoom": 6.65}, 34, 6),
    K(ini("f4") + 1.0, SUL, 0, 0), K(fim("f4") - .2, {**SUL, "lon": -52.0, "zoom": 4.75}, 4, 0),
    K(ini("f5") + 1.2, CALOR, 0, 0), K(fim("f5") - .2, {**CALOR, "zoom": 3.9}, 4, 0),
    K(ini("f6") + 1.0, NORTE, 0, 0), K(fim("f6") - .2, {**NORTE, "lon": -50.0, "zoom": 3.8}, 0, 0),
    K(ini("f7") + 1.2, SUL, 30, -10), K(fim("f7") - .2, {**SUL, "zoom": 5.0}, 34, 6),
    K(ini("f8") + 1.0, COL, 55, -20), K(em("f8", "Paulo"), {**COL, "zoom": 5.75}, 56, 0), K(fim("f8") - .2, {**COL, "zoom": 5.8}, 56, 18),
    K(ini("f9") + 1.0, DOM, 0, 0), K(fim("f9") - .2, {**DOM, "zoom": 4.8}, 4, 0),
    K(ini("f10") + 1.0, SERRA, 35, -10), K(fim("f10") - .2, {**SERRA, "zoom": 5.7}, 40, 6),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na chuva que entra pelo oeste (f2)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# câmera inclinada no oeste do Sul: o Blue Marble do mundo por baixo do geocolor (sem borda preta)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": ini("f2") - .3, "fim": ini("f3") + .4, "dur": fim("f2") - ini("f2") + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])
assert len(BONS) >= 20, f"poucos quadros bons de infravermelho: {len(BONS)}"

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA em 7 dias (21 a 27/10), Open-Meteo
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-21" and P7["dias"][-1] == "2026-10-27", P7["dias"]
TOP = dict(P7["acumulado_7d_top"])
CAPS = {"Curitiba": (-49.27, -25.43), "São Paulo": (-46.63, -23.55), "Florianópolis": (-48.55, -27.60)}
MM = {c: TOP[c] for c in CAPS}
assert 99 <= MM["Curitiba"] <= 102 and 91.5 <= MM["São Paulo"] <= 93, MM   # a fala diz "cem" e "noventa e dois" milímetros
col = [{"id": i, "p": list(CAPS[c]), "v": MM[c], "cor": [60, 150, 255] if MM[c] >= 90 else [120, 190, 255]} for i, c in enumerate(CAPS)]
ordem = {c["id"]: i * .2 for i, c in enumerate(col)}
colunas = [{"id": "chuva3d", "ini": ini("f8") + .2, "fim": ini("f9") + .2, "dados": col, "raio": 22000, "escala": 4000, "ordem": ordem, "varredura": 1}]
fmm = lambda v: f"{v:.0f}"

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, granizo e geada
GRANIZO = em("f3", "tarde")
GEAR = em("f10", "gear")
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": GRANIZO - .1, "fim": ini("f4") + .3, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/geada.png", "ini": GEAR - .1, "fim": ini("f11") + .3, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
HOJE = ufs_av(56127)     # tempestade amarela 21/10: 623 (PR 323, RS 147, SC 121, MS 28, SP 4)
assert len(geo(56127)) == 623 and sum(c[:2] == "41" for c in geo(56127)) == 323, len(geo(56127))
assert aviso[56127]["descricao"] == "Tempestade" and aviso[56127]["inicio"].startswith("2026-10-21")
SEXTA = ufs_av(56139)    # tempestade laranja sexta 23/10: 678 (PR 342, RS 189, SC 132, MS 14, SP 1)
assert len(geo(56139)) == 678 and aviso[56139]["severidade"] == "Perigo" and aviso[56139]["inicio"].startswith("2026-10-23")
assert aviso[56124]["descricao"] == "Chuvas Intensas" and aviso[56124]["inicio"].startswith("2026-10-21")
CHUVA_N = [u for u in ufs_av(56124) if u in ("AM", "AC", "RO")]
assert CHUVA_N == ["AC", "AM", "RO"], CHUVA_N
assert len(geo(56135)) == 1489 and aviso[56135]["descricao"] == "Baixa Umidade"   # baixa umidade 21/10: 1.489 cidades
NORDESTE = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
estados = [
    {"id": "rs", "ini": GRANIZO1, "fim": ini("f2") + .3, "ufs": ["RS"], "cor": AZUL, "alfa": .4},
    {"id": "oeste", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .3},
    {"id": "gran", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["RS"], "cor": FRIO, "alfa": .18},
    {"id": "pr", "ini": ini("f4"), "fim": em("f4", "623") - .9, "ufs": ["PR"], "cor": LAR, "alfa": .6},
    {"id": "hoje", "ini": em("f4", "623") - 1.0, "fim": ini("f5") + .3, "ufs": HOJE, "cor": LAR, "alfa": .5},
    {"id": "calor", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["MT", "MS", "PI"], "cor": VERM, "alfa": .45},
    {"id": "chuvan", "ini": ini("f6"), "fim": em("f6", "Nordeste") + .3, "ufs": CHUVA_N, "cor": AZUL, "alfa": .45},
    {"id": "seco", "ini": em("f6", "Nordeste"), "fim": ini("f7") + .3, "ufs": NORDESTE, "cor": LAR, "alfa": .4},
    {"id": "sexta", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": SEXTA, "cor": [255, 90, 20], "alfa": .5},
    {"id": "dom", "ini": ini("f9"), "fim": em("f9", "Paraná") + .3, "ufs": ["RS", "SC", "PR", "SP"], "cor": AZUL, "alfa": .35},
    {"id": "dompr", "ini": em("f9", "Paraná"), "fim": ini("f10") + .3, "ufs": ["PR"], "cor": AZUL, "alfa": .6},
    {"id": "frio", "ini": ini("f10"), "fim": ini("f11") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .45},
]

pinos = [
    {"nome": "Horizontina (RS)", "sub": "granizo nesta manhã", "lon": -54.31, "lat": -27.63, "ini": em("f3", "Horizontina"), "fim": GRANIZO, "h": 200},
    {"nome": "Miraguaí (RS)", "sub": "granizo nesta manhã", "lon": -53.69, "lat": -27.50, "ini": em("f3", "Miraguaí"), "fim": GRANIZO, "h": 120},
    {"nome": "Palmitinho (RS)", "sub": "granizo nesta manhã", "lon": -53.56, "lat": -27.36, "ini": em("f3", "Palmitinho"), "fim": GRANIZO, "h": 40},
    {"nome": "Sul de MT · MS", "sub": "até 40 °C hoje", "lon": -54.64, "lat": -16.47, "ini": em("f5", "Mato"), "fim": ini("f6"), "h": 160},
    {"nome": "Teresina (PI)", "sub": "até 40 °C hoje", "lon": -42.80, "lat": -5.09, "ini": em("f5", "Teresina"), "fim": ini("f6"), "h": 160},
    *[{"nome": c, "sub": f"{fmm(MM[c])} mm em 7 dias (previsão)", "lon": CAPS[c][0], "lat": CAPS[c][1], "ini": t, "fim": ini("f9"), "h": h}
      for c, t, h in [("Curitiba", em("f8", "Curitiba"), 200), ("São Paulo", em("f8", "Paulo"), 200), ("Florianópolis", em("f8", "Paulo") + .8, 90)]],
    {"nome": "Serra Catarinense", "sub": "geada possível na terça, 27/10", "lon": -49.93, "lat": -28.29, "ini": GEAR, "fim": ini("f11"), "h": 200},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)   # número dito logo no começo da fala: o contador começa com a fala
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
H = em("f1", "calor") - .1   # o hero (data grande) fica até a palavra "calor"
TOTAL = em("f4", "623") - 1.1   # o painel do total do Brasil entra 1,1 s antes do número
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:104px">GRANIZO</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">no Sul e 40 °C no centro do país</div>'}]
paineis = [
    {"ini": H + .1, "fim": ini("f2"), "k": "HOJE · QUARTA, 21/10",
     "itens": [{"t": H + .1, "txt": "🧊 granizo de manhã no RS"},
               {"t": em("f1", "40") - .6, "txt": "🔥 calor de até 40 °C"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "DE ONDE VEM A CHUVA",
     "itens": [{"t": em("f2", "Paraguai"), "txt": "⛈️ Paraguai e Argentina"},
               {"t": em("f2", "oeste"), "txt": "➡️ oeste do RS, de SC e do PR"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": GRANIZO - .1, "k": "GRANIZO NESTA MANHÃ · RS",
     "itens": [{"t": em("f3", "Horizontina"), "txt": "🧊 Horizontina"},
               {"t": em("f3", "Miraguaí"), "txt": "🧊 Miraguaí"},
               {"t": em("f3", "Palmitinho"), "txt": "🧊 Palmitinho"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f4"), "fim": TOTAL, "k": "AVISO DE TEMPESTADE · HOJE",
     "contador": conta(323, "f4", "323", "#ff8c1a", "CIDADES NO PARANÁ"),
     "l": "INMET · quarta, 21/10", "borda": "rgba(255,140,26,.8)"},
    {"ini": TOTAL, "fim": ini("f5"), "k": "AVISO DE TEMPESTADE · HOJE",
     "contador": conta(623, "f4", "623", "#ff8c1a", "CIDADES NO TOTAL"),
     "l": "PR, RS, SC, MS e SP · INMET", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "MÁXIMA PREVISTA HOJE",
     "contador": conta(40, "f5", "40", "#ff2a1f", "°C"),
     "l": "entre MT e MS · perto de Teresina (PI)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "HOJE NO NORTE E NO NORDESTE",
     "itens": [{"t": em("f6", "Amazonas"), "txt": "🌧️ pancadas no AM, AC e RO"},
               {"t": em("f6", "Nordeste"), "txt": "☀️ Nordeste com tempo seco"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SEXTA, 23/10 · AVISO LARANJA",
     "contador": conta(678, "f7", "678", "#ff5a14", "CIDADES"),
     "l": "tempestade com granizo e vento · INMET", "borda": "rgba(255,90,20,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA EM 7 DIAS (PREVISÃO)",
     "contador": conta(100, "f8", "100", "#5ec8ff", "MM EM CURITIBA"),
     "l": f"São Paulo {fmm(MM['São Paulo'])} mm · Florianópolis {fmm(MM['Florianópolis'])} mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "DOMINGO, 25/10 · ELEIÇÃO",
     "itens": [{"t": em("f9", "instáveis"), "txt": "⛈️ Sul e São Paulo instáveis"},
               {"t": em("f9", "Paraná"), "txt": "🌧️ chuva forte no Paraná"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "PRÓXIMA SEMANA (PREVISÃO)",
     "itens": [{"t": em("f10", "cai"), "txt": "🧊 a temperatura cai no Sul"},
               {"t": GEAR, "txt": "❄️ geada na terça, 27/10"}],
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
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE} · <b>{MET}</b>"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b> · foto do granizo: ilustração"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INMET</b>, aviso de tempestade para 21/10 (623 municípios)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · <b>INMET</b>: chuvas intensas no AM, AC e RO, baixa umidade em 1.489 cidades"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>, aviso laranja de tempestade para 23/10 (678 municípios)"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>Open-Meteo</b>, chuva prevista de 21 a 27/10 nas capitais"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": f"<b>{MET}</b> · previsão · foto da geada: ilustração"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "chuvas": "#5ec8ff", "tempestade": "#ff8c1a", "alerta": "#ff8c1a", "intensas": "#ff8c1a",
         "seco": "#ff8c1a", "frio": "#96d2ff", "geada": "#96d2ff", "zero": "#96d2ff", "gear": "#96d2ff", "milimetros": "#5ec8ff",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "quente": "#ff2a1f", "fria": "#96d2ff", "severo": "#ff8c1a", "irregular": "#ff8c1a", "excesso": "#5ec8ff", "agua": "#5ec8ff", "granizo": "#96d2ff", "gelo": "#96d2ff", "trovoada": "#ff8c1a", "tempestade": "#ff8c1a", "laranja": "#ff8c1a", "vento": "#ff8c1a", "instaveis": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "parana", "paraguai", "argentina", "oeste", "gaucho", "catarinense", "horizontina", "miraguai", "palmitinho", "mato", "grosso",
         "teresina", "piaui", "amazonas", "acre", "rondonia", "nordeste", "curitiba", "sao", "paulo", "serra", "inemaclub", "onde"}
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
