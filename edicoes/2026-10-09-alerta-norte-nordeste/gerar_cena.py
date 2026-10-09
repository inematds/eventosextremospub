#!/usr/bin/env python3
"""Monta cena.js (linha do tempo do mapa) a partir de tempos.json (palavras da narração),
dos alertas do INMET (fonte/alertas_nne.json), dos focos do INPE (fonte/focos/), da grade do
Open-Meteo (om/calor7.json) e da base pesquisada (base.md).
Render: GEO=geo-nne.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto (ou --avatar) usa avatar/tempos.json; depois GEO=geo-nne.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parents[1]
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())
AL = json.loads((AQUI / "fonte/alertas_nne.json").read_text())
GEO = json.loads((REPO / "motor/geo-nne.js").read_text()[len("window.GEO="):-1])
UFS = ("11", "12", "13", "14", "15", "16", "17", "21", "22", "23", "24", "25", "26", "27", "28", "29")


def n(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


COORD = {}
with open(REPO / "geo/municipios.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["codigo_uf"] in UFS:
            COORD[n(r["nome"]) + r["codigo_uf"]] = (float(r["longitude"]), float(r["latitude"]), r["codigo_ibge"])


def xy(nome, uf):
    return COORD[n(nome) + uf]


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

# ordem de varredura oeste→leste (0..1) por município
ORD = {f["properties"]["id"]: round((f["properties"]["c"][0] + 74) / 40, 3)
       for f in GEO["mun"]["features"] if f["properties"]["c"]}


def ids(aviso):
    return AL[aviso]["geocodes"]


VERM, LAR, AMA = [255, 42, 31], [255, 140, 26], [255, 214, 10]

# ---------------------------------------------------------------- câmera (9:16: N/NE inteiro é largo, então são 4 regiões)
TUDO = {"lon": -52.5, "lat": -7.5, "zoom": 4.35}
SERTAO = {"lon": -42.8, "lat": -9.6, "zoom": 5.55}
AMAZ = {"lon": -59.0, "lat": -3.6, "zoom": 5.15}
MANAUS = {"lon": -60.6, "lat": -2.6, "zoom": 6.1}
OESTE = {"lon": -65.0, "lat": -8.8, "zoom": 5.25}
K = lambda t, r, pitch=0, bearing=0, **kw: {"t": t, **r, **kw, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, TUDO),
    K(ini("f2") - .6, TUDO, 8, -2),
    K(ini("f2") + .8, {**SERTAO, "zoom": 5.2}, 30, -6),
    K(ini("f3") + .6, SERTAO, 50, -14),
    K(fim("f3") - .3, {**SERTAO, "lon": -43.6}, 55, -24),
    K(ini("f4") + 1.0, AMAZ, 35, -8),
    K(fim("f4") - .2, {**AMAZ, "lon": -58.0}, 45, 6),
    K(ini("f5") + 1.0, MANAUS, 50, -18),
    K(fim("f5") - .2, {**MANAUS, "lon": -60.0, "zoom": 6.0}, 55, -30),
    K(ini("f6") + 1.0, OESTE, 40, -10),
    K(fim("f6") - .2, {**OESTE, "lon": -64.0}, 45, 8),
    K(ini("f7") + 1.2, TUDO, 20, 0),
    K(ini("f8") + .5, {**TUDO, "zoom": 4.45}, 25, -8),
    K(ini("f9"), {**TUDO, "zoom": 4.5}, 28, 6),
    K(DUR, {**TUDO, "zoom": 4.6}, 30, 12),
]

# ---------------------------------------------------------------- alertas (cor = nível do INMET)
amarelo_hoje, laranja_hoje = ids("56030"), ids("56017")
tempestade = sorted(set().union(*[set(ids(k)) for k in ("56021", "56027", "56011", "56014")]))
alertas = [
    {"id": "seco-ama", "ini": -3.0, "fim": ini("f4") + .4, "ids": amarelo_hoje, "cor": AMA, "alfa": .45, "ordem": ORD, "varredura": .9},
    {"id": "seco-lar", "ini": -3.0, "fim": ini("f4") + .4, "ids": laranja_hoje, "cor": LAR, "alfa": .85, "ordem": ORD, "varredura": 1.0},
    {"id": "temp", "ini": ini("f6"), "fim": ini("f7") + .4, "ids": tempestade, "cor": AMA, "alfa": .55, "ordem": ORD, "varredura": .6},
    {"id": "fim-ama", "ini": ini("f7"), "fim": DUR, "ids": amarelo_hoje, "cor": AMA, "alfa": .4, "ordem": ORD, "varredura": .8},
    {"id": "fim-lar", "ini": ini("f7"), "fim": DUR, "ids": laranja_hoje, "cor": LAR, "alfa": .8, "ordem": ORD, "varredura": .9},
]

# ---------------------------------------------------------------- colunas: máxima prevista em 7 dias (Open-Meteo)
C7 = json.loads((AQUI / "om/calor7.json").read_text())["pts"]


def cor_t(t):
    return [255, 255, 255] if t >= 40 else [255, 60, 40] if t >= 38 else [255, 140, 26] if t >= 36 else [255, 214, 10] if t >= 34 else [120, 90, 60]


calor = []
for i, q in enumerate(C7):
    tm = max(t for t in q["tmax"] if t is not None)
    if tm >= 33:
        calor.append({"id": f"c{i}", "p": q["p"], "v": round(tm - 30, 1), "t": tm, "cor": cor_t(tm)})
quente = max(calor, key=lambda d: d["t"])
colunas = [{"id": "calor", "ini": ini("f3"), "fim": ini("f4") + .3, "dados": calor, "escala": 24000, "raio": 36000,
            "cor": [255, 140, 26], "ordem": {d["id"]: (d["p"][0] + 74) / 40 for d in calor}, "varredura": 1.2}]

# ---------------------------------------------------------------- pontos: focos de calor de 08/10 (INPE, VIIRS em grade de 0,08°)
grade = {}
with open(AQUI / "fonte/focos/focos_diario_br_20261008.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["estado_id"].strip() in UFS and r["satelite"].strip() in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)  # aparece de norte para sul
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f4"), "fim": ini("f6") + .3, "dados": fogo, "dur": 3.2, "raio": 2.6, "cor": [255, 90, 20]},
          {"id": "fogo2", "ini": ini("f7"), "fim": DUR, "dados": fogo, "dur": 2.0, "raio": 2.2, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- referência oficial dos focos (satélite AQUA_M-T)
ref = 0
with open(AQUI / "fonte/focos/focos_diario_br_20261008.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        ref += r["estado_id"].strip() in UFS and r["satelite"].strip() == "AQUA_M-T"
assert ref == 1731, ref


# ---------------------------------------------------------------- pinos
def pino(nome, uf, sub, a, b, h=110, rot=None):
    x, y, _ = xy(nome, uf)
    return {"nome": rot or nome, "sub": sub, "lon": x, "lat": y, "ini": a, "fim": b, "h": h}


pinos = [
    {"nome": "Centro do Piauí", "sub": "41,7 °C · umidade 11%", "lon": -41.5, "lat": -7.5, "ini": em("f3", "Piauí"), "fim": ini("f4"), "h": 300},
    {"nome": "Oeste da Bahia", "sub": "40,6 °C · umidade 10%", "lon": -43.5, "lat": -13.5, "ini": em("f3", "Bahia"), "fim": ini("f4"), "h": 230},
    pino("Manaus", "13", "debaixo de fumaça · 08/10", em("f4", "Manaus"), ini("f5"), 150),
    pino("Manaus", "13", "Rio Negro −5,21 m em setembro", ini("f5") + .6, ini("f6"), 170),
    pino("Rio Branco", "12", "tempestade · granizo", em("f6", "Acre"), ini("f7"), 110),
    pino("Porto Velho", "11", "vento de 40 a 60 km/h", em("f6", "Rondônia"), ini("f7"), 150),
]

SAT = {"base": "sat/web/geocolor.jpg", "bbox": [-82, -26, -26, 11], "tint": [175, 175, 175]}

# ---------------------------------------------------------------- textos
hero = [
    {"ini": 0, "fim": ini("f2") - .05,
     "html": '<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">09/10/2026</div>'
             '<div class="dt" style="background:#ff8c1a;color:#0b0f14">SEXTA · NORTE E NORDESTE</div>'
             '<div class="t1">AR DE</div><div class="t2" style="color:#ff8c1a">DESERTO</div>'
             '<div class="t3" style="color:#ffd23f;text-shadow:0 0 30px rgba(255,140,26,.6)">ATÉ 12%</div>'
             '<div class="t4">1.210 cidades em alerta de ar seco do INMET hoje</div>'},
    {"ini": ini("f7") + .1, "fim": ini("f8") - .05,
     "html": '<div class="dt" style="background:#ff2a1f;color:#fff">EL NIÑO MUITO FORTE</div>'
             '<div class="t1">PICO ATÉ</div><div class="t2">DEZEMBRO</div>'
             '<div class="t4">calor acima da média, chuva abaixo e o início da estação chuvosa pode atrasar</div>'},
]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "INMET · alerta laranja · sexta 09/10",
     "contador": {"de": 0, "ate": 474, "dur": 1.2, "cor": "#ff8c1a", "unid": "CIDADES"},
     "l": "umidade entre 20% e 12% · risco de incêndio e à saúde",
     "itens": [{"t": em("f2", "Bahia"), "txt": "BA · 152"}, {"t": em("f2", "Piauí"), "txt": "PI · 139"},
               {"t": em("f2", "Ceará"), "txt": "CE · 49 · PB · 44"}], "borda": "rgba(255,140,26,.6)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "PREVISÃO · máxima nos próximos 7 dias",
     "contador": {"de": 30, "ate": quente["t"], "dec": 1, "ini": ini("f3") + .3, "dur": 2.0, "cor": "#ffffff", "unid": "°C"},
     "l": "centro do PI e oeste da BA · 7 dias seguidos sem chuva prevista", "borda": "rgba(255,255,255,.4)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "JÁ ACONTECEU · focos de calor · quinta 08/10",
     "contador": {"de": 0, "ate": ref, "ini": ini("f4") + .4, "dur": 2.0, "cor": "#ff5a14", "unid": "FOCOS"},
     "l": "Norte e Nordeste num dia só · BA 524 · MA 464 · PI 311 · AM 138", "borda": "rgba(255,90,20,.6)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "RIO NEGRO EM MANAUS · setembro",
     "contador": {"de": 0, "ate": 5.21, "dec": 2, "ini": ini("f5") + .5, "dur": 1.8, "cor": "#5ec8ff", "unid": "METROS A MENOS"},
     "l": "24,09 → 18,88 m · pior cenário do SGB para outubro: 12,92 m · recorde: 12,66 m em 2024", "borda": "rgba(94,200,255,.5)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "INMET · tempestade · até terça 13/10",
     "contador": {"de": 0, "ate": len(tempestade), "dur": 1.2, "cor": "#ffd60a", "unid": "CIDADES"},
     "l": "AC, RO e sul do AM · 20 a 30 mm/h · vento de 40 a 60 km/h · granizo", "borda": "rgba(255,214,10,.6)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f8", "acontecendo"), "txt": "📍 Tá acontecendo aí?"}, {"t": em("f8", "Calor"), "txt": "🌡️ Calor?"},
               {"t": em("f8", "seco"), "txt": "💨 Ar seco?"}, {"t": em("f8", "fumaça"), "txt": "🔥 Fumaça?"},
               {"t": em("f8", "região"), "txt": "🗺️ Tua cidade e região"}],
     "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f9"), "fim": em("f9", "prepara") - .1, "k": "SE PROTEGE HOJE",
     "itens": [{"t": em("f9", "água"), "txt": "💧 bebe água"}, {"t": em("f9", "sol"), "txt": "☀️ sem sol ao meio-dia"},
               {"t": em("f9", "queima"), "txt": "🚫🔥 não queima nada"}],
     "borda": "rgba(255,42,31,.7)"},
]

cta = {"ini": em("f9", "prepara"), "fim": DUR, "a": "PREPARA TAMBÉM O TEU TRABALHO",
       "b": "Cursos gratuitos de tecnologia e IA para aprender uma profissão nova."}
club = {"ini": em("f9", "inema"), "fim": DUR, "a": "inema.club", "b": "grátis · manda pra quem mora no Norte e no Nordeste"}

fontes = [
    {"ini": .5, "fim": ini("f3"), "html": "<b>INMET</b>, avisos 56030 (amarelo, 1.210 cidades) e 56017 (laranja, 474) · baixa umidade · sexta 09/10 · fundo: satélite GOES-19 (NOAA) via <b>NASA</b> GIBS, 08/10 14h30"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>Open-Meteo</b> (modelos, lido 09/10) · máxima prevista de 09 a 15/10 em grade de 1° · altura e cor = °C"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INPE</b> Programa Queimadas, 08/10 · contagem pelo satélite de referência (AQUA) · pontos = VIIRS · foco não é igual a incêndio · fumaça em Manaus: <b>Vocativo</b>, 08/10"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>Portal do Amazonas</b> (cota do Porto de Manaus), 10/2026 · cenários do <b>SGB</b> (Serviço Geológico do Brasil)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INMET</b>, avisos 56021, 56027, 56011, 56014 · tempestade, perigo potencial · 09 a 13/10"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>NOAA</b>/CPC e <b>CPTEC/INPE</b>: El Niño muito forte, pico de outubro a dezembro · <b>Cemaden</b>/INMET: estação chuvosa do Norte pode atrasar · salas do NE: OND quente e seco"},
    {"ini": ini("f9"), "fim": DUR, "html": "<b>Defesa Civil</b> · em emergência ligue 199 · incêndio: Bombeiros 193 · alertas por SMS: envie o CEP para 40199"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"seco": "#ff8c1a", "laranja": "#ff8c1a", "deserto": "#ff8c1a", "calor": "#ff2a1f", "fogo": "#ff5a14",
         "focos": "#ff5a14", "fumaca": "#ff5a14", "rios": "#5ec8ff", "negro": "#5ec8ff", "secando": "#5ec8ff",
         "tempestade": "#ffd60a", "granizo": "#ffd60a", "dezembro": "#ff2a1f", "pico": "#ff2a1f", "pior": "#ff2a1f",
         "comenta": "#ffd23f", "gratuito": "#ffd23f", "club": "#ffd23f", "agua": "#5ec8ff", "chuva": "#5ec8ff"}
LUGAR = {"norte", "nordeste", "bahia", "piaui", "ceara", "paraiba", "amazonia", "manaus", "amazonas", "acre", "rondonia",
         "inema", "regiao", "cidade"}
NUM = re.compile(r"\d|^(mil|duzentas|dez|quatrocentas|setenta|quatro|doze|quarenta|sete|setecentos|trinta|um|cinco|vinte)$")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = re.sub(r"^(IMET|Inmet|INMET)", "INMET", p["w"]).replace("Inema", "inema").replace("Inpe", "INPE")
        w = re.sub(r"^Ni[nñ]h?o", "Niño", w)
        if t["id"] == "f5" and w.startswith("2020"):  # a fala diz 2024 (conferido no áudio original); o Whisper cortou
            w = w.replace("2020", "2024")
        if w[:1] in ".-," and bloco:  # ".club", ".210", ",21" e "-dia" grudam na palavra anterior
            bloco[-1]["w"] += w.rstrip(".,")
            continue
        k = n(w)
        cor = CORES.get(k) or ("#ffd23f" if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        fim_frase = w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1
        if len(bloco) == 3 or fim_frase:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

rios = [{"nome": "Negro", "ini": ini("f5") + .2, "fim": ini("f6") + .3, "dur": 2.4, "largura": 8},
        {"nome": "Amazonas", "ini": ini("f5") + .8, "fim": ini("f6") + .3, "dur": 2.4, "largura": 6}]

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR, "marca": "INEMA · ALERTA N/NE", "selo": "INMET · INPE · SEX 09/10",
     "camera": camera, "alertas": alertas, "colunas": colunas, "rios": rios, "pontos": pontos, "sat": SAT,
     "pinos": pinos, "hero": hero, "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(calor)} colunas de calor (máx {quente['t']} °C em {quente['p']}) · {len(fogo)} pontos de fogo · ref INPE {ref}")
