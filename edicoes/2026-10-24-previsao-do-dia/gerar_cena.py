#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 24/10/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa do Codex no quadro 0 (capa-dia/abertura.png), infravermelho do GOES-19 sobre o Sul (baixa pressão e aglomerado de
tempestades), foto do granizo e vendaval (ilustração), o que já caiu no sudoeste do PR, colunas 3D da chuva prevista hoje no oeste do Sul,
foto da enchente (ilustração), alerta vermelho do INMET hoje e laranja no domingo, gráfico da chuva prevista no Sul e no Sudeste em 7 dias.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "24/10/2026"
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
OPR = {"lon": -52.2, "lat": -25.7, "zoom": 5.4}      # f1: áreas do Paraná (centro e sudoeste)
SIST = {"lon": -53.5, "lat": -27.0, "zoom": 4.6}     # f2: baixa pressão e aglomerado de tempestades sobre o Sul (IR)
HS = {"lon": -52.7, "lat": -26.2, "zoom": 6.3}       # f3: Honório Serpa e Francisco Beltrão (já caiu)
COL = {"lon": -52.4, "lat": -26.4, "zoom": 5.8}      # f4: colunas 3D da chuva prevista hoje
LESTE = {"lon": -49.6, "lat": -26.2, "zoom": 6.0}    # f5: Grande Curitiba e Vale do Itajaí
IGU = {"lon": -51.8, "lat": -26.3, "zoom": 5.9}      # f6: rios do oeste e Vale do Rio Iguaçu
SUL = {"lon": -51.8, "lat": -27.2, "zoom": 4.9}      # f7: alerta vermelho hoje, no Sul
SESP = {"lon": -49.5, "lat": -22.5, "zoom": 4.7}     # f8: domingo: leste do PR, SP, MS, RJ e MG
SEAL = {"lon": -48.5, "lat": -22.3, "zoom": 4.6}     # f9: alerta laranja no domingo
SULG = {"lon": -51.5, "lat": -27.5, "zoom": 4.6}     # f10: seg e ter seco no Sul (gráfico)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CAPA = 2.2  # quadro 0 = capa cheia do Codex até aqui
GRAN = em("f2", "granizo")
ENCH = em("f6", "enchentes")
camera = [
    K(0, BR), K(CAPA, BR), K(CAPA + 1.2, OPR, 0, 0), K(fim("f1") - .2, {**OPR, "zoom": 5.5}, 0, 0),
    K(ini("f2") + 1.0, SIST, 0, 0), K(fim("f2") - .2, {**SIST, "zoom": 4.7}, 0, 0),
    K(ini("f3") + 1.0, HS, 30, -8), K(fim("f3") - .2, {**HS, "zoom": 6.4}, 34, 6),
    K(ini("f4") + 1.0, COL, 54, -20), K(fim("f4") - .2, {**COL, "zoom": 5.9}, 58, 16),
    K(ini("f5") + 1.0, LESTE, 20, -4), K(fim("f5") - .2, {**LESTE, "zoom": 6.1}, 24, 4),
    K(ini("f6") + 1.0, IGU, 25, -6), K(fim("f6") - .2, {**IGU, "zoom": 6.0}, 28, 6),
    K(ini("f7") + 1.0, SUL, 0, 0), K(fim("f7") - .2, {**SUL, "zoom": 5.0}, 0, 0),
    K(ini("f8") + 1.0, SESP, 15, -4), K(fim("f8") - .2, {**SESP, "zoom": 4.8}, 18, 4),
    K(ini("f9") + 1.0, SEAL, 0, 0), K(fim("f9") - .2, {**SEAL, "zoom": 4.7}, 0, 0),
    K(ini("f10") + 1.0, SULG, 0, 0), K(fim("f10") - .2, {**SULG, "zoom": 4.7}, 0, 0),
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

# colunas 3D: chuva PREVISTA hoje, sábado 24/10 (Meteorologia · 24/10): 80 a 100 mm no oeste do Sul,
# até 150 mm em áreas do Paraná (centro e sudoeste); o que já choveu fica de fora
REG = [("Honório Serpa", -52.39, -26.14, 150), ("Francisco Beltrão", -53.06, -26.08, 150), ("Pato Branco", -52.67, -26.23, 150),
       ("Laranjeiras do Sul", -52.41, -25.41, 150), ("Guarapuava", -51.46, -25.39, 150), ("Cascavel", -53.46, -24.96, 100),
       ("Campo Erê", -53.08, -26.39, 100), ("São Miguel do Oeste", -53.52, -26.73, 100), ("Chapecó", -52.62, -27.10, 100),
       ("Xanxerê", -52.40, -26.88, 100), ("Itapiranga", -53.71, -27.17, 90), ("Concórdia", -52.03, -27.23, 80),
       ("Tenente Portela", -53.76, -27.37, 90), ("Frederico Westphalen", -53.39, -27.36, 90), ("Erechim", -52.27, -27.63, 80)]
cor_mm = lambda mm: [120, 90, 255] if mm < 150 else [255, 42, 31]
col = [{"id": i, "p": [lon, lat], "v": v, "cor": cor_mm(v)} for i, (_, lon, lat, v) in enumerate(REG)]
ordem = {c["id"]: i * .1 for i, c in enumerate(col)}
colunas = [{"id": "chuvahoje", "ini": ini("f4") + .3, "fim": ini("f5") + .5, "dados": col, "raio": 13000, "escala": 1600, "ordem": ordem, "varredura": 1}]

# gráfico: chuva prevista no Sul e no Sudeste em 7 dias (soma das capitais, Open-Meteo)
P7 = json.loads((B / "previsao7d.json").read_text())
HOJE = "2026-10-24"
assert P7["dias"][0] == HOJE and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sáb", "dom", "seg", "ter", "qua", "qui", "sex"], ROTD
SULV = [d["por_regiao_mm"]["S"] for d in P7["por_dia"]]
SEV = [d["por_regiao_mm"]["SE"] for d in P7["por_dia"]]
assert max(SULV) == SULV[0] and SULV[0] > 60 and max(SULV[2:5]) < 10, SULV   # nas capitais do Sul: pico hoje, seg a qua quase sem chuva
series = [{"nome": "Sul", "cor": "#5ec8ff", "v": SULV}, {"nome": "Sudeste", "cor": "#ff8c1a", "v": SEV}]

rios = []

# ---------------------------------------------------------------- fotos de tela cheia (Codex, pela assinatura): capa, granizo e enchente
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05},
         {"src": "capa-dia/granizo.png", "ini": GRAN - .1, "fim": fim("f2") - .1, "fade": .25, "selo": "ilustração"},
         {"src": "capa-dia/enchente.png", "ini": ENCH - .1, "fim": em("f6", "Vale") - .1, "fade": .25, "selo": "ilustração"}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
por_uf = lambda i, uf: sum(UF[c[:2]] == uf for c in geo(i))
VHOJE = ufs_av(56168)    # tempestade VERMELHA (Grande Perigo) hoje, sábado 24/10, 6h às 21h: 325 (SC 146, PR 99, RS 80)
assert len(geo(56168)) == 325 and por_uf(56168, "SC") == 146 and por_uf(56168, "PR") == 99 and por_uf(56168, "RS") == 80
assert aviso[56168]["descricao"] == "Tempestade" and aviso[56168]["severidade"] == "Grande Perigo" and aviso[56168]["inicio"].startswith("2026-10-24")
LDOM = ufs_av(56171)     # tempestade LARANJA (Perigo) domingo 25/10: 1.250 (SP 567, PR 326, MG 223, RJ 72, MS 61, SC 1)
assert len(geo(56171)) == 1250 and por_uf(56171, "SP") == 567 and por_uf(56171, "PR") == 326 and por_uf(56171, "MG") == 223
assert aviso[56171]["descricao"] == "Tempestade" and aviso[56171]["severidade"] == "Perigo" and aviso[56171]["inicio"].startswith("2026-10-25")
estados = [
    {"id": "pr0", "ini": CAPA, "fim": ini("f2") + .3, "ufs": ["PR"], "cor": AZUL, "alfa": .3},
    {"id": "sul", "ini": em("f2", "baixa"), "fim": ini("f3") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .3},
    {"id": "pr", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["PR"], "cor": LAR, "alfa": .3},
    {"id": "oeste", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZUL, "alfa": .25},
    {"id": "leste", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["PR", "SC"], "cor": AZUL, "alfa": .3},
    {"id": "ench", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["PR", "SC"], "cor": LAR, "alfa": .3},
    {"id": "vhoje", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": VHOJE, "cor": VERM, "alfa": .45},
    {"id": "dom", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["PR", "SP", "MS", "RJ", "MG"], "cor": AZUL, "alfa": .3},
    {"id": "ldom", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": LDOM, "cor": LAR, "alfa": .45},
    {"id": "seco", "ini": ini("f10"), "fim": ini("f11") + .3, "ufs": ["RS", "SC", "PR"], "cor": AMA, "alfa": .22},
]

pinos = [
    {"nome": "Centro e sudoeste do Paraná", "sub": "até 150 mm hoje · previsão", "lon": -52.4, "lat": -25.6, "ini": em("f1", "Paraná"), "fim": ini("f2"), "h": 200},
    {"nome": "Sul do Brasil", "sub": "baixa pressão e tempestades", "lon": -52.5, "lat": -27.3, "ini": em("f2", "baixa"), "fim": GRAN - .1, "h": 160},
    {"nome": "Honório Serpa", "sub": "160 mm já caíram", "lon": -52.39, "lat": -26.14, "ini": em("f3", "Honório"), "fim": ini("f4"), "h": 200},
    {"nome": "Francisco Beltrão", "sub": "130 mm já caíram", "lon": -53.06, "lat": -26.08, "ini": em("f3", "Francisco"), "fim": ini("f4"), "h": 80},
    {"nome": "Grande Curitiba", "sub": "perto de 100 mm · previsão", "lon": -49.27, "lat": -25.43, "ini": em("f5", "Curitiba"), "fim": ini("f6"), "h": 180},
    {"nome": "Vale do Itajaí", "sub": "50 a 80 mm · previsão", "lon": -49.07, "lat": -26.92, "ini": em("f5", "Itajaí"), "fim": ini("f6"), "h": 60},
    {"nome": "Vale do Rio Iguaçu", "sub": "em atenção", "lon": -51.09, "lat": -26.23, "ini": em("f6", "Vale"), "fim": ini("f7"), "h": 160},
    {"nome": "Leste do Paraná", "sub": "chuva cedo no domingo", "lon": -49.6, "lat": -25.2, "ini": em("f8", "leste"), "fim": ini("f9"), "h": 40},
    {"nome": "São Paulo", "sub": "chuva cedo no domingo", "lon": -47.5, "lat": -23.2, "ini": em("f8", "Paulo"), "fim": ini("f9"), "h": 140},
    {"nome": "Mato Grosso do Sul", "sub": "chuva cedo no domingo", "lon": -54.2, "lat": -21.5, "ini": em("f8", "Mato"), "fim": ini("f9"), "h": 220},
    {"nome": "Rio e Minas", "sub": "chuva à tarde no domingo", "lon": -44.0, "lat": -21.0, "ini": em("f8", "Minas"), "fim": ini("f9"), "h": 260},
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
                 '<div class="t1" style="font-size:92px;color:#5ec8ff">ATÉ 150 MM</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">de chuva hoje em áreas do Paraná</div>'}]
paineis = [
    {"ini": ini("f2"), "fim": GRAN - .1, "k": "POR QUE (PREVISÃO)",
     "itens": [{"t": em("f2", "baixa"), "txt": "🌀 Baixa pressão"}, {"t": em("f2", "aglomerado"), "txt": "⛈️ Aglomerado de tempestades"}],
     "l": "sobre o Sul do Brasil", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "JÁ CAIU · SUDOESTE DO PR",
     "contador": conta(160, "f3", "160", "#5ec8ff", "MM EM HONÓRIO SERPA"),
     "l": "130 mm em Francisco Beltrão", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE, 24/10 · CHUVA PREVISTA",
     "contador": conta(150, "f4", "150", "#ff2a1f", "MM EM ÁREAS DO PARANÁ", de=80),
     "l": "80 a 100 mm no oeste do Sul · coluna = mm previstos", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "HOJE · LESTE (PREVISÃO)",
     "itens": [{"t": em("f5", "Curitiba"), "txt": "🌧️ Grande Curitiba: ~100 mm"}, {"t": em("f5", "Itajaí"), "txt": "🌧️ Vale do Itajaí: 50 a 80 mm"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": em("f6", "Vale") - .1, "fim": ini("f7"), "k": "RISCO HOJE (PREVISÃO)",
     "itens": [{"t": em("f6", "Vale") - .1, "txt": "🌊 Enchentes nos rios do oeste"}, {"t": em("f6", "Iguaçu"), "txt": "⚠️ Vale do Rio Iguaçu em atenção"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE, 24/10 · ALERTA VERMELHO",
     "contador": conta(325, "f7", "325", "#ff2a1f", "CIDADES EM ALERTA"),
     "l": "SC 146 · PR 99 · RS 80 · tempestade (INMET)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "DOMINGO, 25/10 · ELEIÇÃO (PREVISÃO)",
     "itens": [{"t": em("f8", "cedo"), "txt": "🌧️ Cedo: leste do PR, SP e MS"}, {"t": em("f8", "Rio"), "txt": "⛈️ Tarde: Rio e Minas"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "DOMINGO, 25/10 · ALERTA LARANJA",
     "contador": conta(1250, "f9", "1.250", "#ff8c1a", "CIDADES EM ALERTA"),
     "l": "SP 567 · PR 326 · MG 223 · RJ 72 · MS 61 · tempestade (INMET)", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "PRÓXIMOS 7 DIAS · CHUVA PREVISTA",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 0, "ini": ini("f10") + .3, "dur": 1.6},
     "l": "seg e ter: seco no Sul · qua e qui: pancadas isoladas · mm somados nas capitais", "borda": "rgba(250,204,21,.7)"},
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

GOES = f"satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"
fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": f"<b>{MET}</b> · {GOES}"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": f"<b>{MET}</b> · {GOES} · foto do granizo: ilustração"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>{MET}</b> · chuva já registrada"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · chuva prevista para 24/10 · altura da coluna = milímetros"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · foto da enchente: ilustração"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>INMET</b>, aviso vermelho de tempestade para 24/10 (325 municípios)"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>INMET</b>, aviso laranja de tempestade para 25/10 (1.250 municípios)"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": f"<b>{MET}</b> · {OM}, 24 a 30/10"},
    {"ini": ini("f11"), "fim": DUR, "html": f"<b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chover": "#5ec8ff", "milimetros": "#5ec8ff", "umidade": "#5ec8ff", "enchentes": "#ff2a1f", "laranja": "#ff8c1a", "vermelho": "#ff2a1f", "encharcado": "#5ec8ff", "vendaval": "#ff8c1a", "aglomerado": "#ff8c1a", "pancadas": "#5ec8ff", "seco": AM,
         "tempestade": "#ff8c1a", "tempestades": "#ff8c1a", "alerta": "#ff8c1a", "raios": "#ff8c1a", "granizo": "#ff8c1a",
         "alagamentos": "#ff2a1f", "enxurradas": "#ff2a1f", "deslizamentos": "#ff2a1f", "forte": "#ff8c1a", "atencao": "#ff8c1a",
                  "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"parana", "sul", "oeste", "honorio", "serpa", "francisco", "beltrao", "curitiba", "vale", "itajai", "iguacu", "leste",
         "sao", "paulo", "mato", "grosso", "minas", "rio", "grande", "inemaclub", "onde"}
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
        if len(bloco) == 3 or longo or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
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
      f"vermelho hoje {VHOJE} · laranja dom {LDOM} · 7 dias {ROTD} · Sul {SULV} · Sudeste {SEV}")
