#!/usr/bin/env python3
"""Monta cena.js do "Clima do dia" de 13/10/2026 a partir de tempos.json (palavras da narração),
do boletim de meteorologia do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS),
dos avisos do INMET e dos focos do INPE (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual refeito em 13/10 (Nei): capa do Codex no quadro 0 (capa-dia/abertura.png), voo ao Pacífico com a anomalia do mar
(GHRSST MUR 12/10, sat/web/anomalia.png sobre sat/web/mundo.jpg), colunas 3D da chuva prevista (coleta_colunas.py → Open-Meteo),
foto de granizo (capa-dia/granizo.png, ilustração) e o total de focos do Brasil depois do Pará.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "13/10/2026"
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
SULC = {"lon": -51.0, "lat": -27.6, "zoom": 5.15}   # f1 (fim) e f5: colunas 3D sobre PR, SC e norte do RS
PAC = {"lon": -112.0, "lat": -5.0, "zoom": 2.6}     # f2/f9: Pacífico equatorial, de -175 a -50
PERU = {"lon": -92.0, "lat": -6.0, "zoom": 3.3}     # f2: perto do Peru (Niño 1+2)
ATL = {"lon": -53.0, "lat": -33.5, "zoom": 3.6}     # f2: água fria no Atlântico, perto da foz do Prata
SUL = {"lon": -50.8, "lat": -26.4, "zoom": 5.6}     # f3: PR e SC, vales do Iguaçu e do Rio Negro
PRSP = {"lon": -51.6, "lat": -24.0, "zoom": 5.2}    # f4: alerta laranja de hoje (PR, SP, MS)
CSE = {"lon": -46.5, "lat": -16.5, "zoom": 4.35}    # f6: Centro-Oeste, Sudeste, Matopiba, Irecê
CSUL = {"lon": -50.5, "lat": -23.0, "zoom": 4.4}    # f7: frio no centro-sul
PA = {"lon": -53.5, "lat": -6.5, "zoom": 5.0}       # f8: Pará (fogo)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
SUL1 = em("f1", "Sul")
camera = [
    K(0, BR), K(CAPA, BR), K(SUL1 - .2, {**BR, "zoom": 3.9}, 10, 0),
    K(SUL1 + 1.2, SULC, 52, -18), K(fim("f1") - .2, {**SULC, "zoom": 5.2}, 55, -4),
    K(ini("f2") + 1.6, PAC, 0, 0), K(em("f2", "Perto") - .1, {**PAC, "lon": -108.0}, 0, 0),
    K(em("f2", "Perto") + 1.0, PERU, 15, 0), K(em("f2", "Atlântico") - .3, {**PERU, "lon": -90.0}, 18, 3),
    K(em("f2", "Atlântico") + 1.1, ATL, 20, 0), K(fim("f2") - .2, {**ATL, "lon": -53.6}, 22, 3),
    K(ini("f3") + 1.0, SUL, 40, -10), K(fim("f3") - .2, {**SUL, "lon": -50.6}, 45, 6),
    K(ini("f4") + 1.0, PRSP, 30, -6), K(fim("f4") - .2, {**PRSP, "lon": -51.3}, 34, 4),
    K(ini("f5") + .6, SULC, 55, -22), K(fim("f5") - .2, {**SULC, "zoom": 5.25}, 58, 22),
    K(ini("f6") + 1.0, CSE, 10, -3), K(fim("f6") - .2, {**CSE, "lon": -46.2}, 12, 3),
    K(ini("f7") + 1.0, CSUL, 15, 0), K(fim("f7") - .2, {**CSUL, "zoom": 4.3}, 15, 2),
    K(ini("f8") + 1.0, PA, 6, -2), K(em("f8", "focos") + .2, {**PA, "lon": -53.2}, 8, 2),
    K(ini("f9") + 1.0, {**BR, "zoom": 3.7}, 0, 0), K(ini("f9") + 2.8, PAC, 0, 0), K(fim("f9") - .2, {**PAC, "lon": -106.0}, 0, 0),
    K(ini("f10") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
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
              "ini": CAPA - .6, "fim": SUL1 + 1.0, "dur": SUL1 - CAPA + .6, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- Pacífico: anomalia da temperatura do mar (GHRSST MUR 12/10 via NASA GIBS) sobre o Blue Marble
MUNDO = {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
ANOM = {"src": "sat/web/anomalia.png", "bbox": [-180, -66, -20, 30], "alfa": .85}
imagens = [{**MUNDO, "ini": em("f2", "Pacífico") - .3, "fim": ini("f3") + .6, "fade": 1.0},
           {**ANOM, "ini": em("f2", "Pacífico") - .3, "fim": ini("f3") + .6, "fade": 1.0},
           {**MUNDO, "ini": ini("f9") + 1.2, "fim": ini("f10") + .6, "fade": 1.0},
           {**ANOM, "ini": ini("f9") + 1.2, "fim": ini("f10") + .6, "fade": 1.0}]

# ---------------------------------------------------------------- colunas 3D: chuva prevista de 13 a 28/10 (Open-Meteo, coleta_colunas.py)
CO = json.loads((B / "colunas_sul_16d.json").read_text())
assert CO["dias"][0] == "2026-10-13" and len(CO["pontos"]) > 100, (CO["dias"][0], len(CO["pontos"]))
FIM_PREV = datetime.strptime(CO["dias"][-1], "%Y-%m-%d").strftime("%d/%m")
TOPO = max(CO["pontos"], key=lambda q: q["mm"])
cor_mm = lambda mm: [150, 215, 255] if mm < 150 else [60, 150, 255] if mm < 300 else [120, 90, 255]
col = [{"id": i, "p": [q["lon"], q["lat"]], "v": q["mm"], "cor": cor_mm(q["mm"]), "uf": q["uf"]} for i, q in enumerate(CO["pontos"])]
# f1 (gancho): todas sobem juntas, de norte a sul; f5: cada estado sobe quando é dito
ordem_f1 = {c["id"]: (-c["p"][1] - 22.5) * .12 for c in col}
quando = {"PR": em("f5", "Paraná"), "SC": em("f5", "Catarina"), "RS": em("f5", "gaúcho")}
ordem_f5 = {c["id"]: max(0, quando[c["uf"]] - .3 - ini("f5")) for c in col}
colunas = [{"id": "f1", "ini": SUL1, "fim": ini("f2") + .5, "dados": col, "raio": 13000, "escala": 1300, "ordem": ordem_f1, "varredura": 1},
           {"id": "f5", "ini": ini("f5"), "fim": ini("f6") + .5, "dados": col, "raio": 13000, "escala": 1300, "ordem": ordem_f5, "varredura": 1}]

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e granizo
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": em("f4", "granizo") - .1, "fim": ini("f5") + .3, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/granizo.png", "ini": em("f7", "granizo") - .1, "fim": ini("f8") + .1, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- focos de 12/10 (INPE: pontos VIIRS em grade de 0,08°; conta pelo AQUA)
grade, ref, ref_pa = {}, 0, 0
with open(B / "inpe_focos_diario_br_20261012.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            ref_pa += r["estado"].strip().upper() == "PARÁ"
assert (ref, ref_pa) == (1401, 1064), (ref, ref_pa)
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f8"), "fim": ini("f9") + 2.0, "dados": fogo, "dur": 3.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
HOJE = ufs_av(56056)     # tempestade laranja 13/10: 499 (PR 341, SP 123, MS 34, SC 1)
assert len(geo(56056)) == 499, len(geo(56056))
assert sum(c[:2] == "41" for c in geo(56056)) == 341
assert aviso[56056]["severidade"] == "Perigo" and aviso[56056]["descricao"] == "Tempestade"
# regiões do boletim (Meteorologia 13/10/2026)
SUL_CHUVA = ["PR", "SC", "RS"]
CENTRO_SUL = ["MS", "GO", "MT", "DF", "SP", "MG", "RJ", "ES", "MA", "TO", "PI", "BA"]
FRIO_CS = ["RS", "SC", "PR", "SP", "MS", "MG", "RJ", "ES", "GO", "DF"]
estados = [
    {"id": "sul", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["PR", "SC"], "cor": AZUL, "alfa": .5},
    {"id": "hoje", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": HOJE, "cor": LAR, "alfa": .55},
    {"id": "sul31", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": SUL_CHUVA, "cor": AZUL, "alfa": .22},
    {"id": "cs", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": CENTRO_SUL, "cor": AZUL, "alfa": .42},
    {"id": "frio", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": FRIO_CS, "cor": FRIO, "alfa": .42},
    {"id": "seco", "ini": ini("f8"), "fim": ini("f9") + 2.0, "ufs": ["AM", "PA"], "cor": [255, 90, 20], "alfa": .3},
]

pinos = [
    {"nome": "PACÍFICO EQUATORIAL", "sub": "até +2,8 °C acima do normal", "lon": -128.0, "lat": 0.0, "ini": em("f2", "2,8") - .2, "fim": em("f2", "Perto") + .3, "h": 150},
    {"nome": "PERTO DO PERU +4,7 °C", "sub": "acima do normal (Niño 1+2)", "lon": -84.0, "lat": -4.0, "ini": em("f2", "Perto"), "fim": em("f2", "Atlântico") + .2, "h": 170},
    {"nome": "ÁGUA FRIA NO ATLÂNTICO", "sub": "puxa o frio pro centro-sul", "lon": -51.0, "lat": -38.5, "ini": em("f2", "Atlântico") + .5, "fim": ini("f3"), "h": 150},
    {"nome": "Vale do Iguaçu", "sub": "União da Vitória (PR)", "lon": -51.09, "lat": -26.23, "ini": em("f3", "Iguaçu"), "fim": ini("f4"), "h": 160},
    {"nome": "Vale do Rio Negro", "sub": "Rio Negro (PR) · Mafra (SC)", "lon": -49.8, "lat": -26.1, "ini": em("f3", "Negro"), "fim": ini("f4"), "h": 230},
    {"nome": f"{TOPO['mm']:.0f} mm".replace(".", ","), "sub": f"o ponto mais chuvoso até {FIM_PREV} (previsão)", "lon": TOPO["lon"], "lat": TOPO["lat"],
     "ini": em("f5", "gaúcho"), "fim": ini("f6"), "h": 260},
    {"nome": "Irecê (BA)", "sub": "chuva até 31/10", "lon": -41.86, "lat": -11.3, "ini": em("f6", "Irecê"), "fim": ini("f7"), "h": 170},
    {"nome": "São Paulo", "sub": "30 dias bem acima do normal", "lon": -46.63, "lat": -23.55, "ini": em("f6", "Paulo"), "fim": ini("f7"), "h": 170},
    {"nome": "Pará", "sub": "1.064 focos em 12/10", "lon": -52.2, "lat": -3.8, "ini": em("f8", "Pará"), "fim": em("f8", "focos") + .5, "h": 160},
    {"nome": "EL NIÑO 2,2", "sub": "até pelo menos o inverno de 2027", "lon": -120.0, "lat": 0.0, "ini": ini("f9") + 3.0, "fim": ini("f10"), "h": 150},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
conta = lambda ate, fid, palavra, cor, unid, dec=0, lead=LEAD: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, palavra) - lead, "dur": lead, "cor": cor, "unid": unid}
hero = [{"ini": CAPA - .2, "fim": SUL1 - .1,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">CLIMA DO DIA</div>'
                 '<div class="t1" style="font-size:112px">EL NIÑO 2,2</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">o começo mais forte entre os grandes</div>'}]
FOCOS_A = em("f8", "focos") + .5   # o Pará vira o total do Brasil
paineis = [
    {"ini": SUL1, "fim": ini("f2"), "k": "SUL · PR · SC · NORTE DO RS",
     "contador": conta(15, "f1", "15", "#5ec8ff", "DIAS"),
     "l": "chuva de um mês em menos de 15 dias (previsão)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "PACÍFICO · MAR ACIMA DO NORMAL",
     "contador": conta(2.8, "f2", "2,8", "#ff2a1f", "°C", dec=1),
     "l": "vermelho = mar mais quente que o normal · perto do Peru: +4,7 °C", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "SUL · SOLO ENCHARCADO",
     "itens": [{"t": em("f3", "enchente"), "txt": "🌊 já teve enchente no Paraná"},
               {"t": em("f3", "Iguaçu"), "txt": "⚠️ vales do Iguaçu e do Rio Negro"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE · ALERTA LARANJA DE TEMPESTADE",
     "contador": conta(499, "f4", "499", "#ff8c1a", "CIDADES"),
     "l": "PR 341 · SP 123 · MS 34 · SC 1 — vento de 60 a 100 km/h e granizo", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": f"PREVISÃO · CHUVA SOMADA ATÉ {FIM_PREV}",
     "contador": {"de": 0, "ate": round(TOPO["mm"]), "dec": 0, "ini": em("f5", "Paraná") - .2, "dur": em("f5", "gaúcho") - em("f5", "Paraná") + .2, "cor": "#5ec8ff", "unid": "MM"},
     "l": "no ponto mais chuvoso · cada coluna = chuva prevista · PR, SC e norte do RS: chuva de um mês", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "CHUVA NO CENTRO-SUL (PREVISÃO)",
     "itens": [{"t": em("f6", "Centro-Oeste"), "txt": "🌧️ Centro-Oeste e Sudeste"},
               {"t": em("f6", "Matopiba"), "txt": "🌱 Matopiba, até Irecê (BA)"},
               {"t": em("f6", "Paulo"), "txt": "📈 São Paulo: 30 dias bem acima do normal"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "PRIMAVERA FRIA NO CENTRO-SUL",
     "itens": [{"t": em("f7", "frio"), "txt": "❄️ até 18/10: entra ar frio"},
               {"t": em("f7", "semanas"), "txt": "❄️ 19 a 25/10: predomina o frio"},
               {"t": em("f7", "granizo"), "txt": "⛈️ granizo, vento e temporal"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f8"), "fim": FOCOS_A, "k": "AMAZÔNIA · SECA E FOGO · 12/10",
     "contador": conta(1064, "f8", "1.064", "#ff5a14", "FOCOS NO PARÁ"),
     "l": "segunda-feira, 12/10 · INPE", "borda": "rgba(255,90,20,.7)"},
    {"ini": FOCOS_A, "fim": ini("f9") + 1.6, "k": "BRASIL INTEIRO · 12/10",
     "contador": {"de": 1064, "ate": 1401, "dec": 0, "ini": FOCOS_A, "dur": .8, "cor": "#ff5a14", "unid": "FOCOS NO BRASIL"},
     "l": "segunda-feira, 12/10 · INPE", "borda": "rgba(255,90,20,.7)"},
    {"ini": ini("f9") + 1.6, "fim": ini("f10"), "k": "EL NIÑO · ATÉ QUANDO?",
     "itens": [{"t": ini("f9") + 1.6, "txt": "🌡️ já em 2,2: o começo mais forte entre os grandes"},
               {"t": em("f9", "inverno"), "txt": "📅 até pelo menos o inverno de 2027"}],
     "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "onde"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f10", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
     "borda": "rgba(250,204,21,.8)"},
]
for a, b in zip(paineis, paineis[1:]):
    assert a["fim"] <= b["ini"] + 1e-6, (a["k"], b["k"])
    if a.get("contador"):
        c = a["contador"]
        assert a["ini"] - .01 <= c["ini"] and c["ini"] + c["dur"] <= a["fim"], ("contador fora do painel", a["k"])

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

ANOM_F = "anomalia da temperatura do mar em 12/10/2026: GHRSST MUR (<b>NOAA</b> · <b>NASA</b> GIBS), vermelho = mais quente que o normal"
fontes = [
    {"ini": CAPA, "fim": SUL1, "html": f"Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 12/10 18h a 13/10 18h · El Niño: <b>{MET}</b>"},
    {"ini": SUL1, "fim": ini("f2"), "html": f"Colunas: chuva prevista de 13 a {FIM_PREV} (<b>Open-Meteo</b>) · chuva de um mês em menos de 15 dias: <b>{MET}</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"{ANOM_F} · índices do El Niño: <b>{MET}</b>"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INMET</b>, aviso laranja de tempestade para 13/10 (499 municípios): 30 a 60 mm/h, vento de 60 a 100 km/h e granizo · foto: ilustração"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"Colunas: chuva prevista de 13 a {FIM_PREV}, grade de 0,5° (<b>Open-Meteo</b>) · chuva de um mês até 31/10: <b>{MET}</b>"},
    {"ini": ini("f6"), "fim": ini("f8"), "html": f"<b>{MET}</b> · previsão de chuva e temperatura até o fim de outubro · foto do granizo: ilustração"},
    {"ini": ini("f8"), "fim": ini("f9") + 1.2, "html": f"Focos: <b>INPE</b> Programa Queimadas, 12/10 (satélite de referência AQUA) · foco não é igual a incêndio · seca: <b>{MET}</b>"},
    {"ini": ini("f9") + 1.2, "fim": ini("f10"), "html": f"{ANOM_F} · <b>{MET}</b>"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"focos": "#ff5a14", "queimando": "#ff5a14", "seca": "#ff8c1a", "chuva": "#5ec8ff", "enchente": "#5ec8ff", "encharcado": "#5ec8ff",
         "tempestade": "#ff8c1a", "vento": "#5ec8ff", "granizo": "#ff8c1a", "temporal": "#ff8c1a", "alerta": "#ff8c1a", "laranja": "#ff8c1a",
         "frio": "#96d2ff", "frias": "#96d2ff", "graus": "#ff2a1f", "el": "#ff2a1f", "nino": "#ff2a1f", "comenta": AM,
         "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "norte", "pacifico", "peru", "atlantico", "centrosul", "parana", "iguacu", "rio", "negro", "santa", "catarina", "gaucho",
         "centrooeste", "sudeste", "matopiba", "irece", "bahia", "sao", "paulo", "amazonia", "para", "inemaclub", "onde"}
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
     "marca": "INEMA · CLIMA DO DIA", "selo": DATA[:5] + " · INMET · INPE · NOAA",
     "camera": camera, "sat": SAT, "imagens": imagens, "colunas": colunas, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · {len(fogo)} pontos de fogo · "
      f"tempestade hoje {HOJE}")
