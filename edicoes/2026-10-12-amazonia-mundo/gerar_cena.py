#!/usr/bin/env python3
"""Monta cena.js de "Amazônia e o mundo" (vídeo longo 16:9, layout "largo") a partir de tempos.json e da base conferida (base.md).
Fundo: mundo (NASA Blue Marble) + Amazônia em cor real (VIIRS NOAA-20, 10/10/2026, fumaça visível) em C.imagens.
Fogo: focos VIIRS de 01 a 11/10 (INPE) · contagens oficiais pelo satélite de referência (pesquisa/bruto/focos_resumo.txt).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=largo motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "12/10/2026"
AVATAR = "--avatar" in sys.argv
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
DUR = round(fim(T[-1]["id"]) + 1.6, 2)

# ---------------------------------------------------------------- câmera (padding à direita: o avatar ocupa x 1280–1920)
MUNDO = {"lon": -45.0, "lat": 15.0, "zoom": 2.0}
PAC = {"lon": -115.0, "lat": 2.0, "zoom": 2.5}
NORTE_AM = {"lon": -80.0, "lat": 42.0, "zoom": 2.4}
AMZ = {"lon": -59.0, "lat": -5.0, "zoom": 4.55}
PARA = {"lon": -52.5, "lat": -4.5, "zoom": 5.3}
AMAZONAS = {"lon": -63.0, "lat": -4.8, "zoom": 5.1}
MANAUS = {"lon": -60.0, "lat": -2.2, "zoom": 6.4}
RIO = {"lon": -61.5, "lat": -1.5, "zoom": 5.6}
ACRE = {"lon": -66.0, "lat": -7.5, "zoom": 5.0}
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.6}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, AMZ, 20, -6), K(fim("f1") - .4, {**AMZ, "zoom": 4.75}, 30, 6),
    K(ini("f2") + 1.2, MUNDO), K(fim("f2") - .3, {**MUNDO, "lon": -47.0, "zoom": 2.05}, 0, 0),
    K(ini("f3") + 1.2, PAC, 10, -4), K(fim("f3") - .3, {**PAC, "lon": -100.0}, 15, 4),
    K(ini("f4") + 1.0, NORTE_AM, 10, 0), K(em("f4", "Europa") - .3, {"lon": -45.0, "lat": 32.0, "zoom": 2.1}, 5, 0),
    K(fim("f4") - .2, {"lon": -40.0, "lat": 32.0, "zoom": 2.2}, 5, 0),
    K(ini("f5") + 1.4, AMZ, 25, -6), K(fim("f5") - .3, {**AMZ, "lon": -58.0}, 35, 6),
    K(ini("f6") + .9, PARA, 40, -8), K(em("f6", "Amazonas") + .6, AMAZONAS, 40, 8),
    K(ini("f7") + 1.0, AMZ, 25, 0), K(fim("f7") - .3, {**AMZ, "zoom": 4.7}, 30, -6),
    K(ini("f8") + 1.0, MANAUS, 45, -14), K(fim("f8") - .3, {**MANAUS, "lon": -59.8}, 50, -24),
    K(ini("f9") + 1.0, RIO, 40, 0), K(fim("f10") - .3, {**RIO, "lon": -60.5}, 45, 14),
    K(ini("f11") + 1.0, ACRE, 30, -8), K(em("f11", "julho") + .3, RIO, 35, 4), K(fim("f11") - .3, AMZ, 25, 0),
    K(ini("f12") + 1.2, BR, 10, 0), K(fim("f12") - .3, {**BR, "zoom": 3.8}, 15, 6),
    K(ini("f13") + 1.0, AMZ, 20, -4), K(DUR, {**AMZ, "zoom": 4.8}, 30, 8),
]

SAT = {"base": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
AMZ_IMG = "sat/web/v_NOAA20_2026-10-10.jpg"
AMZ_BBOX = [-76, -16, -42, 6]
imagens = [
    {"src": AMZ_IMG, "bbox": AMZ_BBOX, "ini": -1.0, "fim": ini("f2") + .8, "fade": .8},
    {"src": AMZ_IMG, "bbox": AMZ_BBOX, "ini": ini("f5") + .2, "fim": DUR, "fade": 1.0},
]

# focos VIIRS de 01 a 11/10 no bioma Amazônia (INPE), em grade de 0,08°, aparecem de norte para sul
fogo = [{"p": p, "i": i} for i, p in enumerate(json.loads((AQUI / "pesquisa/bruto/fogo_viirs_out_1a11.json").read_text()))]
FOGO = [255, 90, 20]
pontos = [
    {"id": "fogo0", "ini": -1.0, "fim": ini("f2") + .5, "dados": fogo, "dur": 1.0, "raio": 2.2, "cor": FOGO},
    {"id": "fogo", "ini": em("f5", "5.970"), "fim": ini("f9") + .4, "dados": fogo, "dur": 3.0, "raio": 2.4, "cor": FOGO},
    {"id": "fogo2", "ini": ini("f11"), "fim": DUR, "dados": fogo, "dur": 2.0, "raio": 2.0, "cor": FOGO},
]
rios = [{"nome": "Negro", "ini": ini("f9") + .2, "fim": fim("f11"), "dur": 2.4, "largura": 8},
        {"nome": "Amazonas", "ini": ini("f9") + .8, "fim": fim("f11"), "dur": 2.4, "largura": 6},
        {"nome": "Purús", "ini": em("f11", "Acre"), "fim": fim("f11"), "dur": 1.6, "largura": 5}]

pinos = [
    {"nome": "Pacífico", "sub": "El Niño: 83% de chance de ser histórico", "lon": -125.0, "lat": 0.0, "ini": em("f3", "Niño"), "fim": ini("f4"), "h": 140},
    {"nome": "Furacão Isaias · EUA", "sub": "≥ 4 mortos · ~480 mil sem luz", "lon": -86.5, "lat": 30.4, "ini": em("f4", "Isaias"), "fim": ini("f5"), "h": 120},
    {"nome": "Furacão Simon · México", "sub": "aulas suspensas em 22 municípios", "lon": -105.3, "lat": 19.6, "ini": em("f4", "Simon"), "fim": ini("f5"), "h": 90},
    {"nome": "Califórnia", "sub": "41,7 °C · recorde do dia (03/10)", "lon": -117.9, "lat": 33.75, "ini": em("f4", "Califórnia"), "fim": ini("f5"), "h": 160},
    {"nome": "Europa", "sub": "verão e setembro secos", "lon": 2.0, "lat": 46.0, "ini": em("f4", "Europa"), "fim": ini("f5"), "h": 120},
    {"nome": "Pará", "sub": "3.333 focos em 10 dias", "lon": -52.0, "lat": -4.5, "ini": em("f6", "Pará"), "fim": ini("f7"), "h": 140},
    {"nome": "Amazonas", "sub": "setembro: 3.726 focos (2025: 942)", "lon": -64.0, "lat": -4.5, "ini": em("f6", "Amazonas"), "fim": ini("f7"), "h": 140},
    {"nome": "Manaus", "sub": "200 µg/m³ · aulas suspensas", "lon": -60.02, "lat": -3.1, "ini": em("f8", "Manaus"), "fim": ini("f9"), "h": 160},
    {"nome": "Porto de Manaus", "sub": "abaixo de 18 m · −10 m desde julho", "lon": -60.02, "lat": -3.14, "ini": em("f9", "Negro"), "fim": ini("f11"), "h": 150},
    {"nome": "Rio Branco · jan/2026", "sub": "Rio Acre: 14,55 m, acima da cota", "lon": -67.81, "lat": -9.97, "ini": em("f11", "Acre"), "fim": ini("f12"), "h": 130},
]

hero = [
    {"ini": 0, "fim": em("f1", "fumaça") - .1,
     "html": f'<div style="font:400 96px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
             '<div class="dt" style="background:#ff2a1f;color:#fff">AMAZÔNIA EM CHAMAS</div>'
             '<div class="t1">5.970 FOCOS</div><div class="t2">EM 10 DIAS</div>'
             '<div class="t4">mais do que nos mesmos dias de 2024, o pior ano desde 2007 · INPE</div>'},
    {"ini": em("f1", "fumaça"), "fim": ini("f2") - .05,
     "html": '<div class="dt" style="background:#ff2a1f;color:#fff">E O MUNDO?</div><div class="t1">O QUE ESTÁ</div><div class="t2">ACONTECENDO</div>'},
    {"ini": ini("f11") + .1, "fim": em("f11", "janeiro") - .05,
     "html": '<div class="dt" style="background:#ff2a1f;color:#fff">2026</div><div class="t1">ENCHENTE</div><div class="t2">E SECA</div>'
             '<div class="t4">no mesmo ano, nos mesmos rios</div>'},
]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "O PLANETA · COPERNICUS, 12/10/2026",
     "itens": [it("f2", "setembro", "🌡️ setembro: 2º mais quente da história"), it("f2", "oceanos", "🌊 oceanos: recorde para o mês"),
               it("f2", "agosto", "🔥 agosto: empatou o recorde")], "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "EL NIÑO · NOAA, 08/10/2026",
     "contador": {"de": 0, "ate": 83, "dec": 0, "ini": em("f3", "83"), "dur": 1.4, "cor": "#ff2a1f", "unid": "% DE CHANCE"},
     "l": "de ser o mais forte desde 1950 · tira a chuva do norte do Brasil", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "EXTREMOS NO MUNDO · OUTUBRO",
     "itens": [it("f4", "Isaias", "🌀 EUA: Isaias, ≥ 4 mortos"), it("f4", "Simon", "🌀 México: Simon, aulas suspensas"),
               it("f4", "Califórnia", "🌡️ Califórnia: 41,7 °C, recorde"), it("f4", "Europa", "🏜️ Europa: fim de verão seco")], "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "AMAZÔNIA · FOCOS DE 01 A 10/10 · INPE",
     "contador": {"de": 0, "ate": 5970, "dec": 0, "ini": em("f5", "5.970"), "dur": 1.6, "cor": "#ff5a14", "unid": "FOCOS"},
     "l": "2,4× o mesmo período de 2025 · pior dia do ano: 09/10, com 1.282", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "POR ESTADO · INPE",
     "itens": [it("f6", "Pará", "🔥 Pará: 3.333 focos em 10 dias"), it("f6", "2023", "📈 2023: 2.880 · 2024: 1.818"),
               it("f6", "Amazonas", "🔥 Amazonas, setembro: 3.726"), it("f6", "passado", "📉 setembro de 2025: 942")], "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "NO ANO · 01/01 A 10/10 · INPE",
     "itens": [it("f7", "ano", "🏁 2024 (pior desde 2007): 109.926"), it("f7", "1/3", "🔥 2026: 35.550 (1/3)"),
               it("f7", "direção", "📈 +54% sobre 2025"), it("f7", "pico", "⚠️ o pico da seca ainda vem")], "borda": "rgba(255,210,63,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "MANAUS · FUMAÇA FINA (PM2,5)",
     "contador": {"de": 0, "ate": 200, "dec": 0, "ini": em("f8", "200"), "dur": 1.4, "cor": "#ff2a1f", "unid": "µg/m³"},
     "l": "quinta, 22h · acima de 160 = péssimo · sexta: aulas suspensas", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "RIO NEGRO · PORTO DE MANAUS",
     "contador": {"de": 28.5, "ate": 18.0, "dec": 1, "ini": em("f9", "Hoje"), "dur": 1.6, "cor": "#5ec8ff", "unid": "METROS"},
     "l": "julho: ~28,5 m (cheia) → hoje: abaixo de 18 m · setembro: −5,21 m", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "ATÉ 31/10 · PROJEÇÃO DO SGB",
     "itens": [it("f10", "projeta", "📉 entre 12,31 e 16,50 m"), it("f10", "recorde", "🏁 recorde: pouco acima de 12 m (2024)"),
               it("f10", "pior", "⚠️ pior cenário encosta no recorde")], "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f11", "janeiro"), "fim": ini("f12"), "k": "ENCHENTE E SECA NO MESMO ANO",
     "itens": [it("f11", "janeiro", "🌊 jan: Rio Acre acima da cota"), it("f11", "julho", "🌊 jul: Manaus na cota de enchente"),
               it("f11", "fogo", "🔥 out: fogo e rio baixando")], "borda": "rgba(255,210,63,.7)"},
    {"ini": ini("f12"), "fim": ini("f13"), "k": "E VOCÊ COM ISSO?",
     "itens": [it("f12", "viaja", "💨 fumaça viaja milhares de km"), it("f12", "frete", "🚢 rio baixo: frete mais caro"),
               it("f12", "voadores", "☁️ rios voadores: chuva do Centro-Sul")], "borda": "rgba(255,210,63,.7)"},
    {"ini": ini("f13"), "fim": ini("f14"), "k": "O QUE VOCÊ FAZ",
     "itens": [it("f13", "queima", "🚫🔥 não queima lixo nem mato"), it("f13", "PFF2", "😷 janela fechada + PFF2"),
               it("f13", "asma", "👵 criança, idoso, asma"), it("f13", "193", "📞 viu fogo? 193")], "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f14"), "fim": em("f14", "Manda") - .05, "k": "COMENTA AQUI 👇",
     "itens": [it("f14", "fumaça", "💨 a fumaça chegou aí?"), it("f14", "calor", "🌡️ e o calor?"), it("f14", "cidade", "🗺️ sua cidade")],
     "borda": "rgba(255,210,63,.8)"},
]

cta = {"ini": em("f14", "Manda"), "fim": DUR, "a": "MANDA PRA QUEM ACHA QUE A AMAZÔNIA ESTÁ LONGE",
       "b": "Fumaça, frete e chuva: a floresta mexe com o país inteiro."}
club = {"ini": em("f14", "inema"), "fim": DUR, "a": "inema.club", "b": "cursos gratuitos de tecnologia e IA"}

fontes = [
    {"ini": .5, "fim": ini("f2"), "html": "<b>INPE</b> Programa Queimadas: focos do satélite de referência (AQUA), bioma Amazônia · pontos = VIIRS, 01 a 11/10 · imagem: <b>NASA</b> VIIRS NOAA-20, 10/10/2026"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>Copernicus</b> C3S, boletim de 12/10/2026 (setembro) e de 10/09/2026 (agosto) · mapa: NASA Blue Marble"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>NOAA</b>/CPC, discussão do ENSO de 08/10/2026: 83% de chance de evento histórico em out–dez"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Isaias: CNN, 10/10 · Simon: KSAT/AP, 09/10 · Califórnia: CGTN, 05/10 (Santa Ana, 03/10) · Europa: <b>Copernicus</b> C3S"},
    {"ini": ini("f5"), "fim": ini("f8"), "html": "<b>INPE</b> BDQueimadas, satélite de referência AQUA_M-T, bioma Amazônia, contagem de 01/01 a 10/10 de 2023 a 2026 · foco de calor não é igual a incêndio"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>Defesa Civil de Manaus</b> (sensores PurpleAir) via Agência Brasil, 09/10/2026 · pior ar do país em 07/10: IQAir, via Band"},
    {"ini": ini("f9"), "fim": ini("f11"), "html": "Porto de Manaus e <b>SGB</b> (boletim 40, 07/10; alerta de vazante, set/2026: 12,31 a 16,50 m em 31/10) · recorde: <b>SGB</b>, mínima de 2024 entre 12,11 e 12,26 m (10 a 12/10/2024)"},
    {"ini": ini("f11"), "fim": ini("f12"), "html": "Rio Acre: <b>SGB</b>, 14,55 m em 18/01/2026 (cota de inundação 14,00 m) · Manaus: cota de inundação 27,50 m, ~28,5 m em 01/07/2026"},
    {"ini": ini("f12"), "fim": ini("f13"), "html": "Taxa de seca: ANTAQ, referência de 17,7 m no Porto de Manaus · rios voadores: <b>INPE</b>"},
    {"ini": ini("f13"), "fim": DUR, "html": "Bombeiros 193 · Defesa Civil 199 · máscara PFF2 em dia de fumaça (Ministério da Saúde)"},
]

CORES = {"fogo": "#ff5a14", "focos": "#ff5a14", "fumaca": "#ff8c1a", "seca": "#ff8c1a", "enchente": "#3c96ff", "rio": "#5ec8ff",
         "oceanos": "#5ec8ff", "quente": "#ff2a1f", "recorde": "#ff2a1f", "elnino": "#ff2a1f", "nino": "#ff2a1f", "pessimo": "#ff2a1f",
         "furacao": "#ff8c1a", "calor": "#ff2a1f", "comenta": "#ffd23f", "gratis": "#ffd23f", "graca": "#ffd23f", "longe": "#ffd23f",
         "chuva": "#5ec8ff", "cheia": "#3c96ff", "baixando": "#ff8c1a", "pff2": "#ffd23f"}
LUGAR = {"amazonia", "manaus", "para", "amazonas", "mexico", "california", "europa", "estados", "unidos", "pacifico", "brasil",
         "negro", "acre", "branco", "inemaclub", "planeta", "mundo", "isaias", "simon", "centrosul"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or ("#ffd23f" if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 4 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "largo", "padding_dir": 640, "coluna": not AVATAR, "duracao": DUR,
     "marca": "INEMA · AMAZÔNIA E O MUNDO", "selo": "INPE · NOAA · COPERNICUS · " + DATA[:5],
     "camera": camera, "sat": SAT, "imagens": imagens, "pontos": pontos, "rios": rios, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(fogo)} pontos de fogo")
