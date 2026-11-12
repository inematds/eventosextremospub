#!/usr/bin/env python3
"""Monta cena.js do "Impacto Sul" de 11/11/2026 (quarta), visual do auto/roteiro-sul.md (3c, Nei 07/11/2026):
  - a chuva voltou cedo pelo noroeste gaúcho e oeste catarinense, pancadas mais fortes nas Missões (fonte do dia);
  - gancho do INMET: aviso de tempestade até quinta 12h em 470 cidades do Sul (SC 257, PR 183, RS 30);
    quinta 12/11: 286 cidades do Paraná; Curitiba 19 mm na quinta (Open-Meteo);
  - ONDE = MAPA: noroeste gaúcho / oeste catarinense / Missões (satélite IR), Sul (470), oeste do Paraná, Curitiba
    → mapa PARADO nele, pino com o nome, estado pintado, >= 3 s desde a palavra do lugar;
  - O QUÊ: modelo de chuva e radar do dia (micro clipes limpos: sem data, legenda ou rosto do outro perfil) e
    ilustrações do Codex (tempestade sobre o oeste catarinense, temporal na lavoura, pancada na cidade) com selo "ilustração";
  - o céu nublado do dia não entra (não mostra o fenômeno);
  - DURAÇÃO: nenhuma cena < 2,5 s; mapa >= 3 s.
Fontes: fonte do dia (Meteorologia · 11/11/2026), INMET (avisos 56378, 56381), GOES-19 IR (NASA GIBS), Open-Meteo (Curitiba).
Com avatar: gerar_cena.py --canto (avatar/tempos.json); depois GEO=geo-br.js LAYOUT=canto motor-sul/compor_avatar.sh <esta pasta>
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, math, re, subprocess, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "11/11/2026"
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
# clip-01 modelo de chuva com núcleos fortes (Paraguai → oeste gaúcho), data apagada com delogo
# clip-02/03 radar com núcleos vermelhos nas Missões (Santa Rosa, Santo Ângelo), recorte sem a data
# clip-04 modelo com a chuva espalhada pelo Sul (data apagada)
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
BASE, TROVOADA, PANCADA = (("foto", "capa-dia/base.png", ILU), ("foto", "capa-dia/trovoada.png", ILU),
                           ("foto", "capa-dia/pancada.png", ILU))
clamp = lambda x, lo, hi: max(lo, min(hi, x))

# ---------------------------------------------------------------- linha do tempo (cada corte na palavra que ele mostra)
CAPA = 2.5                                                         # quadro 0: tempestade no oeste catarinense + gancho + data
IR0 = em("f2", "noroeste") - .15                                   # satélite IR + mapa: noroeste gaúcho, oeste de SC, Missões
IR1 = max(IR0 + MIN_MAPA, em("f3", "Missões") + MIN_MAPA, em("f3", "Sul") + MIN_CENA)
C0 = em("f5", "470") - .3                                          # mapa C: o Sul inteiro em aviso (470 cidades)
C1 = max(C0 + MIN_MAPA, em("f5", "Sul") + MIN_MAPA)
D0 = em("f7", "oeste") - .15                                       # mapa D: oeste do Paraná (286 cidades na quinta)
E0 = em("f8", "Curitiba") - .15                                    # mapa E: Curitiba (19 mm na quinta), emenda no D
D1 = E0
E1 = max(E0 + MIN_MAPA, em("f8", "quinta") + 1.2)
J0 = min(ini("f9"), ini("f10") - 2 * MIN_CENA - .05)                # engajamento (avatar rápido: cabe clipe + foto)
K0 = ini("f10")                                                    # CTA

# ---------------------------------------------------------------- câmera: só aparece nos trechos de mapa/satélite
K = lambda t, r, pitch=0, bearing=0: {"t": round(t, 3), **r, "pitch": pitch, "bearing": bearing}
NOROESTE = {"lon": -53.6, "lat": -27.9, "zoom": 6.2}    # noroeste gaúcho + oeste catarinense + Missões
SUL = {"lon": -51.4, "lat": -27.4, "zoom": 5.7}
OESTEPR = {"lon": -52.6, "lat": -24.9, "zoom": 6.5}
CURITIBA = {"lon": -49.4, "lat": -25.45, "zoom": 7.4}
VIAGEM = .7                                             # a câmera chega antes do mapa aparecer e fica parada
trechos = [(IR0, IR1, NOROESTE), (C0, C1, SUL), (D0, D1, OESTEPR), (E0, E1, CURITIBA)]
camera = [K(0, NOROESTE)]
for a, b, r in trechos:
    camera += [K(a - VIAGEM, r) if camera[-1]["lon"] != r["lon"] else K(a, r), K(b, r)]
camera.append(K(DUR, SUL))
camera = [c for i, c in enumerate(camera) if i == 0 or c["t"] > camera[i - 1]["t"]]
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: GOES-19 infravermelho de quarta 11/11 (f2/f3)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 130 and "2026-11-11T00:00:00Z" <= TS[i] < "2026-11-12T03:00:00Z"]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": IR0, "fim": IR1, "dur": IR1 - IR0, "alfa": .9, "rotulo": "satélite · infravermelho"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])
assert len(BONS) >= 20, f"poucos quadros bons de infravermelho: {len(BONS)}"

# ---------------------------------------------------------------- telas (clipes do dia e ilustrações)
telas = [foto("capa-dia/abertura.png", 0, CAPA, zoom=.05)]                       # tempestade + gancho + data
telas += encher(CAPA, IR0, ["clip-01", PANCADA, BASE])                                    # "alerta de tempestade" / "a chuva voltou"
# satélite IR (noroeste gaúcho, oeste de SC, Missões)
telas += encher(IR1, C0, ["clip-02", TROVOADA, "clip-01"])                       # "pancadas mais fortes" (radar) / "nuvens de tempestade"
# mapa C (Sul, 470)
telas += encher(C1, D0, ["clip-03", PANCADA, TROVOADA])                          # "50 mm, vento de 60 km/h, granizo"
# mapa D (oeste do Paraná) → mapa E (Curitiba)
telas += encher(E1, J0, ["clip-04", PANCADA])                                    # "volumes não altos, mas pancada isolada"
telas += encher(J0, K0, ["clip-02", BASE])                                       # pergunta
telas += encher(K0, DUR, ["clip-03", BASE])                                            # CTA (o vídeo acaba com o avatar)
assert telas[0]["ini"] == 0   # vis() não faz fade-in quando ini <= 0 (quadro 0 cheio)

# ---------------------------------------------------------------- portões das 3 regras (3c)
mapas = [("IR noroeste/Missões", IR0, IR1, em("f2", "noroeste")), ("C Sul", C0, C1, em("f5", "470")),
         ("D oeste do Paraná", D0, D1, em("f7", "oeste")), ("E Curitiba", E0, E1, em("f8", "Curitiba"))]
for m in telas:
    assert min(m["fim"], FIM_VIDEO) - m["ini"] >= MIN_CENA - .01, ("cena curta", m.get("src") or m["seq"][0], round(min(m["fim"], FIM_VIDEO) - m["ini"], 2))
for nome, a, b, palavra in mapas:
    assert b - a >= MIN_MAPA - .01, ("mapa curto", nome, round(b - a, 2))
    assert a <= palavra + .25, ("mapa entra depois da palavra do lugar", nome, round(a - palavra, 2))
# lugares ditos (f1 "catarinenses"/"impacto no Sul" ficam na capa: é o gancho escrito; f4 "região" e f9 "cidade do Sul"
# não são lugar do fato)
fim_mapa = lambda t: max(b for _, a, b, _ in mapas if a - .01 <= t + .25 and t < b)
LUGARES = [("f2", "noroeste"), ("f2", "Santa"), ("f3", "Missões"), ("f3", "Rio"), ("f5", "Sul"),
           ("f7", "oeste"), ("f7", "Paraná"), ("f8", "Curitiba")]
for fid, w in LUGARES:
    assert any(a - .01 <= em(fid, w) + .25 and em(fid, w) < b for _, a, b, _ in mapas), ("lugar fora de mapa", fid, w)
    ate = fim_mapa(em(fid, w))
    if fid == "f7":
        ate = E1          # o mapa do oeste do Paraná emenda no de Curitiba
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
assert aviso[56378]["descricao"] == "Tempestade" and aviso[56378]["fim"].startswith("2026-11-12 12")
TATE = geo(56378); TATE_UF = uf(TATE)
assert len(TATE) == 470 and (TATE_UF["SC"], TATE_UF["PR"], TATE_UF["RS"]) == (257, 183, 30), TATE_UF   # f1/f5
assert "50 mm/dia" in aviso[56378]["riscos"][0] and "40-60 km/h" in aviso[56378]["riscos"][0] and "granizo" in aviso[56378]["riscos"][0]  # f6
assert aviso[56381]["descricao"] == "Tempestade" and aviso[56381]["inicio"].startswith("2026-11-12")
TQUI = geo(56381); TQUI_UF = uf(TQUI)
assert len(TQUI) == 286 and TQUI_UF["PR"] == 286, TQUI_UF                                              # f7

OM = json.loads((B / "openmeteo_capitais_3d.json").read_text())
CWB = next(x for x in OM if abs(x["latitude"] + 25.41) < .05)["daily"]
assert CWB["time"][1] == "2026-11-12" and round(CWB["precipitation_sum"][1]) == 19, CWB["precipitation_sum"]   # f8

# ---------------------------------------------------------------- mapa: estados pintados e pinos (só nos trechos de mapa)
estados = [
    {"id": "a_rs", "ini": IR0, "fim": IR1, "ufs": ["RS"], "cor": LAR, "alfa": .22},
    {"id": "a_sc", "ini": em("f2", "Santa") - .3, "fim": IR1, "ufs": ["SC"], "cor": LAR, "alfa": .22},
    {"id": "c_sc", "ini": C0, "fim": C1, "ufs": ["SC"], "cor": VERM, "alfa": .34},
    {"id": "c_pr", "ini": C0, "fim": C1, "ufs": ["PR"], "cor": LAR, "alfa": .3},
    {"id": "c_rs", "ini": C0, "fim": C1, "ufs": ["RS"], "cor": AMA, "alfa": .18},
    {"id": "d_pr", "ini": D0, "fim": E1, "ufs": ["PR"], "cor": VERM, "alfa": .3},
]
pino = lambda nome, sub, lon, lat, a, b, h=120: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    pino("Noroeste gaúcho", "a chuva voltou hoje cedo", -54.0, -27.9, IR0, IR1, 90),
    pino("Oeste catarinense", "nuvens carregadas", -52.6, -26.9, em("f2", "Santa") - .3, IR1, 130),
    pino("Missões", "pancadas mais fortes de manhã", -54.3, -28.3, em("f3", "Missões") - .3, IR1, 60),
    pino("Santa Catarina", f"{TATE_UF['SC']} cidades em aviso", -50.6, -27.3, C0, C1, 90),
    pino("Paraná", f"{TATE_UF['PR']} cidades em aviso", -51.6, -24.9, C0, C1, 70),
    pino("Rio Grande do Sul", f"{TATE_UF['RS']} cidades em aviso", -51.0, -29.2, C0, C1, 70),
    pino("Oeste do Paraná", f"{len(TQUI)} cidades do PR · tempestade quinta", -53.46, -24.95, D0, D1, 110),
    pino("Curitiba", f"{round(CWB['precipitation_sum'][1])} mm na quinta (previsão)", -49.27, -25.43, E0, E1, 110),
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
    {"ini": CAPA, "fim": ini("f2"), "k": "⚠️ INMET · ATÉ QUINTA 12/11 · SC",
     "itens": [{"t": CAPA, "txt": f"⛈️ tempestade em {TATE_UF['SC']} cidades"}], "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "HOJE · QUARTA 11/11 · SUL",
     "itens": [{"t": em("f2", "chuva"), "txt": "🌧️ a chuva voltou cedo"}, {"t": em("f2", "noroeste"), "txt": "📍 noroeste do RS"},
               {"t": em("f2", "Santa"), "txt": "📍 oeste de SC"}], "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "HOJE DE MANHÃ · MISSÕES (RS)",
     "itens": [{"t": em("f3", "pancadas"), "txt": "⛈️ pancadas mais fortes"}], "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "POR QUÊ",
     "itens": [{"t": em("f4", "quente"), "txt": "🌡️ ar quente sobre o Sul"}, {"t": em("f4", "umidade"), "txt": "💧 calor + umidade"},
               {"t": em("f4", "tempestade"), "txt": "⛈️ nuvens de tempestade crescem"}], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "INMET · TEMPESTADE · ATÉ QUINTA 12H",
     "contador": conta(len(TATE), "f5", "470", "#FACC15", "CIDADES DO SUL"),
     "l": f"SC {TATE_UF['SC']} · PR {TATE_UF['PR']} · RS {TATE_UF['RS']} · perigo potencial", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "⚠️ O QUE O AVISO PREVÊ",
     "itens": [{"t": em("f6", "50"), "txt": "🌧️ até 50 mm por dia"}, {"t": em("f6", "60"), "txt": "💨 vento até 60 km/h"},
               {"t": em("f6", "granizo"), "txt": "🧊 queda de granizo"}], "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "INMET · TEMPESTADE · QUINTA 12/11",
     "contador": conta(len(TQUI), "f7", "286", "#FACC15", "CIDADES DO PARANÁ"),
     "l": "aviso para quinta inteira · perigo potencial", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CURITIBA (PREVISÃO)",
     "contador": conta(round(CWB["precipitation_sum"][1]), "f8", "19", "#5ec8ff", "MM DE CHUVA NA QUINTA"),
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
    {"ini": CAPA, "fim": ini("f2"), "html": "<b>INMET</b>, aviso de tempestade até 12/11 · ilustração"},
    {"ini": ini("f2"), "fim": IR0, "html": f"<b>{MET}</b>"},
    {"ini": IR0, "fim": ini("f4"), "html": f"satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE} · <b>{MET}</b>"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>{MET}</b> · ilustração"},
    {"ini": ini("f5"), "fim": ini("f8"), "html": "<b>INMET</b>, avisos de tempestade (11 e 12/11) · ilustração"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>Open-Meteo</b>, previsão para Curitiba · <b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "volumes": "#5ec8ff", "umidade": "#5ec8ff", "quente": "#ff8c1a",
         "calor": "#ff8c1a", "tempestade": "#ff2a1f", "alerta": "#ff2a1f", "pancadas": "#ff2a1f", "pancada": "#ff2a1f",
         "fortes": "#ff2a1f", "granizo": "#ff2a1f", "raios": "#ff2a1f", "vento": "#ff8c1a", "aviso": "#ff8c1a",
         "atencao": "#ff8c1a", "carregadas": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "rio", "grande", "noroeste", "oeste", "gaucho", "santa", "catarina", "catarinenses", "missoes",
         "parana", "paranaenses", "curitiba", "inemaclub", "cidade"}
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
