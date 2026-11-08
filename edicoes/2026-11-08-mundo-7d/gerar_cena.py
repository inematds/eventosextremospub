#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (2 a 08/11/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + VIIRS NOAA-20 do Murasu em 2/11 (NASA GIBS, sat/).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "08/11/2026"
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


# ---------------------------------------------------------------- câmera (9:16), de país em país
ORIENTE = {"lon": 44.0, "lat": 32.0, "zoom": 1.6}
JAPAO_W = {"lon": 132.0, "lat": 33.0, "zoom": 1.6}
GAZA_W = {"lon": 38.0, "lat": 30.0, "zoom": 1.7}
ASIA = {"lon": 80.0, "lat": 18.0, "zoom": 1.5}
MUNDO = {"lon": 20.0, "lat": 20.0, "zoom": 1.2}
EQUADOR = {"lon": -79.8, "lat": -1.2, "zoom": 6.0}
ANDHRA = {"lon": 80.3, "lat": 15.0, "zoom": 6.0}
GAZA_C = {"lon": 34.40, "lat": 31.40, "zoom": 8.6}
ERBIL_C = {"lon": 44.0, "lat": 36.15, "zoom": 6.6}
IRA_C = {"lon": 49.5, "lat": 32.0, "zoom": 5.2}
SHIZ_C = {"lon": 137.4, "lat": 34.9, "zoom": 7.2}
SELANGOR = {"lon": 101.2, "lat": 3.6, "zoom": 7.2}
VIETNA = {"lon": 107.9, "lat": 16.0, "zoom": 6.2}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, ORIENTE), K(em("f1", "Japão") - .9, {**ORIENTE, "zoom": 1.8}),
    K(em("f1", "Japão") + .5, JAPAO_W), K(em("f1", "Gaza") - .6, {**JAPAO_W, "zoom": 1.8}),
    K(em("f1", "Gaza") + .6, GAZA_W), K(fim("f1") - .3, {**GAZA_W, "zoom": 1.9}),
    K(ini("f2") + 1.0, ANDHRA, 30, -6), K(fim("f2") - .3, {**ANDHRA, "zoom": 6.4}, 38, 6),
    K(ini("f3") + 1.0, EQUADOR, 30, -6), K(fim("f3") - .3, {**EQUADOR, "zoom": 6.4}, 38, 6),
    K(ini("f4") + 1.0, GAZA_C, 30, -6), K(fim("f4") - .3, {**GAZA_C, "zoom": 9.0}, 38, 6),
    K(ini("f5") + 1.0, ERBIL_C, 30, -6), K(fim("f5") - .3, {**ERBIL_C, "zoom": 7.0}, 38, 6),
    K(ini("f6") + 1.0, IRA_C, 25, -4), K(fim("f6") - .3, {**IRA_C, "zoom": 5.6}, 32, 4),
    K(ini("f7") + 1.0, SHIZ_C, 30, -6), K(fim("f7") - .3, {**SHIZ_C, "zoom": 7.6}, 38, 6),
    K(ini("f8") + 1.0, SELANGOR, 30, -6), K(fim("f8") - .3, {**SELANGOR, "zoom": 7.6}, 38, 6),
    K(ini("f9") + 1.0, VIETNA, 25, -4), K(fim("f9") - .3, {**VIETNA, "zoom": 6.6}, 32, 4),
    K(ini("f10") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": -10.0, "zoom": 1.6}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
MU_IMG = "sat/murasu_02_VIIRS_NOAA20.jpg"   # NASA GIBS, VIIRS NOAA-20 cor verdadeira, 2/11/2026
MU_BOX = [76, 8, 92, 24]
imagens = [I(MU_IMG, MU_BOX, ini("f2") - .2, ini("f3") + .6)]
pontos = []

GAZA = (34.45, 31.50)         # Cidade de Gaza
KHAN = (34.30, 31.35)         # Khan Younis / Mawasi
ONGOLE = (80.05, 15.50)       # Kothapatnam, perto de Ongole: barco virou
BAPATLA = (80.47, 15.90)      # 5 vítimas
GUNTUR = (80.44, 16.31)       # 2 vítimas
PALNADU = (80.05, 16.23)      # 1 vítima
CHENNAI = (80.30, 13.12)      # Kasimedu
GUAYAQUIL = (-79.89, -2.19)
ESMERALDAS = (-79.65, 0.96)
BABAHOYO = (-79.53, -1.80)
ERBIL = (44.01, 36.19)
AHVAZ = (48.67, 31.32)        # Khuzistão: 2 vítimas por raio
KHORRAM = (48.35, 33.49)      # Lorestão: 190 vilarejos isolados
YASUJ = (51.59, 30.67)        # Kohgiluyeh e Boyer-Ahmad: feridos
HAMAMATSU = (137.73, 34.71)   # oeste de Shizuoka: epicentro
AICHI = (137.20, 35.00)       # Aichi: feridos
IJOK = (101.42, 3.33)         # Batu 8 Ijok, Kuala Selangor
TELUK = (101.02, 4.02)        # Teluk Intan, Hilir Perak
DANANG = (108.20, 16.05)
QNGAI = (108.80, 15.12)
P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Erbil · Iraque", "enxurrada · 2 vítimas", *ERBIL, em("f1", "Iraque"), em("f1", "Japão"), 60),
    P("Shizuoka · Japão", "terremoto 5,7 · mais de 20 feridos", *HAMAMATSU, em("f1", "Japão"), em("f1", "Gaza"), 60),
    P("Gaza", "70 mil barracas alagadas", *GAZA, em("f1", "Gaza"), ini("f2"), 60),
    P("Bapatla", "5 vítimas", *BAPATLA, em("f2", "8"), em("f2", "pescadores"), 300),
    P("Guntur", "2 vítimas", *GUNTUR, em("f2", "vítimas"), em("f2", "pescadores"), 180),
    P("Palnadu", "1 vítima", *PALNADU, em("f2", "terra"), em("f2", "pescadores"), 110),
    P("Kothapatnam · Ongole", "barco de 9 pescadores virou", *ONGOLE, em("f2", "pescadores"), ini("f3"), 200),
    P("Kasimedu · Chennai", "porto dos pescadores", *CHENNAI, em("f2", "Chennai"), ini("f3"), 160),
    P("Guayas", "12 rios transbordados", *GUAYAQUIL, em("f3", "Equador"), ini("f4"), 150),
    P("Esmeraldas", "5 rios transbordados", *ESMERALDAS, em("f3", "57"), ini("f4"), 220),
    P("Los Ríos", "5 rios transbordados", *BABAHOYO, em("f3", "28"), ini("f4"), 300),
    P("Cidade de Gaza", "acampamentos alagados", *GAZA, em("f4", "Gaza"), ini("f5"), 220),
    P("Khan Younis", "barracas de deslocados", *KHAN, em("f4", "barracas"), ini("f5"), 120),
    P("Erbil", "carros arrastados · 2 vítimas", *ERBIL, em("f5", "Erbil"), ini("f6"), 200),
    P("Khuzistão", "2 vítimas por raio", *AHVAZ, em("f6", "4"), ini("f7"), 60),
    P("Kohgiluyeh", "feridos", *YASUJ, em("f6", "11"), ini("f7"), 60),
    P("Lorestão", "190 vilarejos isolados", *KHORRAM, em("f6", "190"), ini("f7"), 60),
    P("Oeste de Shizuoka", "epicentro · 40 km de profundidade", *HAMAMATSU, em("f7", "terremoto"), ini("f8"), 120),
    P("Aichi", "feridos", *AICHI, em("f7", "20"), ini("f8"), 260),
    P("Ijok · Selangor", "2.999 num só abrigo", *IJOK, em("f8", "Selangor"), ini("f9"), 160),
    P("Teluk Intan · Perak", "270 em abrigos", *TELUK, em("f8", "Perak"), ini("f9"), 260),
    P("Da Nang", "chuva torrencial · previsão", *DANANG, em("f9", "Vietnã"), ini("f10"), 220),
    P("Quang Ngai", "mais de 700 mm em pontos", *QNGAI, em("f9", "torrencial"), ini("f10"), 130),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">IRAQUE</div><div class="t2" style="font-size:92px;line-height:1.05">ENXURRADA<br>EM ERBIL: 2 VÍTIMAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌍 Japão: terremoto, mais de 20 feridos · 🌊 Gaza: 70 mil barracas alagadas</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid, k=1: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal, k) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "8") - 1.0, "fim": em("f2", "7") - 1.0, "k": "CICLONE MURASU · ANDHRA PRADESH",
     "contador": cont("f2", "8", 8, 0, "#ff2a1f", "VÍTIMAS EM TERRA"),
     "l": "5 em Bapatla · 2 em Guntur · 1 em Palnadu", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f2", "7") - 1.0, "fim": em("f2", "2") - 1.0, "k": "PESCADORES DE CHENNAI · NO MAR",
     "contador": cont("f2", "7", 7, 0, "#ff2a1f", "VÍTIMAS NO MAR"),
     "l": "Barco com 9 pescadores virou perto de Ongole", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f2", "2") - 1.0, "fim": ini("f3"), "k": "PESCADORES DE CHENNAI · BUSCAS",
     "contador": cont("f2", "2", 2, 0, "#ff8c1a", "DESAPARECIDOS"),
     "l": "Guarda Costeira segue a busca (7/11)", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f3", "57") - 1.0, "fim": em("f3", "12") - 1.0, "k": "EQUADOR · CHUVAS DO EL NIÑO · DESDE AGOSTO",
     "contador": cont("f3", "57", 56798, 0, "#ff8c1a", "PESSOAS ATINGIDAS"),
     "l": "12.925 casas afetadas · 42 destruídas", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f3", "12") - 1.0, "fim": em("f3", "28") - 1.0, "k": "EQUADOR · GESTÃO DE RISCOS",
     "contador": cont("f3", "12", 12, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "Balanço com corte às 7h de sexta (6/11)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f3", "28") - 1.0, "fim": ini("f4"), "k": "EQUADOR · SEXTA (6/11)",
     "contador": cont("f3", "28", 28, 0, "#3c96ff", "RIOS E ESTEIROS TRANSBORDADOS"),
     "l": "Em 6 províncias · Guayas é a mais atingida", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f4", "70") - 1.0, "fim": em("f4", "1.500") - 1.0, "k": "GAZA · DESDE SÁBADO (7/11)",
     "contador": cont("f4", "70", 70000, 0, "#3c96ff", "BARRACAS ALAGADAS"),
     "l": "Em 12 horas · gabinete de mídia do governo de Gaza", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f4", "1.500") - 1.0, "fim": ini("f5"), "k": "GAZA · DEFESA CIVIL",
     "contador": cont("f4", "1.500", 1500, 0, "#ff8c1a", "PEDIDOS DE SOCORRO"),
     "l": "Em 10 horas · muros desabaram, há feridos", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f5", "enxurrada") - .2, "fim": em("f5", "2") - 1.0, "k": "ERBIL, IRAQUE · SÁBADO (7/11) À NOITE",
     "itens": [it("f5", "enxurrada", "🌊 enxurrada com granizo e vento"),
               it("f5", "carros", "🚗 carros arrastados, casas invadidas")], "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f5", "2") - 1.0, "fim": ini("f6"), "k": "ERBIL · GOVERNO PROVINCIAL",
     "contador": cont("f5", "2", 2, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "Criança de 5 anos · voluntário de 28 que ajudava moradores", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f6", "4") - 1.0, "fim": em("f6", "190") - 1.0, "k": "IRÃ · TEMPORAIS DESDE SEXTA (6/11)",
     "contador": cont("f6", "4", 4, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "2 por raio no Khuzistão · 11 feridos", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f6", "190") - 1.0, "fim": ini("f7"), "k": "IRÃ · LORESTÃO",
     "contador": cont("f6", "190", 190, 0, "#ff8c1a", "VILAREJOS ISOLADOS"),
     "l": "Alerta vermelho segue em várias províncias", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f7", "5,7") - 1.0, "fim": em("f7", "20") - 1.0, "k": "JAPÃO · DOMINGO (8/11), 1H04",
     "contador": cont("f7", "5,7", 5.7, 1, "#ff2a1f", "DE MAGNITUDE"),
     "l": "40 km de profundidade · sem alerta de tsunami", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f7", "20") - 1.0, "fim": ini("f8"), "k": "JAPÃO · AICHI E SHIZUOKA",
     "contador": cont("f7", "20", 20, 0, "#ff8c1a", "FERIDOS · MAIS DE"),
     "l": "Alguns caíram na escada ao fugir", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f8", "4.068") - 1.0, "fim": ini("f9"), "k": "MALÁSIA · SÁBADO (7/11)",
     "contador": cont("f8", "4.068", 4068, 0, "#ff8c1a", "PESSOAS EM ABRIGOS"),
     "l": "Selangor 3.798 · Perak 270 · de manhã eram 1.404", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f9", "700") - 1.0, "fim": ini("f10"), "k": "E AGORA? · CENTRO DO VIETNÃ · PREVISÃO",
     "contador": cont("f9", "700", 700, 0, "#5ec8ff", "MM EM ALGUNS PONTOS"),
     "l": "Da noite de domingo (8/11) até quarta (11/11)", "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [it("f10", "região", "🗺️ Sua região?"), it("f10", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Rudaw · 964media · Al Jazeera/AP · Al Jazeera/AFP · capa: ilustração · mapa: <b>NASA</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "The News Minute, 6/11 · Guarda Costeira via PTI, 7/11/2026 · imagem: <b>NASA</b> GIBS, 2/11"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Secretaria de Gestão de Riscos do Equador via Extra.ec, 6/11/2026"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Gabinete de mídia do governo de Gaza e defesa civil, via Al Jazeera, 7 e 8/11/2026"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Rudaw, 7/11 · 964media, 8/11/2026"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "Emergência nacional do Irã (ISNA) via Iran International, 8/11/2026"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Agência Meteorológica do Japão · Kyodo via Al Jazeera/AP, 8/11/2026"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Bernama, com o portal InfoBencana (JKM), 7/11/2026"},
    {"ini": ini("f9"), "fim": DUR, "html": "Centro Nacional de Previsão do Vietnã via DTiNews e Tuoi Tre, 7 e 8/11/2026 · previsão, pode mudar"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "brigadistas": "#ff2a1f", "militares": "#ff2a1f", "feridos": "#ff2a1f", "vilarejos": "#ff8c1a", "isolados": "#ff8c1a", "temporais": "#ff8c1a", "luz": AM, "recorde": "#5ec8ff", "comenta": AM, "abrigos": "#ff8c1a", "tornado": "#ff8c1a", "ciclone": "#ff8c1a", "supertufao": "#ff8c1a", "neve": "#5ec8ff", "avalanches": "#5ec8ff", "enchentes": "#3c96ff", "enchente": "#3c96ff", "enxurradas": "#3c96ff", "criancas": "#ff2a1f", "inteligencia": AM, "artificial": AM, "vulcao": "#ff5a14", "erupcao": "#ff5a14", "cinzas": "#ff5a14", "cratera": "#ff5a14", "deslizamento": "#ff8c1a", "resgatados": "#5ec8ff", "bebe": "#ff2a1f", "alerta": "#ff8c1a", "chuva": "#5ec8ff", "rios": "#3c96ff", "migrantes": "#ff2a1f", "resgates": "#5ec8ff", "milimetros": "#5ec8ff", "carros": "#3c96ff", "carro": "#3c96ff", "barco": "#ff2a1f", "vitima": "#ff2a1f", "desaparecidos": "#ff2a1f", "rio": "#3c96ff", "historica": "#5ec8ff", "transbordaram": "#3c96ff", "barracas": "#3c96ff", "deslocados": "#ff2a1f", "socorro": "#ff8c1a", "torrencial": "#5ec8ff", "abrigos": "#ff8c1a", "enchentes": "#3c96ff"}
LUGAR = {"iraque", "erbil", "ira", "shizuoka", "aichi", "japao", "lorestao", "khuzistao", "gaza", "malasia", "selangor", "perak", "vietna", "centro", "georgia", "tennessee", "chennai", "esmeraldas", "nordeste", "estados", "unidos", "galapagos", "santa", "cruz", "pescadores", "quinta", "equador", "guayas", "manabi", "canarias", "atlantico", "murasu", "palm", "bay", "brevard", "rodes", "agneta", "bermudas", "eua", "ganjam", "gidipabali", "kandhamal", "gajapati", "dangesi", "siria", "hasakah", "alepo", "mayon", "filipinas", "leste", "infa", "oeste", "grecia", "raqqa", "deir", "ezzor", "aleppo", "phuket", "agrihan", "ilhas", "india", "infa", "marianas", "pagan", "kakinada", "odisha", "andhra", "pradesh", "londres", "antalia", "arnab", "tailandia", "nepal", "grecia", "turquia", "tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
         "rachel", "isaias", "espanha", "valencia", "alicante", "ibiza", "formentera", "barcelona", "adam", "norte", "merizo", "trudy", "istambul", "turquia", "guam", "champi", "pacifico", "inemaclub", "boelo", "reino", "unido", "escocia", "novo", "farmington", "san", "juan", "colima", "yilan", "uist", "costa", "china", "japao", "tibete", "nagqu", "franca", "bretanha", "normandia", "austen", "vance", "sul", "regiao", "cidade", "taiwan", "marselha", "regiao", "cidade", "nepal", "gorkha", "rota", "colima", "manzanillo", "california", "unidos", "estados", "jalisco", "menorca", "ciutadella", "indonesia", "java", "bromo", "taiwan", "filipinas", "noaa", "mexico", "corsega", "franca", "ghisonaccia", "canada", "alberta", "tibete", "nagqu", "china", "marselha", "austen", "vance", "bretanha", "normandia", "japao", "kyushu", "sul", "pais", "boelo", "reino", "escocia", "colima", "yilan", "uist", "costa"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        nxt = len(t["palavras"][i + 1]["w"]) if i + 1 < len(t["palavras"]) else 0
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1 or sum(len(b["w"]) + 1 for b in bloco) + nxt > 21:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR, "padding_topo": 0 if AVATAR else 560,
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "Rudaw · Al Jazeera · NASA · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
