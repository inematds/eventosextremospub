#!/usr/bin/env python3
"""Situação dos Eventos Extremos de 05/11/2026 (impactos de 04/11): dois tornados no oeste de SC (Chapecó ~10h30 e
Xanxerê ~10h48), Maringá (PR) e o granizo na Grande Curitiba, balanço da Defesa Civil do PR, como nasce um tornado
(3 ilustrações do Codex) e o alerta para sábado. Fatos e fontes: pesquisa/FATOS.md.
Grava cena.js (motor/mapa.html) e clipes_tempo.json (onde entra cada clipe real; montar_clipes.sh põe por cima).
Render: GEO=geo-br.js motor/montar.sh <esta pasta> → video.mp4, depois montar_clipes.sh video.mp4 810
Com avatar: gerar_cena.py --canto (avatar/tempos.json) → GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh → montar_clipes.sh 880"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "05/11/2026"
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / (os.environ.get("TEMPOS") or ("avatar/tempos.json" if AVATAR else "tempos.json"))).read_text())


def n(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


def roteiro(t, texto):
    """troca as palavras ouvidas pelo Whisper pelas do roteiro (campo legenda), mantendo os tempos."""
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
        if n(palavra) == n(p["w"]) or (len(n(palavra)) > 3 and n(palavra) in n(p["w"])):
            achou += 1
            if achou == k:
                return p["t"]
    raise KeyError(f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in FALA[fid]["palavras"]))


ini = lambda fid: FALA[fid]["ini"]
fim = lambda fid: FALA[fid]["fim"]
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
LAR, AMA, VERM, AZUL, FRIO = [255, 140, 26], [250, 204, 21], [255, 42, 31], [60, 150, 255], [150, 210, 255]

# ---------------------------------------------------------------- clipes reais (montar_clipes.sh põe na janela do meio)
CL = {c["nome"]: c for c in json.loads((AQUI / "clipes.json").read_text())}
clipes = []
def clipe(nome, a, b):
    assert b - a >= 1.2, (nome, a, b)
    assert b - a <= CL[nome]["dur"] + .01, (nome, round(b - a, 2), "maior que o clipe")
    clipes.append({"nome": nome, "ini": round(a, 3), "fim": round(b, 3)})

CAPA = 2.0
ONTEM = em("f1", "Ontem")
clipe("c01-ceu-chapeco", ONTEM - .1, em("f1", "atingiram"))
clipe("c02-camera-rua", em("f1", "atingiram"), fim("f1"))
RAJ = em("f2", "rajadas")
clipe("c03-destrocos-ar", RAJ - .2, fim("f2"))
AERO = em("f3", "aeroporto")
ARR = em("f3", "arrancou")
FECH = em("f3", "fechou")
clipe("c05-aeroporto", ini("f3") + .1, ARR)
clipe("c06-telhados", ARR, FECH - .1)
clipe("c04-para-brisa", FECH - .1, fim("f4") if False else fim("f3"))
FOR = em("f4", "Foram")
BOMB = em("f4", "bombeiros")
clipe("c07-casas-lona", ini("f4"), FOR - .1)
clipe("c08-outdoor-casa", FOR - .1, BOMB - .1)
clipe("c09-rua-destrocos", BOMB - .1, fim("f4"))
XAN = em("f5", "Xanxerê")
MAIS = em("f5", "Mais")
REC = em("f5", "atingidas")  # avatar fala mais rápido: o clipe da carreta entra uma palavra antes
clipe("c10-xanxere-aereo", em("f5", "radar") - .1, MAIS - .1)
clipe("c11-xanxere-galpao", MAIS - .1, REC - .1)
clipe("c12-xanxere-carreta", REC - .1, fim("f5"))
DEST = em("f6", "destruiu")
GRAN = em("f6", "granizo")
MGA0 = em("f6", "Maringá") + .3
MGAM = (MGA0 + GRAN - .2) / 2
clipe("c13-maringa-aereo", MGA0, MGAM)
clipe("c14-maringa-galpao", MGAM, GRAN - .2)
(AQUI / ("clipes_tempo-canto.json" if CANTO else "clipes_tempo.json")).write_text(json.dumps(clipes, ensure_ascii=False, indent=1))

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
OSC = {"lon": -52.6, "lat": -27.0, "zoom": 7.6}       # oeste de SC
CHA = {"lon": -52.62, "lat": -27.10, "zoom": 9.0}     # Chapecó
XANC = {"lon": -52.40, "lat": -26.88, "zoom": 9.0}    # Xanxerê
MGA = {"lon": -51.94, "lat": -23.42, "zoom": 8.2}     # Maringá
CWB = {"lon": -49.27, "lat": -25.43, "zoom": 8.2}     # Curitiba
PR = {"lon": -51.5, "lat": -24.6, "zoom": 6.0}
SUL = {"lon": -52.0, "lat": -28.0, "zoom": 5.0}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 2.0, OSC), K(fim("f1") - .2, {**OSC, "zoom": 7.7}),
    K(ini("f2") + .8, CHA, 30, -8), K(fim("f2") - .2, {**CHA, "zoom": 9.2}, 35, 4),
    K(ini("f3") + .6, {**CHA, "lon": -52.70, "zoom": 8.6}, 0, 0), K(fim("f4") - .2, {**CHA, "zoom": 8.8}, 0, 0),
    K(ini("f5") + .8, XANC, 30, -6), K(fim("f5") - .2, {**XANC, "zoom": 9.1}, 32, 4),
    K(ini("f6") + .8, MGA, 0, 0), K(GRAN - .3, {**MGA, "zoom": 8.3}, 0, 0), K(GRAN + .9, CWB, 0, 0), K(fim("f6") - .2, {**CWB, "zoom": 8.3}, 0, 0),
    K(ini("f7") + 1.0, PR, 0, 0), K(fim("f7") - .2, {**PR, "zoom": 6.1}, 0, 0),
    K(ini("f11") + 1.0, SUL, 0, 0), K(fim("f11") - .2, {**SUL, "zoom": 5.1}, 0, 0),
    K(ini("f12") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: GOES-19 infravermelho de 04/11, 10h às 14h (a tempestade dos tornados)
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
brt = lambda z: (lambda d: f"{DIAS[d.weekday()]} {d:%Hh%M}")(datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3))
IRQ = list(range(9))
assert TS[0] == "2026-11-04T13:00:00Z", TS[0]
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in IRQ], "tempos": [brt(TS[i]) for i in IRQ],
              "ini": CAPA, "fim": ONTEM + .3, "dur": ONTEM - CAPA + .3, "alfa": .9, "rotulo": "GOES-19 · 04/11, 10h às 14h"}}

# ---------------------------------------------------------------- telas cheias: capa e "como nasce um tornado" (Codex, ilustração)
telas = [{"src": "capa-dia/abertura-916.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/explica1.png", "ini": ini("f8") - .1, "fim": ini("f9") + .3, "fade": .3, "zoom": .06, "selo": "ilustração"},
         {"src": "capa-dia/explica2.png", "ini": ini("f9"), "fim": ini("f10") + .3, "fade": .3, "zoom": .06, "selo": "ilustração"},
         {"src": "capa-dia/explica3.png", "ini": ini("f10"), "fim": fim("f10") + .3, "fade": .3, "zoom": .06, "selo": "ilustração"}]

estados = [
    {"id": "sc", "ini": CAPA + .5, "fim": ini("f6") + .3, "ufs": ["SC"], "cor": VERM, "alfa": .22},
    {"id": "pr", "ini": ini("f6"), "fim": ini("f8") + .3, "ufs": ["PR"], "cor": LAR, "alfa": .35},
    {"id": "sul", "ini": ini("f11"), "fim": ini("f12") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .3},
]
pinos = [
    {"nome": "Chapecó", "sub": "tornado ~10h30 de 04/11", "lon": -52.618, "lat": -27.100, "ini": CAPA + 1.0, "fim": ini("f5"), "h": 220},
    {"nome": "Xanxerê", "sub": "2º tornado ~10h48", "lon": -52.404, "lat": -26.877, "ini": CAPA + 1.4, "fim": ini("f6"), "h": 160},
    {"nome": "Guatambu", "sub": "o tornado passou aqui", "lon": -52.789, "lat": -27.133, "ini": em("f3", "Guatambu") - .2, "fim": ini("f4"), "h": 120},
    {"nome": "Maringá", "sub": "tornado · parque industrial destruído", "lon": -51.938, "lat": -23.420, "ini": ini("f6") + .4, "fim": ini("f7"), "h": 200},
    {"nome": "Grande Curitiba", "sub": "granizo em 04/11", "lon": -49.273, "lat": -25.428, "ini": GRAN - .1, "fim": ini("f7"), "h": 200},
    {"nome": "Sul", "sub": "nova frente fria no sábado 07/11", "lon": -53.0, "lat": -29.5, "ini": em("f11", "sábado"), "fim": ini("f12"), "h": 200},
]

# ---------------------------------------------------------------- painéis e contadores (chegam ao número quando a palavra é dita)
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
hero = [{"ini": CAPA - .2, "fim": ONTEM - .1,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">SITUAÇÃO DOS EVENTOS EXTREMOS</div>'
                 '<div class="t1" style="font-size:96px">2 TORNADOS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">em 18 minutos no oeste de SC</div>'}]
P2 = em("f4", "2.478") - 1.1
P3 = em("f4", "400") - 1.1
P7 = em("f7", "2.695") - 1.1
X200 = em("f5", "200") - 1.1
paineis = [
    {"ini": ONTEM - .1, "fim": ini("f2"), "k": "OESTE DE SC · QUARTA 04/11",
     "itens": [{"t": ONTEM, "txt": "🌪️ Chapecó · ~10h30"}, {"t": em("f1", "18"), "txt": "🌪️ Xanxerê · ~10h48"}], "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "CHAPECÓ · TORNADO CONFIRMADO",
     "contador": conta(126, "f2", "126", "#ff2a1f", "KM/H · RAJADAS", de=40),
     "l": "Inmet · confirmado pela Defesa Civil no radar", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "O CAMINHO DO TORNADO",
     "itens": [{"t": em("f3", "Guatambu"), "txt": "🌪️ Guatambu"}, {"t": AERO, "txt": "✈️ aeroporto atingido"},
               {"t": ARR, "txt": "🏠 telhados arrancados"}, {"t": FECH, "txt": "⛔ voos suspensos"}], "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f4"), "fim": P2, "k": "CHAPECÓ · DECRETO 52.988",
     "contador": conta(180, "f4", "180", "#ff2a1f", "DIAS DE EMERGÊNCIA"), "l": "áreas urbana e rural", "borda": "rgba(255,42,31,.8)"},
    {"ini": P2, "fim": P3, "k": "CHAPECÓ · OCORRÊNCIAS",
     "contador": conta(2478, "f4", "2.478", "#ff8c1a", "CHAMADOS"), "l": "destelhamentos, árvores, rede elétrica", "borda": "rgba(255,140,26,.8)"},
    {"ini": P3, "fim": ini("f5"), "k": "CORPO DE BOMBEIROS (CBMSC)",
     "contador": conta(400, "f4", "400", "#ff8c1a", "FAMÍLIAS ATENDIDAS (MAIS DE)"), "l": "lonas, remoção de árvores", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f5"), "fim": X200, "k": "XANXERÊ · 2º TORNADO",
     "itens": [{"t": em("f5", "radar"), "txt": "📡 confirmado no radar"}, {"t": XAN, "txt": "🌪️ ~10h48 · 18 min depois"}], "borda": "rgba(255,42,31,.8)"},
    {"ini": X200, "fim": ini("f6"), "k": "XANXERÊ · DEFESA CIVIL",
     "contador": conta(200, "f5", "200", "#ff8c1a", "CASAS ATINGIDAS (MAIS DE)"), "l": "lonas distribuídas até a tarde de 04/11", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "PARANÁ · ESTA SEMANA",
     "itens": [{"t": em("f6", "Maringá"), "txt": "🌪️ Maringá · parque industrial"}, {"t": GRAN, "txt": "🧊 granizo · Grande Curitiba"}], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f7"), "fim": P7, "k": "PARANÁ · DESDE 01/11",
     "contador": conta(11960, "f7", "11.960", "#ff8c1a", "PESSOAS AFETADAS"), "l": "46 cidades atingidas", "borda": "rgba(255,140,26,.8)"},
    {"ini": P7, "fim": ini("f8"), "k": "PARANÁ · DESDE 01/11",
     "contador": conta(2695, "f7", "2.695", "#ff8c1a", "CASAS DANIFICADAS"), "l": "7 destruídas · 284 desalojados", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f8"), "fim": ini("f11"), "k": "COMO NASCE UM TORNADO",
     "itens": [{"t": em("f8", "quente"), "txt": "1️⃣ ar quente e úmido sobe"}, {"t": em("f9", "girar"), "txt": "2️⃣ o vento faz o ar girar"},
               {"t": em("f10", "pé"), "txt": "3️⃣ o giro fica em pé"}, {"t": em("f10", "chão"), "txt": "🌪️ toca o chão: tornado"}],
     "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "SÁBADO 07/11 · ALERTA",
     "itens": [{"t": em("f11", "frente"), "txt": "❄️ nova frente fria"}, {"t": em("f11", "tempestade"), "txt": "⛈️ tempestade forte no Sul"}],
     "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f12"), "fim": ini("f13"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f12", "onde"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f12", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
     "borda": "rgba(250,204,21,.8)"},
]
for a, b in zip(paineis, paineis[1:]):
    assert a["fim"] <= b["ini"] + 1e-6, (a["k"], b["k"])
for a in paineis:
    if a.get("contador"):
        c = a["contador"]
        assert a["ini"] - .01 <= c["ini"] and c["ini"] + c["dur"] <= a["fim"] + .01, ("contador fora do painel", a["k"])

cta = {"ini": ini("f13"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f13", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}
SC_F = "<b>Defesa Civil de SC</b> · Prefeitura de Chapecó · <b>CBMSC</b> · <b>Inmet</b>"
fontes = [
    {"ini": CAPA, "fim": ONTEM, "html": f"satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 04/11"},
    {"ini": ONTEM, "fim": ini("f6"), "html": SC_F + " · vídeos de 04/11"},
    {"ini": ini("f6"), "fim": ini("f8"), "html": "<b>Defesa Civil do PR</b> (SISDC, 18h de 04/11)"},
    {"ini": ini("f8"), "fim": ini("f11"), "html": "como nasce um tornado: ilustração"},
    {"ini": ini("f11"), "fim": DUR, "html": "<b>INMET</b> · previsão de 05/11/2026"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"tornado": "#ff2a1f", "tornados": "#ff2a1f", "rajadas": "#ff2a1f", "emergencia": "#ff2a1f", "granizo": "#96d2ff",
         "tempestade": "#ff8c1a", "telhados": "#ff8c1a", "afetadas": "#ff8c1a", "danificadas": "#ff8c1a", "giro": AM, "girar": AM,
         "supercelula": AM, "quente": "#ff8c1a", "frente": "#96d2ff", "fria": "#96d2ff", "inteligencia": AM, "artificial": AM}
LUGAR = {"santa", "catarina", "chapeco", "guatambu", "xanxere", "parana", "maringa", "curitiba", "sul", "inemaclub", "onde", "aeroporto"}
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
     "marca": "INEMA · EVENTOS EXTREMOS", "selo": DATA[:5] + " · Defesa Civil · Inmet · NOAA",
     "camera": camera, "sat": SAT, "imagens": [], "colunas": [], "telas": telas, "estados": estados, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · {len(clipes)} clipes ({sum(c['fim'] - c['ini'] for c in clipes):.0f} s)")
