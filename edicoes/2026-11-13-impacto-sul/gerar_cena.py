#!/usr/bin/env python3
"""Monta cena.js do "Impacto Sul" de 13/11/2026 (sexta), visual do auto/roteiro-sul.md (3c, Nei 07/11/2026):
  - gancho (fonte do dia): mais de 130 mm em pouco mais de 1 hora destruíram estradas e pontilhões no noroeste gaúcho;
  - RS: Tenente Portela e região (extremo noroeste); nesta sexta, levantamento dos estragos (estradas e pontilhões);
  - PR: queda de granizo em áreas do estado;
  - NOAA (METAR): Foz do Iguaçu 36 °C nesta sexta (o calor dispara, fonte do dia);
  - INMET: aviso de tempestade no sábado 14/11 em 949 cidades do Sul (RS 497, SC 295, PR 157) e domingo 15/11 em 1.017;
  - ONDE = MAPA: noroeste do RS (satélite IR), Paraná, Sul inteiro (949) → mapa PARADO 3 s, pino, estado pintado;
  - O QUÊ: micro clipes reais do dia, limpos (sem data, sirene, legenda ou rosto do outro perfil) + 2 ilustrações (Codex);
  - DURAÇÃO: nenhuma cena < 2,5 s; mapa >= 3 s.
Fontes: fonte do dia (Meteorologia · 13/11/2026), INMET (avisos 56398, 56399), GOES-19 IR (NASA GIBS), NOAA METAR (SBFI).
Com avatar: gerar_cena.py --canto (avatar/tempos.json); depois GEO=geo-br.js LAYOUT=canto motor-sul/compor_avatar.sh <esta pasta>
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, math, re, subprocess, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "13/11/2026"
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
# fonte do dia: 1 vídeo (v1, 576x1024). Data/sirene do outro perfil em x 48-160, y 320-387; legenda queimada em y 733-776;
# rosto dele no topo (y < 350) só de 0 a 4,4 s. Recortes: "alto" 400x712+176+0 (CHEIO) e "faixa" 576x320+0+400.
# clip-01 enxurrada despencando com névoa (faixa, 0,2 s)       clip-02 estrada de terra arrancada, sob chuva (alto, 4,6 s)
# clip-03 estrada de terra arrancada (faixa, 5 s)              clip-05..08 rio cheio de enxurrada vermelha (alto, 13,6–25,4 s)
# clip-09/10 torrente estourando em névoa no pontilhão (alto)  clip-11/12 torrente sobre o pontilhão (faixa, 31,6–37,2 s)
# clip-14 torrente (faixa, 26,5 s)
# ilu-granizo / ilu-tempestade: ilustrações do Codex (selo "ilustração"): granizo no PR e tempestade do sábado no RS
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


GRANIZO = ("foto", "cenas/ilu-granizo.jpg", "ilustração")
TEMPESTADE = ("foto", "cenas/ilu-tempestade.jpg", "ilustração")

# ---------------------------------------------------------------- linha do tempo (cada corte na palavra que ele mostra)
CAPA = 2.5                                                         # quadro 0: rio cheio real + gancho + data
IR0 = em("f2", "Tenente") - .15                                    # satélite IR + mapa: Tenente Portela, extremo noroeste do RS
IR1 = IR0 + MIN_MAPA                                               # Nei 13/11: imagem real vence o mapa; lugar 1x por estado, 3 s
EST = em("f3", "arrancou") - .3                                    # estradas arrancadas
if 4.1 < EST - IR1 < 2 * MIN_CENA:                                 # avatar mais rápido: trecho longo p/ 1 clipe (4,1 s) e curto p/ 2
    IR1 = EST - 4.1                                                #   o satélite IR fica um pouco mais (>= 3 s)
P0 = em("f4", "Paraná") - .15                                      # mapa P: Paraná (granizo)
P1 = P0 + MIN_MAPA
C0 = em("f6", "949") - .3                                          # mapa C: 949 cidades do Sul em aviso no sábado
C1 = C0 + MIN_MAPA
GR7 = em("f7", "granizo") - .3                                     # granizo previsto
K0 = ini("f10")                                                    # CTA

# ---------------------------------------------------------------- câmera: só aparece nos trechos de mapa/satélite
K = lambda t, r, pitch=0, bearing=0: {"t": round(t, 3), **r, "pitch": pitch, "bearing": bearing}
NOROESTE = {"lon": -53.75, "lat": -27.8, "zoom": 7.0}   # Tenente Portela e o extremo noroeste
PARANA = {"lon": -51.6, "lat": -24.9, "zoom": 6.2}
SUL = {"lon": -51.6, "lat": -27.6, "zoom": 5.5}         # RS + SC + PR
VIAGEM = .7                                             # a câmera chega antes do mapa aparecer e fica parada
trechos = [(IR0, IR1, NOROESTE), (P0, P1, PARANA), (C0, C1, SUL)]
camera = [K(0, NOROESTE)]
for a, b, r in trechos:
    camera += [K(a - VIAGEM, r) if camera[-1]["lon"] != r["lon"] else K(a, r), K(b, r)]
camera.append(K(DUR, SUL))
camera = [c for i, c in enumerate(camera) if i == 0 or c["t"] > camera[i - 1]["t"]]
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: GOES-19 infravermelho das últimas 24 h (f2)
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 130 and "2026-11-13T00:00:00Z" <= TS[i] <= "2026-11-14T03:00:00Z"]
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

# ---------------------------------------------------------------- telas (clipes reais do dia + 2 ilustrações)
telas = [foto("capa-dia/abertura.png", 0, CAPA, zoom=.05)]                       # rio cheio + gancho + data
telas += encher(CAPA, IR0, ["clip-09", "clip-02", "clip-06", "clip-11"])         # "130 mm... estradas e pontilhões... noroeste"
# satélite IR (Tenente Portela, extremo noroeste) 3 s
telas += encher(IR1, EST, ["clip-05", "clip-10", "clip-07", "clip-14"])         # "rios viraram enxurrada... municípios contam"
telas += encher(EST, P0, ["clip-02", "clip-03", "clip-12", "clip-01"])           # "arrancou estradas... pontilhões"
# mapa P (Paraná) 3 s
G5 = max(P1 + MIN_CENA, ini("f5"))                                                # granizo segue até o começo da f5
telas += encher(P1, G5, [GRANIZO])                                               # "queda de granizo"
telas += encher(G5, ini("f6"), ["clip-08", "clip-01", "clip-10", "clip-06"])   # "calor com umidade... Foz 36 graus"
telas += encher(ini("f6"), C0, [TEMPESTADE])                                     # "no sábado a tempestade volta"
# mapa C (Sul, 949) 3 s
telas += encher(C1, GR7, ["clip-09", "clip-11", "clip-05", TEMPESTADE])          # "497 no RS... 50 mm, vento 60"
G8 = max(GR7 + MIN_CENA, ini("f8"))
telas += encher(GR7, G8, [GRANIZO])                                              # "e granizo"
telas += encher(G8, ini("f9"), ["clip-07", "clip-12", "clip-03", "clip-02", "clip-14"])   # "domingo... rio... estrada de terra"
telas += encher(ini("f9"), K0, ["clip-06", "clip-10", "clip-08"])                # pergunta
telas += encher(K0, DUR, ["clip-05", "clip-01"])                                 # CTA (o vídeo acaba com o avatar)
assert telas[0]["ini"] == 0   # vis() não faz fade-in quando ini <= 0 (quadro 0 cheio)

# ---------------------------------------------------------------- portões das 3 regras (3c)
mapas = [("IR noroeste do RS", IR0, IR1, em("f2", "Tenente")), ("P Paraná", P0, P1, em("f4", "Paraná")),
         ("C Sul 949", C0, C1, em("f6", "949"))]
for m in telas:
    assert min(m["fim"], FIM_VIDEO) - m["ini"] >= MIN_CENA - .01, ("cena curta", m.get("src") or m["seq"][0], round(min(m["fim"], FIM_VIDEO) - m["ini"], 2))
for nome, a, b, palavra in mapas:
    assert b - a >= MIN_MAPA - .01, ("mapa curto", nome, round(b - a, 2))
    assert a <= palavra + .25, ("mapa entra depois da palavra do lugar", nome, round(a - palavra, 2))
# lugares ditos (f1 "noroeste gaúcho" fica na capa: é o gancho escrito; f9 "cidade do Sul" não é lugar do fato)
fim_mapa = lambda t: max(b for _, a, b, _ in mapas if a - .01 <= t + .25 and t < b)
LUGARES = [("f2", "Tenente"), ("f4", "Paraná")]   # Nei 13/11: mapa só na 1ª vez de cada estado; o resto vai no painel por cima da cena real
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
assert aviso[56398]["descricao"] == "Tempestade" and aviso[56398]["inicio"].startswith("2026-11-14")
TSAB = geo(56398); TSAB_UF = uf(TSAB)
assert len(TSAB) == 949 and (TSAB_UF["RS"], TSAB_UF["SC"], TSAB_UF["PR"]) == (497, 295, 157), TSAB_UF   # f6
R0 = aviso[56398]["riscos"][0]
assert "50 mm/dia" in R0 and "40-60 km/h" in R0 and "granizo" in R0                                       # f7
assert aviso[56399]["descricao"] == "Tempestade" and aviso[56399]["inicio"].startswith("2026-11-15")
TDOM = geo(56399); TDOM_UF = uf(TDOM)
assert len(TDOM) == 1017, len(TDOM)                                                                         # f8 "mais de mil"

ME = json.loads((B / "noaa_metar_brasil_24h.json").read_text())
FOZ = max(m["temp"] for m in ME if m["icaoId"] == "SBFI" and m.get("temp") is not None and m["reportTime"] >= "2026-11-13T09")
assert FOZ == 36, FOZ                                                                                       # f5

# ---------------------------------------------------------------- mapa: estados pintados e pinos (só nos trechos de mapa)
estados = [
    {"id": "a_rs", "ini": IR0, "fim": IR1, "ufs": ["RS"], "cor": VERM, "alfa": .22},
    {"id": "p_pr", "ini": P0, "fim": P1, "ufs": ["PR"], "cor": VERM, "alfa": .26},
    {"id": "c_rs", "ini": C0, "fim": C1, "ufs": ["RS"], "cor": VERM, "alfa": .32},
    {"id": "c_sc", "ini": C0, "fim": C1, "ufs": ["SC"], "cor": LAR, "alfa": .3},
    {"id": "c_pr", "ini": C0, "fim": C1, "ufs": ["PR"], "cor": LAR, "alfa": .22},
]
pino = lambda nome, sub, lon, lat, a, b, h=120: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    pino("Tenente Portela", "+130 mm em pouco mais de 1 h", -53.76, -27.37, IR0, IR1, 110),
    pino("Paraná", "queda de granizo", -51.6, -24.6, P0 + .2, P1, 90),
    pino("Rio Grande do Sul", f"{TSAB_UF['RS']} cidades em aviso", -53.4, -29.4, C0, C1, 80),
    pino("Santa Catarina", f"{TSAB_UF['SC']} cidades", -50.6, -27.3, C0, C1, 80),
    pino("Paraná", f"{TSAB_UF['PR']} cidades", -51.6, -24.8, C0, C1, 80),
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
    {"ini": CAPA, "fim": ini("f2"), "k": "QUINTA 12/11 · NOROESTE DO RS",
     "itens": [{"t": CAPA, "txt": "🌧️ +130 mm em pouco mais de 1 hora"}, {"t": CAPA + .6, "txt": "⚠️ estradas e pontilhões destruídos"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f2"), "fim": ini("f3"), "k": "EXTREMO NOROESTE · RIO GRANDE DO SUL",
     "itens": [{"t": em("f2", "Tenente"), "txt": "📍 Tenente Portela e região"}, {"t": em("f2", "enxurrada"), "txt": "🌊 rios viraram enxurrada"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "SEXTA 13/11 · O QUE FICOU",
     "itens": [{"t": em("f3", "estradas"), "txt": "🛣️ estradas de terra arrancadas"}, {"t": em("f3", "pontilhões"), "txt": "🌉 pontilhões danificados"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "PARANÁ · QUINTA 12/11",
     "itens": [{"t": em("f4", "tempestade"), "txt": "⛈️ tempestade"}, {"t": em("f4", "granizo"), "txt": "🧊 queda de granizo"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "🌡️ CALOR + UMIDADE · FOZ DO IGUAÇU HOJE",
     "contador": conta(FOZ, "f5", "36", "#ff8c1a", "°C", de=20),
     "l": "NOAA · aeroporto de Foz do Iguaçu · sexta 13/11", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "INMET · TEMPESTADE · SÁBADO 14/11",
     "contador": conta(len(TSAB), "f6", "949", "#FACC15", "CIDADES DO SUL"),
     "l": f"RS {TSAB_UF['RS']} · SC {TSAB_UF['SC']} · PR {TSAB_UF['PR']} · perigo potencial", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "⚠️ SÁBADO (PREVISÃO)",
     "itens": [{"t": em("f7", "50"), "txt": "🌧️ até 50 mm por dia"}, {"t": em("f7", "vento"), "txt": "💨 vento de até 60 km/h"},
               {"t": em("f7", "granizo"), "txt": "🧊 granizo"}], "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "INMET · DOMINGO 15/11 (PREVISÃO)",
     "contador": conta(len(TDOM), "f8", "mil", "#FACC15", "CIDADES EM AVISO"),
     "l": f"PR {TDOM_UF['PR']} · SC {TDOM_UF['SC']} · RS {TDOM_UF['RS']} · perto de rio e estrada de terra: atenção",
     "borda": "rgba(255,42,31,.8)"},
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
    {"ini": CAPA, "fim": IR0, "html": f"<b>{MET}</b>"},
    {"ini": IR0, "fim": ini("f3"), "html": f"satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de {IR_DE} a {IR_ATE} · <b>{MET}</b>"},
    {"ini": ini("f3"), "fim": ini("f5"), "html": f"<b>{MET}</b>"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>NOAA</b>, METAR do aeroporto de Foz do Iguaçu (13/11)"},
    {"ini": ini("f6"), "fim": ini("f9"), "html": "<b>INMET</b>, avisos de tempestade (14 e 15/11)"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "agua": "#5ec8ff", "enxurrada": "#5ec8ff", "umidade": "#5ec8ff",
         "rios": "#5ec8ff", "rio": "#5ec8ff",
         "calor": "#ff8c1a", "disparou": "#ff8c1a", "graus": "#ff8c1a", "destruiram": "#ff2a1f", "arrancou": "#ff2a1f",
         "tempestade": "#ff2a1f", "granizo": "#ff2a1f", "estragos": "#ff2a1f",
         "vento": "#ff8c1a", "aviso": "#ff8c1a", "atencao": "#ff8c1a", "atento": "#ff8c1a", "comenta": AM,
         "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "rio", "grande", "noroeste", "gaucho", "santa", "catarina", "parana", "tenente", "portela", "foz", "iguacu",
         "inemaclub", "cidade"}
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
