#!/usr/bin/env python3
"""Monta cena.js do "Impacto Sul" de 14/11/2026 (sábado), visual do auto/roteiro-sul.md (3c, Nei 07/11/2026):
  - gancho (INMET 56408): tempestade com granizo pode atingir 684 cidades do Sul no domingo 15/11 (PR 399, SC 270, RS 15);
  - fonte do dia: granizo em Rio do Sul (SC) neste sábado; vendaval com estragos no Paraguai; tempestades avançam sobre o oeste do PR,
    SC e metade norte do RS; calor de até 35 graus; chuva quase todo dia à tarde (El Niño);
  - INMET 56405: tempestade esta noite em 330 cidades do Sul (PR 149, RS 94, SC 87), vento 40-60 km/h e granizo;
  - ONDE = MAPA: Rio do Sul/SC (3 s), satélite IR sobre o Sul (oeste do PR), domingo PR+SC pintados (3 s);
  - O QUÊ: micro clipes reais do dia, limpos (sem data/selo nem legenda do outro perfil) + 2 ilustrações (Codex).
Fontes: fonte do dia (Meteorologia · 14/11/2026), INMET (avisos 56405, 56408), GOES-19 IR (NASA GIBS).
Com avatar: gerar_cena.py --canto (avatar/tempos.json); depois GEO=geo-br.js LAYOUT=canto motor-sul/compor_avatar.sh <esta pasta>
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, math, re, subprocess, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "14/11/2026"
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
# fonte do dia: 1 vídeo (v1, 576x1024). Data/selo do outro perfil em x 80-220, y 280-365; legenda queimada em y 680-725;
# quadros com tarja preta (29,4-33,3 s e 42,8-52,5 s) só têm imagem em y 135-890. Recortes: "alto" 340x660+236+0 (CHEIO),
# "tarja" 340x530+236+135 (CHEIO) e "faixa" 576x295+0+375.
# clip-01..03 granizo na mão, chão coberto de gelo (faixa, 33,5-42,7 s)   clip-04 telhado arrancado, Paraguai (alto)
# clip-05 telhado arrancado (faixa)        clip-06 frente de tempestade escura (alto)     clip-07 chuva forte nas árvores (tarja)
# clip-08/09 cortina de chuva da tempestade (tarja)   clip-10 cortina de chuva sobre a lavoura (faixa)
# clip-11 céu escuro (alto)   clip-12 céu carregado (alto)   clip-13 barranco sob chuva (alto)   clip-14 chuva nas árvores (faixa)
# cenas/ilu-*.jpg: ilustrações do Codex (selo "ilustração"): tempestade no oeste do PR e calor com nuvem de tempestade
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


TEMPESTADE = ("foto", "cenas/ilu-tempestade.jpg", "ilustração") if (AQUI / "cenas/ilu-tempestade.jpg").exists() else "clip-09"
CALOR = ("foto", "cenas/ilu-calor.jpg", "ilustração") if (AQUI / "cenas/ilu-calor.jpg").exists() else "clip-10"

# ---------------------------------------------------------------- linha do tempo (cada corte na palavra que ele mostra)
CAPA = 2.5                                                         # quadro 0: granizo real + gancho + data
R0 = em("f2", "Rio") - .15                                         # mapa A: Rio do Sul (SC), granizo
R1 = R0 + MIN_MAPA if ini("f3") - (R0 + MIN_MAPA) >= MIN_CENA else ini("f3")   # sem sobra de 2,5 s até a f3 (fala do avatar mais rápida): o mapa vai até a f3
IR0 = em("f4", "oeste") - .5                                      # satélite IR: tempestades avançam sobre oeste do PR, SC, norte do RS
IR1 = ini("f5") if ini("f5") - IR0 <= 6.0 else IR0 + 4.5           # até o fim da f4 (no máximo 6 s de satélite)
C0 = ini("f7")                                                     # mapa C: domingo, PR 399 e SC 270
C1 = max(C0 + MIN_MAPA, em("f7", "399") + 1.2)
K0 = ini("f10")                                                    # CTA

# ---------------------------------------------------------------- câmera: só aparece nos trechos de mapa/satélite
K = lambda t, r, pitch=0, bearing=0: {"t": round(t, 3), **r, "pitch": pitch, "bearing": bearing}
SC = {"lon": -50.0, "lat": -27.3, "zoom": 6.6}          # Rio do Sul, vale do Itajaí
SUL = {"lon": -51.6, "lat": -27.0, "zoom": 5.5}         # RS + SC + PR
VIAGEM = .7                                             # a câmera chega antes do mapa aparecer e fica parada
trechos = [(R0, R1, SC), (IR0, IR1, SUL), (C0, C1, SUL)]
camera = [K(0, SC)]
for a, b, r in trechos:
    camera += [K(a - VIAGEM, r) if camera[-1]["lon"] != r["lon"] else K(a, r), K(b, r)]
camera.append(K(DUR, SUL))
camera = [c for i, c in enumerate(camera) if i == 0 or c["t"] > camera[i - 1]["t"]]
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: GOES-19 infravermelho das últimas 24 h (f4)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 130 and "2026-11-14T00:00:00Z" <= TS[i] <= "2026-11-15T00:00:00Z"]
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

# ---------------------------------------------------------------- telas (clipes reais do dia + ilustrações)
telas = [foto("capa-dia/abertura.png", 0, CAPA, zoom=.05)]                       # granizo real + gancho + data
telas += encher(CAPA, R0, ["clip-06", "clip-08", "clip-01"])                     # "tempestade com granizo... domingo... granizo já caiu"
# mapa A (Rio do Sul, SC) 3 s
if ini("f3") - R1 > .05:
    telas += encher(R1, ini("f3"), ["clip-02", "clip-03", "clip-01"])                # "pedras de gelo cobriram o chão"
telas += encher(ini("f3"), IR0, ["clip-04", "clip-05", "clip-07"])               # "Paraguai... arrancaram telhados... estragos... avançam"
# satélite IR (Sul) 4-5,5 s
if ini("f5") - IR1 > .05:
    telas += encher(IR1, ini("f5"), ["clip-07", "clip-12", "clip-14"])           # "metade norte do Rio Grande do Sul"
telas += encher(ini("f5"), ini("f6"), [CALOR, "clip-10", "clip-09"])             # "calor... 35 graus"
telas += encher(ini("f6"), C0, ["clip-14", "clip-06", TEMPESTADE, "clip-08"])    # "esta noite... 330 cidades... vento"
# mapa C (domingo, PR e SC) 3 s
telas += encher(C1, ini("f8"), ["clip-09", TEMPESTADE])                          # "270 em Santa Catarina"
telas += encher(ini("f8"), ini("f9"), ["clip-08", "clip-14", "clip-09", "clip-13", "clip-07", "clip-12"])  # previsão
telas += encher(ini("f9"), K0, ["clip-12", "clip-01", "clip-07"])                # pergunta (clip-12 cobre o trecho de 4,4 s da fala do avatar)
telas += encher(K0, DUR, ["clip-02", "clip-04"])                                 # CTA (o vídeo acaba com o avatar)
assert telas[0]["ini"] == 0   # vis() não faz fade-in quando ini <= 0 (quadro 0 cheio)

# ---------------------------------------------------------------- portões das 3 regras (3c)
mapas = [("A Rio do Sul", R0, R1, em("f2", "Rio")), ("IR Sul", IR0, IR1, em("f4", "oeste")),
         ("C domingo PR/SC", C0, C1, em("f7", "domingo"))]
for m in telas:
    assert min(m["fim"], FIM_VIDEO) - m["ini"] >= MIN_CENA - .01, ("cena curta", m.get("src") or m["seq"][0], round(min(m["fim"], FIM_VIDEO) - m["ini"], 2))
for nome, a, b, palavra in mapas:
    assert b - a >= MIN_MAPA - .01, ("mapa curto", nome, round(b - a, 2))
    assert b - a <= 6.0, ("mapa longo", nome, round(b - a, 2))
    assert a <= palavra + .25, ("mapa entra depois da palavra do lugar", nome, round(a - palavra, 2))
# lugares ditos (f1 "Sul" fica na capa: é o gancho escrito; Paraguai não é do Sul; f9 "cidade do Sul" não é lugar do fato)
fim_mapa = lambda t: max(b for _, a, b, _ in mapas if a - .01 <= t + .25 and t < b)
LUGARES = [("f2", "Rio"), ("f4", "oeste")]   # Nei 13/11: mapa só na 1ª vez de cada estado; o resto vai no painel por cima da cena real
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
assert aviso[56405]["descricao"] == "Tempestade" and aviso[56405]["inicio"].startswith("2026-11-14 20")
TNOI = geo(56405); TNOI_UF = uf(TNOI)
assert len(TNOI) == 330 and (TNOI_UF["PR"], TNOI_UF["RS"], TNOI_UF["SC"]) == (149, 94, 87), TNOI_UF        # f6
R5 = aviso[56405]["riscos"][0]
assert "40-60 km/h" in R5 and "granizo" in R5                                                              # f6 vento 60
assert aviso[56408]["descricao"] == "Tempestade" and aviso[56408]["inicio"].startswith("2026-11-15")
TDOM = geo(56408); TDOM_UF = uf(TDOM)
assert len(TDOM) == 684 and (TDOM_UF["PR"], TDOM_UF["SC"], TDOM_UF["RS"]) == (399, 270, 15), TDOM_UF      # f1, f7
assert "granizo" in aviso[56408]["riscos"][0]

# ---------------------------------------------------------------- mapa: estados pintados e pinos (só nos trechos de mapa)
estados = [
    {"id": "a_sc", "ini": R0, "fim": R1, "ufs": ["SC"], "cor": VERM, "alfa": .22},
    {"id": "i_pr", "ini": IR0, "fim": IR1, "ufs": ["PR"], "cor": VERM, "alfa": .14},
    {"id": "c_pr", "ini": C0, "fim": C1, "ufs": ["PR"], "cor": VERM, "alfa": .32},
    {"id": "c_sc", "ini": C0, "fim": C1, "ufs": ["SC"], "cor": LAR, "alfa": .3},
]
pino = lambda nome, sub, lon, lat, a, b, h=120: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    pino("Rio do Sul", "granizo neste sábado", -49.64, -27.21, R0, R1, 110),
    pino("Oeste do Paraná", "tempestades avançam", -53.4, -24.9, IR0 + .3, IR1, 80),
    pino("Norte do RS", "tempestades isoladas", -53.0, -28.4, IR0 + .3, IR1, 80),
    pino("Paraná", f"{TDOM_UF['PR']} cidades em aviso", -51.6, -24.8, C0, C1, 80),
    pino("Santa Catarina", f"{TDOM_UF['SC']} cidades", -50.6, -27.3, C0, C1, 80),
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
    {"ini": CAPA, "fim": ini("f2"), "k": "INMET · DOMINGO 15/11 (PREVISÃO)",
     "itens": [{"t": CAPA, "txt": "⛈️ tempestade com granizo"}, {"t": CAPA + .6, "txt": f"📍 {len(TDOM)} cidades do Sul"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "SÁBADO 14/11 · RIO DO SUL (SC)",
     "itens": [{"t": em("f2", "granizo"), "txt": "🧊 granizo já caiu"}, {"t": em("f2", "cobriram"), "txt": "⚪ chão coberto de gelo"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "PARAGUAI · VIZINHO DO OESTE DO PR",
     "itens": [{"t": em("f3", "vento"), "txt": "💨 tempestades de vento"}, {"t": em("f3", "telhados"), "txt": "🏚️ telhados arrancados"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "⛈️ AS TEMPESTADES AVANÇAM",
     "itens": [{"t": em("f4", "oeste"), "txt": "📍 oeste do Paraná"}, {"t": em("f4", "Catarina"), "txt": "📍 Santa Catarina"},
               {"t": em("f4", "metade"), "txt": "📍 metade norte do RS"}], "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "🌡️ O CALOR DISPAROU · SÁBADO 14/11",
     "contador": conta(35, "f5", "35", "#ff8c1a", "°C", de=20),
     "l": "em pontos do Sul · o calor alimenta as tempestades", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "INMET · TEMPESTADE · ESTA NOITE",
     "contador": conta(len(TNOI), "f6", "330", "#FACC15", "CIDADES DO SUL"),
     "l": f"PR {TNOI_UF['PR']} · RS {TNOI_UF['RS']} · SC {TNOI_UF['SC']} · vento até 60 km/h e granizo", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "INMET · DOMINGO 15/11 (PREVISÃO)",
     "itens": [{"t": em("f7", "399"), "txt": f"🔴 Paraná: {TDOM_UF['PR']} cidades"}, {"t": em("f7", "270"), "txt": f"🟠 Santa Catarina: {TDOM_UF['SC']} cidades"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "⚠️ PRÓXIMOS DIAS (PREVISÃO)",
     "itens": [{"t": em("f8", "chuva"), "txt": "🌧️ chuva quase todo dia"}, {"t": em("f8", "tarde"), "txt": "🕐 do fim da manhã à tarde"},
               {"t": em("f8", "Niño"), "txt": "🌊 El Niño sobre o Sul"}], "borda": "rgba(255,42,31,.8)"},
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
    {"ini": CAPA, "fim": ini("f2"), "html": "<b>INMET</b>, aviso de tempestade (15/11)"},
    {"ini": ini("f2"), "fim": IR0, "html": f"<b>{MET}</b>"},
    {"ini": IR0, "fim": ini("f5"), "html": f"satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE} · <b>{MET}</b>"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f6"), "fim": ini("f8"), "html": "<b>INMET</b>, avisos de tempestade (14 e 15/11)"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": f"<b>{MET}</b> · previsão"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "gelo": "#5ec8ff", "nino": "#5ec8ff",
         "calor": "#ff8c1a", "dispararam": "#ff8c1a", "graus": "#ff8c1a", "combustivel": "#ff8c1a", "arrancaram": "#ff2a1f",
         "tempestade": "#ff2a1f", "tempestades": "#ff2a1f", "granizo": "#ff2a1f", "estragos": "#ff2a1f", "telhados": "#ff2a1f",
         "vento": "#ff8c1a", "aviso": "#ff8c1a", "dispara": "#ff8c1a", "atencao": "#ff8c1a", "atento": "#ff8c1a", "comenta": AM,
         "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "rio", "grande", "oeste", "norte", "santa", "catarina", "parana", "paraguai", "inemaclub", "cidade"}
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
     "marca": "INEMA · IMPACTO SUL", "selo": DATA[:5] + " · INMET · NOAA",
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
