#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 20/10/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png), infravermelho do GOES-19 (alta pressão, céu limpo no Sul),
gráfico da chuva prevista no Sul em 7 dias, alertas do INMET (chuvas intensas hoje, tempestade quarta e quinta),
caminho da umidade da Amazônia ao Sul, colunas 3D da faixa de chuva prevista até domingo, foto do alagamento (ilustração),
rio Paraná e o Iguaçu, Curitiba no sábado.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "20/10/2026"
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
SULIR = {"lon": -51.0, "lat": -26.0, "zoom": 4.9}    # f1/f2: o Sul no IR (céu limpo da alta pressão)
TRES = {"lon": -50.0, "lat": -20.5, "zoom": 4.3}     # f3: Sul, Sudeste e Centro-Oeste com sol
NEL = {"lon": -44.5, "lat": -15.5, "zoom": 4.3}      # f4: Bahia, Tocantins e o litoral ES→PR
OESTE = {"lon": -53.2, "lat": -26.6, "zoom": 5.7}    # f5: oeste de SC, noroeste do RS, sudoeste do PR
QUI = {"lon": -49.5, "lat": -23.5, "zoom": 4.6}      # f6: tempestade na quinta (PR, SP, MG)
AMZ = {"lon": -58.0, "lat": -13.0, "zoom": 3.9}      # f7: a umidade sai da Amazônia...
SUL = {"lon": -51.5, "lat": -26.5, "zoom": 5.0}      # ...e chega ao Sul
COL = {"lon": -52.0, "lat": -26.6, "zoom": 5.6}      # f8: colunas 3D até domingo
RIOS = {"lon": -53.0, "lat": -25.4, "zoom": 6.0}     # f9: rio Iguaçu e rio Paraná
CWB = {"lon": -49.27, "lat": -25.43, "zoom": 6.6}    # f10: Curitiba
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
SEXTA = em("f7", "sexta")
CHEGA = em("f7", "chega")
ALAG = em("f9", "alagamento")
RIO = em("f9", "rios")
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, SULIR, 0, 0), K(fim("f1") - .2, {**SULIR, "zoom": 5.0}, 0, 0),
    K(ini("f2") + 1.0, {**SULIR, "lat": -26.5}, 20, -6), K(fim("f2") - .2, {**SULIR, "lat": -26.7, "zoom": 5.1}, 24, 6),
    K(ini("f3") + 1.0, TRES, 10, -4), K(fim("f3") - .2, {**TRES, "zoom": 4.4}, 14, 4),
    K(ini("f4") + 1.0, NEL, 0, 0), K(fim("f4") - .2, {**NEL, "zoom": 4.4}, 0, 0),
    K(ini("f5") + 1.0, OESTE, 30, -8), K(fim("f5") - .2, {**OESTE, "zoom": 5.8}, 34, 6),
    K(ini("f6") + 1.0, QUI, 0, 0), K(fim("f6") - .2, {**QUI, "zoom": 4.65}, 0, 0),
    K(SEXTA + .6, AMZ, 0, 0), K(CHEGA + 1.6, SUL, 15, -4), K(fim("f7") - .2, {**SUL, "zoom": 5.1}, 18, 4),
    K(ini("f8") + 1.0, COL, 52, -20), K(fim("f8") - .2, {**COL, "zoom": 5.7}, 56, 16),
    K(RIO + .6, RIOS, 25, -6), K(fim("f9") - .2, {**RIOS, "zoom": 6.1}, 28, 6),
    K(ini("f10") + 1.0, CWB, 35, -8), K(fim("f10") - .2, {**CWB, "zoom": 6.7}, 40, 6),
    K(ini("f11") + 1.4, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) sobre o Sul (f1–f2)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
assert len(BONS) >= 40, BONS
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": CAPA - .3, "fim": ini("f3") + .3, "dur": ini("f3") - CAPA + .3, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])

# ---------------------------------------------------------------- previsão Open-Meteo nas capitais (pesquisa/bruto/resumo.json)
OMC = json.loads((B / "resumo.json").read_text())["openmeteo_capitais"]["linhas"]
chuva = lambda cap, dia: next(l["chuva"] for l in OMC if l["cap"] == cap and l["dia"] == dia)
SAB, DOM = "2026-10-24", "2026-10-25"
assert chuva("Curitiba", SAB) == 48.2 and chuva("Curitiba", DOM) == 46.0

# colunas 3D: faixa de chuva PREVISTA até domingo, 25/10 (Meteorologia · 20/10: 100 a 150 mm, passa de 300 em pontos do PR)
REG = [("Sudoeste do PR", -52.9, -25.9, 300), ("Oeste do PR", -53.6, -24.9, 300), ("Centro do PR", -51.6, -25.0, 150),
       ("Oeste de SC", -52.7, -26.9, 150), ("Noroeste do RS", -54.0, -28.0, 100), ("Leste do PR", -49.6, -25.3, 100)]
cor_mm = lambda mm: [60, 150, 255] if mm < 150 else [120, 90, 255] if mm < 300 else [255, 42, 31]
col = [{"id": i, "p": [lon, lat], "v": v, "cor": cor_mm(v)} for i, (_, lon, lat, v) in enumerate(REG)]
ordem = {c["id"]: i * .15 for i, c in enumerate(col)}
colunas = [{"id": "chuvadom", "ini": ini("f8") + .3, "fim": ini("f9") + .5, "dados": col, "raio": 26000, "escala": 1500, "ordem": ordem, "varredura": 1}]

# gráfico: chuva prevista no Sul em 7 dias (soma das capitais do Sul)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-20" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["ter", "qua", "qui", "sex", "sáb", "dom", "seg"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
assert SULV[0] < 1 and max(SULV[3:6]) > 50   # seco hoje; a chuva forte vem de sexta a domingo
series = [{"nome": "Sul", "cor": "#5ec8ff", "v": SULV}]

# rio Paraná desenhado na f9 (o Iguaçu não está no geo-br: vai como pino)
rios = [{"nome": "Paraná", "ini": RIO, "fim": ini("f10") + .3, "dur": 2.0, "largura": 9}]

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa e alagamento
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/enchente.png", "ini": ALAG - .1, "fim": RIO - .1, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
CHUVA = ufs_av(56112)    # chuvas intensas amarelo até 20/10: 1144 (BA 382, TO 139, PI 127, MG 114, AM 62, MA 60)
assert len(geo(56112)) == 1144 and aviso[56112]["descricao"] == "Chuvas Intensas" and aviso[56112]["fim"].startswith("2026-10-20")
assert por_uf(56112, "BA") == 382 and por_uf(56112, "TO") == 139
TQUA = ufs_av(56127)     # tempestade amarelo quarta 21/10 à tarde: 623 (PR 323, RS 147, SC 121, MS 28)
assert len(geo(56127)) == 623 and por_uf(56127, "PR") == 323 and por_uf(56127, "RS") == 147 and por_uf(56127, "SC") == 121
assert aviso[56127]["descricao"] == "Tempestade" and aviso[56127]["inicio"].startswith("2026-10-21")
TQUI = ufs_av(56129)     # tempestade amarelo quinta 22/10: 2853 (SP 643, MG 592, RS 496, PR 399, SC 293, RJ 91)
assert len(geo(56129)) == 2853 and por_uf(56129, "SP") == 643 and por_uf(56129, "MG") == 592 and por_uf(56129, "PR") == 399
assert aviso[56129]["descricao"] == "Tempestade" and aviso[56129]["inicio"].startswith("2026-10-22")
estados = [
    {"id": "sul0", "ini": CAPA, "fim": ini("f3") + .3, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .2},
    {"id": "sol", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["RS", "SC", "PR", "SP", "RJ", "MG", "ES", "MS", "MT", "GO", "DF"], "cor": LAR, "alfa": .25},
    {"id": "chuvas", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": CHUVA, "cor": AMA, "alfa": .45},
    {"id": "tqua", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": TQUA, "cor": LAR, "alfa": .45},
    {"id": "tqui", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": TQUI, "cor": LAR, "alfa": .45},
    {"id": "baixa", "ini": CHEGA, "fim": ini("f8") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .35},
    {"id": "pr", "ini": ini("f8"), "fim": ini("f10") + .3, "ufs": ["PR"], "cor": VERM, "alfa": .3},
]

pinos = [
    {"nome": "Paraná", "sub": "mais de 300 mm até domingo · previsão", "lon": -51.6, "lat": -24.9, "ini": em("f1", "Paraná"), "fim": ini("f2"), "h": 200},
    {"nome": "Oeste catarinense", "sub": "chuva a partir de quarta", "lon": -52.62, "lat": -27.0, "ini": em("f5", "oeste"), "fim": em("f5", "noroeste") - .1, "h": 140},
    {"nome": "Noroeste gaúcho", "sub": "chuva a partir de quarta", "lon": -54.2, "lat": -28.0, "ini": em("f5", "noroeste"), "fim": ini("f6"), "h": 220},
    {"nome": "Sudoeste do Paraná", "sub": "temporais isolados", "lon": -52.9, "lat": -25.9, "ini": em("f5", "sudoeste"), "fim": ini("f6"), "h": 300},
    {"nome": "Amazônia", "sub": "ar quente e úmido", "lon": -62.0, "lat": -6.0, "ini": SEXTA, "fim": CHEGA + .8, "h": 200},
    {"nome": "Rio Iguaçu", "sub": "atenção · chuva forte até domingo", "lon": -52.2, "lat": -25.75, "ini": em("f9", "Iguaçu"), "fim": ini("f10"), "h": 420},
    {"nome": "Rio Paraná", "sub": "atenção", "lon": -54.45, "lat": -24.6, "ini": em("f9", "Paraná"), "fim": ini("f10"), "h": 90},
    {"nome": "Curitiba", "sub": "48,2 mm sábado · 46 mm domingo", "lon": -49.27, "lat": -25.43, "ini": em("f10", "Curitiba"), "fim": ini("f11"), "h": 300},
]

# ---------------------------------------------------------------- textos
# contador chega ao número QUANDO a palavra é dita: começa LEAD s antes e termina no início da palavra (em tempos.json e avatar/tempos.json)
LEAD = 1.0
conta = lambda ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1: {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}
hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,   # a data grande e o número da capa ficam toda a f1
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DO DIA</div>'
                 '<div class="t1" style="font-size:92px;color:#5ec8ff">+300 MM</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">de chuva em pontos do Paraná até domingo</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "POR QUE · SUL · CHUVA PREVISTA EM 7 DIAS",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f2") + .3, "dur": 1.6},
     "l": "alta pressão hoje · baixa pressão a partir de quarta · mm somados nas capitais do Sul", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "HOJE, 20/10 · TEMPO FIRME (PREVISÃO)",
     "itens": [{"t": em("f3", "Sul"), "txt": "☀️ Sul"}, {"t": em("f3", "Sudeste"), "txt": "☀️ Sudeste"},
               {"t": em("f3", "Centro"), "txt": "☀️ Centro-Oeste"}],
     "l": "céu esbranquiçado e halo solar: fina camada de gelo no alto", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE · CHUVAS INTENSAS",
     "contador": conta(1144, "f4", "1144", "#facc15", "CIDADES EM ALERTA"),
     "l": "BA 382 · TO 139 · PI 127 · MG 114 · alerta amarelo (INMET)", "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "QUARTA, 21/10 · TEMPESTADE",
     "contador": conta(623, "f5", "623", "#ff8c1a", "CIDADES EM ALERTA"),
     "l": "PR 323 · RS 147 · SC 121 · MS 28 · a partir das 15 h (INMET)", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "QUINTA, 22/10 · TEMPESTADE",
     "contador": conta(2853, "f6", "2853", "#ff8c1a", "CIDADES EM ALERTA", de=623),
     "l": "SP 643 · MG 592 · RS 496 · PR 399 · SC 293 (INMET)", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SEXTA E SÁBADO (PREVISÃO)",
     "itens": [{"t": SEXTA, "txt": "🌧️ Sexta: a chuva aumenta"}, {"t": em("f7", "Sábado"), "txt": "⛈️ Sábado: o pior dia"}],
     "l": "umidade da Amazônia levada ao Sul pela baixa pressão", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f8"), "fim": ALAG - .1, "k": "ATÉ DOMINGO, 25/10 · CHUVA PREVISTA",
     "contador": conta(300, "f8", "300", "#ff2a1f", "MM EM PONTOS DO PARANÁ", de=100),
     "l": "100 a 150 mm na maior parte · coluna = mm previstos", "borda": "rgba(255,42,31,.8)"},
    {"ini": RIO - .1, "fim": ini("f10"), "k": "ATENÇÃO · RIOS (PREVISÃO)",
     "itens": [{"t": em("f9", "Iguaçu"), "txt": "📍 Rio Iguaçu"}, {"t": em("f9", "Paraná"), "txt": "📍 Rio Paraná"}],
     "l": "alagamento · enxurrada · deslizamento", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "SÁBADO, 24/10 · CURITIBA (PREVISÃO)",
     "contador": conta(48.2, "f10", "48", "#5ec8ff", "MM DE CHUVA", dec=1),
     "l": "domingo: mais 46 mm, chuva perde força à tarde (Open-Meteo)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "onde"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f11", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
     "borda": "rgba(250,204,21,.8)"},
]
for a, b in zip(paineis, paineis[1:]):
    assert a["fim"] <= b["ini"] + 1e-6, (a["k"], b["k"])
for a in paineis:
    assert a["ini"] < a["fim"], ("painel vazio", a["k"])
    if a.get("contador"):
        c = a["contador"]
        assert a["ini"] - .01 <= c["ini"] and c["ini"] + c["dur"] <= a["fim"] + .01, ("contador fora do painel", a["k"], c, a["ini"], a["fim"])

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>{MET}</b> · satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · {OM}, 20 a 26/10"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso amarelo de chuvas intensas até 20/10 (1.144 municípios)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso amarelo de tempestade para 21/10 (623 municípios)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · <b>INMET</b>, aviso amarelo de tempestade para 22/10 (2.853 municípios)"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · faixa de chuva prevista até 25/10 · altura da coluna = milímetros"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · foto do alagamento: ilustração"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": f"<b>{MET}</b> · {OM} para 24 e 25/10"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chuvas": "#5ec8ff", "milimetros": "#5ec8ff", "umidade": "#5ec8ff", "umido": "#5ec8ff",
         "alagamento": "#ff2a1f", "enxurrada": "#ff2a1f", "deslizamento": "#ff2a1f", "enchente": "#ff2a1f",
         "temporal": "#ff8c1a", "tempestade": "#ff8c1a", "alerta": "#ff8c1a", "intensas": "#ff8c1a", "trovoada": "#ff8c1a",
         "baixa": "#ff8c1a", "pressao": "#ff8c1a", "alta": "#96d2ff", "sol": "#ff8c1a", "halo": "#96d2ff",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"parana", "sul", "sudeste", "centrooeste", "bahia", "tocantins", "litoral", "espirito", "santo", "oeste", "catarinense",
         "noroeste", "gaucho", "sudoeste", "amazonia", "curitiba", "rios", "iguacu", "inemaclub", "onde"}
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
     "marca": "INEMA · PREVISÃO DO DIA", "selo": DATA[:5] + " · INMET · NOAA",
     "camera": camera, "sat": SAT, "imagens": [], "colunas": colunas, "rios": rios, "telas": telas, "estados": estados, "pinos": pinos,
     "hero": hero, "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros ({IR_DE} a {IR_ATE}) · "
      f"chuvas hoje {CHUVA} · tempestade qua {TQUA} · qui {TQUI} · 7 dias {ROTD} · Sul {SULV}")
