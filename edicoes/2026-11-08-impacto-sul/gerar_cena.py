#!/usr/bin/env python3
"""Monta cena.js do "Impacto Sul" de 08/11/2026 (domingo), visual do auto/roteiro-sul.md (3c, Nei 07/11/2026):
  - ONDE = MAPA, O QUÊ = IMAGEM REAL: Rio do Sul/Vale do Itajaí, Lontras/Abdon Batista, oeste e centro-leste de SC (IR),
    Santo Augusto/noroeste gaúcho, Palmeira das Missões, SC e PR, Rio do Sul, o Sul (INMET) e Curitiba
    → mapa PARADO nele, pino com o nome, estado pintado, >= 3 s desde a palavra do lugar;
  - O QUÊ: enchente em Rio do Sul e no Vale do Itajaí, tornado em Santo Augusto, cooperativa destruída em Palmeira
    das Missões (micro clipes limpos dos vídeos do dia); o frio (ilustração com selo);
  - DURAÇÃO: nenhuma cena < 2,5 s; mapa >= 3 s.
Fontes: fonte do dia (Meteorologia · 08/11/2026), CEMADEN (acumulado 72 h), GOES-19 IR (NASA GIBS), INMET (aviso de
declínio de temperatura 08/11), Open-Meteo (Curitiba).
Com avatar: gerar_cena.py --canto (avatar/tempos.json); depois GEO=geo-br.js LAYOUT=canto motor-sul/compor_avatar.sh <esta pasta>
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, math, re, subprocess, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "08/11/2026"
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


# ---------------------------------------------------------------- micro clipes reais (cenas/clip-NN, 30 fps, limpos do outro perfil)
def nq(nome):
    return len(os.listdir(AQUI / "cenas" / nome))


def clipe(nome, a, b, zoom=.03):
    q = sorted(os.listdir(AQUI / "cenas" / nome))
    assert q and (min(b, FIM_VIDEO) - a) <= len(q) / 30 + .15, (nome, round(b - a, 2), len(q) / 30)
    return {"seq": [f"cenas/{nome}/{x}" for x in q], "fps": 30, "ini": a, "fim": b, "fade": .2, "zoom": zoom}


def foto(src, a, b, selo=None, zoom=.06):
    return {"src": src, "ini": a, "fim": b, "fade": .25, "zoom": zoom, **({"selo": selo} if selo else {})}


def encher(a, b, itens):
    """divide [a, b] em k cenas (cada >= 2,5 s, nenhum clipe além do que tem); itens: nomes de clipe ou ('foto', src)"""
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


# ---------------------------------------------------------------- linha do tempo (cada corte na palavra que ele mostra)
CAPA = 2.5                                                        # quadro 0: bairro alagado + gancho + data (sem fade)
A0 = max(em("f2", "Rio"), CAPA + MIN_CENA)                         # mapa A: Rio do Sul, Vale do Itajaí
A1 = max(A0 + MIN_MAPA, em("f2", "Itajaí") + MIN_CENA)            # → ruas, comércios e casas alagados
B0 = em("f3", "Lontras") - .15                                     # mapa B: Lontras (110 mm), vizinha de Rio do Sul
if B0 - A1 < MIN_CENA:                                             #   sem espaço para as casas alagadas: o mapa A segue
    A1 = B0
B1 = max(B0 + MIN_MAPA, em("f3", "Rio") + MIN_CENA, em("f3", "110") + .6)
B2 = em("f3", "Abdon")                                             # mapa B2: Abdon Batista (passou de 200 mm)
if B2 - B1 < MIN_CENA:                                             #   sem espaço para a cena da chuva: o mapa segue
    B1 = B2
IR0 = max(B2 + MIN_MAPA, em("f3", "200") + 1.0)                    # satélite IR: tempestades no oeste, chuva do centro ao leste de SC
C0 = em("f5", "Santo")                                             # mapa C: Santo Augusto, noroeste gaúcho
C1 = max(C0 + MIN_MAPA, em("f5", "noroeste") + MIN_CENA)           # → tornado (micro clipe + quadro)
D0 = em("f6", "Palmeira")                                          # mapa D: Palmeira das Missões
D1 = max(D0 + MIN_MAPA, em("f6", "Missões") + MIN_CENA)            # → cooperativa destruída
E0 = ini("f7")                                                     # rio cheio no Vale do Itajaí ("atenção ... menos chuva")
G0 = em("f7", "Santa")                                             # mapa G: Santa Catarina e Paraná (instabilidade)
G1 = max(G0 + MIN_MAPA, em("f7", "Paraná") + MIN_CENA)
H0 = em("f7", "Rio")                                               # mapa H: Rio do Sul (os problemas se agravam)
if H0 - G1 < MIN_CENA:                                             #   sem espaço para a enchente no meio: um mapa só
    G1 = H0
H1 = max(H0 + MIN_MAPA, H0 + MIN_CENA)
I0 = em("f8", "Sul")                                               # mapa I: o Sul (1.191 cidades) e Curitiba
I1 = max(I0 + MIN_MAPA, em("f9", "Curitiba") + MIN_CENA)
J0 = ini("f10")                                                    # engajamento: enchente
K0 = ini("f11")                                                    # CTA
if K0 - J0 < 2 * MIN_CENA:                                         #   só cabe 1 clipe: o clip-04 tem 2,9 s, a foto do frio cobre o resto
    J0 = max(J0, K0 - nq("clip-04") / 30)

# ---------------------------------------------------------------- câmera: só aparece nos trechos de mapa/satélite
K = lambda t, r, pitch=0, bearing=0: {"t": round(t, 3), **r, "pitch": pitch, "bearing": bearing}
RSUL = {"lon": -49.75, "lat": -27.3, "zoom": 7.6}       # Rio do Sul, Vale do Itajaí
VALE = {"lon": -50.35, "lat": -27.45, "zoom": 7.0}      # Lontras + Abdon Batista
SCIR = {"lon": -50.9, "lat": -27.2, "zoom": 6.2}        # Santa Catarina inteira (IR)
NOROESTE = {"lon": -53.55, "lat": -27.9, "zoom": 7.6}   # Santo Augusto e Palmeira das Missões
SCPR = {"lon": -50.6, "lat": -26.3, "zoom": 6.0}        # SC e PR (e Rio do Sul)
SUL = {"lon": -51.4, "lat": -27.6, "zoom": 5.75}
VIAGEM = .7                                             # a câmera chega antes do mapa aparecer e fica parada
trechos = [(A0, A1, RSUL), (B0, IR0, VALE), (IR0, C0, SCIR), (C0, C1, NOROESTE), (D0, D1, NOROESTE), (G0, H1, SCPR), (I0, I1, SUL)]
camera = [K(0, RSUL)]
for a, b, r in trechos:
    camera += [K(a - VIAGEM, r) if camera[-1]["lon"] != r["lon"] else K(a, r), K(b, r)]
camera.append(K(DUR, SUL))
camera = [c for i, c in enumerate(camera) if i == 0 or c["t"] > camera[i - 1]["t"]]
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: GOES-19 infravermelho do domingo 08/11 (f4)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 130 and "2026-11-08T03:00:00Z" <= TS[i] < "2026-11-09T03:00:00Z"]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


IR1 = C0
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": IR0, "fim": IR1, "dur": IR1 - IR0, "alfa": .9, "rotulo": "satélite · infravermelho"}}
IR_DE, IR_ATE = brt(TS[BONS[0]]), brt(TS[BONS[-1]])
assert len(BONS) >= 20, f"poucos quadros bons de infravermelho: {len(BONS)}"

# ---------------------------------------------------------------- telas (cenas reais e ilustração do frio)
telas = [foto("capa-dia/abertura.png", 0, CAPA, zoom=.05)]                       # bairro alagado + gancho + data
telas += encher(CAPA, A0, ["clip-01", "clip-08"])                                # "Rio do Sul começa a alagar": bairro e rio cheios
# mapa A (Rio do Sul, Vale do Itajaí)
if B0 > A1:
    telas += encher(A1, B0, ["clip-03", "clip-02"])                                  # "ruas, comércios e casas", "moradores retirados"
# mapa B (Lontras, 110 mm)
if B2 > B1:
    telas += encher(B1, B2, ["clip-10"])                                         # "a chuva somou ... em três dias": rua alagada sob chuva
# mapa B2 (Abdon Batista) → satélite IR (oeste e centro-leste de SC) → mapa C (Santo Augusto)
telas += encher(C1, D0, ["clip-05", ("foto", "cenas/real-01.jpg")])              # "tornado", "o funil": o tornado com raios
# mapa D (Palmeira das Missões)
telas += encher(D1, E0, ["clip-06", "clip-07"])                                  # "estrutura de uma cooperativa", "ferro retorcido"
telas += encher(E0, G0, ["clip-08"])                                             # "atenção ... menos chuva": rio cheio no Vale do Itajaí
# mapa G (Santa Catarina e Paraná)
if H0 > G1:
    telas += encher(G1, H0, ["clip-09"])                                         # "os problemas se agravam": bairro alagado
# mapa H (Rio do Sul)
telas += [foto("cenas/real-02.jpg", H1, I0, "ilustração")]                       # "o frio chega": gente agasalhada na chuva
# mapa I (o Sul, Curitiba)
telas += [foto("capa-dia/frio.png", I1, J0, "ilustração")]                       # "mínima pode cair a 10 graus"
telas += encher(J0, K0, ["clip-04", "clip-02"])                                  # pergunta: casas alagadas
telas += encher(K0, DUR, ["clip-01", "clip-10"])                                 # CTA (o vídeo acaba com o avatar)
assert telas[0]["ini"] == 0   # vis() não faz fade-in quando ini <= 0 (quadro 0 cheio)

# ---------------------------------------------------------------- portões das 3 regras (3c)
mapas = [("A Rio do Sul", A0, A1, em("f2", "Rio")), ("B Lontras/Abdon Batista", B0, B1, em("f3", "Lontras"))]
if B2 > B1:
    mapas += [("B2 Abdon Batista", B2, IR0, em("f3", "Abdon"))]
else:
    mapas[-1] = ("B Lontras/Abdon Batista", B0, IR0, em("f3", "Lontras"))
mapas += [("IR Santa Catarina", IR0, C0, em("f4", "oeste")), ("C Santo Augusto", C0, C1, em("f5", "Santo")),
          ("D Palmeira das Missões", D0, D1, em("f6", "Palmeira"))]
if H0 > G1:
    mapas += [("G SC e PR", G0, G1, em("f7", "Santa")), ("H Rio do Sul", H0, H1, em("f7", "Rio"))]
else:
    mapas += [("G SC, PR e Rio do Sul", G0, H1, em("f7", "Santa"))]
mapas += [("I Sul/Curitiba", I0, I1, em("f8", "Sul"))]
for m in telas:
    assert min(m["fim"], FIM_VIDEO) - m["ini"] >= MIN_CENA - .01, ("cena curta", m.get("src") or m["seq"][0], round(min(m["fim"], FIM_VIDEO) - m["ini"], 2))
for nome, a, b, palavra in mapas:
    assert b - a >= MIN_MAPA - .01, ("mapa curto", nome, round(b - a, 2))
    assert a <= palavra + .25, ("mapa entra depois da palavra do lugar", nome, round(a - palavra, 2))
# lugares ditos (f1 "Rio do Sul"/"impacto no Sul" ficam na capa e no bairro alagado: é o gancho escrito;
# f10 "cidade do Sul" é a pergunta ao público, não um lugar do fato)
fim_mapa = lambda t: max(b for _, a, b, _ in mapas if a - .01 <= t + .25 and t < b)
LUGARES = [("f2", "Rio"), ("f2", "Itajaí"), ("f3", "Lontras"), ("f3", "Rio"), ("f3", "Abdon"), ("f4", "oeste"),
           ("f4", "centro"), ("f4", "Santa"), ("f5", "Santo"), ("f5", "noroeste"), ("f6", "Palmeira"), ("f7", "Santa"),
           ("f7", "Paraná"), ("f7", "Rio"), ("f8", "Sul"), ("f9", "Curitiba")]
for fid, w in LUGARES:
    assert any(a - .01 <= em(fid, w) + .25 and em(fid, w) < b for _, a, b, _ in mapas), ("lugar fora de mapa", fid, w)
    # o mapa segue >= 2,5 s; o satélite (f4) emenda no mapa de Santo Augusto
    ate = fim_mapa(em(fid, w))
    if fid == "f4":
        ate = C1
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
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
SULC = {"41": "PR", "42": "SC", "43": "RS"}
geo = lambda i: {c for c in aviso[i]["geocodes"].split(",") if c[:2] in SULC}
assert aviso[56281]["descricao"] == "Declínio de Temperatura" and aviso[56281]["inicio"].startswith("2026-11-08")
FRIO8 = geo(56281)
assert len(FRIO8) == 1191, len(FRIO8)                     # f8: "1.191 cidades do Sul"
from collections import Counter
F_UF = Counter(SULC[c[:2]] for c in FRIO8)
assert (F_UF["PR"], F_UF["SC"], F_UF["RS"]) == (399, 295, 497), F_UF

CEM = json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())
num = lambda v: float(v) if v not in ("-", None, "") else 0.0
acc72 = lambda cid: max(num(x["acc72hr"]) for x in CEM if x["uf"] == "SC" and x["cidade"] == cid)
LON, ABD = acc72("LONTRAS"), acc72("ABDON BATISTA")
assert round(LON) == 110, LON                              # f3: 110 mm em 3 dias em Lontras
assert ABD > 200, ABD                                      # f3: passou de 200 mm em Abdon Batista

OM = json.loads((B / "openmeteo_capitais_3d.json").read_text())
CWB = next(x for x in OM if abs(x["latitude"] + 25.41) < .05)["daily"]
assert CWB["time"][0] == "2026-11-08" and round(CWB["temperature_2m_max"][0]) == 17, CWB["temperature_2m_max"]
assert round(CWB["temperature_2m_min"][1]) == 10, CWB["temperature_2m_min"]   # f9: mínima de 10 graus na segunda 09/11

# ---------------------------------------------------------------- mapa: estados pintados e pinos (só nos trechos de mapa)
G_FIM = G1 if H0 > G1 else H1
estados = [
    {"id": "a_sc", "ini": A0, "fim": A1, "ufs": ["SC"], "cor": AZUL, "alfa": .3},
    {"id": "b_sc", "ini": B0, "fim": IR0, "ufs": ["SC"], "cor": AZUL, "alfa": .3},
    {"id": "c_rs", "ini": C0, "fim": D1, "ufs": ["RS"], "cor": VERM, "alfa": .3},
    {"id": "g_sc", "ini": G0, "fim": G_FIM, "ufs": ["SC"], "cor": AZUL, "alfa": .3},
    {"id": "g_pr", "ini": em("f7", "Paraná"), "fim": G_FIM, "ufs": ["PR"], "cor": AZUL, "alfa": .3},
    {"id": "i_frio", "ini": I0, "fim": I1, "ufs": ["RS", "SC", "PR"], "cor": FRIO, "alfa": .4},
]
pino = lambda nome, sub, lon, lat, a, b, h=120: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    pino("Rio do Sul", "Vale do Itajaí · alagamentos", -49.64, -27.21, A0, A1),
    pino("Lontras", f"{round(LON)} mm em 72 h", -49.54, -27.17, B0, IR0, 90),
    pino("Abdon Batista", f"{round(ABD)} mm em 72 h", -51.02, -27.61, B2, IR0, 90),
    pino("Santo Augusto", "noroeste gaúcho · tornado", -53.78, -27.85, C0, C1),
    pino("Palmeira das Missões", "cooperativa destruída", -53.31, -27.90, D0, D1),
    pino("Santa Catarina", "instabilidade (previsão)", -50.4, -27.3, G0, G_FIM, 60),
    pino("Paraná", "instabilidade (previsão)", -51.6, -24.9, em("f7", "Paraná"), G_FIM, 60),
    pino("Rio do Sul", "problemas se agravam", -49.64, -27.21, H0, H1, 140),
    pino("Sul", f"{len(FRIO8):,} cidades em aviso".replace(",", "."), -52.2, -28.8, I0, I1, 60),
    pino("Curitiba", f"máx. {round(CWB['temperature_2m_max'][0])} °C hoje (previsão)", -49.27, -25.43, em("f9", "Curitiba"), I1, 100),
]
for p in pinos:   # pino que nasce até 0,3 s antes do mapa entra junto com o mapa
    for _, a, b, _ in mapas:
        if a - .3 <= p["ini"] < a and p["fim"] <= b + .01:
            p["ini"] = a
    assert any(a - .01 <= p["ini"] and p["fim"] <= b + .01 for _, a, b, _ in mapas) or \
        (p["ini"] >= B0 - .01 and p["fim"] <= IR0 + .01) or (p["ini"] >= G0 - .01 and p["fim"] <= H1 + .01), \
        ("pino fora de trecho de mapa", p["nome"])

# ---------------------------------------------------------------- textos
LEAD = 1.0
def conta(ate, fid, palavra, cor, unid, dec=0, lead=LEAD, de=0, k=1):
    lead = min(lead, em(fid, palavra, k) - ini(fid) - .05)
    return {"de": de, "ate": ate, "dec": dec, "ini": em(fid, palavra, k) - lead, "dur": lead, "cor": cor, "unid": unid}


hero = []   # a manchete e a data estão escritas na capa (quadro 0)
paineis = [
    {"ini": CAPA, "fim": ini("f2"), "k": "DOMINGO 08/11 · SUL",
     "itens": [{"t": CAPA, "txt": "🌊 Rio do Sul (SC) começa a alagar"}], "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "RIO DO SUL (SC) · HOJE",
     "itens": [{"t": em("f2", "ruas"), "txt": "🌊 água nas ruas"}, {"t": em("f2", "casas"), "txt": "🏠 comércios e casas"},
               {"t": em("f2", "Moradores"), "txt": "🚨 moradores retirados"}], "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f3"), "fim": B2, "k": "LONTRAS (SC) · 3 DIAS",
     "contador": conta(round(LON), "f3", "110", "#5ec8ff", "MM DE CHUVA"),
     "l": "CEMADEN · acumulado de 72 h", "borda": "rgba(60,150,255,.8)"},
    {"ini": B2, "fim": ini("f4"), "k": "ABDON BATISTA (SC) · 3 DIAS",
     "contador": conta(round(ABD), "f3", "200", "#5ec8ff", "MM DE CHUVA"),
     "l": "CEMADEN · acumulado de 72 h", "borda": "rgba(60,150,255,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "A SEMANA EM SC",
     "itens": [{"t": em("f4", "tempestades"), "txt": "⛈️ tempestades no oeste"},
               {"t": em("f4", "chuva"), "txt": "🌧️ chuva do centro ao leste"}], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "SANTO AUGUSTO (RS) · SÁBADO 07/11",
     "itens": [{"t": em("f5", "tornado"), "txt": "🌪️ tornado atinge a cidade"},
               {"t": em("f5", "funil"), "txt": "📹 funil filmado de manhã cedo"}], "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "PALMEIRA DAS MISSÕES (RS) · SÁBADO",
     "itens": [{"t": em("f6", "ventos"), "txt": "💨 ventos fortes"}, {"t": em("f6", "cooperativa"), "txt": "🏚️ cooperativa destruída"},
               {"t": em("f6", "ferro"), "txt": "🔩 telhado retorcido"}], "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "⚠️ PRÓXIMOS DIAS (PREVISÃO)",
     "itens": [{"t": em("f7", "menos"), "txt": "🌦️ menos chuva na semana"}, {"t": em("f7", "Santa"), "txt": "⛈️ SC e PR instáveis"},
               {"t": em("f7", "agravam"), "txt": "🌊 Rio do Sul: problemas se agravam"}], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "INMET · QUEDA DE TEMPERATURA · 08/11",
     "contador": conta(len(FRIO8), "f8", "1.191", "#96d2ff", "CIDADES DO SUL"),
     "l": f"PR {F_UF['PR']} · RS {F_UF['RS']} · SC {F_UF['SC']}", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "CURITIBA (PREVISÃO)",
     "contador": conta(round(CWB["temperature_2m_min"][1]), "f9", "10", "#96d2ff", "°C DE MÍNIMA NA SEGUNDA"),
     "l": f"máxima de {round(CWB['temperature_2m_max'][0])} °C hoje · Open-Meteo", "borda": "rgba(150,210,255,.8)"},
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
    {"ini": CAPA, "fim": ini("f3"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f3"), "fim": IR0, "html": "<b>CEMADEN</b>, chuva acumulada em 72 h até 08/11"},
    {"ini": IR0, "fim": ini("f5"), "html": f"satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE}"},
    {"ini": ini("f5"), "fim": ini("f7"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": f"<b>{MET}</b> · previsão"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>INMET</b>, aviso de declínio de temperatura de 08/11 · frio: ilustração"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": "<b>Open-Meteo</b>, previsão para Curitiba · ilustração"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "alagar": "#5ec8ff", "agua": "#5ec8ff", "frio": "#96d2ff",
         "temperatura": "#96d2ff", "graus": "#96d2ff", "minima": "#96d2ff", "tornado": "#ff2a1f", "funil": "#ff2a1f",
         "destruiram": "#ff2a1f", "retorcido": "#ff2a1f", "ventos": "#ff8c1a", "tempestades": "#ff8c1a", "aviso": "#ff8c1a",
         "atencao": "#ff8c1a", "instabilidade": "#ff8c1a", "agravam": "#ff2a1f", "retirados": "#ff2a1f", "invadiu": "#ff2a1f",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "rio", "vale", "itajai", "lontras", "abdon", "batista", "santo", "augusto", "palmeira", "missoes",
         "gaucho", "santa", "catarina", "parana", "curitiba", "inemaclub", "cidade", "noroeste"}
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
     "marca": "INEMA · IMPACTO SUL", "selo": DATA[:5] + " · INMET · CEMADEN · Open-Meteo",
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
