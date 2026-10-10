#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 10/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE e dos avisos do INMET (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "10/10/2026"
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())
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
LAR, AZUL, VERM = [255, 140, 26], [60, 150, 255], [255, 42, 31]

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
AM = {"lon": -60.0, "lat": -4.0, "zoom": 4.7}
PA = {"lon": -53.0, "lat": -5.5, "zoom": 4.5}
CO = {"lon": -47.9, "lat": -14.5, "zoom": 4.7}
SP = {"lon": -46.2, "lat": -23.3, "zoom": 6.6}
SUL = {"lon": -53.0, "lat": -28.5, "zoom": 5.2}
NE = {"lon": -45.0, "lat": -4.5, "zoom": 4.7}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, AM, 35, -8), K(fim("f2") - .2, {**AM, "lon": -59.0}, 40, 4),
    K(ini("f3") + 1.0, PA, 30, -4), K(fim("f3") - .2, {**PA, "zoom": 4.3}, 35, 6),
    K(ini("f4") + 1.0, CO, 35, -6), K(fim("f4") - .2, {**CO, "lon": -47.5}, 40, 6),
    K(ini("f5") + 1.0, SP, 40, -10), K(fim("f5") - .2, {**SP, "lon": -46.0}, 45, 8),
    K(ini("f6") + 1.0, SUL, 40, -12), K(fim("f6") - .2, {**SUL, "lon": -52.0}, 45, -18),
    K(ini("f7") + 1.0, {**SUL, "lat": -26.0, "zoom": 4.6}, 25, 0), K(fim("f7") - .2, {**SUL, "lat": -25.5, "zoom": 4.5}, 30, 8),
    K(ini("f8") + 1.0, {**NE, "lat": -6.0}, 15, -4), K(fim("f8") - .2, {**NE, "lat": -6.0, "lon": -46.0}, 20, 4),
    K(ini("f9") + 1.0, BR, 0, 0), K(DUR, {**BR, "zoom": 3.9}, 8, 4),
]

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


SAT = {"base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- focos de 09/10 (INPE: pontos VIIRS em grade de 0,08°; conta pelo AQUA)
grade, ref, ref_pa = {}, 0, 0
with open(B / "inpe_focos_diario_br_20261009.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            ref_pa += r["estado"].strip() == "PARÁ"
assert (ref, ref_pa) == (2001, 1115), (ref, ref_pa)
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f3"), "fim": ini("f4") + .3, "dados": fogo, "dur": 3.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET (estados com aviso laranja)
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in aviso[i]["geocodes"].split(",")
                                    if sum(x[:2] == c[:2] for x in aviso[i]["geocodes"].split(",")) >= minimo})
SECO = ufs_av(56017, 1)      # baixa umidade, laranja (702 municípios)
TEMP = ufs_av(56004)       # tempestade, laranja (439 municípios: PR, SC, RS, MS)
assert len(aviso[56004]["geocodes"].split(",")) == 439 and len(aviso[56017]["geocodes"].split(",")) == 702
estados = [
    {"id": "seco", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": SECO, "cor": LAR, "alfa": .5},
    {"id": "temp", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": TEMP, "cor": VERM, "alfa": .5},
]

pinos = [
    {"nome": "Manaus", "sub": "pior ar do Brasil", "lon": -60.02, "lat": -3.1, "ini": em("f2", "Manaus"), "fim": ini("f3"), "h": 170},
    {"nome": "Pará", "sub": "1.115 focos em 1 dia", "lon": -52.2, "lat": -3.8, "ini": em("f3", "Pará"), "fim": ini("f4"), "h": 160},
    {"nome": "Brasília", "sub": "umidade 15%", "lon": -47.93, "lat": -15.78, "ini": em("f4", "Brasília"), "fim": ini("f5"), "h": 170},
    {"nome": "São José dos Campos", "sub": "rajada de 83 km/h", "lon": -45.89, "lat": -23.18, "ini": em("f5", "José"), "fim": ini("f6"), "h": 200},
    {"nome": "Nazaré Paulista", "sub": "86,8 mm em 24 h", "lon": -46.4, "lat": -23.18, "ini": em("f5", "Nazaré"), "fim": ini("f6"), "h": 110},
    {"nome": "Rio Uruguai", "sub": "acima da cota de inundação", "lon": -56.55, "lat": -29.13, "ini": em("f6", "Uruguai"), "fim": ini("f7"), "h": 170},
    {"nome": "Rio Jacuí", "sub": "acima da cota", "lon": -52.89, "lat": -30.03, "ini": em("f6", "Jacuí"), "fim": ini("f7"), "h": 120},
    {"nome": "Teresina", "sub": "até 39 °C (previsão)", "lon": -42.8, "lat": -5.09, "ini": em("f8", "Teresina"), "fim": ini("f9"), "h": 170},
    {"nome": "Belém", "sub": "Círio no calor", "lon": -48.5, "lat": -1.45, "ini": em("f8", "Belém"), "fim": ini("f9"), "h": 130},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">😷 fumaça · ⛈️ temporal · 🏜️ ar de deserto</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "MANAUS · 09/10",
     "itens": [{"t": em("f2", "pior"), "txt": "😷 pior ar do Brasil"}, {"t": em("f2", "Escola"), "txt": "🏫 escola fechada"},
               {"t": em("f2", "celular"), "txt": "📱 alerta: use máscara"}], "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "FOCOS DE FOGO · 09/10",
     "contador": {"de": 0, "ate": 2001, "dec": 0, "ini": em("f3", "2") , "dur": 1.4, "cor": "#ff5a14", "unid": "NO BRASIL"},
     "l": "1.115 só no Pará · satélite de referência do INPE", "borda": "rgba(255,90,20,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "BRASÍLIA · UMIDADE DO AR",
     "contador": {"de": 60, "ate": 15, "dec": 0, "ini": em("f4", "umidade"), "dur": 1.4, "cor": "#ff8c1a", "unid": "%"},
     "l": "💧 bebe água · ☀️ foge do sol do meio-dia", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "SÃO PAULO · TEMPORAL",
     "itens": [{"t": em("f5", "Rajada"), "txt": "💨 rajada de 83 km/h"}, {"t": em("f5", "chuva"), "txt": "🌧️ 86,8 mm em 24 h"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SUL",
     "itens": [{"t": em("f6", "rios"), "txt": "🌊 Uruguai e Jacuí acima da cota"}, {"t": em("f6", "Catarina"), "txt": "🏠 SC: 536 desalojados na semana"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA LARANJA DE TEMPESTADE",
     "contador": {"de": 0, "ate": 439, "dec": 0, "ini": em("f7", "439"), "dur": 1.2, "cor": "#ff2a1f", "unid": "CIDADES"},
     "l": "PR · SC · RS · MS — e até quarta pode passar de 200 mm no Sul", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "NORTE E NORDESTE · CALOR",
     "itens": [{"t": em("f8", "Teresina"), "txt": "🌡️ Teresina até 39 °C"}, {"t": em("f8", "Círio"), "txt": "🙏 Círio de Belém no calor"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f9", "Fumaça"), "txt": "😷 Fumaça?"}, {"t": em("f9", "calor"), "txt": "🌡️ Calor?"},
               {"t": em("f9", "chuva"), "txt": "🌧️ Chuva?"}, {"t": em("f9", "cidade"), "txt": "📍 Tua cidade"}],
     "borda": "rgba(255,210,63,.8)"},
]

cta = {"ini": ini("f10"), "fim": DUR, "a": "TODO DIA: O CLIMA DAS ÚLTIMAS 24 HORAS", "b": "Segue o canal pra não ser pego de surpresa."}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "cursos gratuitos de tecnologia e IA"}

fontes = [
    {"ini": .5, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 09/10 06h a 10/10 06h · rajada: METAR do aeroporto de São José dos Campos (<b>NOAA</b>)"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "Manaus, 09/10: qualidade do ar <b>IQAir</b>; escolas municipais fechadas e alerta da <b>Defesa Civil</b> (g1 Amazonas)"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INPE</b> Programa Queimadas, 09/10 · contagem pelo satélite de referência (AQUA) · pontos = VIIRS · foco não é igual a incêndio"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Umidade de Brasília calculada do METAR do aeroporto (<b>NOAA</b>), 09/10 · estados em laranja: aviso de baixa umidade do <b>INMET</b>"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Rajada: METAR (<b>NOAA</b>), 09/10 15h07 · chuva: pluviômetro do <b>CEMADEN</b> em Nazaré Paulista, 24 h até 10/10 03h"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>Defesa Civil RS</b>, boletins de 09/10 (cotas dos rios) · <b>Defesa Civil SC</b>, balanço de 04 a 09/10"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>, aviso laranja de tempestade para 10/10 (439 municípios) · chuva até quarta: <b>Meteored</b>"},
    {"ini": ini("f8"), "fim": DUR, "html": "Teresina: previsão <b>Open-Meteo</b> para 10/10 · Belém: g1 Pará com dados do <b>INMET</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"fumaca": "#ff8c1a", "fogo": "#ff5a14", "focos": "#ff5a14", "temporal": "#5ec8ff", "chuva": "#5ec8ff", "deserto": "#ff8c1a",
         "umidade": "#ff8c1a", "calor": "#ff2a1f", "alerta": "#ff2a1f", "tempestade": "#ff2a1f", "inundacao": "#3c96ff",
         "desalojados": "#3c96ff", "rajada": "#5ec8ff", "pior": "#ff2a1f", "comenta": "#ffd23f", "gratuito": "#ffd23f", "laranja": "#ff8c1a"}
LUGAR = {"manaus", "para", "brasilia", "saopaulo", "sao", "paulo", "jose", "campos", "nazare", "paulista", "sul", "uruguai", "jacui",
         "santa", "catarina", "teresina", "belem", "nordeste", "brasil", "inemaclub", "cidade", "mato", "grosso"}
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
     "marca": "INEMA · CLIMA 24 H", "selo": "INMET · INPE · NOAA · " + DATA[:5],
     "camera": camera, "sat": SAT, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · {len(fogo)} pontos de fogo · seco {SECO} · tempestade {TEMP}")
