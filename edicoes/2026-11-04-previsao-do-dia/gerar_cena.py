#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 04/11/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "AVISO VERMELHO NO SUL · RAJADAS ACIMA DE 100 KM/H"),
infravermelho do GOES-19 (complexo de tempestades sobre o RS, frente fria à noite), foto do vendaval (ilustração),
aviso vermelho do INMET (705 cidades) → total do país em aviso de tempestade (2.026), quinta no Paraná,
colunas 3D de 100 a 200 mm previstos no oeste do Sul com câmera inclinada girando, 80–100 mm no centro-leste de SP e MG,
calor de 45 °C no Nordeste, gráfico dos 7 dias no Sul (sábado nova frente fria, geada fraca no domingo).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "04/11/2026"
MET = "Meteorologia · " + DATA
OM = "<b>Open-Meteo</b>, previsão nas capitais"
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
ABRE = {"lon": -52.5, "lat": -27.5, "zoom": 4.7}     # f1: aviso vermelho no Sul, rajadas > 100 km/h
CCM = {"lon": -54.0, "lat": -29.0, "zoom": 4.5}      # f2: complexo de tempestades sobre o RS (IR GOES-19)
HOJE = {"lon": -52.5, "lat": -28.8, "zoom": 5.2}     # f3: RS e SC hoje
AVI = {"lon": -52.0, "lat": -27.5, "zoom": 4.9}      # f4: aviso vermelho 705 → país 2.026
PAIS = {"lon": -50.0, "lat": -20.0, "zoom": 4.0}
QUI = {"lon": -51.5, "lat": -25.2, "zoom": 5.1}      # f5: madrugada de quinta no Paraná
TEND = {"lon": -53.2, "lat": -27.2, "zoom": 5.2}     # f6: colunas 3D de 100–200 mm no oeste do Sul
SPMG = {"lon": -46.0, "lat": -20.8, "zoom": 5.0}     # f7: centro-leste de SP e MG, 80–100 mm
NE = {"lon": -40.5, "lat": -8.5, "zoom": 4.6}        # f8: Nordeste 45 °C
QUE = {"lon": -50.0, "lat": -11.0, "zoom": 3.9}      # f8: MT, MS, PA
SUL = {"lon": -51.5, "lat": -27.5, "zoom": 4.8}      # f9: Sul nos próximos dias
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
VENDAVAL = em("f3", "vendaval")
VFIM = em("f3", "Santa") - .2
PAIS_T = em("f4", "país")
MATO = em("f8", "Mato")
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, ABRE, 0, 0), K(fim("f1") - .2, {**ABRE, "zoom": 4.8}, 0, 0),
    K(ini("f2") + 1.0, CCM, 0, 0), K(fim("f2") - .2, {**CCM, "zoom": 4.6}, 0, 0),
    K(ini("f3") + 1.0, HOJE, 20, -6), K(fim("f3") - .2, {**HOJE, "zoom": 5.3}, 28, 6),
    K(ini("f4") + 1.0, AVI, 0, 0), K(PAIS_T - .2, {**AVI, "zoom": 5.0}, 0, 0),
    K(PAIS_T + 1.2, PAIS, 0, 0), K(fim("f4") - .2, {**PAIS, "zoom": 4.1}, 0, 0),
    K(ini("f5") + 1.0, QUI, 0, 0), K(fim("f5") - .2, {**QUI, "zoom": 5.2}, 0, 0),
    K(ini("f6") + 1.0, {**TEND, "zoom": 5.0}, 45, -16), K(fim("f6") - .2, {**TEND, "zoom": 5.3}, 58, 18),
    K(ini("f7") + 1.0, SPMG, 0, 0), K(fim("f7") - .2, {**SPMG, "zoom": 5.1}, 0, 0),
    K(ini("f8") + 1.0, NE, 0, 0), K(MATO - .2, {**NE, "zoom": 4.7}, 0, 0),
    K(MATO + 1.0, QUE, 0, 0), K(fim("f8") - .2, {**QUE, "zoom": 4.0}, 0, 0),
    K(ini("f9") + 1.0, SUL, 0, 0), K(fim("f9") - .2, {**SUL, "zoom": 4.9}, 0, 0),
    K(ini("f10") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) (f1–f2)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 130]
assert len(BONS) >= 36, BONS
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


IRF = fim("f2") - .3
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": CAPA - .3, "fim": IRF, "dur": IRF - CAPA, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

# ---------------------------------------------------------------- colunas 3D: 100 a 200 mm previstos no oeste do Sul (f6)
# a previsão disse "uns colocam 100, 150, 200 mm… o oeste da região Sul é a área mais afetada": 200 no núcleo, 100–150 nas bordas
PROJ = {"Oeste do PR": ((-53.6, -24.9), 150), "Sudoeste do PR": ((-52.9, -25.9), 150), "Oeste de SC": ((-52.7, -26.9), 200),
        "Meio-oeste de SC": ((-51.5, -27.1), 150), "Noroeste gaúcho": ((-54.0, -27.8), 200), "Missões (RS)": ((-55.0, -28.4), 150),
        "Centro do RS": ((-53.5, -29.5), 100)}
proj = [{"id": i, "p": list(p), "v": v, "cor": VERM if v >= 200 else LAR} for i, (c, (p, v)) in enumerate(PROJ.items())]
COL0 = em("f6", "chuva") - .3
colunas = [{"id": "proj", "ini": COL0, "fim": ini("f7") + .4, "dados": proj, "raio": 22000, "escala": 2600,
            "ordem": {c["id"]: i * .12 for i, c in enumerate(proj)}, "varredura": 1}]

# ---------------------------------------------------------------- previsão Open-Meteo (7 dias): gráfico
P7 = json.loads((B / "previsao7d.json").read_text())
HOJE_D = "2026-11-04"
assert P7["dias"][0] == HOJE_D and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qua", "qui", "sex", "sáb", "dom", "seg", "ter"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
SEV = [d["por_regiao_mm"]["SE"] for d in P7["por_dia"]]
COV = [d["por_regiao_mm"]["CO"] for d in P7["por_dia"]]
assert SULV[0] == max(SULV) and round(SULV[0]) == 67 and round(SULV[3]) == 41 and round(SULV[2]) == 2, SULV  # Sul: 67 hoje, 2 na sexta, 41 no sábado
series = [{"nome": "Sudeste", "cor": "#ff8c1a", "v": SEV}, {"nome": "Centro-Oeste", "cor": "#a78bfa", "v": COV},
          {"nome": "Sul", "cor": "#5ec8ff", "v": SULV}]

rios = []

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e vendaval
assert VFIM - VENDAVAL > 1.0, (VENDAVAL, VFIM)
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/vendaval.png", "ini": VENDAVAL - .1, "fim": VFIM, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
VERMELHO = ufs_av(56266)  # tempestade VERMELHO (Grande Perigo) hoje 4/11: 705 (RS 332, SC 295 = todo o estado, PR 78)
assert len(geo(56266)) == 705 and por_uf(56266, "RS") == 332 and por_uf(56266, "SC") == 295 and por_uf(56266, "PR") == 78
assert aviso[56266]["descricao"] == "Tempestade" and aviso[56266]["severidade"] == "Grande Perigo" and aviso[56266]["inicio"].startswith("2026-11-04")
TEMP_HOJE = geo(56266) | geo(56265) | geo(56269)   # união dos avisos de tempestade de hoje (vermelho, laranja, amarelo)
assert len(TEMP_HOJE) == 2026, len(TEMP_HOJE)
assert all(aviso[i]["descricao"] == "Tempestade" and aviso[i]["inicio"].startswith("2026-11-04") for i in (56265, 56269))
PAIS_UF = sorted({UF[c[:2]] for c in TEMP_HOJE if sum(x[:2] == c[:2] for x in TEMP_HOJE) >= 5})
QUI_ = ufs_av(56273)      # tempestade LARANJA quinta 5/11: 502 (PR 251, SP 221, MS 30)
assert len(geo(56273)) == 502 and por_uf(56273, "PR") == 251 and aviso[56273]["inicio"].startswith("2026-11-05")
NORDESTE = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
estados = [
    {"id": "abre", "ini": CAPA, "fim": ini("f2") + .3, "ufs": VERMELHO, "cor": VERM, "alfa": .35},
    {"id": "hoje", "ini": em("f3", "Rio"), "fim": ini("f4") + .3, "ufs": ["RS", "SC"], "cor": LAR, "alfa": .35},
    {"id": "vermelho", "ini": em("f4", "vermelho"), "fim": PAIS_T + .3, "ufs": VERMELHO, "cor": VERM, "alfa": .45},
    {"id": "pais", "ini": PAIS_T, "fim": ini("f5") + .3, "ufs": PAIS_UF, "cor": LAR, "alfa": .35},
    {"id": "quinta", "ini": em("f5", "Paraná"), "fim": ini("f6") + .3, "ufs": QUI_, "cor": LAR, "alfa": .4},
    {"id": "spmg", "ini": em("f7", "Paulo"), "fim": ini("f8") + .3, "ufs": ["SP", "MG"], "cor": AZUL, "alfa": .35},
    {"id": "ne", "ini": em("f8", "Nordeste"), "fim": MATO + .3, "ufs": NORDESTE, "cor": VERM, "alfa": .4},
    {"id": "calor", "ini": MATO, "fim": ini("f9") + .3, "ufs": ["MT", "MS", "PA"], "cor": LAR, "alfa": .4},
    {"id": "frente", "ini": em("f9", "frente"), "fim": ini("f10") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .35},
]

pinos = [
    {"nome": "Sul do Brasil", "sub": "aviso vermelho · rajadas acima de 100 km/h (previsão)", "lon": -52.0, "lat": -28.0, "ini": em("f1", "Sul"), "fim": ini("f2"), "h": 200},
    {"nome": "Rio Grande do Sul", "sub": "complexo de tempestades agora", "lon": -54.0, "lat": -29.5, "ini": em("f2", "Rio"), "fim": em("f2", "baixa"), "h": 160},
    {"nome": "Frente fria", "sub": "deve se formar hoje à noite (previsão)", "lon": -54.5, "lat": -31.0, "ini": em("f2", "frente"), "fim": ini("f3"), "h": 120},
    {"nome": "Rio Grande do Sul", "sub": "temporais à tarde e à noite (previsão)", "lon": -53.5, "lat": -29.5, "ini": em("f3", "Rio"), "fim": ini("f4"), "h": 140},
    {"nome": "Santa Catarina", "sub": "vendaval e chuva forte (previsão)", "lon": -50.5, "lat": -27.2, "ini": em("f3", "Santa"), "fim": ini("f4"), "h": 60},
    {"nome": "Santa Catarina", "sub": "todas as 295 cidades em aviso vermelho", "lon": -50.5, "lat": -27.2, "ini": em("f4", "Santa"), "fim": PAIS_T, "h": 80},
    {"nome": "Paraná", "sub": "chuva na madrugada de quinta (previsão)", "lon": -51.5, "lat": -24.6, "ini": em("f5", "Paraná"), "fim": ini("f6"), "h": 120},
    {"nome": "Oeste do Sul", "sub": "100 a 200 mm somados (previsão)", "lon": -53.0, "lat": -25.9, "ini": em("f6", "oeste"), "fim": ini("f7"), "h": 340},
    {"nome": "Centro-leste de SP", "sub": "80 a 100 mm (previsão)", "lon": -47.5, "lat": -22.5, "ini": em("f7", "Paulo"), "fim": ini("f8"), "h": 120},
    {"nome": "Centro-leste de MG", "sub": "80 a 100 mm (previsão)", "lon": -43.8, "lat": -19.6, "ini": em("f7", "Minas"), "fim": ini("f8"), "h": 220},
    {"nome": "Nordeste", "sub": "até 45 °C · mais quente na sexta (previsão)", "lon": -40.5, "lat": -9.0, "ini": em("f8", "45"), "fim": MATO, "h": 160},
    {"nome": "Mato Grosso", "sub": "calor forte (previsão)", "lon": -55.5, "lat": -13.0, "ini": MATO, "fim": ini("f9"), "h": 120},
    {"nome": "Pará", "sub": "calor forte (previsão)", "lon": -52.0, "lat": -4.5, "ini": em("f8", "Pará"), "fim": ini("f9"), "h": 200},
    {"nome": "Sul do Brasil", "sub": "nova frente fria no sábado, 7/11 (previsão)", "lon": -52.0, "lat": -27.5, "ini": em("f9", "frente"), "fim": em("f9", "geada"), "h": 260},
    {"nome": "Serra gaúcha", "sub": "geada fraca no domingo, 8/11 (previsão)", "lon": -50.8, "lat": -28.9, "ini": em("f9", "geada"), "fim": ini("f10"), "h": 180},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0


def conta(ate, fid, palavra, cor, unid, dec=0, de=0, k=1, desde=None):
    t = em(fid, palavra, k)
    lead = max(.4, min(LEAD, t - (desde if desde is not None else ini(fid))))   # número logo no começo: o contador cabe no painel
    return {"de": de, "ate": ate, "dec": dec, "ini": t - lead, "dur": lead, "cor": cor, "unid": unid}


hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o fato da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:76px;color:#ff2a1f">AVISO VERMELHO NO SUL</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">rajadas acima de 100 km/h · previsão</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "POR QUE (PREVISÃO)",
     "itens": [{"t": em("f2", "complexo"), "txt": "⛈️ Complexo de tempestades no RS"}, {"t": em("f2", "pressão"), "txt": "🌀 Baixa pressão"},
               {"t": em("f2", "frente"), "txt": "❄️ Frente fria hoje à noite"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": VFIM, "fim": ini("f4"), "k": "HOJE, 4/11 · TARDE E NOITE",   # entra depois da foto do vendaval
     "itens": [{"t": VFIM + .1, "txt": "⛈️ Temporais no RS e em SC"}, {"t": em("f3", "tarde"), "txt": "💨 Vendaval e chuva forte"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f4"), "fim": PAIS_T, "k": "HOJE, 4/11 · AVISO VERMELHO",
     "contador": conta(705, "f4", "705", "#ff2a1f", "CIDADES"),
     "l": "RS 332 · SC 295 (todas) · PR 78 (INMET)", "borda": "rgba(255,42,31,.85)"},
    {"ini": PAIS_T, "fim": ini("f5"), "k": "BRASIL · AVISO DE TEMPESTADE HOJE",
     "contador": conta(2026, "f4", "2.026", "#ff2a1f", "CIDADES", desde=PAIS_T),
     "l": "vermelho, laranja e amarelo somados (INMET)", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "QUINTA, 5/11 · MADRUGADA",
     "itens": [{"t": em("f5", "frente"), "txt": "❄️ Frente fria avança"}, {"t": em("f5", "Paraná"), "txt": "🌧️ Chuva chega ao Paraná"},
               {"t": em("f5", "vendaval"), "txt": "💨 Risco de vendaval forte"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "OESTE DO SUL · CHUVA SOMADA",
     "contador": conta(200, "f6", "200", "#ff2a1f", "MM (PREVISÃO)", de=100),
     "l": "mais de 100 mm · alguns modelos até 200 mm", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "CENTRO-LESTE DE SP E MG",
     "contador": conta(100, "f7", "100", "#5ec8ff", "MM (PREVISÃO)", de=80),
     "l": "chuva prevista entre 80 e 100 mm", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "NORDESTE · MÁXIMA (PREVISÃO)",
     "contador": conta(45, "f8", "45", "#ff2a1f", "°C"),
     "l": "mais quente na sexta · calor forte também em MT, MS e PA", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "SUL · PRÓXIMOS 7 DIAS (CHUVA PREVISTA)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f9") + .3, "dur": 1.6},
     "l": "Sul: 67 mm hoje · 2 na sexta · 41 no sábado · mm somados nas capitais", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "onde"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f10", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
     "borda": "rgba(250,204,21,.8)"},
]
for a, b in zip(paineis, paineis[1:]):
    assert a["fim"] <= b["ini"] + 1e-6, (a["k"], b["k"])
for a in paineis:
    assert a["ini"] < a["fim"], ("painel vazio", a["k"])
    if a.get("contador"):
        c = a["contador"]
        assert a["ini"] - .01 <= c["ini"] and c["ini"] + c["dur"] <= a["fim"] + .01, ("contador fora do painel", a["k"], c, a["ini"], a["fim"])

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

GOES = f"satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"
fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso vermelho de tempestade para 04/11 · {GOES}"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · {GOES}"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b> · foto do vendaval: ilustração"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · <b>INMET</b>, avisos de tempestade para 04/11 (vermelho: 705 municípios; todos: 2.026)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso laranja de tempestade para 05/11 (502 municípios, 251 no PR)"},
    {"ini": ini("f6"), "fim": ini("f8"), "html": f"<b>{MET}</b>, chuva somada prevista para os próximos dias"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · {OM}, 04/11 a 10/11"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chuvas": "#5ec8ff", "milimetros": "#5ec8ff", "pancadas": "#5ec8ff", "sol": AM, "seco": AM,
         "frente": "#5ec8ff", "fria": "#5ec8ff", "geada": "#5ec8ff", "complexo": "#ff2a1f", "vermelho": "#ff2a1f",
         "calor": "#ff2a1f", "graus": "#ff2a1f", "tempestade": "#ff8c1a", "tempestades": "#ff8c1a", "temporais": "#ff8c1a",
         "vendaval": "#ff8c1a", "rajadas": "#ff8c1a", "risco": "#ff2a1f", "aviso": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"parana", "sul", "sao", "paulo", "minas", "catarina", "santa", "mato", "grosso", "rio", "grande", "nordeste", "para",
         "centroleste", "oeste", "serra", "pais", "inemaclub", "onde"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        prox = t["palavras"][i + 1]["w"] if i + 1 < len(t["palavras"]) else ""
        longo = sum(len(b["w"]) + 1 for b in bloco) + len(prox) > 20   # "marcaram 500 milímetros" passava da borda
        if len(bloco) == 3 or longo or w[-1:] in ".?!,:;" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · PREVISÃO DO DIA", "selo": DATA[:5] + " · INMET · NOAA · Open-Meteo",
     "camera": camera, "sat": SAT, "imagens": [], "colunas": colunas, "rios": rios, "telas": telas, "estados": estados, "pinos": pinos,
     "hero": hero, "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"vermelho {VERMELHO} · país {PAIS_UF} · quinta {QUI_} · Sul {SULV}")
