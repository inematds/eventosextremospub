#!/usr/bin/env python3
"""Monta cena.js de "Queimadas na Amazônia, ano a ano" REFEITO em 3D com o mesmo avatar (16:9 largo com avatar, 15/10/2026) a partir de tempos.json e de base.md.
Gráficos (valores do INPE contados em pesquisa/contar.py): série anual 2003–2026, 01/01–14/10 por estado 2019–2026,
outubro (01–14) 2019–2026, Pará em outubro. Entre os gráficos, fotos do Codex (selo "ilustração") em C.telas.
Mapa: Blue Marble + VIIRS NOAA-20 de 14/10/2026 (fumaça real); pontos = focos VIIRS/AQUA de 01 a 14/10 em grade de 0,08°.
Só mapa: GEO=geo-br.js motor/montar.sh <pasta> · com avatar: gerar_cena.py --avatar e GEO=geo-br.js LAYOUT=largo motor/compor_avatar.sh"""
import difflib, json, os, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "15/10/2026"
AVATAR = "--avatar" in sys.argv
T = json.loads((AQUI / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())
S = json.loads((AQUI / "pesquisa/bruto/serie.json").read_text())


def n(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


def roteiro(t, texto):
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
chega = lambda fid, pal, k=1: round(em(fid, pal, k) - 1.0, 3)   # contador/gráfico CHEGA ao número quando a palavra é dita
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
FOTO = 2.6   # segundos de foto cheia entre um gráfico e outro

# ---------------------------------------------------------------- câmera (avatar ocupa x 1280–1920; padding_dir 640)
AMZ = {"lon": -58.5, "lat": -5.0, "zoom": 4.55}
PARA = {"lon": -52.5, "lat": -4.8, "zoom": 5.3}
AMAZONAS = {"lon": -62.0, "lat": -5.0, "zoom": 5.1}
NORTE = {"lon": -55.0, "lat": -1.5, "zoom": 4.9}
SUL = {"lon": -59.0, "lat": -10.5, "zoom": 5.0}
XINGU = {"lon": -53.5, "lat": -5.2, "zoom": 6.0}
MANAUS = {"lon": -60.0, "lat": -3.0, "zoom": 6.2}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [   # refeito 3D (15/10/2026): pitch 50–62 e órbita contínua, nunca parada de cima
    K(0, {**AMZ, "zoom": 3.6}, 10, -4), K(fim("f1"), {**AMZ, "zoom": 4.7}, 55, 14),
    K(ini("f3"), {**AMZ, "lon": -57.0, "zoom": 4.8}, 58, -12),
    K(ini("f5"), {**AMZ, "lon": -56.0, "zoom": 4.9}, 60, 16),
    K(fim("f6") - .2, {**AMZ, "zoom": 4.8}, 56, -14),
    K(ini("f7") + FOTO, PARA, 60, -10), K(fim("f7") - .3, {**PARA, "lon": -52.0}, 62, 18),
    K(ini("f8") + 1.0, AMAZONAS, 58, 8), K(em("f8", "Amapá") + .2, NORTE, 55, -6),
    K(ini("f9") + .8, SUL, 56, -14), K(em("f9", "subiu") + .2, NORTE, 55, 10),
    K(ini("f10") + .8, XINGU, 62, -18), K(em("f10", "Apuí") + .2, {"lon": -58.0, "lat": -6.0, "zoom": 5.6}, 60, 12),
    K(ini("f11") + .8, AMZ, 52, 0), K(em("f11", "fumaça") + .2, MANAUS, 62, -20),
    K(ini("f12") + 1.0, AMZ, 55, 6), K(DUR, {**AMZ, "zoom": 4.9}, 58, 26),
]

SAT = {"fundo": {"src": "sat/web/bmng_sa.jpg", "bbox": [-110, -45, -20, 25], "tint": [215, 215, 215]},
       "base": "sat/web/bmng.jpg", "bbox": [-80, -20, -40, 8], "tint": [235, 235, 235]}   # NASA Blue Marble NG (GIBS), sem nuvem
CEU = "linear-gradient(180deg,#05080c 0,#0b1422 14%,#3a2a22 24%,#8a4a24 30%,#05080c 46%)"
imagens = []
import math
from collections import Counter
P = json.loads((AQUI / "pesquisa/bruto/fogo_out_1a14.json").read_text())
PASSO = .5
cel = Counter((math.floor(lon / PASSO), math.floor(lat / PASSO)) for lon, lat in P)
cor_n = lambda v: [255, 214, 70] if v < 6 else [255, 150, 30] if v < 14 else [255, 75, 20] if v < 23 else [235, 20, 45]
col = sorted(({"p": [(i + .5) * PASSO, (j + .5) * PASSO], "v": v, "cor": cor_n(v)} for (i, j), v in cel.items()), key=lambda d: d["p"][0])
for k, d in enumerate(col):
    d["id"] = k
lon0, lon1 = col[0]["p"][0], col[-1]["p"][0]
ordem = {d["id"]: (d["p"][0] - lon0) / (lon1 - lon0) * 2.2 for d in col}
colunas = [{"id": "fogo", "ini": -1.0, "fim": DUR + 1, "dados": col, "raio": 17000, "escala": 7000, "ordem": ordem, "varredura": 1, "brilho": 2.6}]
pontos = []
fogo = P

# estados: os que subiram em vermelho, os que caíram em cinza-azulado
VERM, CINZA = [255, 42, 31], [150, 170, 190]
estados = [
    {"id": "pa", "ufs": ["PA"], "cor": VERM, "alfa": .42, "ini": em("f7", "Pará"), "fim": ini("f9")},
    {"id": "am", "ufs": ["AM"], "cor": VERM, "alfa": .38, "ini": em("f8", "Amazonas"), "fim": ini("f9")},
    {"id": "ap", "ufs": ["AP"], "cor": VERM, "alfa": .5, "ini": em("f8", "Amapá"), "fim": ini("f9")},
    {"id": "caiu", "ufs": ["MT", "RO"], "cor": CINZA, "alfa": .35, "ini": em("f9", "Mato"), "fim": fim("f9")},
    {"id": "subiu", "ufs": ["PA", "AM", "AP"], "cor": VERM, "alfa": .45, "ini": em("f9", "subiu"), "fim": fim("f9")},
]

pinos = [
    {"nome": "Altamira · PA", "sub": "1.878 focos em 2026", "lon": -52.21, "lat": -3.20, "ini": em("f10", "Altamira"), "fim": ini("f11"), "h": 150},
    {"nome": "São Félix do Xingu · PA", "sub": "1.547 focos", "lon": -51.99, "lat": -6.64, "ini": em("f10", "Félix"), "fim": ini("f11"), "h": 110},
    {"nome": "Itaituba · PA", "sub": "1.213 focos", "lon": -55.98, "lat": -4.28, "ini": em("f10", "Itaituba"), "fim": ini("f11"), "h": 130},
    {"nome": "Apuí · AM", "sub": "983 focos", "lon": -59.89, "lat": -7.20, "ini": em("f10", "Apuí"), "fim": ini("f11"), "h": 120},
    {"nome": "Amapá", "sub": "747 focos (2025: 192)", "lon": -51.5, "lat": 1.2, "ini": em("f8", "Amapá"), "fim": ini("f9"), "h": 120},
]

TELA = lambda src, a, b, selo="ilustração": {"src": f"capa/{src}", "ini": a, "fim": b, "fade": .5 if a > 0 else .3, "zoom": .06, "selo": selo}
telas = [
    {"src": "capa/abertura-v.png", "ini": -1.0, "fim": em("f1", "pior") - .1, "fade": .4, "zoom": .05},
    TELA("cinzas.png", ini("f4") - .2, ini("f4") + FOTO),
    TELA("mata-chamas.png", ini("f6") - .2, ini("f6") + FOTO),
    TELA("brigadista.png", em("f8", "governo") - .2, em("f8", "Amapá") - .1),
    TELA("manaus-fumaca.png", em("f11", "fumaça") - .2, fim("f11")),
    TELA("rio-seco.png", ini("f12") - .2, ini("f12") + FOTO),
]

hero = [
    {"ini": em("f1", "pior") - .05, "fim": em("f1", "outubro", 2) - .05,
     "html": f'<div style="font:400 72px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
             '<div class="dt" style="background:#ff2a1f;color:#fff">PIOR DIA DE 2026</div>'
             '<div class="t1">1.500 FOCOS</div><div class="t2">EM UM DIA</div>'
             '<div class="t4">14/10/2026 · bioma Amazônia · INPE</div>'},
    {"ini": em("f1", "outubro", 2), "fim": ini("f2") - .05,
     "html": '<div class="dt" style="background:#FACC15;color:#0b0f14">OUTUBRO</div><div class="t1">DEVIA CAIR.</div><div class="t2">ESTÁ SUBINDO.</div>'},
]

# ---------------------------------------------------------------- gráficos (valores do INPE, satélite de referência)
ANOS = list(range(2003, 2027))
mil = lambda v: round(v / 1000, 1)
an = S["anual"]
g_serie = {"rotulos": [f"{a % 100:02d}" if a != 2026 else "26*" for a in ANOS],
           "series": [{"nome": "ano inteiro (mil focos)", "cor": "#ff8c1a", "v": [mil(an[str(a)]) if a < 2026 else 0 for a in ANOS]},
                      {"nome": "2026 até 14/10", "cor": "#ff2a1f", "v": [0] * 23 + [mil(an["2026"])]}],
           "marcar": [ANOS.index(a) for a in (2004, 2007, 2010, 2024, 2025, 2026)],
           "marcar_x": [ANOS.index(a) for a in (2004, 2007, 2010, 2015, 2020, 2024, 2026)],
           "ini": chega("f2", "2004") - .6, "dur": 1.6}
ANOS8 = list(range(2019, 2027))
UFS = [("PARÁ", "Pará", "#ff2a1f"), ("AMAZONAS", "Amazonas", "#ff8c1a"), ("MATO GROSSO", "Mato Grosso", "#FACC15"),
       ("RONDÔNIA", "Rondônia", "#5ec8ff"), ("ACRE", "Acre", "#9b8cff")]
ey = S["estados_ytd"]
outros = [mil(S["ytd"][str(a)] - sum(ey[str(a)].get(u, 0) for u, _, _ in UFS)) for a in ANOS8]
g_estados = {"rotulos": [str(a) for a in ANOS8],
             "series": [{"nome": nm, "cor": c, "v": [mil(ey[str(a)].get(u, 0)) for a in ANOS8]} for u, nm, c in UFS]
                       + [{"nome": "outros", "cor": "#7d8794", "v": outros}],
             "ini": ini("f4") + FOTO, "dur": 1.6}
g_out = {"rotulos": [str(a) for a in ANOS8],
         "series": [{"nome": "focos de 01 a 14/10", "cor": "#ff8c1a", "v": [S["out"][str(a)] if a < 2026 else 0 for a in ANOS8]},
                    {"nome": "2026", "cor": "#ff2a1f", "v": [0] * 7 + [S["out"]["2026"]]}],
         "ini": chega("f5", "9.141") - .4, "dur": 1.4}
oe = json.loads((AQUI / "pesquisa/bruto/out_estados.json").read_text())
g_para = {"rotulos": [str(a) for a in ANOS8],
          "series": [{"nome": "Pará, focos de 01 a 14/10", "cor": "#ff8c1a", "v": [oe[str(a)].get("PARÁ", 0) if a < 2026 else 0 for a in ANOS8]},
                     {"nome": "2026", "cor": "#ff2a1f", "v": [0] * 7 + [oe["2026"]["PARÁ"]]}],
          "ini": chega("f7", "5.549") - .4, "dur": 1.2}
y26 = ey["2026"]
rk_estados = {"itens": [{"nome": nm, "v": y26[u]} for u, nm in
                        [("PARÁ", "Pará"), ("AMAZONAS", "Amazonas"), ("MATO GROSSO", "Mato Grosso"), ("RORAIMA", "Roraima"),
                         ("ACRE", "Acre"), ("MARANHÃO", "Maranhão"), ("RONDÔNIA", "Rondônia"), ("AMAPÁ", "Amapá")]],
              "cor": "#ff8c1a", "cor_top": "#ff2a1f", "unid": "", "ini": chega("f7", "17") , "dur": 1.0}
rk_dias = {"itens": [{"nome": "14/10/2026", "v": 1500}, {"nome": "12/10/2026", "v": 1335}, {"nome": "09/10/2026", "v": 1282},
                     {"nome": "21/09/2026", "v": 1208}],
           "cor": "#ff8c1a", "cor_top": "#ff2a1f", "unid": "", "ini": chega("f6", "1.282"), "dur": 2.0}
SIGLA = {"PARÁ": "PA", "AMAZONAS": "AM", "MATO GROSSO": "MT", "ACRE": "AC", "RONDÔNIA": "RO", "RORAIMA": "RR", "MARANHÃO": "MA", "AMAPÁ": "AP"}
rk_mun = {"itens": [{"nome": f"{m.replace(' Do ', ' do ')} · {SIGLA.get(u, u)}", "v": v} for m, u, v in S["mun26"][:6]],
          "cor": "#ff8c1a", "cor_top": "#ff2a1f", "unid": "", "ini": chega("f10", "1.878"), "dur": 1.0}

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
B_RED, B_ORG, B_YEL, B_BLU = "rgba(255,42,31,.7)", "rgba(255,140,26,.7)", "rgba(250,204,21,.7)", "rgba(94,200,255,.7)"
paineis = [
    {"ini": ini("f2"), "fim": em("f3", "veio") - .05, "k": "FOCOS POR ANO NA AMAZÔNIA · MIL FOCOS · INPE",
     "grafico": g_serie, "l": "2004: 218,6 mil (recorde) · 2024: 140,3 mil, o pior desde 2007", "borda": B_ORG},
    {"ini": em("f3", "veio"), "fim": ini("f4") - .25, "k": "FOCOS POR ANO NA AMAZÔNIA · MIL FOCOS · INPE",
     "grafico": {**g_serie, "ini": ini("f2"), "dur": .1},
     "l": "2025: 43,1 mil, o menor desde 2003 · 2026: 38,7 mil até 14/10", "borda": B_RED},
    {"ini": ini("f4") + FOTO, "fim": ini("f5") - .05, "k": "01/01 A 14/10 DE CADA ANO · MIL FOCOS POR ESTADO",
     "grafico": g_estados, "l": "2026: +63% sobre 2025 · cerca de 1/3 de 2024", "borda": B_ORG},
    {"ini": ini("f5"), "fim": ini("f6") - .25, "k": "OUTUBRO, DE 01 A 14 · FOCOS NA AMAZÔNIA",
     "grafico": g_out, "l": "2026: 9.141 · 2,9× 2025 · acima de 2024 · só 2020 e 2023 passaram", "borda": B_RED},
    {"ini": ini("f6") + FOTO, "fim": ini("f7") - .25, "k": "OS DIAS COM MAIS FOCOS EM 2026",
     "ranking": rk_dias, "l": "pior dia de 2024: 3.445 focos (02/09/2024)", "borda": B_RED},
    {"ini": ini("f7"), "fim": em("f7", "outubro") - .05, "k": "FOCOS POR ESTADO · 01/01 A 14/10/2026",
     "ranking": rk_estados, "l": "Pará: 45% da Amazônia · 2,3× 2025 · total da Amazônia: 38.721", "borda": B_RED},
    {"ini": em("f7", "outubro"), "fim": ini("f8") - .05, "k": "PARÁ · OUTUBRO, DE 01 A 14",
     "grafico": g_para, "l": "o maior desde pelo menos 2015", "borda": B_RED},
    {"ini": ini("f8"), "fim": em("f8", "governo") - .25, "k": "AMAZONAS · 01/01 A 14/10",
     "itens": [it("f8", "Amazonas", "🔥 2025: 3.667 focos"), it("f8", "dobro", "🔥 2026: 7.896 focos")], "borda": B_RED},
    # quem combate (não narrado, Nei 15/10: "números de bombeiros, locais, estaduais, federais, mesmo que não narre")
    {"ini": em("f8", "governo"), "fim": em("f8", "Amapá") - .25, "k": "QUEM COMBATE O FOGO NO AMAZONAS",
     "itens": [{"t": em("f8", "governo"), "txt": "🇧🇷 federal: 290 brigadistas"}, {"t": em("f8", "governo") + .6, "txt": "✈️ 4 aviões + 2 helicópteros · 2 KC-390"},
               {"t": em("f8", "emergência"), "txt": "🚒 Bombeiros do AM: 1.500+ militares"}, {"t": em("f8", "municípios"), "txt": "🏘️ 36 municípios em emergência"},
               {"t": em("f8", "estado"), "txt": "🔥 229 incêndios apagados, 20 ativos"}], "borda": B_YEL,
     "l": "Ibama/ICMBio (MMA, 10–12/10) · FAB (11/10) · efetivo total do CBMAM (CETAM, 2026)"},
    {"ini": em("f8", "Amapá"), "fim": ini("f9") - .05, "k": "AMAPÁ · 01/01 A 14/10",
     "itens": [it("f8", "Amapá", "🔥 2025: 192 · 2026: 747"), it("f8", "2024", "📈 acima de 2024 (315)")], "borda": B_RED},
    {"ini": ini("f9"), "fim": ini("f10") - .05, "k": "O FOGO MUDOU DE LUGAR",
     "itens": [it("f9", "Mato", "↘ Mato Grosso: −9%"), it("f9", "Rondônia", "↘ Rondônia: −24%"),
               it("f9", "subiu", "↗ Pará, Amazonas, Amapá")], "borda": B_YEL},
    {"ini": ini("f10"), "fim": ini("f11") - .05, "k": "MUNICÍPIOS COM MAIS FOCOS · 2026",
     "ranking": rk_mun, "l": "as três primeiras no Pará", "borda": B_RED},
    {"ini": ini("f11"), "fim": em("f11", "fumaça") - .25, "k": "POR QUE AGORA",
     "itens": [it("f11", "Niño", "🌊 El Niño: 83% de chance de ser histórico"), it("f11", "sozinha", "🔥 floresta úmida não pega fogo sozinha"),
               it("f11", "humana", "👤 fogo de ação humana")], "borda": B_ORG},
    {"ini": em("f11", "fumaça"), "fim": ini("f12") - .25, "k": "MANAUS · FUMAÇA FINA (PM2,5)",
     "contador": {"de": 0, "ate": 196, "dec": 0, "ini": chega("f11", "200"), "dur": 1.0, "cor": "#ff2a1f", "unid": "µg/m³"},
     "l": "sábado, 10/10, 6h · acima de 160 = péssimo", "borda": B_RED},
    {"ini": ini("f12") + FOTO, "fim": ini("f13") - .05, "k": "O QUE VOCÊ FAZ",
     "itens": [it("f12", "janela", "🪟 janela fechada + PFF2"), it("f12", "criança", "👵 criança, idoso, asma"),
               it("f12", "queime", "🚫🔥 não queime lixo nem mato"), it("f12", "193", "📞 viu fogo? 193")], "borda": B_RED},
    {"ini": ini("f13"), "fim": em("f13", "Manda") - .05, "k": "COMENTA AQUI 👇",
     "itens": [it("f13", "região", "🗺️ de que região você é?"), it("f13", "cidade", "🏙️ de que cidade?")], "borda": B_YEL},
]

cta = {"ini": em("f13", "Manda"), "fim": DUR, "a": "MANDA PRA QUEM ACHA QUE A AMAZÔNIA ESTÁ LONGE",
       "b": "Fogo, fumaça e seca: 38.721 focos em 2026 até 14/10."}
club = {"ini": em("f13", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

INPE = "<b>INPE</b> Programa Queimadas, satélite de referência (AQUA), bioma Amazônia, contagem própria dos arquivos anuais e mensais · foco de calor não é igual a incêndio"
fontes = [
    {"ini": .5, "fim": ini("f2"), "html": INPE + " · mapa: <b>NASA</b> Blue Marble · colunas: focos de 01 a 14/10 numa grade de ~55 km"},
    {"ini": ini("f2"), "fim": ini("f7"), "html": INPE + " · 2003 a 2026 (2026 até 14/10)"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": INPE + " · Pará, 01 a 14/10, de 2015 a 2026"},
    {"ini": ini("f8"), "fim": ini("f10"), "html": INPE + " · combate: MMA/Ibama via Agência Brasil (10 e 12/10), FAB, CBMAM · emergência em 36 municípios: governo federal, 10/10/2026"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": INPE + " · 01/01 a 14/10/2026"},
    {"ini": ini("f11"), "fim": ini("f12"), "html": "<b>NOAA</b>/CPC, 08/10/2026 · ministro do Meio Ambiente e <b>Prefeitura de Manaus</b> (PM2,5 de 196,4 µg/m³, 10/10), via Poder360"},
    {"ini": ini("f12"), "fim": DUR, "html": "Bombeiros 193 · Defesa Civil 199 · máscara PFF2 em dia de fumaça (Ministério da Saúde)"},
]

CORES = {"fogo": "#ff5a14", "focos": "#ff5a14", "fumaca": "#ff8c1a", "seca": "#ff8c1a", "pior": "#ff2a1f", "recorde": "#ff2a1f",
         "subindo": "#ff2a1f", "assusta": "#ff2a1f", "acelera": "#ff2a1f", "dobro": "#ff2a1f", "quadruplicou": "#ff2a1f",
         "emergencia": "#ff2a1f", "pessimo": "#ff2a1f", "elnino": "#ff2a1f", "nino": "#ff2a1f", "caiu": "#5ec8ff", "menor": "#5ec8ff",
         "comentarios": "#FACC15", "longe": "#FACC15", "regiao": "#FACC15", "cidade": "#FACC15", "pff2": "#FACC15"}
LUGAR = {"amazonia", "para", "amazonas", "amapa", "mato", "grosso", "rondonia", "altamira", "sao", "felix", "xingu", "itaituba",
         "apui", "manaus", "inemaclub", "norte", "brasil"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or ("#FACC15" if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "largo", "padding_dir": 640, "coluna": not AVATAR and not os.environ.get("PREVIA_AVATAR"), "duracao": DUR,
     "marca": "INEMA · QUEIMADAS NA AMAZÔNIA", "selo": "INPE · " + DATA[:5],
     "ceu": CEU, "uf_cor": [255, 255, 255, 110], "uf_largura": 1.6, "colunas": colunas,
     "camera": camera, "sat": SAT, "imagens": imagens, "pontos": pontos, "estados": estados, "pinos": pinos, "telas": telas,
     "hero": hero, "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(fogo)} pontos de fogo")
