#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 20/10/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS),
dos avisos do INMET e da chuva prevista para 7 dias (Open-Meteo, pesquisa/bruto/previsao7d.json).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, El Niño mais forte já registrado), anomalia real da temperatura
do mar (GHRSST MUR via NASA GIBS, 18/10/2026) no Pacífico e na Bacia do Prata, infravermelho do GOES-19 no Sul encharcado,
colunas 3D da chuva prevista até 3/12 (Chapecó, Caçador, norte gaúcho), seca irregular no centro-norte, frio no centro-sul, foto da geada (ilustração).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "20/10/2026"
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
PAC = {"lon": -100.0, "lat": -10.0, "zoom": 2.55}      # f1: Pacífico equatorial + América do Sul
N34 = {"lon": -138.0, "lat": -4.0, "zoom": 3.1}        # f2: centro do Pacífico (Niño 3.4)
PRATA = {"lon": -53.0, "lat": -35.5, "zoom": 4.4}      # f3: água fria na Bacia do Prata
SUL = {"lon": -51.0, "lat": -26.5, "zoom": 4.9}        # f4: Sul encharcado, Paraná
COL = {"lon": -52.0, "lat": -27.6, "zoom": 6.0}        # f5: colunas 3D Chapecó, Caçador, norte gaúcho
SECO = {"lon": -49.5, "lat": -9.5, "zoom": 4.0}        # f6: MT, TO, PA, norte de GO e Matopiba
NORTE = {"lon": -54.0, "lat": -8.0, "zoom": 3.75}      # f7: calor no centro e no norte
CSUL = {"lon": -50.5, "lat": -23.0, "zoom": 4.3}       # f8: centro-sul abaixo da média
SERRA = {"lon": -50.5, "lat": -27.5, "zoom": 5.6}      # f9: geada no Sul
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
PACT = em("f1", "Pacífico")
camera = [
    K(0, BR), K(CAPA, BR), K(PACT - .3, {**PAC, "lon": -80.0, "zoom": 3.0}, 0, 0),
    K(PACT + 1.3, PAC, 0, 0), K(fim("f1") - .2, {**PAC, "zoom": 2.6}, 0, 0),
    K(ini("f2") + 1.3, N34, 20, -6), K(fim("f2") - .2, {**N34, "lon": -134.0}, 25, 6),
    K(ini("f3") + 1.3, PRATA, 15, -6), K(fim("f3") - .2, {**PRATA, "zoom": 4.5}, 20, 4),
    K(ini("f4") + 1.0, SUL, 0, 0), K(fim("f4") - .2, {**SUL, "zoom": 5.0}, 4, 0),
    K(ini("f5") + 1.0, COL, 55, -20), K(em("f5", "Caçador"), {**COL, "zoom": 6.1}, 56, 0), K(fim("f5") - .2, {**COL, "zoom": 6.15}, 56, 18),
    K(ini("f6") + 1.0, SECO, 0, 0), K(fim("f6") - .2, {**SECO, "zoom": 4.05}, 4, 0),
    K(ini("f7") + 1.0, NORTE, 0, 0), K(fim("f7") - .2, {**NORTE, "zoom": 3.8}, 0, 0),
    K(ini("f8") + 1.0, CSUL, 6, 0), K(fim("f8") - .2, {**CSUL, "zoom": 4.35}, 8, 0),
    K(ini("f9") + 1.0, SERRA, 35, -10), K(fim("f9") - .2, {**SERRA, "zoom": 5.7}, 40, 6),
    K(ini("f10") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) no Sul encharcado (f4)
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
              "ini": ini("f4") - .3, "fim": ini("f5") + .4, "dur": fim("f4") - ini("f4") + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

# anomalia da temperatura do mar (GHRSST MUR via NASA GIBS, 18/10/2026, recorte -180,-60,-20,32, EPSG:3857)
ANOM_DIA = (AQUI / "sat/web/anomalia-data.txt").read_text().strip()
assert ANOM_DIA == "2026-10-18", ANOM_DIA
ANOM = {"src": "sat/web/anomalia.png", "bbox": [-180, -60, -20, 32], "alfa": .85}
imagens = [{**ANOM, "ini": PACT - .3, "fim": ini("f4") + .4, "fade": .8}]

# ---------------------------------------------------------------- colunas 3D: chuva PREVISTA até 3/12 (boletim de meteorologia)
CHUVA3D = [("Chapecó (SC)", -52.62, -27.10, 500, "mais de 500 mm até 3/12"),
           ("Caçador (SC)", -51.01, -26.78, 480, "quase 500 mm até 3/12"),
           ("Passo Fundo (RS)", -52.41, -28.26, 450, "norte gaúcho: até 450 mm")]
col = [{"id": i, "p": [lon, lat], "v": v, "cor": [60, 150, 255] if v >= 490 else [120, 190, 255]} for i, (_, lon, lat, v, _) in enumerate(CHUVA3D)]
ordem = {c["id"]: i * .2 for i, c in enumerate(col)}
colunas = [{"id": "chuva3d", "ini": ini("f5") + .2, "fim": ini("f6") + .2, "dados": col, "raio": 16000, "escala": 700, "ordem": ordem, "varredura": 1}]

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e geada
GEAR = em("f9", "gear")
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/geada.png", "ini": GEAR - .1, "fim": ini("f10") + .3, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- estados
SECO_UF = ["MT", "TO", "PA", "GO", "MA", "PI", "BA"]
CALOR_UF = ["AC", "AM", "RO", "RR", "PA", "AP", "TO", "MT", "GO", "DF", "MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
CSUL_UF = ["RS", "SC", "PR", "SP", "MS", "MG", "RJ", "ES"]
estados = [
    {"id": "fria", "ini": em("f3", "Sul"), "fim": ini("f4") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .4},
    {"id": "sul", "ini": ini("f4"), "fim": em("f4", "Paraná") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .35},
    {"id": "pr", "ini": em("f4", "Paraná"), "fim": ini("f5") + .3, "ufs": ["PR"], "cor": AZUL, "alfa": .55},
    {"id": "sul5", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["SC", "RS", "PR"], "cor": AZUL, "alfa": .3},
    {"id": "seco", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": SECO_UF, "cor": LAR, "alfa": .45},
    {"id": "calor", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": CALOR_UF, "cor": VERM, "alfa": .4},
    {"id": "csul", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": CSUL_UF, "cor": FRIO, "alfa": .4},
    {"id": "geada", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .45},
]

pinos = [
    {"nome": "Costa do Peru · Niño 1+2", "sub": "+4,4 °C acima do normal", "lon": -84.0, "lat": -5.0, "ini": em("f1", "4") - .2, "fim": ini("f2"), "h": 200},
    {"nome": "Centro do Pacífico · Niño 3.4", "sub": "+2,8 °C acima da média", "lon": -145.0, "lat": 0.0, "ini": em("f2", "2,8") - .2, "fim": ini("f3"), "h": 200},
    {"nome": "Bacia do Prata", "sub": "mancha de água fria", "lon": -54.5, "lat": -37.5, "ini": em("f3", "Prata") - .2, "fim": ini("f4"), "h": 180},
    {"nome": "Paraná", "sub": "outubro encharcado", "lon": -51.5, "lat": -24.6, "ini": em("f4", "Paraná"), "fim": ini("f5"), "h": 180},
    *[{"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": em("f5", pal), "fim": ini("f6"), "h": 120}
      for (nome, lon, lat, _, sub), pal in zip(CHUVA3D, ["Chapecó", "Caçador", "gaúcho"])],
    {"nome": "Matopiba", "sub": "chuva irregular", "lon": -46.0, "lat": -9.5, "ini": em("f6", "Matopiba"), "fim": ini("f7"), "h": 160},
    {"nome": "Serra Catarinense", "sub": "geada possível (previsão)", "lon": -49.93, "lat": -28.29, "ini": em("f9", "gear"), "fim": ini("f10"), "h": 200},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)   # número dito logo no começo da fala: o contador começa com a fala
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
H = PACT - .1   # o hero (data grande) fica até a câmera chegar ao Pacífico
hero = [{"ini": CAPA - .2, "fim": H,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:112px">EL NIÑO</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">o mais forte já registrado</div>'}]
paineis = [
    {"ini": H + .1, "fim": ini("f2"), "k": "EL NIÑO · COSTA DO PERU",
     "contador": conta(4.4, "f1", "4", "#ff2a1f", "°C ACIMA DO NORMAL", dec=1, lead=max(.6, min(LEAD, em("f1", "4") - H - .2))),
     "l": "Niño 1+2 · o mais forte já registrado", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "CENTRO DO PACÍFICO · NIÑO 3.4",
     "contador": conta(2.8, "f2", "2,8", "#ff2a1f", "°C ACIMA DA MÉDIA", dec=1),
     "l": "forte até o inverno de 2027 (previsão)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "POR QUE ESFRIA NO SUL",
     "itens": [{"t": em("f3", "fria"), "txt": "🌊 água fria na Bacia do Prata"},
               {"t": em("f3", "entrada"), "txt": "🌬️ o ar frio entra no Sul"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "SUL · ATÉ O COMEÇO DE DEZEMBRO",
     "itens": [{"t": em("f4", "excesso"), "txt": "🌧️ excesso de chuva"},
               {"t": em("f4", "Paraná"), "txt": "💧 Paraná encharcado em outubro"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "CHUVA ATÉ 3/12 (PREVISÃO)",
     "contador": conta(500, "f5", "500", "#5ec8ff", "MM EM CHAPECÓ (SC)"),
     "l": "Caçador quase 500 mm · norte do RS até 450 mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "CHUVA ABAIXO DA MÉDIA",
     "itens": [{"t": em("f6", "Mato"), "txt": "🟠 Mato Grosso e Tocantins"},
               {"t": em("f6", "Pará"), "txt": "🟠 Pará e norte de Goiás"},
               {"t": em("f6", "Matopiba"), "txt": "🟠 Matopiba: chuva irregular"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "CENTRO E NORTE DO PAÍS",
     "itens": [{"t": em("f7", "calor"), "txt": "🔥 o calor predomina"},
               {"t": em("f7", "acima"), "txt": "🌡️ temperatura acima da média"}],
     "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CENTRO-SUL · ATÉ DEZEMBRO",
     "itens": [{"t": em("f8", "abaixo"), "txt": "🧊 temperatura abaixo da média"},
               {"t": em("f8", "onda"), "txt": "🚫 sem onda de calor de MT e SP para baixo"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "PRÓXIMAS SEMANAS (PREVISÃO)",
     "itens": [{"t": em("f9", "gear"), "txt": "❄️ geada na semana que vem e em novembro"},
               {"t": em("f9", "severo"), "txt": "⛈️ tempo severo nas mudanças"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f10", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
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
    {"ini": CAPA, "fim": ini("f3"), "html": f"<b>{MET}</b> · anomalia da temperatura do mar em 18/10: GHRSST MUR via <b>NASA</b> GIBS"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b> · anomalia do mar em 18/10: GHRSST MUR via <b>NASA</b> GIBS"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE} · <b>{MET}</b>"},
    {"ini": ini("f5"), "fim": ini("f9"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · previsão · foto da geada: ilustração"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "chuvas": "#5ec8ff", "tempestade": "#ff8c1a", "alerta": "#ff8c1a", "intensas": "#ff8c1a",
         "seco": "#ff8c1a", "frio": "#96d2ff", "geada": "#96d2ff", "zero": "#96d2ff", "gear": "#96d2ff", "milimetros": "#5ec8ff",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "quente": "#ff2a1f", "fria": "#96d2ff", "severo": "#ff8c1a", "irregular": "#ff8c1a", "excesso": "#5ec8ff", "agua": "#5ec8ff", "nino": "#ff2a1f", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"pacifico", "oceano", "bacia", "prata", "sul", "parana", "chapeco", "cacador", "norte", "gaucho", "mato", "grosso", "tocantins",
         "para", "goias", "matopiba", "centrosul", "sao", "paulo", "inemaclub", "regiao"}
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
     "marca": "INEMA · CLIMA DO DIA", "selo": DATA[:5] + " · NOAA · NASA",
     "camera": camera, "sat": SAT, "imagens": imagens, "colunas": colunas, "telas": telas, "estados": estados, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"anomalia do mar {ANOM_DIA} · colunas {[(c[0], c[3]) for c in CHUVA3D]}")
