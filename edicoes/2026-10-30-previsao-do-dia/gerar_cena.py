#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 30/10/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png, "ATÉ 300 MM DE CHUVA NO SUL"), infravermelho do GOES-19 (baixa pressão
fraca no Sul), colunas 3D da chuva das últimas 24 h na Serra Catarinense (Bocaina do Sul 97, Bom Retiro 85), hoje no Sul (aviso
INMET 666) e fora do Sul (aviso 1.500, MG 795), gráfico dos 7 dias (Sul esquenta no fim de semana, chuva volta na quarta 4/11),
baixa pressão no Paraguai em Finados, aviso laranja de tempestade de 2/11 (366, PR 337), foto do granizo (ilustração) em 3 e 4/11
e colunas 3D da chuva projetada até 15/11 (até 300 mm no PR e oeste de SC).
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "30/10/2026"
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
ABRE = {"lon": -51.5, "lat": -25.5, "zoom": 4.6}     # f1: oeste do Sul, até 300 mm até 15/11
SERRA = {"lon": -50.6, "lat": -27.9, "zoom": 6.0}    # f2: Serra Catarinense, colunas 3D das últimas 24 h
SUL = {"lon": -50.5, "lat": -26.5, "zoom": 5.0}      # f3: hoje SC e norte gaúcho; PR e SP pancadas
FORA = {"lon": -47.0, "lat": -16.0, "zoom": 4.3}     # f4: aviso de chuvas intensas fora do Sul (1.500, MG 795)
G7 = {"lon": -51.5, "lat": -27.0, "zoom": 4.8}       # f5: fim de semana quente no Sul + gráfico dos 7 dias
PARAG = {"lon": -55.0, "lat": -23.5, "zoom": 5.0}    # f6: baixa pressão sobre o Paraguai em Finados
PR = {"lon": -51.5, "lat": -24.8, "zoom": 5.6}       # f7: aviso laranja de tempestade 2/11 (PR 337)
OESTE = {"lon": -53.0, "lat": -26.8, "zoom": 5.4}    # f8: terça e quarta, frente fria no oeste do Sul
COL = {"lon": -52.6, "lat": -26.6, "zoom": 5.5}      # f9: colunas 3D da chuva projetada até 15/11
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
NOV = em("f2", "97")
GRANIZO = em("f8", "granizo")
P300 = em("f9", "300")
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, ABRE, 0, 0), K(fim("f1") - .2, {**ABRE, "zoom": 4.7}, 0, 0),
    K(ini("f2") + .8, {**SERRA, "zoom": 5.6}, 20, -6), K(NOV + .6, SERRA, 52, -18), K(fim("f2") - .2, {**SERRA, "zoom": 6.1}, 56, 16),
    K(ini("f3") + 1.0, SUL, 0, 0), K(fim("f3") - .2, {**SUL, "zoom": 5.1}, 0, 0),
    K(ini("f4") + 1.0, FORA, 0, 0), K(fim("f4") - .2, {**FORA, "zoom": 4.4}, 0, 0),
    K(ini("f5") + 1.0, G7, 0, 0), K(fim("f5") - .2, {**G7, "zoom": 4.9}, 0, 0),
    K(ini("f6") + 1.0, PARAG, 0, 0), K(fim("f6") - .2, {**PARAG, "zoom": 5.1}, 0, 0),
    K(ini("f7") + 1.0, PR, 0, 0), K(fim("f7") - .2, {**PR, "zoom": 5.7}, 0, 0),
    K(ini("f8") + 1.0, OESTE, 16, -6), K(GRANIZO - .2, {**OESTE, "zoom": 5.5}, 20, 4),
    K(ini("f9") + .8, {**COL, "zoom": 5.2}, 25, -10), K(P300 + .4, COL, 55, -22), K(fim("f9") - .2, {**COL, "zoom": 5.6}, 58, 16),
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


SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": CAPA - .3, "fim": NOV - .5, "dur": NOV - CAPA, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

# ---------------------------------------------------------------- colunas 3D: chuva das últimas 24 h na serra (f2) e projeção até 15/11 (f9)
OBS = {"Bocaina do Sul": ((-49.94, -27.74), 97), "Bom Retiro": ((-49.49, -27.80), 85), "São Joaquim": ((-49.93, -28.29), 60),
       "Vargem Bonita": ((-51.74, -27.01), 51), "Chapecó": ((-52.62, -27.10), 32)}
cor_mm = lambda mm: [255, 42, 31] if mm >= 80 else [255, 140, 26] if mm >= 50 else [120, 90, 255]
obs = [{"id": i, "p": list(p), "v": v, "cor": cor_mm(v)} for i, (c, (p, v)) in enumerate(OBS.items())]
# projeção do modelo citada na previsão: "acima dos 200, 300 mm" no PR, oeste de SC e pontas do noroeste gaúcho, de 30/10 a 14–15/11
PROJ = {"Oeste do PR": ((-53.6, -24.9), 300), "Sudoeste do PR": ((-52.9, -25.9), 300), "Oeste de SC": ((-52.7, -26.9), 300),
        "Centro-sul do PR": ((-51.2, -25.4), 250), "Noroeste gaúcho": ((-54.0, -27.7), 200)}
proj = [{"id": i, "p": list(p), "v": v, "cor": [255, 42, 31] if v >= 300 else [255, 140, 26]} for i, (c, (p, v)) in enumerate(PROJ.items())]
colunas = [{"id": "obs24h", "ini": NOV - .5, "fim": ini("f3") + .4, "dados": obs, "raio": 12000, "escala": 3000,
            "ordem": {c["id"]: i * .12 for i, c in enumerate(obs)}, "varredura": 1},
           {"id": "proj15d", "ini": P300 - 1.0, "fim": ini("f10") + .4, "dados": proj, "raio": 22000, "escala": 1500,
            "ordem": {c["id"]: i * .12 for i, c in enumerate(proj)}, "varredura": 1}]

# ---------------------------------------------------------------- previsão Open-Meteo (7 dias): gráfico
P7 = json.loads((B / "previsao7d.json").read_text())
HOJE = "2026-10-30"
assert P7["dias"][0] == HOJE and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sex", "sáb", "dom", "seg", "ter", "qua", "qui"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
SEV = [d["por_regiao_mm"]["SE"] for d in P7["por_dia"]]
COV = [d["por_regiao_mm"]["CO"] for d in P7["por_dia"]]
assert SULV[5] == max(SULV) and SULV[5] > 25 and max(SULV[1:3]) < 6, SULV   # Sul quase seco no fim de semana, pico na quarta 4/11 (frente fria)
series = [{"nome": "Sudeste", "cor": "#ff8c1a", "v": SEV}, {"nome": "Centro-Oeste", "cor": "#a78bfa", "v": COV},
          {"nome": "Sul", "cor": "#5ec8ff", "v": SULV}]

rios = []

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e granizo
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": GRANIZO - .1, "fim": ini("f9") + .3, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
SUL_ = ufs_av(56222)     # chuvas intensas AMARELO hoje 30/10 no Sul: 666 (SC 295, RS 240, PR 131)
assert len(geo(56222)) == 666 and por_uf(56222, "SC") == 295 and por_uf(56222, "RS") == 240 and por_uf(56222, "PR") == 131
assert aviso[56222]["descricao"] == "Chuvas Intensas" and aviso[56222]["inicio"].startswith("2026-10-30")
FORA_ = ufs_av(56221)    # chuvas intensas AMARELO hoje 30/10 fora do Sul: 1.500 (MG 795, GO 152, RJ 92, TO 82, ES 78, SP 66)
assert len(geo(56221)) == 1500 and por_uf(56221, "MG") == 795 and por_uf(56221, "TO") == 82 and por_uf(56221, "RJ") == 92
assert aviso[56221]["descricao"] == "Chuvas Intensas" and aviso[56221]["inicio"].startswith("2026-10-30")
FIN_ = ufs_av(56227)     # tempestade LARANJA (Perigo) segunda 2/11: 366 (PR 337, SP 16, MS 13)
assert len(geo(56227)) == 366 and por_uf(56227, "PR") == 337 and por_uf(56227, "SP") == 16 and por_uf(56227, "MS") == 13
assert aviso[56227]["descricao"] == "Tempestade" and aviso[56227]["severidade"] == "Perigo" and aviso[56227]["inicio"].startswith("2026-11-02")
estados = [
    {"id": "oeste", "ini": CAPA, "fim": ini("f2") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .3},
    {"id": "serra", "ini": em("f2", "baixa"), "fim": ini("f3") + .3, "ufs": ["SC"], "cor": AZUL, "alfa": .3},
    {"id": "sulhoje", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": SUL_, "cor": AMA, "alfa": .35},
    {"id": "fora", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": FORA_, "cor": AMA, "alfa": .35},
    {"id": "calor", "ini": em("f5", "esquentar"), "fim": ini("f6") + .3, "ufs": ["PR", "SC", "RS"], "cor": LAR, "alfa": .3},
    {"id": "finados", "ini": em("f6", "temporais"), "fim": ini("f7") + .3, "ufs": ["MS", "PR"], "cor": AZUL, "alfa": .35},
    {"id": "laranja", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": FIN_, "cor": LAR, "alfa": .45},
    {"id": "frente", "ini": em("f8", "frente"), "fim": ini("f9") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .35},
    {"id": "proj", "ini": em("f9", "Paraná"), "fim": ini("f10") + .3, "ufs": ["PR", "SC"], "cor": AZUL, "alfa": .3},
]

pinos = [
    {"nome": "Oeste do Sul", "sub": "até 300 mm até 15/11 (projeção)", "lon": -53.0, "lat": -26.0, "ini": em("f1", "oeste"), "fim": ini("f2"), "h": 220},
    {"nome": "Bocaina do Sul", "sub": "97 mm em 24 h", "lon": -49.94, "lat": -27.74, "ini": em("f2", "Bocaina"), "fim": ini("f3"), "h": 340},
    {"nome": "Bom Retiro", "sub": "85 mm em 24 h", "lon": -49.49, "lat": -27.80, "ini": em("f2", "Bom"), "fim": ini("f3"), "h": 160},
    {"nome": "Santa Catarina", "sub": "chuva hoje (previsão)", "lon": -50.5, "lat": -27.2, "ini": em("f3", "Santa"), "fim": ini("f4"), "h": 40},
    {"nome": "Norte gaúcho", "sub": "chuva hoje (previsão)", "lon": -53.8, "lat": -28.8, "ini": em("f3", "norte"), "fim": ini("f4"), "h": 30},
    {"nome": "Paraná", "sub": "pancadas à tarde", "lon": -51.5, "lat": -24.6, "ini": em("f3", "Paraná"), "fim": ini("f4"), "h": 160},
    {"nome": "São Paulo", "sub": "pancadas à tarde", "lon": -48.5, "lat": -22.3, "ini": em("f3", "São"), "fim": ini("f4"), "h": 100},
    {"nome": "Tocantins", "sub": "82 cidades em aviso", "lon": -48.3, "lat": -10.2, "ini": em("f4", "Tocantins"), "fim": ini("f5"), "h": 100},
    {"nome": "Minas Gerais", "sub": "795 cidades em aviso", "lon": -44.5, "lat": -18.5, "ini": em("f4", "795"), "fim": ini("f5"), "h": 180},
    {"nome": "Sul do Brasil", "sub": "perto de 30 °C no fim de semana", "lon": -52.0, "lat": -28.0, "ini": em("f5", "30"), "fim": ini("f6"), "h": 90},
    {"nome": "Baixa pressão", "sub": "sobre o Paraguai · Finados", "lon": -57.0, "lat": -23.5, "ini": em("f6", "Paraguai"), "fim": ini("f7"), "h": 200},
    {"nome": "Mato Grosso do Sul", "sub": "temporais (previsão)", "lon": -54.6, "lat": -20.8, "ini": em("f6", "Mato"), "fim": ini("f7"), "h": 120},
    {"nome": "Oeste do Paraná", "sub": "temporais (previsão)", "lon": -53.5, "lat": -24.9, "ini": em("f6", "oeste"), "fim": ini("f7"), "h": 80},
    {"nome": "Paraná", "sub": "337 cidades · tempestade 2/11", "lon": -51.5, "lat": -24.6, "ini": em("f7", "337"), "fim": ini("f8"), "h": 200},
    {"nome": "Oeste do Sul", "sub": "granizo e vendaval 3 e 4/11 (previsão)", "lon": -53.2, "lat": -26.9, "ini": em("f8", "frente"), "fim": GRANIZO, "h": 200},
    {"nome": "Oeste do PR e de SC", "sub": "até 300 mm até 15/11 (projeção)", "lon": -53.2, "lat": -25.8, "ini": em("f9", "Paraná"), "fim": ini("f10"), "h": 320},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0


def conta(ate, fid, palavra, cor, unid, dec=0, de=0, k=1):
    t = em(fid, palavra, k)
    lead = max(.4, min(LEAD, t - ini(fid)))   # número logo no começo da fala: o contador cabe no painel
    return {"de": de, "ate": ate, "dec": dec, "ini": t - lead, "dur": lead, "cor": cor, "unid": unid}


hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o número da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:92px;color:#FACC15">ATÉ 300 MM</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">de chuva no oeste do Sul até 15/11 · projeção</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "SERRA CATARINENSE · ÚLTIMAS 24 H",
     "contador": conta(97, "f2", "97", "#ff2a1f", "MM EM BOCAINA DO SUL"),
     "l": "Bom Retiro 85 · São Joaquim 60 · Vargem Bonita 51 mm", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "HOJE NO SUL (PREVISÃO)",
     "itens": [{"t": em("f3", "Santa"), "txt": "🌧️ Chuva em SC e norte gaúcho"}, {"t": em("f3", "Paraná"), "txt": "⛈️ PR e SP: pancadas à tarde"}],
     "l": "aviso de chuvas intensas em 666 cidades (INMET)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE, 30/10 · FORA DO SUL",
     "contador": conta(1500, "f4", "1.500", "#FACC15", "CIDADES · CHUVAS INTENSAS"),
     "l": "MG 795 · GO 152 · RJ 92 · TO 82 · ES 78 (INMET)", "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "PRÓXIMOS 7 DIAS · CHUVA PREVISTA",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f5") + .3, "dur": 1.6},
     "l": "Sul quase seco e quente no fim de semana · mm somados nas capitais", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "FINADOS, 2/11 (PREVISÃO)",
     "itens": [{"t": em("f6", "baixa"), "txt": "🌀 Baixa pressão no Paraguai"}, {"t": em("f6", "temporais"), "txt": "⛈️ Temporais em MS e oeste do PR"}],
     "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SEGUNDA, 2/11 · AVISO LARANJA",
     "contador": conta(366, "f7", "366", "#ff8c1a", "CIDADES · TEMPESTADE"),
     "l": "PR 337 · SP 16 · MS 13 (INMET)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f8"), "fim": GRANIZO - .1, "k": "TERÇA E QUARTA, 3 E 4/11",
     "itens": [{"t": em("f8", "alerta"), "txt": "⚠️ Dias de alerta no oeste do Sul"}, {"t": em("f8", "frente"), "txt": "🌀 Nova frente fria"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f9") + .3, "fim": ini("f10"), "k": "ATÉ 15/11 (PROJEÇÃO)",
     "contador": conta(300, "f9", "300", "#ff2a1f", "MM NO PR E OESTE DE SC"),
     "l": "outra frente fria em 6 e 7/11 · 200 a 300 mm", "borda": "rgba(255,42,31,.8)"},
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
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>{MET}</b>, projeção de 30/10 a 15/11 · {GOES}"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b>, chuva medida nas últimas 24 h · {GOES}"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso de chuvas intensas para 30/10 (666 municípios)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INMET</b>, aviso amarelo de chuvas intensas para 30/10 (1.500 municípios)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · {OM}, 30/10 a 05/11"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>, aviso laranja de tempestade para 02/11 (366 municípios)"},
    {"ini": ini("f8"), "fim": ini("f9") + .3, "html": f"<b>{MET}</b> · foto do granizo: ilustração"},
    {"ini": ini("f9") + .3, "fim": ini("f10"), "html": f"<b>{MET}</b>, projeção de chuva acumulada até 15/11"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chuvas": "#5ec8ff", "milimetros": "#5ec8ff", "pancadas": "#5ec8ff", "sol": AM,
         "frente": "#5ec8ff", "fria": "#5ec8ff", "baixa": "#5ec8ff", "pressao": "#5ec8ff", "esquentar": "#ff2a1f", "mormaco": "#ff2a1f",
         "graus": "#ff2a1f", "laranja": "#ff8c1a", "intensas": "#ff8c1a", "intensa": "#ff8c1a", "tempestade": "#ff8c1a",
         "temporais": "#ff8c1a", "granizo": "#ff8c1a", "vendaval": "#ff8c1a", "alerta": "#ff2a1f", "aviso": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"parana", "sul", "sao", "paulo", "mato", "grosso", "goias", "minas", "rio", "janeiro", "tocantins", "paraguai",
         "santa", "catarina", "gaucho", "oeste", "bocaina", "bom", "retiro", "serra", "catarinense", "finados", "inemaclub", "onde"}
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
      f"sul {SUL_} · fora {FORA_} · finados {FIN_} · 7 dias {ROTD} · Sul {SULV} · Sudeste {SEV} · CO {COV}")
