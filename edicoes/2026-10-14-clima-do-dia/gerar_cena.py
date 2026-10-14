#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 14/10/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS)
e dos avisos do INMET (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png), colunas 3D da chuva medida em 7 dias nas estações do boletim,
infravermelho do GOES-19 na chuva de hoje, alerta laranja de SP e o total do Brasil, fotos de granizo e geada (ilustração).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "14/10/2026"
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
OESTE = {"lon": -53.4, "lat": -26.2, "zoom": 6.0}    # f1/f2: colunas 3D no sudoeste do PR e oeste de SC
MSSP = {"lon": -51.8, "lat": -22.6, "zoom": 4.9}     # f3: do MS para o oeste de SP e o norte do PR
PRRIB = {"lon": -49.8, "lat": -24.4, "zoom": 5.7}    # f4: centro-norte do PR e Vale do Ribeira
SPE = {"lon": -48.6, "lat": -22.3, "zoom": 5.3}      # f5: estado de São Paulo
BRA = {"lon": -50.0, "lat": -17.5, "zoom": 3.95}     # f5: o Brasil do alerta
GSP = {"lon": -47.0, "lat": -23.9, "zoom": 6.6}      # f6: Grande SP, Baixada Santista, Vale do Ribeira
NE = {"lon": -41.5, "lat": -8.0, "zoom": 4.6}        # f7: Nordeste seco, Piauí
SUL = {"lon": -51.0, "lat": -27.8, "zoom": 5.3}      # f8: frio no Sul, Serra Catarinense
CSUL = {"lon": -49.5, "lat": -21.0, "zoom": 4.35}    # f9: ar frio até SP, Goiânia e Brasília
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
CAP = em("f1", "Capanema")
BRASIL = em("f5", "Brasil")
camera = [
    K(0, BR), K(CAPA, BR), K(CAP - .3, {**BR, "lon": -52.5, "lat": -20.0, "zoom": 4.2}, 10, 0),
    K(CAP + 1.2, OESTE, 52, -22), K(fim("f1") - .2, {**OESTE, "zoom": 6.05}, 55, -6), K(fim("f2") - .2, {**OESTE, "zoom": 6.15}, 57, 18),
    K(ini("f3") + 1.0, MSSP, 0, 0), K(fim("f3") - .2, {**MSSP, "lon": -51.4}, 0, 0),
    K(ini("f4") + 1.0, PRRIB, 20, -6), K(fim("f4") - .2, {**PRRIB, "lon": -49.5}, 24, 4),
    K(ini("f5") + 1.0, SPE, 10, 0), K(BRASIL - .2, {**SPE, "zoom": 5.2}, 10, 0), K(BRASIL + 1.2, BRA, 0, 0), K(fim("f5") - .2, {**BRA, "zoom": 3.9}, 0, 0),
    K(ini("f6") + 1.0, GSP, 25, -8), K(fim("f6") - .2, {**GSP, "lon": -46.8}, 28, 4),
    K(ini("f7") + 1.0, NE, 6, -2), K(fim("f7") - .2, {**NE, "lon": -41.8}, 8, 2),
    K(ini("f8") + 1.0, SUL, 30, -8), K(fim("f8") - .2, {**SUL, "zoom": 5.4}, 34, 4),
    K(ini("f9") + 1.0, {**SUL, "lon": -50.2, "lat": -28.0, "zoom": 5.7}, 30, 0), K(em("f9", "frio") + 1.2, CSUL, 5, 0), K(fim("f9") - .2, {**CSUL, "zoom": 4.3}, 5, 2),
    K(ini("f10") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na chuva de hoje (f3)
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
              "ini": ini("f3") - .3, "fim": ini("f4") + .4, "dur": fim("f3") - ini("f3") + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

# ---------------------------------------------------------------- colunas 3D: chuva MEDIDA em 7 dias nas estações (boletim 14/10, 01:11–02:20)
EST = [("Capanema", "PR", -53.81, -25.67, 463), ("Santa Helena", "PR", -54.33, -24.86, 403), ("Chopinzinho", "PR", -52.52, -25.85, 334),
       ("Campo Erê", "SC", -53.08, -26.40, 330), ("Candói", "PR", -52.04, -25.57, 292), ("Guaraciaba", "SC", -53.52, -26.60, 281),
       ("Ijuí", "RS", -53.91, -28.39, 124), ("Santo Ângelo", "RS", -54.26, -28.30, 111)]
cor_mm = lambda mm: [150, 215, 255] if mm < 150 else [60, 150, 255] if mm < 350 else [120, 90, 255]
col = [{"id": i, "p": [lon, lat], "v": mm, "cor": cor_mm(mm)} for i, (_, _, lon, lat, mm) in enumerate(EST)]
ordem = {c["id"]: i * .18 for i, c in enumerate(col)}
colunas = [{"id": "chuva7d", "ini": CAP - .2, "fim": ini("f3") + .5, "dados": col, "raio": 20000, "escala": 1100, "ordem": ordem, "varredura": 1}]

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, granizo e geada
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": em("f6", "risco") - .1, "fim": ini("f7") + .3, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/geada.png", "ini": em("f8", "geada") - .1, "fim": ini("f9") + .6, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
HOJE = ufs_av(56068)     # tempestade laranja 14/10: 1.662 (SP 645, MG 406, PR 328, RJ 92, MS 79, MT 56)
assert len(geo(56068)) == 1662, len(geo(56068))
assert sum(c[:2] == "35" for c in geo(56068)) == 645
assert aviso[56068]["severidade"] == "Perigo" and aviso[56068]["descricao"] == "Tempestade"
NORDESTE = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
estados = [
    {"id": "oeste", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["PR", "SC"], "cor": AZUL, "alfa": .3},
    {"id": "f4pr", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["PR"], "cor": AZUL, "alfa": .4},
    {"id": "sp", "ini": ini("f5"), "fim": BRASIL + .3, "ufs": ["SP"], "cor": LAR, "alfa": .6},
    {"id": "hoje", "ini": BRASIL, "fim": ini("f6") + .3, "ufs": HOJE, "cor": LAR, "alfa": .55},
    {"id": "amanha", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["SP"], "cor": LAR, "alfa": .4},
    {"id": "seco", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": NORDESTE, "cor": [255, 90, 20], "alfa": .3},
    {"id": "pi", "ini": em("f7", "Piauí") - .2, "fim": ini("f8") + .3, "ufs": ["PI"], "cor": VERM, "alfa": .45},
    {"id": "frio", "ini": ini("f8"), "fim": em("f9", "frio") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .45},
    {"id": "friocs", "ini": em("f9", "frio"), "fim": ini("f10") + .3, "ufs": ["RS", "SC", "PR", "SP", "MS", "MG", "GO", "DF"], "cor": FRIO, "alfa": .4},
]

pinos = [
    {"nome": "Capanema (PR)", "sub": "463 mm em 7 dias", "lon": -53.81, "lat": -25.67, "ini": em("f1", "463") - .2, "fim": ini("f2"), "h": 280},
    {"nome": "Santa Helena (PR)", "sub": "403 mm em 7 dias", "lon": -54.33, "lat": -24.86, "ini": em("f2", "403") - .2, "fim": em("f2", "sudoeste"), "h": 260},
    {"nome": "Campo Erê (SC)", "sub": "330 mm em 7 dias", "lon": -53.08, "lat": -26.40, "ini": em("f2", "330") - .2, "fim": ini("f3"), "h": 230},
    {"nome": "Centro-norte do PR", "sub": "40 a 80 mm hoje", "lon": -51.68, "lat": -24.25, "ini": em("f4", "centro-norte"), "fim": ini("f5"), "h": 170},
    {"nome": "Vale do Ribeira", "sub": "40 a 80 mm hoje", "lon": -47.84, "lat": -24.49, "ini": em("f4", "Ribeira"), "fim": ini("f5"), "h": 200},
    {"nome": "Grande São Paulo", "sub": "chuva forte amanhã", "lon": -46.63, "lat": -23.55, "ini": em("f6", "Grande"), "fim": em("f6", "risco"), "h": 200},
    {"nome": "Baixada Santista", "sub": "chuva forte amanhã", "lon": -46.33, "lat": -23.96, "ini": em("f6", "Baixada"), "fim": em("f6", "risco"), "h": 150},
    {"nome": "Vale do Ribeira", "sub": "atenção amanhã", "lon": -47.84, "lat": -24.49, "ini": em("f6", "Ribeira"), "fim": em("f6", "risco"), "h": 110},
    {"nome": "Piauí", "sub": "perto de 40 °C", "lon": -42.80, "lat": -5.09, "ini": em("f7", "Piauí"), "fim": ini("f8"), "h": 170},
    {"nome": "Serra Catarinense", "sub": "geada, perto de 0 °C no domingo", "lon": -49.93, "lat": -28.29, "ini": em("f8", "sábado"), "fim": em("f8", "geada"), "h": 170},
    {"nome": "Alto da serra (SC)", "sub": "pode ficar negativo na segunda", "lon": -49.93, "lat": -28.29, "ini": em("f9", "negativo") - .2, "fim": em("f9", "frio") + .3, "h": 170},
    {"nome": "Goiânia", "sub": "ar frio", "lon": -49.25, "lat": -16.68, "ini": em("f9", "Goiânia"), "fim": ini("f10"), "h": 150},
    {"nome": "Brasília", "sub": "ar frio", "lon": -47.88, "lat": -15.79, "ini": em("f9", "Brasília"), "fim": ini("f10"), "h": 230},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
conta = lambda ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0: {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra) - lead, "dur": lead, "cor": cor, "unid": unid}
H = em("f1", "463") - LEAD - .1   # o hero (data grande) fica até o contador do 463 começar
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:112px">463 MM</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">de chuva em 7 dias no Paraná</div>'}]
D_BR = max(BRASIL + .4, em("f5", "1.662") - LEAD)   # o total do Brasil sobe de 645 a 1.662 até a palavra
paineis = [
    {"ini": H + .1, "fim": ini("f2"), "k": "PARANÁ · CHUVA EM 7 DIAS",
     "contador": conta(463, "f1", "463", "#5ec8ff", "MM"),
     "l": "Capanema (PR) · medido nas estações · cada coluna = chuva de 7 dias", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "SUDOESTE DO PR E OESTE DE SC",
     "itens": [{"t": em("f2", "403") - .3, "txt": "🌧️ Santa Helena (PR): 403 mm"},
               {"t": em("f2", "330") - .3, "txt": "🌧️ Campo Erê (SC): 330 mm"},
               {"t": em("f2", "sudoeste"), "txt": "⚠️ o sudoeste do Paraná sofre com tanta chuva"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "HOJE · CHUVA COM TROVOADA",
     "itens": [{"t": em("f3", "Mato"), "txt": "⛈️ Mato Grosso do Sul"},
               {"t": em("f3", "oeste"), "txt": "➡️ oeste de São Paulo"},
               {"t": em("f3", "norte"), "txt": "➡️ norte do Paraná"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE · CENTRO-NORTE DO PR E VALE DO RIBEIRA",
     "contador": conta(80, "f4", "80", "#5ec8ff", "MM"),
     "l": "de 40 a 80 mm em alguns locais", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": BRASIL, "k": "ALERTA LARANJA DE TEMPESTADE · SP",
     "contador": conta(645, "f5", "645", "#ff8c1a", "CIDADES EM SP"),
     "l": "todas as cidades do estado · INMET, 14/10", "borda": "rgba(255,140,26,.7)"},
    {"ini": BRASIL, "fim": ini("f6"), "k": "BRASIL INTEIRO · HOJE",
     "contador": {"de": 645, "ate": 1662, "dec": 0, "ini": D_BR, "dur": max(.4, em("f5", "1.662") - D_BR), "cor": "#ff8c1a", "unid": "CIDADES NO BRASIL"},
     "l": "MG 406 · PR 328 · RJ 92 · MS 79 · MT 56 · chuva, vento e granizo", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "AMANHÃ · QUINTA, 15/10 (PREVISÃO)",
     "itens": [{"t": em("f6", "Grande"), "txt": "🌧️ chuva forte na Grande São Paulo"},
               {"t": em("f6", "Baixada"), "txt": "🌊 Baixada Santista e Vale do Ribeira"},
               {"t": em("f6", "granizo"), "txt": "⛈️ risco de granizo e vento"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "NORDESTE SECO · CALOR NO PIAUÍ",
     "contador": conta(40, "f7", "40", "#ff2a1f", "°C"),
     "l": "perto de 40 °C · Teresina: 39,5 °C previstos hoje (Open-Meteo)", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "FRIO NO SUL · SÁBADO (PREVISÃO)",
     "contador": conta(5, "f8", "5", "#96d2ff", "°C", de=15, lead=em("f8", "5") - ini("f8") - .2),   # a temperatura cai durante a fala até o 5
     "l": "de 5 a 7 °C · domingo: geada e perto de 0 °C na Serra Catarinense", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "SEGUNDA · AR FRIO (PREVISÃO)",
     "itens": [{"t": em("f9", "negativo"), "txt": "❄️ abaixo de zero no alto da serra (SC)"},
               {"t": em("f9", "Paulo"), "txt": "🌬️ ar frio em São Paulo"},
               {"t": em("f9", "Goiânia"), "txt": "🌬️ até Goiânia e Brasília"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "onde"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f10", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
     "borda": "rgba(250,204,21,.8)"},
]
for a, b in zip(paineis, paineis[1:]):
    assert a["fim"] <= b["ini"] + 1e-6, (a["k"], b["k"])
for a in paineis:
    if a.get("contador"):
        c = a["contador"]
        assert a["ini"] - .01 <= c["ini"] and c["ini"] + c["dur"] <= a["fim"], ("contador fora do painel", a["k"])

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": CAP, "html": f"<b>{MET}</b>"},
    {"ini": CAP, "fim": ini("f3"), "html": f"Chuva medida em 7 dias nas estações: <b>{MET}</b> · altura da coluna = milímetros"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE} · <b>{MET}</b>"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INMET</b>, aviso laranja de tempestade para 14/10 (1.662 municípios): 30 a 60 mm/h, vento de 60 a 100 km/h e granizo"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · foto do granizo: ilustração"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b> · Teresina: <b>Open-Meteo</b>, máxima prevista para 14/10"},
    {"ini": ini("f8"), "fim": ini("f10"), "html": f"<b>{MET}</b> · previsão de temperatura até 20/10 · foto da geada: ilustração"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "trovoada": "#ff8c1a", "tempestade": "#ff8c1a", "alerta": "#ff8c1a", "laranja": "#ff8c1a",
         "granizo": "#ff8c1a", "vento": "#5ec8ff", "forte": "#ff8c1a", "seco": "#ff8c1a", "frio": "#96d2ff", "geada": "#96d2ff",
         "zero": "#96d2ff", "negativo": "#96d2ff", "graus": "#ff2a1f", "sofrendo": "#ff8c1a", "comenta": AM,
         "inteligencia": AM, "artificial": AM}
LUGAR = {"capanema", "parana", "santa", "helena", "campo", "ere", "catarina", "sudoeste", "mato", "grosso", "sul", "oeste", "sao", "paulo",
         "norte", "centronorte", "vale", "ribeira", "grande", "baixada", "santista", "nordeste", "piaui", "serra", "catarinense",
         "goiania", "brasilia", "brasil", "inemaclub", "onde"}
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
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"tempestade hoje {HOJE}")
