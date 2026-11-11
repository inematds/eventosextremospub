#!/usr/bin/env python3
"""Monta cena.js do "Impacto Sul" de 10/11/2026 (terça), visual do auto/roteiro-sul.md (3c, Nei 07/11/2026):
  - dia calmo (só sol e céu limpo nas imagens do dia: céu limpo não entra); o gancho vem do INMET:
    aviso de tempestade para quarta 11/11 em 224 cidades (RS 184, SC 40);
  - ONDE = MAPA: fronteira oeste gaúcha (satélite IR), RS e SC, litoral gaúcho e catarinense, Paraná/Sul, Florianópolis
    → mapa PARADO nele, pino com o nome, estado pintado, >= 3 s desde a palavra do lugar;
  - O QUÊ: mapa de calor e modelos de chuva do dia (micro clipes limpos, sem data/legenda do outro perfil) e
    ilustrações do Codex (tempestade no pampa, vento no litoral, pancada de chuva) com selo "ilustração";
  - DURAÇÃO: nenhuma cena < 2,5 s; mapa >= 3 s.
Fontes: fonte do dia (Meteorologia · 10/11/2026), INMET (avisos 56366, 56365, 56370), GOES-19 IR (NASA GIBS),
Open-Meteo (Florianópolis).
Com avatar: gerar_cena.py --canto (avatar/tempos.json); depois GEO=geo-br.js LAYOUT=canto motor-sul/compor_avatar.sh <esta pasta>
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, math, re, subprocess, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "10/11/2026"
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


# ---------------------------------------------------------------- micro clipes (cenas/clip-NN, 30 fps, limpos do outro perfil)
# clip-01 mapa de calor da tarde · clip-02/03 modelo com núcleos de chuva na fronteira oeste · clip-04/05 chuva espalhada
def nq(nome):
    return len(os.listdir(AQUI / "cenas" / nome))


def clipe(nome, a, b, zoom=.03):
    q = sorted(os.listdir(AQUI / "cenas" / nome))
    assert q and (min(b, FIM_VIDEO) - a) <= len(q) / 30 + .15, (nome, round(b - a, 2), len(q) / 30)
    return {"seq": [f"cenas/{nome}/{x}" for x in q], "fps": 30, "ini": a, "fim": b, "fade": .2, "zoom": zoom}


def foto(src, a, b, selo=None, zoom=.06):
    return {"src": src, "ini": a, "fim": b, "fade": .25, "zoom": zoom, **({"selo": selo} if selo else {})}


def encher(a, b, itens):
    """divide [a, b] em k cenas (cada >= 2,5 s, nenhum clipe além do que tem); itens: nomes de clipe ou ('foto', src[, selo])"""
    b_ef = min(b, FIM_VIDEO)
    cap = lambda it: 1e9 if isinstance(it, tuple) else nq(it) / 30 + .15
    L = b_ef - a
    k = max(1, min(len(itens), int(L // MIN_CENA)))
    durs = [min(cap(it), L / k) for it in itens[:k]]
    fotos = [i for i, it in enumerate(itens[:k]) if isinstance(it, tuple)]
    sobra = L - sum(durs)
    for i in range(k):                      # primeiro nos clipes com folga, depois nas fotos
        if sobra > .01 and i not in fotos:
            mais = min(sobra, cap(itens[i]) - durs[i]); durs[i] += mais; sobra -= mais
    if sobra > .01:
        assert fotos, ("não cabe", itens, round(L, 2))
        for i in fotos:
            durs[i] += sobra / len(fotos)
    out, x0 = [], a
    for i in range(k):
        x1 = x0 + durs[i] if i < k - 1 else b
        it = itens[i]
        out.append(foto(it[1], x0, x1, *(it[2:] or [None])) if isinstance(it, tuple) else clipe(it, x0, x1))
        x0 = x1
    return out


ILU = "ilustração"
BASE, VENTO, PANCADA = ("foto", "capa-dia/base.png", ILU), ("foto", "capa-dia/vento.png", ILU), ("foto", "capa-dia/pancada.png", ILU)
clamp = lambda x, lo, hi: max(lo, min(hi, x))

# ---------------------------------------------------------------- linha do tempo (cada corte na palavra que ele mostra)
CAPA = 2.5                                                        # quadro 0: tempestade no pampa + gancho + data (sem fade)
IR0 = em("f3", "fronteira") - .15                                  # satélite IR + mapa: fronteira oeste gaúcha
B0 = em("f3", "Rio") - .15                                         # mapa B: RS e SC (o IR segue por baixo)
assert B0 - IR0 >= MIN_MAPA, ("fronteira oeste curta", round(B0 - IR0, 2))
B1 = max(B0 + MIN_MAPA, em("f3", "Catarina") + MIN_CENA)
F2 = ini("f2") - .1                                                # o calor entra na pausa antes de "Hoje" (avatar fala mais rápido)
V0 = clamp(em("f2", "atenção") - .1, F2 + MIN_CENA, IR0 - MIN_CENA)   # "o tempo vira": a tempestade chegando
C0 = em("f5", "litoral") - .15                                     # mapa C: litoral gaúcho e catarinense (ventos costeiros)
C1 = max(C0 + MIN_MAPA, em("f5", "catarinense") + MIN_CENA, em("f5", "83") + 1.2)   # o mapa segura até "83 cidades"
D0 = em("f6", "Paraná") - .15                                      # mapa D: Paraná e depois o Sul inteiro (quinta, 856)
D1 = max(D0 + MIN_MAPA, em("f6", "Sul") + MIN_CENA)
E0 = em("f8", "Florianópolis") + .1                                # mapa E: Florianópolis (20 mm na quinta); entra 0,1 s depois da palavra (avatar rápido, limite 0,25)
E1 = max(E0 + MIN_MAPA, em("f8", "Se") - .1)
P0 = clamp(em("f7", "Mas") - .1, D1 + MIN_CENA, E0 - MIN_CENA)     # "pancadas fortes"
J0 = ini("f9")                                                     # engajamento
K0 = ini("f10")                                                    # CTA

# ---------------------------------------------------------------- câmera: só aparece nos trechos de mapa/satélite
K = lambda t, r, pitch=0, bearing=0: {"t": round(t, 3), **r, "pitch": pitch, "bearing": bearing}
FRONT = {"lon": -55.9, "lat": -29.9, "zoom": 6.6}       # fronteira oeste gaúcha
RSSC = {"lon": -52.3, "lat": -28.4, "zoom": 5.9}        # RS e SC
LITORAL = {"lon": -49.4, "lat": -28.8, "zoom": 6.3}     # litoral gaúcho e catarinense
SUL = {"lon": -51.4, "lat": -27.6, "zoom": 5.75}
FLORIPA = {"lon": -48.6, "lat": -27.6, "zoom": 7.6}
VIAGEM = .7                                             # a câmera chega antes do mapa aparecer e fica parada
trechos = [(IR0, B0, FRONT), (B0, B1, RSSC), (C0, C1, LITORAL), (D0, D1, SUL), (E0, E1, FLORIPA)]
camera = [K(0, FRONT)]
for a, b, r in trechos:
    camera += [K(a - VIAGEM, r) if camera[-1]["lon"] != r["lon"] else K(a, r), K(b, r)]
camera.append(K(DUR, SUL))
camera = [c for i, c in enumerate(camera) if i == 0 or c["t"] > camera[i - 1]["t"]]
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: GOES-19 infravermelho de terça 10/11 (f3)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 130 and "2026-11-10T00:00:00Z" <= TS[i] < "2026-11-11T03:00:00Z"]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


IR1 = B1
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": IR0, "fim": IR1, "dur": IR1 - IR0, "alfa": .9, "rotulo": "satélite · infravermelho"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])
assert len(BONS) >= 20, f"poucos quadros bons de infravermelho: {len(BONS)}"

# ---------------------------------------------------------------- telas (clipes do dia e ilustrações)
telas = [foto("capa-dia/abertura.png", 0, CAPA, zoom=.05)]                       # tempestade no pampa + gancho + data
telas += encher(CAPA, F2, ["clip-02", PANCADA])                                  # "alerta de tempestade": núcleos de chuva
telas += encher(F2, V0, ["clip-01"])                                      # "o sol dominou, a tarde esquentou": calor
telas += encher(V0, IR0, [BASE])                                                 # "o tempo vira de novo": tempestade chegando
# satélite IR (fronteira oeste) → mapa B (RS e SC)
telas += encher(B1, C0, [BASE, "clip-03"])                                       # "aviso de tempestade ... 224 cidades"
# mapa C (litoral)
telas += encher(C1, D0, [VENTO])                                                 # "ventos costeiros": mar agitado
# mapa D (Paraná, Sul)
telas += encher(D1, P0, ["clip-04"])                                             # "volumes menores": chuva espalhada, fraca
telas += encher(P0, E0, [PANCADA])                                               # "pancadas fortes em alguns pontos"
# mapa E (Florianópolis)
telas += encher(E1, J0, ["clip-03", BASE])                                             # "fique de olho no céu"
telas += encher(J0, K0, ["clip-05", PANCADA])                                    # pergunta
telas += encher(K0, DUR, ["clip-02"])                                                 # CTA (o vídeo acaba com o avatar)
assert telas[0]["ini"] == 0   # vis() não faz fade-in quando ini <= 0 (quadro 0 cheio)

# ---------------------------------------------------------------- portões das 3 regras (3c)
mapas = [("IR fronteira oeste", IR0, B0, em("f3", "fronteira")), ("B RS e SC", B0, B1, em("f3", "Rio")),
         ("C litoral", C0, C1, em("f5", "litoral")), ("D Paraná/Sul", D0, D1, em("f6", "Paraná")),
         ("E Florianópolis", E0, E1, em("f8", "Florianópolis"))]
for m in telas:
    assert min(m["fim"], FIM_VIDEO) - m["ini"] >= MIN_CENA - .01, ("cena curta", m.get("src") or m["seq"][0], round(min(m["fim"], FIM_VIDEO) - m["ini"], 2))
for nome, a, b, palavra in mapas:
    assert b - a >= MIN_MAPA - .01, ("mapa curto", nome, round(b - a, 2))
    assert a <= palavra + .25, ("mapa entra depois da palavra do lugar", nome, round(a - palavra, 2))
# lugares ditos (f1 "cidades gaúchas"/"impacto no Sul" ficam na capa: é o gancho escrito; f4 "dois estados" retoma o
# mapa B; f8 "região" e f9 "cidade do Sul" falam com o público, não são lugar do fato)
fim_mapa = lambda t: max(b for _, a, b, _ in mapas if a - .01 <= t + .25 and t < b)
LUGARES = [("f3", "fronteira"), ("f3", "Rio"), ("f3", "Catarina"), ("f5", "litoral"), ("f5", "catarinense"),
           ("f6", "Paraná"), ("f6", "Sul"), ("f8", "Florianópolis")]
for fid, w in LUGARES:
    assert any(a - .01 <= em(fid, w) + .25 and em(fid, w) < b for _, a, b, _ in mapas), ("lugar fora de mapa", fid, w)
    ate = fim_mapa(em(fid, w))
    if fid == "f3" and w == "fronteira":
        ate = B1          # o satélite emenda no mapa de RS e SC
    assert ate - em(fid, w) >= MIN_MAPA - .51, ("lugar com mapa curto", fid, w, round(ate - em(fid, w), 2))
cortes = sorted({0, *[x for m in telas for x in (m["ini"], m["fim"])], *[x for _, a, b, _ in mapas for x in (a, b)]})
cortes = [c for c in cortes if c < FIM_VIDEO - .05]
for a, b in zip(cortes, cortes[1:] + [FIM_VIDEO]):
    assert b - a >= MIN_CENA - .01, ("trecho curto (pisca)", round(a, 2), round(b, 2))
ocup = sorted([(m["ini"], m["fim"]) for m in telas] + [(a, b) for _, a, b, _ in mapas])
for (a, b), (c, d) in zip(ocup, ocup[1:]):
    assert abs(b - c) < .02, ("buraco/sobreposição na linha do tempo", round(b, 2), round(c, 2))
assert abs(ocup[-1][1] - DUR) < .02

# ---------------------------------------------------------------- números dos brutos
from collections import Counter
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
SULC = {"41": "PR", "42": "SC", "43": "RS"}
geo = lambda i: {c for c in aviso[i]["geocodes"].split(",") if c[:2] in SULC}
uf = lambda g: Counter(SULC[c[:2]] for c in g)
assert aviso[56366]["descricao"] == "Tempestade" and aviso[56366]["inicio"].startswith("2026-11-11")
TQUA = geo(56366); TQUA_UF = uf(TQUA)
assert len(TQUA) == 224 and (TQUA_UF["RS"], TQUA_UF["SC"]) == (184, 40), TQUA_UF     # f1/f4
assert aviso[56365]["descricao"] == "Ventos Costeiros" and aviso[56365]["fim"].startswith("2026-11-11 09")
VCOS = geo(56365); VCOS_UF = uf(VCOS)
assert len(VCOS) == 83 and (VCOS_UF["RS"], VCOS_UF["SC"]) == (43, 40), VCOS_UF       # f5
assert aviso[56370]["descricao"] == "Tempestade" and aviso[56370]["inicio"].startswith("2026-11-12")
TQUI = geo(56370); TQUI_UF = uf(TQUI)
assert len(TQUI) == 856 and (TQUI_UF["PR"], TQUI_UF["SC"], TQUI_UF["RS"]) == (322, 271, 263), TQUI_UF   # f6

OM = json.loads((B / "openmeteo_capitais_3d.json").read_text())
FLN = next(x for x in OM if abs(x["latitude"] + 27.59) < .05)["daily"]
assert FLN["time"][2] == "2026-11-12" and round(FLN["precipitation_sum"][2]) == 20, FLN["precipitation_sum"]   # f8

# ---------------------------------------------------------------- mapa: estados pintados e pinos (só nos trechos de mapa)
Q2 = em("f6", "quinta", 2)                                         # "Na quinta": o Sul inteiro
estados = [
    {"id": "b_rs", "ini": B0, "fim": B1, "ufs": ["RS"], "cor": VERM, "alfa": .32},
    {"id": "b_sc", "ini": em("f3", "Catarina") - .3, "fim": B1, "ufs": ["SC"], "cor": LAR, "alfa": .3},
    {"id": "c_lit", "ini": C0, "fim": C1, "ufs": ["RS", "SC"], "cor": LAR, "alfa": .22},
    {"id": "d_pr", "ini": D0, "fim": D1, "ufs": ["PR"], "cor": VERM, "alfa": .3},
    {"id": "d_sul", "ini": max(D0, Q2 - .2), "fim": D1, "ufs": ["RS", "SC"], "cor": VERM, "alfa": .3},
    {"id": "e_sc", "ini": E0, "fim": E1, "ufs": ["SC"], "cor": AZUL, "alfa": .3},
]
pino = lambda nome, sub, lon, lat, a, b, h=120: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    pino("Fronteira oeste", "chuva na quarta de manhã (previsão)", -56.2, -29.9, IR0, B0),
    pino("Rio Grande do Sul", f"{TQUA_UF['RS']} cidades · tempestade quarta", -53.4, -29.7, B0, B1, 80),
    pino("Santa Catarina", f"{TQUA_UF['SC']} cidades · tempestade quarta", -51.4, -27.0, em("f3", "Catarina") - .3, B1, 80),
    pino("Litoral gaúcho", f"{VCOS_UF['RS']} cidades · ventos costeiros", -50.15, -29.95, C0, C1, 90),
    pino("Litoral catarinense", f"{VCOS_UF['SC']} cidades · ventos costeiros", -48.7, -27.6, em("f5", "catarinense") - .3, C1, 90),
    pino("Paraná", f"{TQUI_UF['PR']} cidades · tempestade quinta", -51.6, -24.9, D0, D1, 70),
    pino("Sul", f"{len(TQUI)} cidades em aviso na quinta", -52.4, -28.9, em("f6", "Sul") - .3, D1, 70),
    pino("Florianópolis", f"{round(FLN['precipitation_sum'][2])} mm na quinta (previsão)", -48.55, -27.6, E0, E1, 110),
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
    {"ini": CAPA, "fim": ini("f2"), "k": "⚠️ QUARTA 11/11 · RIO GRANDE DO SUL",
     "itens": [{"t": CAPA, "txt": f"⛈️ tempestade em {TQUA_UF['RS']} cidades"}], "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "HOJE · TERÇA 10/11 · SUL",
     "itens": [{"t": em("f2", "sol"), "txt": "☀️ sol nos três estados"}, {"t": em("f2", "esquentou"), "txt": "🌡️ tarde mais quente"},
               {"t": em("f2", "atenção"), "txt": "⚠️ o tempo vira de novo"}], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "⚠️ QUARTA 11/11 (PREVISÃO)",
     "itens": [{"t": em("f3", "fronteira"), "txt": "🌧️ manhã: fronteira oeste (RS)"},
               {"t": em("f3", "tarde"), "txt": "🌧️ tarde: RS e SC"}], "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "INMET · TEMPESTADE · QUARTA 11/11",
     "contador": conta(len(TQUA), "f4", "224", "#FACC15", "CIDADES NO RS E EM SC"),
     "l": f"RS {TQUA_UF['RS']} · SC {TQUA_UF['SC']} · perigo potencial", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "INMET · VENTOS COSTEIROS",
     "contador": conta(len(VCOS), "f5", "83", "#FACC15", "CIDADES NO LITORAL"),
     "l": f"RS {VCOS_UF['RS']} · SC {VCOS_UF['SC']} · até quarta 9h", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "INMET · TEMPESTADE · QUINTA 12/11",
     "contador": conta(len(TQUI), "f6", "856", "#FACC15", "CIDADES DO SUL"),
     "l": f"PR {TQUI_UF['PR']} · SC {TQUI_UF['SC']} · RS {TQUI_UF['RS']}", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "⚠️ PRÓXIMOS DIAS (PREVISÃO)",
     "itens": [{"t": em("f7", "menores"), "txt": "🌦️ volumes menores"}, {"t": em("f7", "primavera"), "txt": "🌸 primavera + El Niño"},
               {"t": em("f7", "pancadas"), "txt": "⛈️ pancadas fortes isoladas"}], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "FLORIANÓPOLIS (PREVISÃO)",
     "contador": conta(round(FLN["precipitation_sum"][2]), "f8", "20", "#5ec8ff", "MM DE CHUVA NA QUINTA"),
     "l": "Open-Meteo · quinta 12/11", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f9", "cidade"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f9", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
     "borda": "rgba(250,204,21,.8)"},
]
for a, b in zip(paineis, paineis[1:]):
    assert a["fim"] <= b["ini"] + 1e-6, (a["k"], b["k"])
for a in paineis:
    if a.get("contador"):
        c = a["contador"]
        assert a["ini"] - .01 <= c["ini"] and c["ini"] + c["dur"] <= a["fim"], ("contador fora do painel", a["k"])

cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "<b>INMET</b>, aviso de tempestade para 11/11 · ilustração"},
    {"ini": ini("f2"), "fim": IR0, "html": f"<b>{MET}</b>"},
    {"ini": IR0, "fim": ini("f4"), "html": f"satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE} · <b>{MET}</b> · previsão"},
    {"ini": ini("f4"), "fim": ini("f7"), "html": "<b>INMET</b>, avisos de tempestade (11 e 12/11) e de ventos costeiros · ilustração"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b> · previsão · ilustração"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>Open-Meteo</b>, previsão para Florianópolis"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "volumes": "#5ec8ff", "sol": "#ff8c1a", "esquentou": "#ff8c1a",
         "tempestade": "#ff2a1f", "alerta": "#ff2a1f", "pancadas": "#ff2a1f", "fortes": "#ff2a1f", "vento": "#ff8c1a",
         "ventos": "#ff8c1a", "costeiros": "#ff8c1a", "aviso": "#ff8c1a", "atencao": "#ff8c1a", "preocupa": "#ff8c1a",
         "elnino": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "rio", "grande", "fronteira", "oeste", "gauchas", "gaucha", "gaucho", "santa", "catarina", "catarinense",
         "litoral", "parana", "florianopolis", "inemaclub", "cidade"}
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
