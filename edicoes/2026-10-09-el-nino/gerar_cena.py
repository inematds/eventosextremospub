#!/usr/bin/env python3
"""Monta cena.js do vídeo explicativo do El Niño a partir de tempos.json (palavras da narração),
da anomalia da temperatura do mar (NASA GIBS, GHRSST MUR) e da base pesquisada (base.md).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "09/10/2026"  # data da abertura (troca numa linha se o render final sair noutro dia)
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())


def n(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


def roteiro(t, texto):
    """troca as palavras ouvidas pelo Whisper pelas do roteiro (campo legenda ou fala), mantendo os tempos:
    "o ninho" vira "El Niño", "40 .199" vira "40199"."""
    tok, W = texto.split(), t["palavras"]
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [n(x) for x in tok], [n(p["w"]) for p in W], autojunk=False).get_opcodes():
        if op == "equal":
            out += [{"w": tok[i1 + k], "t": W[j1 + k]["t"], "f": W[j1 + k]["f"]} for k in range(i2 - i1)]
        elif i2 > i1:  # replace / insert: espalha as palavras do roteiro no trecho ouvido
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
    """instante em que a k-ésima ocorrência de `palavra` é dita na fala `fid`."""
    achou = 0
    for p in FALA[fid]["palavras"]:
        if n(palavra) in n(p["w"]):
            achou += 1
            if achou == k:
                return p["t"]
    raise KeyError(f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in FALA[fid]["palavras"]))


ini = lambda fid: FALA[fid]["ini"]
fim = lambda fid: FALA[fid]["fim"]
ULT = T[-1]["id"]
DUR = round(fim(ULT) + 1.6, 2)

SECA = ["AC", "AM", "RR", "RO", "PA", "AP", "TO", "MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
CHUVA = ["PR", "SC", "RS"]
LAR, AZUL, VERM = [255, 140, 26], [60, 150, 255], [255, 42, 31]

# ---------------------------------------------------------------- câmera
PAC = {"lon": -90.0, "lat": -8.0, "zoom": 2.75}
PERU = {"lon": -86.0, "lat": -5.0, "zoom": 3.45}
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
NNE = {"lon": -52.0, "lat": -6.5, "zoom": 4.2}
SUL = {"lon": -52.0, "lat": -28.0, "zoom": 5.1}
K = lambda t, r, pitch=0, bearing=0, **kw: {"t": t, **r, **kw, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, PAC),
    K(ini("f2") - .3, {**PAC, "zoom": 2.85}, 0, 0),
    K(em("f2", "Peru") - .4, PERU, 8, -4),
    K(fim("f2") - .2, {**PERU, "lon": -84.0}, 10, -6),
    K(ini("f3") + 1.0, {**PAC, "lon": -78.0, "zoom": 2.9}, 5, 0),
    K(fim("f3") - .2, BR, 20, 0),
    K(ini("f4") + 1.0, NNE, 35, -8),
    K(fim("f4") - .2, {**NNE, "lon": -48.0}, 40, 6),
    K(ini("f5") + 1.0, SUL, 40, -12),
    K(fim("f5") - .2, {**SUL, "lon": -51.5, "zoom": 5.3}, 45, -20),
    K(ini("f6") + 1.0, BR, 20, 0),
    K(ini("f7") + 1.0, {**BR, "zoom": 3.6}, 25, 8),
    K(ini("f8") + 1.0, BR, 20, -4),
    K(DUR, {**BR, "zoom": 3.9}, 28, 10),
]

# ---------------------------------------------------------------- mar quente (NASA GIBS, GHRSST MUR, anomalia de 07/10)
SAT = {"base": "sat/web/base.jpg", "bbox": [-160, -56, -28, 22], "tint": [190, 190, 190],
       "ir": {"ini": -1.0, "fim": ini("f4") + .3, "dur": 1, "frames": ["sat/web/anomalia.png"], "tempos": ["07/10"],
              "rotulo": "VERMELHO = MAR MAIS QUENTE QUE O NORMAL · NASA", "alfa": .85}}

estados = [
    {"id": "seca", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": SECA, "cor": LAR, "alfa": .6},
    {"id": "chuva", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": CHUVA, "cor": AZUL, "alfa": .65},
    {"id": "seca2", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": SECA, "cor": LAR, "alfa": .5},
    {"id": "chuva2", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": CHUVA, "cor": AZUL, "alfa": .55},
    {"id": "seca3", "ini": ini("f8"), "fim": DUR, "ufs": SECA, "cor": LAR, "alfa": .4},
    {"id": "chuva3", "ini": ini("f8"), "fim": DUR, "ufs": CHUVA, "cor": AZUL, "alfa": .45},
]

pinos = [
    {"nome": "Costa do Peru", "sub": "mar +5,3 °C acima do normal", "lon": -81.0, "lat": -3.0, "ini": em("f2", "Peru"), "fim": ini("f3"), "h": 160},
    {"nome": "Manaus", "sub": "Rio Negro baixo", "lon": -60.02, "lat": -3.1, "ini": em("f4", "rio"), "fim": ini("f5"), "h": 140},
    {"nome": "Sertão", "sub": "seca grave em 16% do Nordeste", "lon": -40.5, "lat": -8.5, "ini": em("f4", "terra"), "fim": ini("f5"), "h": 200},
    {"nome": "Vale do Taquari (RS)", "sub": "enchente em setembro", "lon": -51.96, "lat": -29.47, "ini": em("f5", "Taquari"), "fim": ini("f6"), "h": 150},
]

# ---------------------------------------------------------------- textos
hero = [
    {"ini": 0, "fim": ini("f2") - .05,
     "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
             '<div class="dt" style="background:#ff2a1f;color:#fff">NÃO É PIADA</div>'
             '<div class="t1">EL NIÑO</div><div class="t2" style="color:#ff2a1f">CHEGOU</div>'
             '<div class="t3" style="color:#ffd23f;text-shadow:0 0 30px rgba(255,42,31,.6)">83%</div>'
             '<div class="t4">de chance de ser o mais forte desde 1950 · NOAA, 08/10</div>'},
    {"ini": ini("f7") + .1, "fim": ini("f8") - .05,
     "html": '<div class="dt" style="background:#ff2a1f;color:#fff">NÃO PASSA AMANHÃ</div>'
             '<div class="t1">PICO ATÉ</div><div class="t2">DEZEMBRO</div>'
             '<div class="t4">e segue forte até março de 2027</div>'},
]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "MAR PERTO DO PERU · semana de 30/09",
     "contador": {"de": 0, "ate": 5.3, "dec": 1, "ini": ini("f2") + .6, "dur": 1.6, "cor": "#ff2a1f", "unid": "°C ACIMA DO NORMAL"},
     "l": "água do Pacífico quente demais = El Niño", "borda": "rgba(255,42,31,.6)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "COMO CHEGA AQUI",
     "itens": [{"t": em("f3", "mar"), "txt": "🌊 mar quente"}, {"t": em("f3", "vento"), "txt": "💨 muda o vento"},
               {"t": em("f3", "chuva"), "txt": "🌧️ muda a chuva do Brasil"}], "borda": "rgba(94,200,255,.6)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "NORTE E NORDESTE",
     "itens": [{"t": em("f4", "chuva"), "txt": "☀️ chuva some"}, {"t": em("f4", "rio"), "txt": "🏞️ rio baixa"},
               {"t": em("f4", "terra"), "txt": "🌵 terra racha"}, {"t": em("f4", "fogo"), "txt": "🔥 fogo pega fácil"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "SUL",
     "itens": [{"t": em("f5", "chove"), "txt": "🌧️ chove demais"}, {"t": em("f5", "enchente"), "txt": "🌊 enchente no Taquari"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "CHEGA NA ROÇA",
     "itens": [{"t": em("f6", "soja"), "txt": "🌱 soja e café em risco"}, {"t": em("f6", "gado"), "txt": "🐄 falta água pro gado"},
               {"t": em("f6", "trigo"), "txt": "🌾 trigo sofre com chuva"}], "borda": "rgba(255,210,63,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "O QUE FAZER",
     "itens": [{"t": em("f8", "água"), "txt": "💧 guarda água"}, {"t": em("f8", "queima"), "txt": "🚫🔥 não queima nada"},
               {"t": em("f8", "CEP"), "txt": "📱 CEP por mensagem → 40199"}], "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f9", "sentindo"), "txt": "📍 Tá sentindo aí?"}, {"t": em("f9", "calor"), "txt": "🌡️ Mais calor?"},
               {"t": em("f9", "seca"), "txt": "🌵 Mais seca?"}, {"t": em("f9", "chuva"), "txt": "🌧️ Chuva demais?"},
               {"t": em("f9", "região"), "txt": "🗺️ Tua cidade e região"}], "borda": "rgba(255,210,63,.8)"},
]

cta = {"ini": ini("f10"), "fim": DUR, "a": "MANDA PRA QUEM ACHA QUE É BRINCADEIRA",
       "b": "El Niño muda a chuva, a roça e o bolso de todo mundo."}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "cursos gratuitos de tecnologia e IA"}

fontes = [
    {"ini": .5, "fim": ini("f2"), "html": "<b>NOAA</b>/CPC, discussão de 08/10/2026: 83% de chance de El Niño histórico (o mais forte desde 1950) em out–dez"},
    {"ini": ini("f2"), "fim": ini("f4"), "html": "<b>NOAA</b>/CPC, índice semanal Niño 1+2 (costa do Peru) +5,3 °C na semana de 30/09 · mapa: anomalia da temperatura do mar em 07/10, GHRSST MUR via <b>NASA</b> GIBS"},
    {"ini": ini("f4"), "fim": ini("f7"), "html": "<b>Painel El Niño nº 4</b> (INMET, INPE, ANA, Cemaden, SGB, Defesa Civil, Censipam), set/2026: seca no centro-norte, chuva acima da média no Sul, cheias no Taquari e no Caí, impactos na safra"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>NOAA</b>/CPC: El Niño forte a muito forte até jan–mar/2027 · Painel El Niño: aquecimento até pelo menos o 1º trimestre de 2027"},
    {"ini": ini("f8"), "fim": DUR, "html": "<b>Defesa Civil</b> · alertas por mensagem de texto (SMS): envie o CEP para 40199 · emergência 199 · incêndio: Bombeiros 193"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"elnino": "#ff2a1f", "nino": "#ff2a1f", "mar": "#5ec8ff", "quente": "#ff2a1f", "vento": "#5ec8ff", "chuva": "#5ec8ff",
         "seca": "#ff8c1a", "fogo": "#ff5a14", "enchente": "#3c96ff", "chove": "#3c96ff", "dezembro": "#ff2a1f",
         "pico": "#ff2a1f", "forte": "#ff2a1f", "agua": "#5ec8ff", "comenta": "#ffd23f", "gratuito": "#ffd23f",
         "brincadeira": "#ffd23f", "piada": "#ffd23f", "novela": "#ffd23f"}
LUGAR = {"norte", "nordeste", "sul", "peru", "pacifico", "brasil", "taquari", "sertao", "inema", "regiao", "cidade", "america"}
NUM = re.compile(r"\d|^(mil|novecentos|cinquenta|cinco|quarenta|cento|noventa|nove)$")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]
        k = n(w)
        cor = CORES.get(k) or ("#ffd23f" if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        fim_frase = w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1
        if len(bloco) == 3 or fim_frase:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · EL NIÑO", "selo": "NOAA · NASA · INPE · " + DATA[:5],
     "camera": camera, "sat": SAT, "estados": estados, "pinos": pinos, "hero": hero, "paineis": paineis, "cta": cta,
     "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda")
