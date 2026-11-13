#!/usr/bin/env python3
"""Monta cena.js do "Impacto Sul" de 12/11/2026 (quinta), visual do auto/roteiro-sul.md (3c, Nei 07/11/2026):
  - gancho (fonte do dia): mais de 100 mm em pouco mais de 1 hora no extremo noroeste gaúcho no fim da tarde;
  - RS: Palmeira das Missões (água dentro de casas, vento, granizo) e Rodeio Bonito (árvores caídas, suspeita de tornado);
  - PR: Itapejara do Oeste, perto de Pato Branco (granizo na rodovia) e Prudentópolis (granizo grande, ventania);
  - INMET: aviso de tempestade até 23h59 de hoje em 612 cidades (PR 399, SC 213); novas pancadas à noite e na sexta;
  - Open-Meteo: Porto Alegre perto de 30 °C no sábado (a temperatura dispara sexta/sábado, fonte do dia);
  - ONDE = MAPA: noroeste do RS (satélite IR), Paraná, PR+SC (612), Porto Alegre → mapa PARADO, pino, estado pintado;
  - O QUÊ: micro clipes e quadros reais do dia, limpos (sem data, sirene, legenda ou rosto do outro perfil);
  - DURAÇÃO: nenhuma cena < 2,5 s; mapa >= 3 s.
Fontes: fonte do dia (Meteorologia · 12/11/2026), INMET (avisos 56383, 56389), GOES-19 IR (NASA GIBS), Open-Meteo (Porto Alegre).
Com avatar: gerar_cena.py --canto (avatar/tempos.json); depois GEO=geo-br.js LAYOUT=canto motor-sul/compor_avatar.sh <esta pasta>
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, math, re, subprocess, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "12/11/2026"
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
# recortes na área sem sirene/data (canto de cima à esquerda) e sem a legenda queimada (embaixo); conferidos quadro a quadro
# clip-01/02 enxurrada na estrada, extremo noroeste do RS (v4)    clip-03 água dentro de casa, Palmeira das Missões (v2)
# clip-04 destroços, suspeita de tornado, Rodeio Bonito (v3)       clip-05 árvores caídas, Rodeio Bonito (v3)
# clip-06 granizo no posto, Itapejara do Oeste (v3)                clip-07 granizo na mão, Prudentópolis (v4)
# clip-08 ventania nas árvores, Prudentópolis (v4)                 clip-09 lavoura tombada, Prudentópolis (v4)
# clip-10 nuvem de tempestade com chuva, RS (v2)                   clip-11 radar com núcleos fortes, noroeste do RS (v2)
# clip-12 estrada sob chuva forte, RS (v2)                         clip-13 granizo caindo no campo, Itapejara do Oeste (v3)
# real-01 granizo na mão · real-02 água dentro de casa · real-03 lavoura tombada · real-04 radar · real-05 nuvem com chuva
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
    cap = lambda it: 1e9 if isinstance(it, tuple) else nq(it) / 30 + .14
    L = b_ef - a
    k = max(1, min(len(itens), int(L // MIN_CENA)))
    if sum(cap(it) for it in itens[:k]) < L and not any(isinstance(it, tuple) for it in itens[:k]):
        fx = [it for it in itens[k:] if isinstance(it, tuple)]   # os clipes não cobrem o trecho: a foto entra no lugar do último
        if fx:
            itens = itens[:k - 1] + fx[:1]
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


R = lambda i: ("foto", f"cenas/real-{i:02d}.jpg")
MAO, CASA, LAVOURA, RADAR, NUVEM = R(1), R(2), R(3), R(4), R(5)

# ---------------------------------------------------------------- linha do tempo (cada corte na palavra que ele mostra)
CAPA = 2.5                                                         # quadro 0: enxurrada real + gancho + data
IR0 = em("f2", "noroeste") - .15                                   # satélite IR + mapa: noroeste do RS, Palmeira, Rodeio Bonito
IR1 = max(IR0 + 4.0, em("f2", "Rodeio") + 2.6)
P0 = em("f4", "Paraná") - .15                                      # mapa P: Paraná (Pato Branco, Itapejara, Prudentópolis)
P1 = max(P0 + MIN_MAPA, em("f4", "Prudentópolis") + 2.6)
C0 = em("f7", "612") - .3                                          # mapa C: 612 cidades do PR e SC em aviso
C1 = max(C0 + MIN_MAPA, em("f7", "Santa") + 2.6)
A0 = ini("f9") - .1                                                # mapa A: Porto Alegre perto de 30 °C no sábado
A1 = max(A0 + MIN_MAPA, em("f9", "Porto") + 2.6, em("f9", "sábado") + .5)
J0 = A1                                                            # engajamento: emenda no mapa de Porto Alegre
K0 = max(ini("f11"), J0 + MIN_CENA)                                # CTA

# ---------------------------------------------------------------- câmera: só aparece nos trechos de mapa/satélite
K = lambda t, r, pitch=0, bearing=0: {"t": round(t, 3), **r, "pitch": pitch, "bearing": bearing}
NOROESTE = {"lon": -53.7, "lat": -27.75, "zoom": 7.0}   # extremo noroeste + Palmeira das Missões + Rodeio Bonito
PARANA = {"lon": -51.9, "lat": -25.75, "zoom": 6.7}     # Itapejara/Pato Branco + Prudentópolis
PRSC = {"lon": -51.0, "lat": -26.2, "zoom": 5.8}
POA = {"lon": -51.23, "lat": -30.03, "zoom": 7.2}
SUL = {"lon": -51.4, "lat": -27.4, "zoom": 5.7}
VIAGEM = .7                                             # a câmera chega antes do mapa aparecer e fica parada
trechos = [(IR0, IR1, NOROESTE), (P0, P1, PARANA), (C0, C1, PRSC), (A0, A1, POA)]
camera = [K(0, NOROESTE)]
for a, b, r in trechos:
    camera += [K(a - VIAGEM, r) if camera[-1]["lon"] != r["lon"] else K(a, r), K(b, r)]
camera.append(K(DUR, POA))
camera = [c for i, c in enumerate(camera) if i == 0 or c["t"] > camera[i - 1]["t"]]
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: GOES-19 infravermelho de quinta 12/11 (f2)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 130 and "2026-11-12T00:00:00Z" <= TS[i] < "2026-11-13T03:00:00Z"]
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

# ---------------------------------------------------------------- telas (clipes e quadros reais do dia)
telas = [foto("capa-dia/abertura.png", 0, CAPA, zoom=.05)]                       # enxurrada + gancho + data
telas += encher(CAPA, IR0, ["clip-01", "clip-02", RADAR])                               # "100 milímetros em pouco mais de 1 hora"
# satélite IR (extremo noroeste, Palmeira das Missões, Rodeio Bonito)
telas += encher(IR1, P0, ["clip-03", "clip-04", "clip-05", CASA])                 # "água invadiu casas... árvores... tornado"
# mapa P (Paraná)
telas += encher(P1, ini("f6"), ["clip-13", "clip-06", "clip-07", MAO])           # "granizo assustou motoristas... encher a mão"
telas += encher(ini("f6"), C0, ["clip-10", "clip-08", NUVEM])         # "calor e umidade, nuvens de tempestade"
# mapa C (PR + SC, 612)
telas += encher(C1, A0, ["clip-11", "clip-12", RADAR])                            # "novas pancadas à noite e na sexta"
# mapa A (Porto Alegre)
telas += encher(J0, K0, ["clip-09", LAVOURA, MAO])                                    # pergunta
telas += encher(K0, DUR, ["clip-02", CASA])                                     # CTA (o vídeo acaba com o avatar)
assert telas[0]["ini"] == 0   # vis() não faz fade-in quando ini <= 0 (quadro 0 cheio)

# ---------------------------------------------------------------- portões das 3 regras (3c)
mapas = [("IR noroeste do RS", IR0, IR1, em("f2", "noroeste")), ("P Paraná", P0, P1, em("f4", "Paraná")),
         ("C PR+SC", C0, C1, em("f7", "612")), ("A Porto Alegre", A0, A1, em("f9", "Porto"))]
for m in telas:
    assert min(m["fim"], FIM_VIDEO) - m["ini"] >= MIN_CENA - .01, ("cena curta", m.get("src") or m["seq"][0], round(min(m["fim"], FIM_VIDEO) - m["ini"], 2))
for nome, a, b, palavra in mapas:
    assert b - a >= MIN_MAPA - .01, ("mapa curto", nome, round(b - a, 2))
    assert a <= palavra + .25, ("mapa entra depois da palavra do lugar", nome, round(a - palavra, 2))
# lugares ditos (f1 "noroeste gaúcho"/"Sul" ficam na capa: é o gancho escrito; f10 "cidade do Sul" não é lugar do fato)
fim_mapa = lambda t: max(b for _, a, b, _ in mapas if a - .01 <= t + .25 and t < b)
LUGARES = [("f2", "noroeste"), ("f2", "Rio"), ("f2", "Palmeira"), ("f2", "Rodeio"), ("f4", "Paraná"), ("f4", "Pato"),
           ("f4", "Itapejara"), ("f4", "Prudentópolis"), ("f7", "Paraná"), ("f7", "Santa"), ("f9", "Porto")]
for fid, w in LUGARES:
    assert any(a - .01 <= em(fid, w) + .25 and em(fid, w) < b for _, a, b, _ in mapas), ("lugar fora de mapa", fid, w)
    assert fim_mapa(em(fid, w)) - em(fid, w) >= MIN_MAPA - .51, ("lugar com mapa curto", fid, w, round(fim_mapa(em(fid, w)) - em(fid, w), 2))
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
assert aviso[56383]["descricao"] == "Tempestade" and aviso[56383]["fim"].startswith("2026-11-12 23:59")
THOJE = geo(56383); THOJE_UF = uf(THOJE)
assert len(THOJE) == 612 and (THOJE_UF["PR"], THOJE_UF["SC"], THOJE_UF["RS"]) == (399, 213, 0), THOJE_UF   # f7
R0 = aviso[56383]["riscos"][0]
assert "50 mm/dia" in R0 and "40-60 km/h" in R0 and "granizo" in R0                                       # f8
assert aviso[56389]["descricao"] == "Tempestade" and aviso[56389]["inicio"].startswith("2026-11-13")
TSEX = geo(56389); assert len(TSEX) == 14 and uf(TSEX)["PR"] == 14                                         # painel f8

OM = json.loads((B / "openmeteo_capitais_3d.json").read_text())
POAD = next(x for x in OM if abs(x["latitude"] + 29.98) < .05)["daily"]
assert POAD["time"][2] == "2026-11-14" and round(POAD["temperature_2m_max"][2]) == 30, POAD["temperature_2m_max"]   # f9
TPOA = POAD["temperature_2m_max"][2]

# ---------------------------------------------------------------- mapa: estados pintados e pinos (só nos trechos de mapa)
estados = [
    {"id": "a_rs", "ini": IR0, "fim": IR1, "ufs": ["RS"], "cor": VERM, "alfa": .22},
    {"id": "p_pr", "ini": P0, "fim": P1, "ufs": ["PR"], "cor": VERM, "alfa": .26},
    {"id": "c_pr", "ini": C0, "fim": C1, "ufs": ["PR"], "cor": VERM, "alfa": .32},
    {"id": "c_sc", "ini": C0, "fim": C1, "ufs": ["SC"], "cor": LAR, "alfa": .3},
    {"id": "t_rs", "ini": A0, "fim": A1, "ufs": ["RS"], "cor": LAR, "alfa": .26},
]
pino = lambda nome, sub, lon, lat, a, b, h=120: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    pino("Extremo noroeste", "+100 mm em pouco mais de 1 h", -54.24, -27.77, IR0, IR1, 110),
    pino("Palmeira das Missões", "água dentro de casas", -53.31, -27.90, em("f2", "Palmeira") - .3, IR1, 60),
    pino("Rodeio Bonito", "suspeita de tornado", -53.17, -27.47, em("f2", "Rodeio") - .3, IR1, 150),
    pino("Itapejara do Oeste", "granizo na rodovia", -52.81, -25.96, em("f4", "Itapejara") - .3, P1, 130),
    pino("Pato Branco", "", -52.67, -26.23, em("f4", "Pato") - .3, P1, 50),
    pino("Prudentópolis", "granizo grande e ventania", -50.98, -25.21, em("f4", "Prudentópolis") - .3, P1, 110),
    pino("Paraná", f"{THOJE_UF['PR']} cidades em aviso", -51.6, -24.9, C0, C1, 80),
    pino("Santa Catarina", f"{THOJE_UF['SC']} cidades em aviso", -50.6, -27.3, C0, C1, 80),
    pino("Porto Alegre", f"{TPOA:.1f}".replace(".", ",") + " °C no sábado (previsão)", -51.23, -30.03, A0, A1, 110),
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
    {"ini": CAPA, "fim": ini("f2"), "k": "HOJE · QUINTA 12/11 · NOROESTE DO RS",
     "itens": [{"t": CAPA, "txt": "🌧️ +100 mm em pouco mais de 1 hora"}, {"t": CAPA + .6, "txt": "⚠️ graves alagamentos"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "FIM DA TARDE · RIO GRANDE DO SUL",
     "itens": [{"t": em("f2", "noroeste"), "txt": "📍 extremo noroeste"}, {"t": em("f2", "Palmeira"), "txt": "📍 Palmeira das Missões"},
               {"t": em("f2", "Rodeio"), "txt": "📍 Rodeio Bonito"}], "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "O QUE O TEMPORAL DEIXOU",
     "itens": [{"t": em("f3", "água"), "txt": "🏠 água dentro de casas"}, {"t": em("f3", "enxurrada"), "txt": "🌊 enxurrada nas estradas"},
               {"t": em("f3", "árvores"), "txt": "🌳 árvores caídas"}, {"t": em("f3", "tornado"), "txt": "🌪️ suspeita de tornado"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "HOJE À TARDE · PARANÁ",
     "itens": [{"t": em("f4", "chuva"), "txt": "🌧️ chuva pesada"}, {"t": em("f4", "ventania"), "txt": "💨 ventania"},
               {"t": em("f4", "granizo"), "txt": "🧊 granizo"}], "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "🧊 GRANIZO NO PARANÁ",
     "itens": [{"t": em("f5", "motoristas"), "txt": "🚗 susto na rodovia"}, {"t": em("f5", "grandes"), "txt": "✋ pedras de encher a mão"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "POR QUÊ",
     "itens": [{"t": em("f6", "calor"), "txt": "🌡️ calor"}, {"t": em("f6", "umidade"), "txt": "💧 muita umidade"},
               {"t": em("f6", "tempestade"), "txt": "⛈️ nuvens crescem rápido à tarde"}], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "INMET · TEMPESTADE · ATÉ 23H59 DE HOJE",
     "contador": conta(len(THOJE), "f7", "612", "#FACC15", "CIDADES DO PR E SC"),
     "l": f"PR {THOJE_UF['PR']} · SC {THOJE_UF['SC']} · perigo potencial", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "⚠️ ESTA NOITE E SEXTA (PREVISÃO)",
     "itens": [{"t": em("f8", "50"), "txt": "🌧️ até 50 mm por dia"}, {"t": em("f8", "vento"), "txt": "💨 vento de até 60 km/h"},
               {"t": em("f8", "granizo"), "txt": f"🧊 granizo · sexta: {len(TSEX)} cidades do PR"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "PORTO ALEGRE · SÁBADO (PREVISÃO)",
     "contador": conta(TPOA, "f9", "30", "#ff8c1a", "°C DE MÁXIMA", dec=1, de=20),
     "l": "Open-Meteo · sábado 14/11", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "cidade"), "txt": "📍 DE ONDE VOCÊ É?"}, {"t": em("f10", "tempo"), "txt": "🌦️ COMO ESTÁ AÍ?"}],
     "borda": "rgba(250,204,21,.8)"},
]
for a, b in zip(paineis, paineis[1:]):
    assert a["fim"] <= b["ini"] + 1e-6, (a["k"], b["k"])
for a in paineis:
    if a.get("contador"):
        c = a["contador"]
        assert a["ini"] - .01 <= c["ini"] and c["ini"] + c["dur"] <= a["fim"], ("contador fora do painel", a["k"])

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": IR0, "html": f"<b>{MET}</b>"},
    {"ini": IR0, "fim": ini("f3"), "html": f"satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE} · <b>{MET}</b>"},
    {"ini": ini("f3"), "fim": ini("f7"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f7"), "fim": ini("f9"), "html": "<b>INMET</b>, avisos de tempestade (12 e 13/11)"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": f"<b>Open-Meteo</b>, previsão para Porto Alegre · <b>{MET}</b>"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "agua": "#5ec8ff", "enxurrada": "#5ec8ff", "umidade": "#5ec8ff",
         "calor": "#ff8c1a", "temperatura": "#ff8c1a", "disparar": "#ff8c1a", "graus": "#ff8c1a",
         "tempestade": "#ff2a1f", "pancadas": "#ff2a1f", "granizo": "#ff2a1f", "tornado": "#ff2a1f", "ventania": "#ff8c1a",
         "vento": "#ff8c1a", "aviso": "#ff8c1a", "atencao": "#ff8c1a", "arvores": "#ff8c1a", "comenta": AM,
         "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "rio", "grande", "noroeste", "gaucho", "santa", "catarina", "parana", "palmeira", "missoes", "rodeio",
         "bonito", "pato", "branco", "itapejara", "oeste", "prudentopolis", "porto", "alegre", "inemaclub", "cidade"}
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
      f"cena real {real / DUR:.0%} · mapa {sum(b - a for _, a, b, _ in mapas) / DUR:.0%} · "
      f"cortes {len(cortes)} · menor trecho {min(b - a for a, b in zip(cortes, cortes[1:] + [FIM_VIDEO])):.2f} s")
for nome, a, b, _ in mapas:
    print(f"  mapa {nome}: {a:.2f}–{b:.2f} ({b - a:.2f} s)")
for m in telas:
    print(f"  tela {(m.get('src') or m['seq'][0]).split('/')[1]}: {m['ini']:.2f}–{m['fim']:.2f}")
