#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (29/10 a 04/11/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + VIIRS NOAA-20 do Murasu e da Flórida em 2/11 e do In-fa em 3/11 (GIBS, sat/), do Arnab em 28/10 (../2026-10-31-mundo-7d).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "04/11/2026"
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())


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
DUR = round(fim(T[-1]["id"]) + 1.4, 2)
CAPA = 2.2  # quadro 0 = capa cheia do Codex (impacto) até aqui (Nei, 15/10/2026)
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05}]
M = "../2026-10-12-mundo-clima/"
EQ_FOTO = (AQUI / "capa-dia/equador.png").exists()
if EQ_FOTO:  # foto cheia do Codex quando o Equador fala dos rios (selo "ilustração"; Nei, 13/10/2026)
    telas.append({"src": "capa-dia/equador.png", "ini": em("f2", "nesta") - .3, "fim": fim("f2") - .1, "fade": .4, "zoom": .06, "selo": "ilustração"})


# ---------------------------------------------------------------- câmera (9:16), de país em país
AMERICAS = {"lon": -72.0, "lat": 12.0, "zoom": 1.3}
ASIA = {"lon": 80.0, "lat": 18.0, "zoom": 1.3}
MUNDO = {"lon": 20.0, "lat": 20.0, "zoom": 1.2}
EQUADOR = {"lon": -79.9, "lat": -1.6, "zoom": 6.2}
SIRIA = {"lon": 39.2, "lat": 35.9, "zoom": 6.0}
CANARIAS = {"lon": -14.6, "lat": 28.6, "zoom": 6.0}
ODISHA = {"lon": 84.2, "lat": 19.6, "zoom": 6.6}
ANDHRA = {"lon": 80.4, "lat": 15.8, "zoom": 6.4}
FLORIDA = {"lon": -80.8, "lat": 27.9, "zoom": 7.0}
FILIP = {"lon": 123.7, "lat": 13.3, "zoom": 6.4}
RODES = {"lon": 28.0, "lat": 36.3, "zoom": 7.6}
INFA = {"lon": 138.5, "lat": 24.5, "zoom": 4.9}
BERMUDA = {"lon": -64.8, "lat": 30.5, "zoom": 4.9}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, AMERICAS), K(em("f1", "Índia") - .9, {**AMERICAS, "lon": -78.0, "zoom": 1.4}),
    K(em("f1", "Índia") + .5, ASIA), K(em("f1", "Equador") - .6, {**ASIA, "zoom": 1.4}),
    K(em("f1", "Equador") + .6, {**AMERICAS, "lat": 2.0}), K(fim("f1") - .3, {**AMERICAS, "lat": 0.0, "zoom": 1.6}),
    K(ini("f2") + 1.0, EQUADOR, 30, -6), K(fim("f2") - .3, {**EQUADOR, "zoom": 6.6}, 38, 6),
    K(ini("f3") + 1.0, SIRIA, 30, -6), K(fim("f3") - .3, {**SIRIA, "zoom": 6.4}, 36, 6),
    K(ini("f4") + 1.0, CANARIAS, 30, -6), K(fim("f4") - .3, {**CANARIAS, "zoom": 6.4}, 36, 6),
    K(ini("f5") + 1.0, ODISHA, 30, -6), K(fim("f5") - .3, {**ODISHA, "zoom": 7.0}, 38, 6),
    K(ini("f6") + 1.0, ANDHRA, 30, -6), K(fim("f6") - .3, {**ANDHRA, "zoom": 6.8}, 38, 6),
    K(ini("f7") + 1.0, FLORIDA, 30, -6), K(fim("f7") - .3, {**FLORIDA, "zoom": 7.4}, 38, 6),
    K(ini("f8") + 1.0, FILIP, 30, -6), K(fim("f8") - .3, {**FILIP, "zoom": 7.0}, 40, 8),
    K(ini("f9") + 1.0, RODES, 30, -6), K(fim("f9") - .3, {**RODES, "zoom": 8.0}, 38, 6),
    K(ini("f10") + 1.0, INFA, 25, -4), K(em("f10", "baixa") - .3, {**INFA, "zoom": 5.2}, 30, 4),
    K(em("f10", "Bermudas") + .1, BERMUDA, 25, -4), K(fim("f10") - .3, {**BERMUDA, "zoom": 5.2}, 30, 4),
    K(ini("f11") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": -10.0, "zoom": 1.6}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
AR_IMG = "../2026-10-31-mundo-7d/sat/arnab_28_VIIRS_NOAA20.jpg"  # NASA GIBS, VIIRS NOAA-20, 28/10/2026
AR_BOX = [76, 8, 94, 24]
MU_IMG = "sat/murasu_02_VIIRS_NOAA20.jpg"   # NASA GIBS, VIIRS NOAA-20 cor verdadeira, 2/11/2026
MU_BOX = [76, 8, 92, 24]
FL_IMG = "sat/florida_02_VIIRS_NOAA20.jpg"  # NASA GIBS, VIIRS NOAA-20 cor verdadeira, 2/11/2026
FL_BOX = [-86, 23, -76, 31]
IF_IMG = "sat/infa_03_VIIRS_NOAA20.jpg"     # NASA GIBS, VIIRS NOAA-20 cor verdadeira, 3/11/2026
IF_BOX = [130, 16, 146, 32]
imagens = [I(MU_IMG, MU_BOX, ini("f6") - .2, ini("f7") + .6),
           I(FL_IMG, FL_BOX, ini("f7") - .3, ini("f8") + .6),
           I(IF_IMG, IF_BOX, ini("f10") - .3, em("f10", "baixa") + .4)]
pontos = []

PALM_BAY = (-80.59, 28.03)
GRANT = (-80.56, 27.96)       # 1 N Grant-Valkaria (627 mm, NWS Melbourne)
GUAYAQUIL = (-79.89, -2.19)
MILAGRO = (-79.59, -2.13)
JIPIJAPA = (-80.58, -1.35)    # Manabí
RAQQA = (39.01, 35.95)
DEIR = (40.14, 35.33)
ARRECIFE = (-13.55, 28.96)    # Lanzarote; barco a ~150 km
GIDIPABALI = (84.30, 19.93)
ONGOLE = (80.05, 15.50)       # chegada do Murasu (IMD via The Hindu)
VIJAYAWADA = (80.65, 16.51)
MAYON = (123.685, 13.257)
RODES_C = (28.22, 36.43)
CENTRO_IF = (138.5, 25.5)     # NWS Guam, aviso 48, 4/11 09 UTC
IWO = (141.32, 24.78)         # Iwo To
BERM = (-64.78, 32.30)
P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Enchente · Flórida, EUA", "2 vítimas · até 627 mm", *PALM_BAY, em("f1", "Flórida"), ini("f2"), 240),
    P("Ciclone Murasu · Índia", "2º ciclone em uma semana · terça", *ONGOLE, em("f1", "Índia"), ini("f2"), 200),
    P("El Niño · Equador", "11 vítimas desde agosto", *GUAYAQUIL, em("f1", "Equador"), ini("f2"), 150),
    P("Guayaquil · Guayas", "10 rios transbordados em Guayas", *GUAYAQUIL, em("f2", "Equador"), ini("f3"), 150),
    P("Milagro", "inundação persiste", *MILAGRO, em("f2", "atingidas"), ini("f3"), 300),
    P("Manabí", "6 rios transbordados", *JIPIJAPA, em("f2", "24"), ini("f3"), 230),
    P("Raqqa · Síria", "enxurradas · 28 a 30/10", *RAQQA, em("f3", "Síria"), ini("f4"), 200),
    P("Deir ez-Zor", "leste da Síria", *DEIR, em("f3", "enxurradas"), ini("f4"), 110),
    P("Arrecife · Lanzarote", "barco a 150 km · 139 a bordo", *ARRECIFE, em("f4", "Canárias"), ini("f5"), 200),
    P("Gidipabali · Odisha", "deslizamento · 10 desaparecidos", *GIDIPABALI, em("f5", "Odisha"), ini("f6"), 200),
    P("Ongole · Prakasam", "chegada do Murasu · terça", *ONGOLE, em("f6", "Murasu"), ini("f7"), 180),
    P("Vijayawada", "ruas alagadas · ~100 mm", *VIJAYAWADA, em("f6", "Pradesh"), ini("f7"), 320),
    P("Palm Bay · Brevard", "2 vítimas · centenas de resgates", *PALM_BAY, em("f7", "Flórida"), ini("f8"), 260),
    P("Grant-Valkaria", "627 mm em 2 dias e meio", *GRANT, em("f7", "627"), ini("f8"), 120),
    P("Vulcão Mayon · Albay", "alerta 3 · cinzas a 1.600 m", *MAYON, em("f8", "Mayon"), ini("f9"), 200),
    P("Rodes · Grécia", "tempestade Agneta · 60 carros", *RODES_C, em("f9", "Grécia"), ini("f10"), 200),
    P("Tufão In-fa", "145 km/h · enfraquece · NOAA", *CENTRO_IF, em("f10", "In-fa"), em("f10", "baixa") + .3, 200),
    P("Iwo To · Japão", "ilhas Ogasawara: ondas altas", *IWO, em("f10", "sexta"), em("f10", "baixa") + .3, 110),
    P("Bermudas", "baixa ao sul · 50% em 7 dias", *BERM, em("f10", "Bermudas"), ini("f11"), 200),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">FLÓRIDA</div><div class="t2" style="font-size:92px">627 MM DE CHUVA</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌧️ 2 vítimas em Palm Bay · 🌀 Índia: 2º ciclone em uma semana · 🌊 Equador: 11 vítimas</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid, k=1: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal, k) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "49") - 1.0, "fim": em("f2", "24") - 1.0, "k": "EQUADOR · CHUVAS DO EL NIÑO · DESDE 29/08",
     "contador": cont("f2", "49", 48958, 0, "#3c96ff", "PESSOAS ATINGIDAS"),
     "l": "1.086 eventos em 24 províncias · 11 vítimas (Secretaria de Gestão de Riscos)", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f2", "24") - 1.0, "fim": ini("f3"), "k": "EQUADOR · QUARTA (4/11)",
     "contador": cont("f2", "24", 24, 0, "#ff8c1a", "RIOS TRANSBORDADOS"),
     "l": "Guayas 10 · Manabí 6 · Los Ríos 4 · Santa Elena 3 · El Oro 1", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f3", "8") - 1.0, "fim": ini("f4"), "k": "ENXURRADAS · SÍRIA · 28 A 30/10",
     "contador": cont("f3", "8", 8, 0, "#ff2a1f", "VÍTIMAS · 5 DELAS CRIANÇAS"),
     "l": "4 desaparecidos · 60 resgatados (ministro de Emergência)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f4", "tempestade") - .2, "fim": em("f4", "7") - 1.0, "k": "RUMO ÀS CANÁRIAS · SEGUNDA (2/11)",
     "itens": [it("f4", "tempestade", "🌊 tempestade no Atlântico"),
               it("f4", "barco", "🚤 barco com 139 migrantes")], "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f4", "7") - 1.0, "fim": ini("f5"), "k": "RUMO ÀS CANÁRIAS · A 150 KM DE ARRECIFE",
     "contador": cont("f4", "7", 7, 0, "#ff2a1f", "VÍTIMAS NO BARCO"),
     "l": "Resgate chegou na manhã de segunda (Al Jazeera)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f5", "6") - 1.0, "fim": em("f5", "10") - 1.0, "k": "ODISHA, ÍNDIA · CICLONE ARNAB",
     "contador": cont("f5", "6", 6, 0, "#ff2a1f", "VÍTIMAS NO ESTADO"),
     "l": "Eram 4 no sábado · 2 corpos achados em Gidipabali", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f5", "10") - 1.0, "fim": ini("f6"), "k": "DESLIZAMENTO · GIDIPABALI · BUSCAS",
     "contador": cont("f5", "10", 10, 0, "#ff8c1a", "DESAPARECIDOS"),
     "l": "Cerca de 118 mil pessoas atingidas em Odisha", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f6", "120") - 1.0, "fim": em("f6", "deixando") - .2, "k": "CICLONE MURASU · ANDHRA PRADESH · TERÇA (3/11)",
     "contador": cont("f6", "120", 120, 0, "#ff8c1a", "KM/H DE VENTO NA CHEGADA"),
     "l": "Chegou perto de Ongole · 110 a 120 km/h (IMD)", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f6", "deixando") - .2, "fim": ini("f7"), "k": "CICLONE MURASU · ANDHRA PRADESH",
     "contador": cont("f6", "2", 2, 0, "#ff2a1f", "VÍTIMAS", 2),
     "l": "52.459 hectares de lavoura · 12.230 pessoas em abrigos (The Hindu)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f7", "627") - 1.0, "fim": em("f7", "2", 2) - 1.0, "k": "FLÓRIDA, EUA · 1 A 3/11",
     "contador": cont("f7", "627", 627, 0, "#5ec8ff", "MM DE CHUVA · GRANT-VALKARIA"),
     "l": "24,69 polegadas · 559 mm em Palm Bay (NOAA/NWS Melbourne)", "borda": "rgba(94,200,255,.8)"},
    {"ini": em("f7", "2", 2) - 1.0, "fim": ini("f8"), "k": "ENCHENTE · PALM BAY, FLÓRIDA",
     "contador": cont("f7", "2", 2, 0, "#ff2a1f", "VÍTIMAS", 2),
     "l": "Centenas de resgates · estado de emergência ampliado", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f8", "4") - 1.0, "fim": ini("f9"), "k": "VULCÃO MAYON · FILIPINAS · ALERTA 3",
     "contador": cont("f8", "4", 3903, 0, "#ff8c1a", "PESSOAS RETIRADAS EM ALBAY"),
     "l": "Cinzas a 1.600 m na terça · Phivolcs avalia subir para o nível 4", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f9", "60") - 1.0, "fim": ini("f10"), "k": "TEMPESTADE AGNETA · RODES, GRÉCIA",
     "contador": cont("f9", "60", 60, 0, "#3c96ff", "CARROS ARRASTADOS"),
     "l": "17 horas de chuva · escolas fechadas", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f10", "In-fa") - .2, "fim": em("f10", "baixa") - .2, "k": "E AGORA? · TUFÃO IN-FA · PREVISÃO DA NOAA",
     "itens": [it("f10", "In-fa", "🌀 145 km/h, perdendo força"),
               it("f10", "sexta", "↗️ vira para nordeste e enfraquece até sexta")], "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f10", "baixa") - .2, "fim": ini("f11"), "k": "E AGORA? · ATLÂNTICO · PREVISÃO DO NHC",
     "itens": [it("f10", "baixa", "🌀 baixa pressão ao sul das Bermudas"),
               it("f10", "tempestade", "📈 50% de chance de virar tempestade em 7 dias")], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [it("f11", "região", "🗺️ Sua região?"), it("f11", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "<b>NOAA</b>/NWS Melbourne · WKMG · IMD via The Hindu · SNGR via Primicias · capa: ilustração · mapa: <b>NASA</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "Secretaria de Gestão de Riscos e COE do Equador via Primicias, 3 e 4/11/2026" + (" · foto: ilustração" if EQ_FOTO else "")},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Ministério de Emergência da Síria via <b>SANA</b>, 31/10/2026"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Al Jazeera, 2/11/2026"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Autoridades de Odisha via Millennium Post, 2/11/2026"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "IMD e governo de Andhra Pradesh via The Hindu, 3/11/2026 · imagem: <b>NASA</b> GIBS, 2/11"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>NOAA</b>/NWS Melbourne, 3/11 · WKMG, 3/11/2026 · imagem: <b>NASA</b> GIBS, 2/11"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Phivolcs e APSEMO via Daily Tribune, 3/11 · Manila Times, 2/11/2026"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": "eKathimerini, 2/11/2026"},
    {"ini": ini("f10"), "fim": DUR, "html": "<b>NOAA</b>/NWS Guam, aviso 48 · <b>NOAA</b>/NHC, 4/11/2026 · imagem: <b>NASA</b> GIBS, 3/11 · previsão, pode mudar"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "brigadistas": "#ff2a1f", "militares": "#ff2a1f", "feridos": "#ff2a1f", "luz": AM, "recorde": "#5ec8ff", "comenta": AM, "abrigos": "#ff8c1a", "tornado": "#ff8c1a", "ciclone": "#ff8c1a", "supertufao": "#ff8c1a", "neve": "#5ec8ff", "avalanches": "#5ec8ff", "enchentes": "#3c96ff", "enchente": "#3c96ff", "enxurradas": "#3c96ff", "criancas": "#ff2a1f", "inteligencia": AM, "artificial": AM, "vulcao": "#ff5a14", "erupcao": "#ff5a14", "cinzas": "#ff5a14", "cratera": "#ff5a14", "deslizamento": "#ff8c1a", "resgatados": "#5ec8ff", "bebe": "#ff2a1f", "alerta": "#ff8c1a", "chuva": "#5ec8ff", "rios": "#3c96ff", "migrantes": "#ff2a1f", "resgates": "#5ec8ff", "milimetros": "#5ec8ff", "carros": "#3c96ff", "historica": "#5ec8ff", "transbordaram": "#3c96ff"}
LUGAR = {"equador", "guayas", "manabi", "canarias", "atlantico", "murasu", "palm", "bay", "brevard", "rodes", "agneta", "bermudas", "eua", "ganjam", "gidipabali", "kandhamal", "gajapati", "dangesi", "siria", "hasakah", "alepo", "mayon", "filipinas", "leste", "infa", "oeste", "grecia", "raqqa", "deir", "ezzor", "aleppo", "phuket", "agrihan", "ilhas", "india", "infa", "marianas", "pagan", "kakinada", "odisha", "andhra", "pradesh", "londres", "antalia", "arnab", "tailandia", "nepal", "grecia", "turquia", "tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
         "rachel", "isaias", "espanha", "valencia", "alicante", "ibiza", "formentera", "barcelona", "adam", "norte", "merizo", "trudy", "istambul", "turquia", "guam", "champi", "pacifico", "inemaclub", "boelo", "reino", "unido", "escocia", "novo", "farmington", "san", "juan", "colima", "yilan", "uist", "costa", "china", "japao", "tibete", "nagqu", "franca", "bretanha", "normandia", "austen", "vance", "sul", "regiao", "cidade", "taiwan", "marselha", "regiao", "cidade", "nepal", "gorkha", "rota", "colima", "manzanillo", "california", "unidos", "estados", "jalisco", "menorca", "ciutadella", "indonesia", "java", "bromo", "taiwan", "filipinas", "noaa", "mexico", "corsega", "franca", "ghisonaccia", "canada", "alberta", "tibete", "nagqu", "china", "marselha", "austen", "vance", "bretanha", "normandia", "japao", "kyushu", "sul", "pais", "boelo", "reino", "escocia", "colima", "yilan", "uist", "costa"}
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

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR, "padding_topo": 0 if AVATAR else 560,
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "NOAA · IMD · SNGR · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
