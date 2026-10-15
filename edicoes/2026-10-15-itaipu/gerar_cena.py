#!/usr/bin/env python3
"""Monta cena.js de "E se Itaipu rompesse?" (16:9 largo com avatar, 15/10/2026) a partir de tempos.json.
Estudo: Levis & Palú (UFPR), ABRHidro 2024 — cenário hipotético (cheia de 10 mil anos + 6 de 14 comportas falhando).
Chuva: Open-Meteo (pesquisa/bruto/grade.json, grade 0,5°): 01/09–14/10 de 2026 × 2024 e previsão 15–30/10.
Fatos de outubro: Itaipu via Oeste Agora (13/10) e O Presente (14/10); Cataratas via Estadão (12/10). Ver pesquisa/web.md.
Prévia: python3 estimar.py && python3 gerar_cena.py · com avatar: gerar_cena.py --avatar e LAYOUT=largo motor/compor_avatar.sh"""
import difflib, json, os, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "15/10/2026"
AVATAR = "--avatar" in sys.argv
T = json.loads((AQUI / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())
G = json.loads((AQUI / "pesquisa/bruto/grade.json").read_text())["pts"]


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
        if n(palavra) == n(p["w"]) or (len(n(palavra)) > 3 and n(palavra) in n(p["w"])):
            achou += 1
            if achou == k:
                return p["t"]
    raise KeyError(f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in FALA[fid]["palavras"]))


ini = lambda fid: FALA[fid]["ini"]
fim = lambda fid: FALA[fid]["fim"]
chega = lambda fid, pal, k=1: round(em(fid, pal, k) - 1.0, 3)   # contador CHEGA ao número quando a palavra é dita
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
FOTO = 2.6

# ---------------------------------------------------------------- câmera (avatar ocupa x 1280–1920; padding_dir 640)
BACIA = {"lon": -52.6, "lat": -23.6, "zoom": 5.75}
ITAIPU = {"lon": -54.56, "lat": -25.38, "zoom": 9.0}
TRI = {"lon": -54.59, "lat": -25.53, "zoom": 10.4}
JUS = {"lon": -55.4, "lat": -26.5, "zoom": 7.3}
OESTE = {"lon": -54.0, "lat": -25.0, "zoom": 7.4}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BACIA, 20, -6), K(ini("f2") - .3, {**BACIA, "zoom": 6.0}, 25, 0),
    K(ini("f2") + 2.5, ITAIPU, 50, -12), K(fim("f2"), {**ITAIPU, "zoom": 9.4}, 55, 8),
    K(fim("f3") - .3, {**ITAIPU, "zoom": 9.6}, 50, 14),
    K(ini("f4") + 1.2, TRI, 45, -6), K(fim("f4") - .3, {**TRI, "zoom": 10.7}, 50, 8),
    K(ini("f5") + 1.4, JUS, 40, -10), K(fim("f5") - .3, {**JUS, "zoom": 7.0}, 40, 4),
    K(ini("f6") + 1.0, ITAIPU, 45, 0), K(fim("f6") - .3, {**ITAIPU, "zoom": 9.2}, 50, -10),
    K(ini("f7") + FOTO + .8, BACIA, 35, -6), K(fim("f7") - .3, OESTE, 45, 6),
    K(em("f8", "segura") + .4, TRI, 45, -8), K(fim("f8") - .3, {**TRI, "zoom": 10.0}, 45, 6),
    K(ini("f9") + 1.0, BACIA, 30, 0), K(fim("f9") - .3, {**BACIA, "zoom": 5.9}, 40, -8),
    K(ini("f10") + 1.0, {**BACIA, "zoom": 5.4}, 20, 0), K(fim("f10"), ITAIPU, 45, 6),
    K(ini("f11") + 1.2, {**OESTE, "zoom": 6.6}, 30, -4), K(DUR, {**OESTE, "zoom": 6.9}, 35, 6),
]

SAT = {"base": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
NUVEM = {"src": "sat/web/geocolor.jpg", "bbox": [-58.5, -28.5, -46, -18]}
imagens = [{**NUVEM, "ini": ini("f7") + FOTO, "fim": em("f7", "Cascavel") + .5, "fade": .8},
           {**NUVEM, "ini": ini("f9"), "fim": em("f9", "Mas") , "fade": .6}]

# ---------------------------------------------------------------- chuva (Open-Meteo, mm)
dias = G[0]["dias"]; i14 = dias.index("2026-10-14"); i01 = dias.index("2026-10-01"); i22 = dias.index("2026-10-22")
soma = lambda v, a, b: sum(x or 0 for x in v[a:b])
AZUL, CIANO, ROXO = [70, 150, 255], [94, 200, 255], [190, 120, 255]
obs = [{"id": f"o{k}", "p": p["p"], "v": soma(p["chuva"], 0, i14 + 1)} for k, p in enumerate(G)]
obs24 = [{"id": f"a{k}", "p": p["p"], "v": soma(p["chuva24"], 0, 44)} for k, p in enumerate(G)]
prev = [{"id": f"p{k}", "p": p["p"], "v": soma(p["chuva"], i22 - 1, len(dias))} for k, p in enumerate(G)]
ordem = lambda dd: {d["id"]: (d["p"][0] + 56) / 9 for d in dd}   # varre de oeste para leste
colunas = [
    {"id": "c24", "ini": em("f7", "mesmo"), "fim": em("f7", "Quase") + .3, "dados": obs24, "escala": 110,
     "raio": 9000, "cor": [150, 170, 190], "ordem": ordem(obs24), "varredura": .8},
    {"id": "c26", "ini": em("f7", "recebeu"), "fim": em("f7", "mesmo") + .2, "dados": obs, "escala": 110, "raio": 9000,
     "cor": AZUL, "ordem": ordem(obs), "varredura": 1.0},
    {"id": "c26b", "ini": em("f7", "Quase"), "fim": fim("f7") + .3, "dados": obs, "escala": 110, "raio": 9000,
     "cor": AZUL, "ordem": {}, "varredura": 0},
    {"id": "prev", "ini": em("f9", "voltando"), "fim": fim("f9") + .2, "dados": prev, "escala": 110, "raio": 9000,
     "cor": ROXO, "ordem": ordem(prev), "varredura": 1.0},
]

# rio Paraná desenhado até a Tríplice Fronteira e rio abaixo
rios = [{"nome": "Paraná", "ini": ini("f2") + 1.0, "fim": fim("f6"), "dur": 2.4, "largura": 6},
        {"nome": "Paraná", "ini": em("f8", "segura"), "fim": fim("f8"), "dur": 1.2, "largura": 6}]

P = lambda nome, sub, lon, lat, a, b, h=110: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Itaipu", "196 m · 29 bilhões de m³", -54.589, -25.408, ini("f2") + 2.0, fim("f3"), 140),
    P("Ciudad del Este · PY", "578 ha alagados (cenário)", -54.635, -25.505, em("f4", "Ciudad"), fim("f4"), 150),
    P("Foz do Iguaçu · BR", "361 ha", -54.565, -25.540, em("f4", "Foz"), fim("f4"), 105),
    P("Puerto Iguazú · AR", "153 ha", -54.570, -25.600, em("f4", "Puerto"), fim("f4"), 70),
    P("Presidente Franco · PY", "fora da conta", -54.611, -25.563, em("f5", "Presidente"), fim("f5"), 90),
    P("Encarnación · PY", "fora da conta", -55.866, -27.330, em("f5", "Encarnación"), fim("f5"), 170),
    P("Posadas · AR", "fora da conta", -55.896, -27.367, em("f5", "Posadas"), fim("f5"), 95),
    P("Yacyretá", "usina rio abaixo", -56.43, -27.48, em("f5", "Yacyretá"), fim("f5"), 40),
    P("Cascavel", "447 mm desde 1º/09", -53.455, -24.956, em("f7", "Cascavel"), fim("f7") + .3, 140),
    P("Cataratas", "11.800 m³/s em 12/10", -54.437, -25.695, em("f8", "segura"), fim("f8"), 120),
    P("Foz do Iguaçu", "áreas baixas em alerta", -54.565, -25.540, em("f8", "alerta"), fim("f8"), 90),
    P("Ciudad del Este", "áreas baixas em alerta", -54.635, -25.505, em("f8", "Ciudad"), fim("f8"), 140),
]

TELA = lambda src, a, b, selo="ilustração": {"src": f"capa/{src}", "ini": a, "fim": b, "fade": .5 if a > 0 else .3, "zoom": .06, "selo": selo}
telas = [
    {"src": "capa/abertura.png", "ini": -1.0, "fim": em("f1", "terça") - .1, "fade": .4, "zoom": .05},
    TELA("vertedouro.png", em("f1", "terça") - .1, em("f1", "pergunta") - .1),
    TELA("chuva-oeste.png", ini("f7") - .2, ini("f7") + FOTO),
    TELA("cataratas.png", ini("f8") - .2, em("f8", "segura") - .1),
    TELA("alagado.png", em("f8", "alerta") - .2, fim("f8")),
    TELA("ponte.png", ini("f11") - .2, ini("f11") + FOTO),
]

hero = [
    {"ini": em("f1", "pergunta"), "fim": em("f1", "UFPR") - .05,
     "html": f'<div style="font:400 72px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
             '<div class="dt" style="background:#ff2a1f;color:#fff">PERGUNTA DE MILHÕES</div>'
             '<div class="t1">E SE ITAIPU</div><div class="t2">ROMPESSE?</div>'
             '<div class="t4">vertedouro aberto desde 30/09 · Itaipu</div>'},
    {"ini": em("f1", "UFPR"), "fim": ini("f2") - .05,
     "html": '<div class="dt" style="background:#FACC15;color:#0b0f14">ESTUDO UFPR · 2024</div><div class="t1">ONDE A ÁGUA</div><div class="t2">CHEGARIA</div>'},
]

# ---------------------------------------------------------------- gráficos
mb = lambda f: round(sum(f(p) for p in G) / len(G))
oeste = [p for p in G if -55.5 <= p["p"][0] <= -52 and -26.5 <= p["p"][1] <= -23.5]
mo = lambda f: round(sum(f(p) for p in oeste) / len(oeste))
pt = lambda x, y: next(p for p in G if p["p"] == [x, y])
c26 = lambda p: soma(p["chuva"], 0, i14 + 1)
c24 = lambda p: soma(p["chuva24"], 0, 44)
CMP = [("bacia", mb(c24), mb(c26)), ("oeste PR", mo(c24), mo(c26)), ("Cascavel", round(c24(pt(-53.5, -25.0))), round(c26(pt(-53.5, -25.0)))),
       ("Foz", round(c24(pt(-54.5, -25.5))), round(c26(pt(-54.5, -25.5))))]
g_cmp = {"rotulos": sum([[nm, ""] for nm, _, _ in CMP], []), "marcar_x": [0, 2, 4, 6],
         "series": [{"nome": "2024 (01/09–14/10)", "cor": "#8a97a6", "v": sum([[a, 0] for _, a, _ in CMP], [])},
                    {"nome": "2026 (01/09–14/10)", "cor": "#4696ff", "v": sum([[0, b] for _, _, b in CMP], [])}],
         "unid": "mm", "ini": chega("f7", "299") - .4, "dur": 1.4}
DIAS = list(range(i01, len(dias)))
media_dia = [round(sum((p["chuva"][j] or 0) for p in G) / len(G), 1) for j in DIAS]
g_dia = {"rotulos": [dias[j][8:] for j in DIAS],
         "series": [{"nome": "chuva média na bacia (mm/dia)", "cor": "#4696ff", "v": media_dia}],
         "previsto_a_partir": DIAS.index(i14 + 1), "marcar": [0, 4, 9, 13, 14, 16, 20, 23, 26, 29], "unid": "mm",
         "ini": ini("f9") + .3, "dur": 1.6}

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
B_RED, B_ORG, B_YEL, B_BLU = "rgba(255,42,31,.7)", "rgba(255,140,26,.7)", "rgba(250,204,21,.7)", "rgba(94,200,255,.7)"
paineis = [
    {"ini": ini("f2"), "fim": ini("f3") - .05, "k": "ITAIPU EM NÚMEROS",
     "itens": [it("f2", "196", "📏 196 m de altura"), it("f2", "8", "🧱 7,9 km de barragem"),
               it("f2", "1.350", "🌊 lago de 1.350 km²"), it("f2", "29", "💧 29 bilhões de m³")], "borda": B_BLU,
     "l": "Itaipu Binacional · potência de 14.000 MW"},
    {"ini": ini("f3"), "fim": em("f3", "ruptura") - .25, "k": "O CENÁRIO DO ESTUDO (HIPOTÉTICO)",
     "itens": [it("f3", "10", "🌧️ cheia de 10 mil anos"), it("f3", "6", "⚙️ 6 de 14 comportas falham"),
               it("f3", "terra", "🧱 água passa por cima da barragem de terra")], "borda": B_ORG,
     "l": "51.451 m³/s chegando ao lago · brecha de 648 m formada em 0,72 h"},
    {"ini": em("f3", "ruptura"), "fim": ini("f4") - .05, "k": "PICO DA RUPTURA · CENÁRIO HIPOTÉTICO",
     "contador": {"de": 0, "ate": 221149, "dec": 0, "ini": chega("f3", "221"), "dur": 1.0, "cor": "#ff2a1f", "unid": "m³/s"},
     "l": "o vertedouro inteiro aguenta 62.200 m³/s", "borda": B_RED},
    {"ini": ini("f4"), "fim": ini("f5") - .05, "k": "ÁREA URBANA ALAGADA NO CENÁRIO · HECTARES",
     "ranking": {"itens": [{"nome": "Ciudad del Este · PY", "v": 578}, {"nome": "Foz do Iguaçu · BR", "v": 361},
                           {"nome": "Puerto Iguazú · AR", "v": 153}],
                 "cor": "#ff8c1a", "cor_top": "#ff2a1f", "unid": " ha", "ini": chega("f4", "578"), "dur": 2.6},
     "l": "39,54 km² no trecho até Puerto Iguazú (fora a calha do rio)", "borda": B_RED},
    {"ini": ini("f5"), "fim": ini("f6") - .05, "k": "O QUE O ESTUDO NÃO CALCULOU",
     "itens": [it("f5", "Encarnación", "🏙️ cidades rio abaixo"), it("f5", "Yacyretá", "⚡ a usina de Yacyretá"),
               it("f5", "vítimas", "👥 vítimas"), it("f5", "chegada", "⏱️ tempo de chegada da onda"),
               it("f5", "encaixado", "⛰️ vale encaixado: água funda e rápida")], "borda": B_YEL},
    {"ini": ini("f6"), "fim": ini("f7") - .25, "k": "ONDE ESTÃO OS RISCOS",
     "itens": [it("f6", "cheia", "🌊 cheia extrema"), it("f6", "erosão", "🕳️ erosão interna"),
               it("f6", "fundação", "🪨 fundação"), it("f6", "terremoto", "🌐 terremoto"),
               it("f6", "várias", "⚠️ falhas ao mesmo tempo"), it("f6", "normal", "✅ revisão 2022: condição normal")],
     "l": "risco muito baixo, não é zero · sem nota numérica pública", "borda": B_ORG},
    {"ini": ini("f7") + FOTO, "fim": ini("f8") - .25, "k": "CHUVA DE 01/09 A 14/10 · 2024 × 2026 · MM",
     "grafico": g_cmp, "l": f"bacia: {mb(c26)} mm em 2026 × {mb(c24)} mm em 2024 · {mb(c26) / mb(c24):.1f}×".replace(".", ","), "borda": B_BLU},
    {"ini": ini("f8"), "fim": em("f8", "segura") - .25, "k": "CATARATAS DO IGUAÇU · VAZÃO",
     "contador": {"de": 1500, "ate": 11800, "dec": 0, "ini": chega("f8", "11.800"), "dur": 1.0, "cor": "#ff2a1f", "unid": "m³/s"},
     "l": "12/10/2026, o maior do ano · média: 1.500 m³/s · passarela fechada", "borda": B_RED},
    {"ini": em("f8", "segura"), "fim": ini("f9") - .05, "k": "RIO PARANÁ NA TRÍPLICE FRONTEIRA",
     "itens": [it("f8", "segura", "🔀 Iguaçu cheio segura o Paraná"), it("f8", "121", "📈 cota passou de 121 m (14/10)"),
               it("f8", "alerta", "⚠️ áreas baixas em alerta")], "borda": B_RED},
    {"ini": ini("f9"), "fim": ini("f10") - .25, "k": "CHUVA NA BACIA, DIA A DIA · OUTUBRO 2026",
     "grafico": g_dia, "l": "hachurado = previsão · 17 a 20/10 trégua · 22 a 30/10: +138 mm em média (tendência)", "borda": B_BLU},
    {"ini": ini("f10"), "fim": em("f10", "escala") - .25, "k": "EL NIÑO OUT–DEZ 2026",
     "contador": {"de": 0, "ate": 98, "dec": 0, "ini": chega("f10", "98%"), "dur": .9, "cor": "#ff2a1f", "unid": "%"},
     "l": "chance de El Niño muito forte (NOAA) · chuva acima da média no Sul (Inmet/Inpe)", "borda": B_RED},
    {"ini": em("f10", "escala"), "fim": ini("f11") - .05, "k": "A ESCALA · M³/S",
     "ranking": {"itens": [{"nome": "ruptura (cenário)", "v": 221149}, {"nome": "vertedouro aguenta", "v": 62200},
                           {"nome": "cheia do cenário", "v": 51451}, {"nome": "vertedouro em 13/10", "v": 11300}],
                 "cor": "#5ec8ff", "cor_top": "#ff2a1f", "unid": "", "ini": chega("f10", "18%"), "dur": 2.0},
     "l": "13/10: cerca de 18% da capacidade do vertedouro", "borda": B_YEL},
    {"ini": ini("f11") + FOTO, "fim": em("f11", "conta") - .05, "k": "O QUE VOCÊ FAZ",
     "itens": [it("f11", "avisos", "📢 avisos da Defesa Civil"), it("f11", "40199", "📱 CEP por SMS no 40199"),
               it("f11", "ir", "🧭 saiba para onde ir")], "borda": B_RED},
    {"ini": em("f11", "conta"), "fim": em("f11", "inema.club") - .05, "k": "COMENTA AQUI 👇",
     "itens": [it("f11", "região", "🗺️ de que região você é?"), it("f11", "cidade", "🏙️ de que cidade?")], "borda": B_YEL},
]

cta = {"ini": em("f11", "inema.club"), "fim": DUR, "a": "MANDA PRA QUEM MORA NA BEIRA DO PARANÁ",
       "b": "Itaipu: estudo hipotético + chuva de 2026 quase 3× a de 2024."}
club = {"ini": em("f11", "inema.club"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

ESTUDO = "<b>Levis &amp; Palú (UFPR)</b>, Simulação de Ruptura Hipotética da UHE Itaipu, ABRHidro 2024 · cenário acadêmico, não é mapa de evacuação"
fontes = [
    {"ini": .5, "fim": ini("f2"), "html": "<b>Itaipu</b> via Oeste Agora (13/10/2026): 2ª calha aberta, 11,3 mil m³/s · vertedouro aberto desde 30/09 (Correio do Lago/G1)"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>Itaipu Binacional</b> · mapa: NASA Blue Marble, Natural Earth"},
    {"ini": ini("f3"), "fim": ini("f6"), "html": ESTUDO},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "Estudo de cenário, out/2026 · revisão de segurança de 2022: condição global normal"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>Open-Meteo</b> (reanálise), média da grade de 0,5° na bacia do Paraná/Iguaçu acima de Itaipu · satélite: <b>NASA GIBS</b> GOES-19, 14/10/2026"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Cataratas: Estadão (12/10/2026) · rio Paraná: Itaipu via O Presente (14/10/2026)"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": "<b>Open-Meteo</b> previsão de 16 dias (lida em 15/10) · trégua: Comissão de Cheias da Itaipu via O Presente · dias 8–16 = tendência"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": "<b>NOAA</b>/CPC e Inpe via Revista Cultivar (20/09/2026) · " + ESTUDO},
    {"ini": ini("f11"), "fim": DUR, "html": "Defesa Civil 199 · alerta por SMS: CEP para 40199"},
]

CORES = {"rompesse": "#ff2a1f", "ruptura": "#ff2a1f", "pior": "#ff2a1f", "falhando": "#ff2a1f", "alagados": "#ff2a1f",
         "agua": "#5ec8ff", "chuva": "#5ec8ff", "cheia": "#ff8c1a", "vertedouro": "#ff8c1a", "risco": "#ff2a1f", "zero": "#ff2a1f",
         "alerta": "#ff2a1f", "nino": "#ff2a1f", "elnino": "#ff2a1f", "tregua": "#5ec8ff", "tendencia": "#FACC15",
         "regiao": "#FACC15", "cidade": "#FACC15", "comentarios": "#FACC15"}
LUGAR = {"itaipu", "ufpr", "ciudad", "del", "este", "paraguai", "foz", "iguacu", "puerto", "iguazu", "argentina", "presidente",
         "franco", "encarnacion", "posadas", "yacyreta", "cascavel", "cataratas", "parana", "sul", "inemaclub", "noaa"}
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
     "marca": "INEMA · E SE ITAIPU ROMPESSE?", "selo": "ESTUDO UFPR + CHUVA · " + DATA[:5],
     "camera": camera, "sat": SAT, "imagens": imagens, "colunas": colunas, "rios": rios, "pontos": [], "pinos": pinos, "telas": telas,
     "hero": hero, "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · comparação {CMP}")
