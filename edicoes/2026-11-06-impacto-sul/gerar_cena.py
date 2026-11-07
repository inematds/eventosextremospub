#!/usr/bin/env python3
"""Monta cena.js do "Impacto Sul" de 06/11/2026 (sexta), texto da v2 (falas.json desta pasta, avatar já gravado),
com o visual novo (auto/roteiro-sul.md, 3c, Nei 07/11/2026):
  - ONDE = MAPA, O QUÊ = IMAGEM REAL: todo lugar dito (Alpestre/norte gaúcho, oeste catarinense, Paraná, Amazônia,
    norte gaúcho/oeste catarinense/Paraná do sábado, cidades do Sul, centro e leste de SC, Curitiba, todo o Sul)
    → mapa PARADO nele, pino com o nome, estado pintado, >= 3 s desde a palavra do lugar
    (a câmera viaja escondida atrás da cena anterior e chega antes);
  - DURAÇÃO: nenhuma cena < 2,5 s; mapa >= 3 s;
  - SÓ IMAGEM QUE AGREGA: granizo, lavoura destruída, radar forte, previsão com chuva forte; o céu limpo (clip-10) saiu,
    clip-11 (= clip-03) e clip-01 (granizo quase invisível na neblina) não entram; vendaval (ilustração) saiu: a rajada de
    Curitiba é dita com o mapa parado em Curitiba.
Fontes: fonte do dia (granizo em Alpestre/RS, oeste de SC e PR), GOES-19 IR (NASA GIBS), avisos do INMET, Open-Meteo.
Com avatar: gerar_cena.py --canto (avatar/tempos.json); depois GEO=geo-br.js LAYOUT=canto motor-sul/compor_avatar.sh <esta pasta>
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, subprocess, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "06/11/2026"
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
FIM_VIDEO = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(AQUI / "avatar/avatar.mp4")], capture_output=True, text=True).stdout or DUR) if AVATAR else DUR
FIM_VIDEO = min(FIM_VIDEO, DUR)   # o compor_avatar corta no fim do avatar: a última cena vale até aqui
LAR, AMA, VERM, AZUL, FRIO = [255, 140, 26], [250, 204, 21], [255, 42, 31], [60, 150, 255], [150, 210, 255]
MIN_CENA, MIN_MAPA = 2.5, 3.0

# ---------------------------------------------------------------- linha do tempo: cortes (cada um na palavra que ele mostra)
CAPA = 2.5                                    # quadro 0 = granizo acumulado com o gancho e a data escritos (sem fade)
A0 = max(em("f2", "Alpestre"), CAPA + MIN_CENA)   # mapa A: Alpestre, norte gaúcho
A1 = em("f2", "norte") + MIN_MAPA             # → clipe: gelo acumulado ("propriedades rurais", "caiu granizo")
B0 = em("f3", "oeste")                        # mapa B: extremo oeste catarinense + Paraná
B1 = em("f4", "frio") - .3                    # → satélite IR (a causa): câmera vai do Sul à Amazônia
S1 = em("f5", "abafado")                      # → clipe: radar com núcleos fortes ("novas tempestades")
C0 = em("f6", "Norte")                        # mapa C: norte gaúcho, oeste catarinense, Paraná → INMET (1.079 cidades do Sul)
R1 = C0 - MIN_CENA                            #   (antes dele: previsão de chuva forte do sábado, "deve chover forte")
C1 = em("f8", "milímetros") - .4              # → clipe: previsão de chuva ("altos volumes")
D0 = em("f9", "centro")                       # mapa D: centro e leste de SC + Curitiba (rajadas de 72 km/h)
D1 = em("f10", "Curitiba") + MIN_MAPA         # → ilustração do frio ("temperatura despenca")
F0 = max(em("f10", "Sul"), D1 + MIN_CENA)     # mapa F: todo o Sul (frio no domingo) e a pergunta "de que cidade do Sul"
F1 = ini("f12")                               # → clipe: granizo no chão (CTA)

# ---------------------------------------------------------------- câmera: só aparece nos trechos de mapa/satélite
K = lambda t, r, pitch=0, bearing=0: {"t": round(t, 3), **r, "pitch": pitch, "bearing": bearing}
ALP = {"lon": -52.6, "lat": -27.9, "zoom": 7.0}
OESTE_PR = {"lon": -51.6, "lat": -26.3, "zoom": 6.1}
AMZ_SUL = {"lon": -56.5, "lat": -17.5, "zoom": 4.25}
PINOS3 = {"lon": -51.6, "lat": -26.7, "zoom": 6.0}   # norte RS / oeste SC / PR e os 3 estados do aviso do INMET
SC_CWB = {"lon": -50.3, "lat": -26.6, "zoom": 6.5}   # centro e leste de SC + Curitiba
SUL = {"lon": -51.4, "lat": -27.6, "zoom": 5.75}
VIAGEM = .7                                   # a câmera chega antes do mapa aparecer e fica parada
camera = [K(0, ALP)]
for a, b, r in [(A0, A1, ALP), (B0, B1, OESTE_PR), (B1 + VIAGEM, S1, AMZ_SUL), (C0, C1, PINOS3), (D0, D1, SC_CWB), (F0, F1, SUL)]:
    camera += [K(a - (VIAGEM if r is not AMZ_SUL else 0), r), K(b, r)]
camera.append(K(DUR, SUL))
camera = [c for i, c in enumerate(camera) if i == 0 or c["t"] > camera[i - 1]["t"]]
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: GOES-19 infravermelho (a causa, f4)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 130 and TS[i] < "2026-11-07T03:00:00Z"]   # só a sexta 06/11 (horário de Brasília)
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


IR0, IR1 = B1, S1 + .3
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": IR0, "fim": IR1, "dur": IR1 - IR0, "alfa": .9, "rotulo": "satélite · infravermelho"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])
assert len(BONS) >= 20, f"poucos quadros bons de infravermelho: {len(BONS)}"


# ---------------------------------------------------------------- micro clipes reais (cenas/clip-NN, 30 fps, limpos do outro perfil)
def clipe(nome, a, b, de=0, zoom=.03):
    q = sorted(os.listdir(AQUI / "cenas" / nome))[de:]
    assert q and (min(b, FIM_VIDEO) - a) <= len(q) / 30 + .15, (nome, round(b - a, 2), len(q) / 30)
    return {"seq": [f"cenas/{nome}/{x}" for x in q], "fps": 30, "ini": a, "fim": b, "fade": .2, "zoom": zoom}


telas = [
    {"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .25, "zoom": .05},   # granizo + gancho + data
    clipe("clip-04", CAPA, A0),                        # "lavouras ... impacto no Sul": lavoura de tabaco destruída
    # mapa A (Alpestre, norte gaúcho)
    clipe("clip-05", A1, B0),                          # "o gelo cobriu o chão" / "caiu granizo": gelo acumulado
    # mapa B (oeste catarinense, Paraná) → satélite IR (a causa, Amazônia)
    clipe("clip-06", S1, R1),                          # "novas tempestades": radar com núcleo roxo/vermelho
    clipe("clip-07", R1, C0),                          # "sábado de manhã, deve chover forte": previsão com chuva forte
    # mapa C (norte gaúcho, oeste catarinense, Paraná → INMET nos 3 estados → norte gaúcho 84 mm)
    clipe("clip-09", C1, D0),                          # "altos volumes": previsão de chuva sobre o RS
    # mapa D (centro e leste de SC, Curitiba)
    {"src": "capa-dia/frio.png", "ini": D1, "fim": F0, "fade": .25, "zoom": .06, "selo": "ilustração"},   # temperatura despenca
    # mapa F (todo o Sul: frio no domingo, "de que cidade do Sul")
    clipe("clip-02", F1, DUR),                         # CTA: chão de terra coberto de granizo (o vídeo acaba com o avatar)
]
assert telas[0]["ini"] == 0   # vis() não faz fade-in quando ini <= 0 (quadro 0 cheio); o .25 é só a saída

# ---------------------------------------------------------------- portões das 3 regras (3c)
mapas = [("A Alpestre", A0, A1, em("f2", "Alpestre")), ("B oeste SC/PR", B0, B1, em("f3", "oeste")),
         ("IR Amazônia", B1, S1, em("f4", "Amazônia")), ("C norte RS/oeste SC/PR/INMET", C0, C1, em("f6", "Norte")),
         ("D centro-leste SC/Curitiba", D0, D1, em("f9", "centro")), ("F todo o Sul", F0, F1, em("f10", "Sul"))]
for m in telas:
    assert min(m["fim"], FIM_VIDEO) - m["ini"] >= MIN_CENA - .01, ("cena curta", m.get("src") or m["seq"][0], round(min(m["fim"], FIM_VIDEO) - m["ini"], 2))
for nome, a, b, palavra in mapas:
    assert b - a >= MIN_MAPA - .01, ("mapa curto", nome, round(b - a, 2))
    assert a <= palavra + .25, ("mapa entra depois da palavra do lugar", nome, round(a - palavra, 2))
# lugares ditos e o mapa que os mostra (>= 3 s desde a palavra; os últimos da fala ficam até o corte seguinte)
# (f1 "estados do Sul" / "impacto no Sul" ficam na capa: é o nome do programa e o gancho escrito)
LUGARES = [("f2", "Alpestre", A1), ("f2", "norte", A1), ("f3", "oeste", B1), ("f3", "Paraná", B1), ("f4", "Amazônia", S1),
           ("f6", "Norte", C1), ("f6", "Oeste", C1), ("f6", "Paraná", C1), ("f7", "Sul", C1), ("f8", "Norte", C1),
           ("f9", "centro", D1), ("f9", "Santa", D1), ("f10", "Curitiba", D1), ("f10", "Sul", F1), ("f11", "Sul", F1)]
for fid, w, ate in LUGARES:
    assert ate - em(fid, w) >= MIN_MAPA - .5, ("lugar com mapa curto", fid, w, round(ate - em(fid, w), 2))
    assert any(a - .01 <= em(fid, w) + .25 and em(fid, w) < b for _, a, b, _ in mapas), ("lugar fora de mapa", fid, w)
cortes = sorted({0, *[x for m in telas for x in (m["ini"], m["fim"])], *[x for _, a, b, _ in mapas for x in (a, b)]})
cortes = [c for c in cortes if c < FIM_VIDEO - .05]
for a, b in zip(cortes, cortes[1:] + [FIM_VIDEO]):
    assert b - a >= MIN_CENA - .01, ("trecho curto (pisca)", round(a, 2), round(b, 2))
ocup = sorted([(m["ini"], m["fim"]) for m in telas] + [(a, b) for _, a, b, _ in mapas])
for (a, b), (c, d) in zip(ocup, ocup[1:]):
    assert abs(b - c) < .02, ("buraco/sobreposição na linha do tempo", round(b, 2), round(c, 2))
assert abs(ocup[-1][1] - DUR) < .02

# ---------------------------------------------------------------- avisos do INMET do Sul (sábado 07/11 e domingo 08/11)
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
SULC = {"41": "PR", "42": "SC", "43": "RS"}
geo = lambda i: {c for c in aviso[i]["geocodes"].split(",") if c[:2] in SULC}
for i in (56310, 56318, 56322):
    assert aviso[i]["descricao"] == "Tempestade" and aviso[i]["inicio"].startswith("2026-11-07"), i
TEMP = geo(56310) | geo(56318) | geo(56322)
assert len(TEMP) == 1079, len(TEMP)                       # a fala f7 diz "1.079 cidades do Sul"
from collections import Counter
T_UF = Counter(SULC[c[:2]] for c in TEMP)
assert (T_UF["PR"], T_UF["SC"], T_UF["RS"]) == (399, 295, 385), T_UF
assert aviso[56281]["descricao"] == "Declínio de Temperatura" and aviso[56281]["inicio"].startswith("2026-11-08")
FRIO8 = len(geo(56281))
assert FRIO8 == 1191, FRIO8

# ---------------------------------------------------------------- previsão Open-Meteo (sábado 07/11)
G15 = json.loads((AQUI / "om/prev15_grade.json").read_text())
PS = [p for p in G15["pts"] if p["uf"] in SULC.values()]
assert PS[0]["dias"][0] == "2026-11-07", PS[0]["dias"][0]
TOPO = max(PS, key=lambda p: p["chuva"][0] or 0)
assert round(TOPO["chuva"][0]) == 84 and TOPO["uf"] == "RS", (TOPO["uf"], TOPO["chuva"][0])   # f8: 84 mm no norte gaúcho
RAJ = max(PS, key=lambda p: max(p["raj"][:2]))
assert round(max(RAJ["raj"][:2])) == 72 and RAJ["uf"] == "PR", RAJ                              # f10: 72 km/h perto de Curitiba

# ---------------------------------------------------------------- mapa: estados pintados e pinos (só nos trechos de mapa)
AVI = em("f7", "aviso")
estados = [
    {"id": "a_rs", "ini": A0, "fim": A1, "ufs": ["RS"], "cor": VERM, "alfa": .3},
    {"id": "b_sc", "ini": B0, "fim": B1, "ufs": ["SC"], "cor": VERM, "alfa": .3},
    {"id": "b_pr", "ini": em("f3", "Paraná"), "fim": B1, "ufs": ["PR"], "cor": VERM, "alfa": .3},
    {"id": "c_chuva", "ini": C0, "fim": AVI, "ufs": ["RS", "SC", "PR"], "cor": AZUL, "alfa": .3},
    {"id": "c_temp", "ini": AVI, "fim": C1, "ufs": ["RS", "SC", "PR"], "cor": LAR, "alfa": .4},
    {"id": "d_sc", "ini": D0, "fim": D1, "ufs": ["SC"], "cor": AZUL, "alfa": .35},
    {"id": "d_pr", "ini": em("f10", "Curitiba"), "fim": D1, "ufs": ["PR"], "cor": FRIO, "alfa": .3},
    {"id": "f_frio", "ini": F0, "fim": F1, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .4},
]
pino = lambda nome, sub, lon, lat, a, b, h=120: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    pino("Alpestre", "norte gaúcho · granizo", -53.03, -27.25, A0, A1),
    pino("Extremo oeste catarinense", "granizo", -53.2, -26.7, B0, B1),
    pino("Paraná", "granizo · tabaco destruído", -51.6, -24.9, em("f3", "Paraná"), B1),
    pino("Amazônia", "corredor de umidade", -61.0, -8.0, em("f4", "Amazônia") - .1, S1),
    pino("Norte gaúcho", "chuva forte no sábado", -52.6, -28.5, C0, AVI, 60),
    pino("Oeste catarinense", "chuva forte no sábado", -52.62, -26.9, em("f6", "Oeste"), AVI, 60),
    pino("Paraná", "chuva forte no sábado", -51.5, -24.7, em("f6", "Paraná"), AVI, 60),
    pino("Rio Grande do Sul", f"{T_UF['RS']} cidades em aviso", -53.4, -29.4, AVI, em("f8", "Norte"), 60),
    pino("Santa Catarina", f"{T_UF['SC']} cidades em aviso", -50.6, -27.3, AVI, em("f8", "Norte"), 60),
    pino("Paraná", f"{T_UF['PR']} cidades em aviso", -51.6, -24.9, AVI, em("f8", "Norte"), 60),
    pino("Norte gaúcho", f"até {round(TOPO['chuva'][0])} mm no sábado", TOPO["p"][0], TOPO["p"][1], em("f8", "Norte"), C1, 140),
    pino("Centro e leste de SC", "altos volumes de chuva", -49.9, -27.2, D0, D1, 60),
    pino("Curitiba", f"rajadas de até {round(max(RAJ['raj'][:2]))} km/h", -49.27, -25.43, em("f10", "Curitiba"), D1, 60),
    pino("Sul", "temperatura despenca no domingo", -51.4, -27.6, F0, F1, 60),
]
for p in pinos:   # pino que nasce até 0,3 s antes do mapa entra junto com o mapa
    for _, a, b, _ in mapas:
        if a - .3 <= p["ini"] < a and p["fim"] <= b + .01:
            p["ini"] = a
    assert any(a - .01 <= p["ini"] and p["fim"] <= b + .01 for _, a, b, _ in mapas), ("pino fora de trecho de mapa", p["nome"])

# ---------------------------------------------------------------- textos
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}


hero = []   # a manchete e a data estão escritas na capa (quadro 0)
paineis = [
    {"ini": CAPA, "fim": ini("f2"), "k": "SEXTA 06/11 · SUL",
     "itens": [{"t": CAPA, "txt": "🧊 granizo no RS, em SC e no PR"}], "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "ALPESTRE (RS) · TARDE DE HOJE",
     "itens": [{"t": em("f2", "gelo"), "txt": "🧊 gelo acumulado"}, {"t": em("f2", "chão"), "txt": "🌾 cobriu o chão das propriedades"}],
     "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "GRANIZO · SC E PR",
     "itens": [{"t": em("f3", "oeste"), "txt": "📍 extremo oeste de SC"}, {"t": em("f3", "Paraná"), "txt": "📍 áreas do Paraná"},
               {"t": em("f3", "tabaco"), "txt": "🌾 tabaco destruído"}], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "A CAUSA",
     "itens": [{"t": em("f4", "frio"), "txt": "❄️ ar frio da manhã"}, {"t": em("f4", "umidade"), "txt": "💧 umidade da Amazônia"},
               {"t": em("f4", "Niño"), "txt": "🌡️ El Niño reforça"}], "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "⚠️ ESTA NOITE · 06/11",
     "itens": [{"t": em("f5", "abafado"), "txt": "🥵 ar abafado"}, {"t": em("f5", "tempestades"), "txt": "⛈️ novas tempestades"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SÁBADO 07/11 · MANHÃ (PREVISÃO)",
     "itens": [{"t": em("f6", "chover"), "txt": "🌧️ chuva forte"}, {"t": em("f6", "Norte"), "txt": "📍 norte gaúcho"},
               {"t": em("f6", "Oeste"), "txt": "📍 oeste catarinense"}, {"t": em("f6", "Paraná"), "txt": "📍 Paraná"}],
     "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "INMET · TEMPESTADE · SÁBADO 07/11",
     "contador": conta(1079, "f7", "1.079", "#ff8c1a", "CIDADES DO SUL"),
     "l": f"PR {T_UF['PR']} · RS {T_UF['RS']} · SC {T_UF['SC']}", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "NORTE GAÚCHO · SÁBADO 07/11",
     "contador": conta(84, "f8", "84", "#5ec8ff", "MM PREVISTOS"),
     "l": "previsão · Open-Meteo", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "SÁBADO PARA DOMINGO (PREVISÃO)",
     "itens": [{"t": em("f9", "volumes"), "txt": "🌊 altos volumes de chuva"}, {"t": em("f9", "centro"), "txt": "📍 centro e leste de SC"}],
     "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f10"), "fim": D1, "k": "PERTO DE CURITIBA (PREVISÃO)",
     "contador": conta(72, "f10", "72", "#96d2ff", "KM/H EM RAJADAS"),
     "l": "previsão · Open-Meteo", "borda": "rgba(150,210,255,.8)"},
    {"ini": D1, "fim": ini("f11"), "k": "DOMINGO 08/11",
     "itens": [{"t": em("f10", "despenca"), "txt": "🥶 temperatura despenca"}, {"t": em("f10", "todo"), "txt": "📍 em todo o Sul"}],
     "l": f"INMET: declínio de temperatura em {FRIO8:,} cidades do Sul".replace(",", "."), "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "cidade"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f11", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
     "borda": "rgba(250,204,21,.8)"},
]
for a, b in zip(paineis, paineis[1:]):
    assert a["fim"] <= b["ini"] + 1e-6, (a["k"], b["k"])
for a in paineis:
    if a.get("contador"):
        c = a["contador"]
        assert a["ini"] - .01 <= c["ini"] and c["ini"] + c["dur"] <= a["fim"], ("contador fora do painel", a["k"])

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": B1, "html": f"<b>{MET}</b>"},
    {"ini": B1, "fim": ini("f6"), "html": f"satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>, avisos de tempestade de 07/11"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>Open-Meteo</b>, chuva prevista para 07/11"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f10"), "fim": D1, "html": "<b>Open-Meteo</b>, rajada prevista"},
    {"ini": D1, "fim": ini("f11"), "html": "<b>INMET</b>, declínio de temperatura de 08/11 · frio: ilustração"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chover": "#5ec8ff", "milimetros": "#5ec8ff", "volumes": "#5ec8ff", "frio": "#96d2ff",
         "umidade": "#5ec8ff", "despenca": "#96d2ff", "temperatura": "#96d2ff", "granizo": "#ff2a1f", "gelo": "#96d2ff",
         "destroi": "#ff2a1f", "destruidas": "#ff2a1f", "tempestade": "#ff8c1a", "tempestades": "#ff8c1a", "aviso": "#ff8c1a",
         "atencao": "#ff8c1a", "rajadas": "#96d2ff", "quilometros": "#96d2ff", "abafado": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "alpestre", "gaucho", "catarinense", "parana", "santa", "catarina", "curitiba", "amazonia", "inemaclub", "cidade"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        if bloco and len(" ".join(b["w"] for b in bloco) + " " + w) > 19:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": t["palavras"][i - 1]["f"] + .12, "palavras": bloco})
            bloco = []
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · IMPACTO SUL", "selo": DATA[:5] + " · INMET · Open-Meteo · NOAA",
     "camera": camera, "sat": SAT, "imagens": [], "colunas": [], "telas": telas, "estados": estados, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
real = sum(m["fim"] - m["ini"] for m in telas)
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} ({IR_DE} a {IR_ATE}) · "
      f"cena real/ilustração {real / DUR:.0%} · mapa {sum(b - a for _, a, b, _ in mapas) / DUR:.0%} · "
      f"cortes {len(cortes)} · menor trecho {min(b - a for a, b in zip(cortes, cortes[1:] + [FIM_VIDEO])):.2f} s")
for nome, a, b, _ in mapas:
    print(f"  mapa {nome}: {a:.2f}–{b:.2f} ({b - a:.2f} s)")
for m in telas:
    print(f"  tela {(m.get('src') or m['seq'][0]).split('/')[1]}: {m['ini']:.2f}–{m['fim']:.2f}")
