#!/usr/bin/env python3
"""Monta cena.js do REEL 9:16 "Amazônia e o mundo" (versão curta do 16:9 em ../2026-10-12-amazonia-mundo) a partir de tempos.json e da base conferida (base.md).
Fundo: mundo (NASA Blue Marble) + Amazônia em cor real (VIIRS NOAA-20, 10/10/2026, fumaça visível) em C.imagens.
Fogo: focos VIIRS de 01 a 11/10 (INPE) · contagens oficiais pelo satélite de referência (pesquisa/bruto/focos_resumo.txt).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "12/10/2026"
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())


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
DUR = round(fim(T[-1]["id"]) + 1.4, 2)
M = "../2026-10-12-amazonia-mundo/"


# ---------------------------------------------------------------- câmera (9:16)
AMZ = {"lon": -58.5, "lat": -5.5, "zoom": 4.3}
MUNDO = {"lon": -75.0, "lat": 5.0, "zoom": 2.3}
PARA = {"lon": -52.5, "lat": -4.5, "zoom": 5.4}
MANAUS = {"lon": -60.0, "lat": -3.1, "zoom": 6.3}
RIO = {"lon": -61.0, "lat": -3.0, "zoom": 5.5}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, AMZ, 25, -6), K(fim("r1") - .3, {**AMZ, "zoom": 4.5}, 35, 6),
    K(ini("r2") + .9, MUNDO), K(fim("r2") - .3, {**MUNDO, "lon": -85.0, "zoom": 2.4}),
    K(ini("r3") + .9, MANAUS, 45, -12), K(em("r3", "Pará") + .5, PARA, 45, 8),
    K(ini("r4") + .9, RIO, 40, 0), K(fim("r4") - .3, {**RIO, "lon": -60.5}, 45, 14),
    K(ini("r5") + .9, AMZ, 25, -4), K(DUR, {**AMZ, "zoom": 4.5}, 30, 8),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
AMZ_IMG, AMZ_BBOX = M + "sat/web/v_NOAA20_2026-10-10.jpg", [-76, -16, -42, 6]
imagens = [{"src": AMZ_IMG, "bbox": AMZ_BBOX, "ini": -1.0, "fim": ini("r2") + .6, "fade": .6},
           {"src": AMZ_IMG, "bbox": AMZ_BBOX, "ini": ini("r3") + .1, "fim": DUR, "fade": .8}]
fogo = [{"p": p, "i": i} for i, p in enumerate(json.loads((AQUI / M / "pesquisa/bruto/fogo_viirs_out_1a11.json").read_text()))]
FOGO = [255, 90, 20]
pontos = [{"id": "fogo0", "ini": -1.0, "fim": ini("r2") + .4, "dados": fogo, "dur": 1.6, "raio": 2.4, "cor": FOGO},
          {"id": "fogo", "ini": ini("r3"), "fim": DUR, "dados": fogo, "dur": 1.6, "raio": 2.2, "cor": FOGO}]
rios = [{"nome": "Negro", "ini": ini("r4") + .2, "fim": ini("r5") + .3, "dur": 2.0, "largura": 9},
        {"nome": "Amazonas", "ini": ini("r4") + .6, "fim": ini("r5") + .3, "dur": 2.0, "largura": 7}]
pinos = [
    {"nome": "Pacífico · El Niño", "sub": "83% de chance de ser histórico", "lon": -120.0, "lat": 0.0, "ini": em("r2", "Niño"), "fim": ini("r3"), "h": 140},
    {"nome": "Manaus", "sub": "pior ar do país · aulas suspensas", "lon": -60.02, "lat": -3.1, "ini": em("r3", "Manaus"), "fim": em("r3", "Pará"), "h": 170},
    {"nome": "Pará", "sub": "3.333 focos em 10 dias", "lon": -52.0, "lat": -4.5, "ini": em("r3", "Pará"), "fim": ini("r4"), "h": 160},
    {"nome": "Porto de Manaus", "sub": "−10 m desde julho", "lon": -60.02, "lat": -3.14, "ini": em("r4", "Negro"), "fim": ini("r5"), "h": 160},
]

hero = [{"ini": 0, "fim": ini("r2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">AMAZÔNIA EM CHAMAS</div>'
                 '<div class="t1">5.970</div><div class="t2">FOCOS EM 10 DIAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🔥 mais que nos mesmos dias de 2024, o pior ano desde 2007</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
paineis = [
    {"ini": ini("r2"), "fim": ini("r3"), "k": "O PLANETA · COPERNICUS · NOAA",
     "itens": [it("r2", "Setembro", "🌡️ setembro: 2º mais quente"), it("r2", "oceanos", "🌊 oceanos: recorde"),
               it("r2", "Niño", "🔥 El Niño: o mais forte desde 1950?")], "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("r3"), "fim": ini("r4"), "k": "FUMAÇA E FOGO · 07 A 10/10",
     "itens": [it("r3", "pior", "😷 Manaus: pior ar do país"), it("r3", "escola", "🏫 aulas suspensas"),
               it("r3", "Pará", "🔥 Pará: 3.333 focos")], "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("r4"), "fim": ini("r5"), "k": "RIO NEGRO · PORTO DE MANAUS",
     "contador": {"de": 28.5, "ate": 18.0, "dec": 1, "ini": em("r4", "desceu"), "dur": 1.4, "cor": "#5ec8ff", "unid": "METROS"},
     "l": "julho: ~28,5 m (cheia) → hoje: abaixo de 18 m · recorde de seca: pouco acima de 12 m", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("r5"), "fim": em("r5", "Comenta") - .05, "k": "O QUE VOCÊ FAZ",
     "itens": [it("r5", "queima", "🚫🔥 não queima nada"), it("r5", "asma", "😷 proteja quem tem asma"), it("r5", "193", "📞 viu fogo? 193")],
     "borda": "rgba(255,42,31,.7)"},
]
cta = {"ini": em("r5", "Comenta"), "fim": DUR, "a": "A FUMAÇA CHEGOU AÍ? COMENTA 👇", "b": "Fogo, fumaça e rio baixo na Amazônia."}
club = {"ini": em("r5", "inema"), "fim": DUR, "a": "inema.club", "b": "cursos gratuitos de tecnologia e IA"}

fontes = [
    {"ini": .5, "fim": ini("r2"), "html": "<b>INPE</b> Queimadas: satélite de referência, bioma Amazônia, 01 a 10/10 de 2024 e 2026 · 2024: pior ano desde 2007 · pontos VIIRS · imagem <b>NASA</b> NOAA-20, 10/10"},
    {"ini": ini("r2"), "fim": ini("r3"), "html": "<b>Copernicus</b> C3S, 12/10/2026 · <b>NOAA</b>/CPC, 08/10/2026: 83% de chance de El Niño histórico"},
    {"ini": ini("r3"), "fim": ini("r4"), "html": "IQAir 07/10 (via Band) · <b>Defesa Civil de Manaus</b> via Agência Brasil, 09/10 · <b>INPE</b>, Pará 01 a 10/10"},
    {"ini": ini("r4"), "fim": ini("r5"), "html": "Porto de Manaus e <b>SGB</b>: ~28,5 m em 01/07, abaixo de 18 m em 12/10 · projeção até 31/10: 12,31 a 16,50 m · recorde de 2024: 12,11 a 12,26 m"},
    {"ini": ini("r5"), "fim": DUR, "html": "Bombeiros 193 · Defesa Civil 199"},
]

CORES = {"fogo": "#ff5a14", "focos": "#ff5a14", "fumaca": "#ff8c1a", "seca": "#ff8c1a", "enchente": "#3c96ff", "oceanos": "#5ec8ff",
         "quente": "#ff2a1f", "recorde": "#ff2a1f", "nino": "#ff2a1f", "comenta": "#ffd23f", "asma": "#ffd23f", "escola": "#ff8c1a"}
LUGAR = {"amazonia", "manaus", "para", "negro", "inemaclub", "pais"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or ("#ffd23f" if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · AMAZÔNIA", "selo": "INPE · NOAA · SGB · " + DATA[:5],
     "camera": camera, "sat": SAT, "imagens": imagens, "pontos": pontos, "rios": rios, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(fogo)} pontos de fogo")
