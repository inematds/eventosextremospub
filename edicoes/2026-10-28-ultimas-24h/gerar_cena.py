#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 28/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "28/10/2026"
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())
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
CAPA = 2.2  # quadro 0 = capa cheia do Codex (impacto) até aqui (Nei, 15/10/2026)
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05, "selo": "ilustração"}] if (AQUI / "capa-dia/abertura.png").exists() else []
if not telas:
    CAPA = 0
LAR, AMA, VERM, AZC, AZU = [255, 140, 26], [250, 204, 21], [255, 42, 31], [150, 210, 255], [60, 150, 255]

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
PAC = {"lon": -53.0, "lat": -0.6, "zoom": 5.5}       # Pará: Santarém, Uruará, Portel (fogo)
BAC = {"lon": -40.8, "lat": -14.6, "zoom": 7.0}      # Vitória da Conquista (BA)
GOC = {"lon": -47.3, "lat": -15.7, "zoom": 7.0}      # Formosa (GO)
SPC = {"lon": -45.9, "lat": -23.0, "zoom": 7.0}      # São José dos Campos (SP)
NNE = {"lon": -51.5, "lat": -1.5, "zoom": 4.5}       # Boa Vista, Santarém e Teresina
RSC = {"lon": -53.0, "lat": -29.2, "zoom": 6.4}      # frio: Canoas, Santa Maria, Santo Ângelo
HOJ = {"lon": -49.0, "lat": -15.0, "zoom": 4.0}      # amarelo de tempestade
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
VOL = {"lon": -41.5, "lat": -13.0, "zoom": 5.4}      # Bahia (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, PAC, 34, -6), K(fim("f2") - .2, {**PAC, "zoom": 5.8}, 36, 4),
    K(ini("f3") + 1.0, BAC, 34, -4), K(fim("f3") - .2, {**BAC, "zoom": 7.1}, 36, 2),
    K(ini("f4") + 1.0, GOC, 34, 0), K(em("f4", "São") - .2, {**GOC, "zoom": 7.1}, 36, 2),
    K(em("f4", "São") + 1.0, SPC, 34, 0), K(fim("f4") - .2, {**SPC, "zoom": 7.1}, 36, 4),
    K(ini("f5") + 1.0, NNE, 26, 0), K(fim("f5") - .2, {**NNE, "zoom": 4.6}, 28, 4),
    K(ini("f6") + 1.0, RSC, 28, 0), K(fim("f6") - .2, {**RSC, "zoom": 6.5}, 30, 2),
    K(ini("f7") + 1.0, HOJ, 16, 0), K(fim("f7") - .2, {**HOJ, "zoom": 4.1}, 18, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f9") + 1.0, VOL, 10, 0), K(fim("f9") - .2, {**VOL, "zoom": 5.5}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-27T08") and TS[-1].startswith("2026-10-28T08"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# fundo: Blue Marble do mundo por baixo, senão a borda do geocolor aparece preta com a câmera inclinada
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- INPE: focos de 27/10 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
grade, ref, ref_uf, ref_mun = {}, 0, {}, {}
with open(B / "inpe_focos_diario_br_20261027.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-27"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
            if uf == "PARÁ":
                ref_mun[r["municipio"].strip()] = ref_mun.get(r["municipio"].strip(), 0) + 1
assert (ref, ref_uf["PARÁ"]) == (1331, 902), (ref, ref_uf["PARÁ"])          # "902 dos 1.331 focos"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["PARÁ", "MARANHÃO", "TOCANTINS", "AMAPÁ", "BAHIA"], RKF
assert (ref_mun["URUARÁ"], ref_mun["PORTEL"]) == (65, 63), ref_mun
SIGLA = {"PARÁ": "PA", "MARANHÃO": "MA", "TOCANTINS": "TO", "AMAPÁ": "AP", "BAHIA": "BA"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": CAPA, "fim": ini("f3") + .3, "dados": fogo, "dur": 2.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET (só amarelo hoje: nenhum laranja/vermelho vigente)
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
assert {a["severidade"] for a in aviso.values()} == {"Perigo Potencial"}, "apareceu laranja/vermelho: rever a fala f7"
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
conta = lambda i, ufs: [sum(UF[c[:2]] == u for c in geo(i)) for u in ufs]
# tempestade amarelo hoje 28/10: 56201 (1.861: SP 409, GO 246, PR 188, PI 186 …)
assert aviso[56201]["descricao"] == "Tempestade" and aviso[56201]["inicio"].startswith("2026-10-28")
HOJE_N = len(geo(56201))
assert HOJE_N == 1861 and conta(56201, ["SP", "GO", "PR"]) == [409, 246, 188], HOJE_N
TEMP = ufs_av(56201, 40)
# quinta 29/10: 2.777 (SP 645, MG 536, PR 399 …); sexta 30/10: 2.430
assert len(geo(56195)) == 2777 and aviso[56195]["inicio"].startswith("2026-10-29") and conta(56195, ["SP", "MG", "PR"]) == [645, 536, 399]
QUI = ufs_av(56195, 40)
assert len(geo(56202)) == 2430 and aviso[56202]["inicio"].startswith("2026-10-30")
assert len(geo(56196)) == 116 and aviso[56196]["descricao"] == "Acumulado de Chuva" and ufs_av(56196, 1) == ["BA"]
estados = [
    {"id": "f1", "ini": CAPA, "fim": ini("f2") + .3, "ufs": ["PA"], "cor": LAR, "alfa": .4},
    {"id": "f1ba", "ini": em("f1", "Bahia"), "fim": ini("f2") + .3, "ufs": ["BA"], "cor": AZU, "alfa": .4},
    {"id": "pa", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["PA"], "cor": LAR, "alfa": .35},
    {"id": "ba", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["BA"], "cor": AZU, "alfa": .35},
    {"id": "go", "ini": ini("f4"), "fim": em("f4", "São") + .3, "ufs": ["GO"], "cor": AZU, "alfa": .35},
    {"id": "sp", "ini": em("f4", "São"), "fim": ini("f5") + .3, "ufs": ["SP"], "cor": LAR, "alfa": .35},
    {"id": "calor", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["PI", "RR", "PA"], "cor": VERM, "alfa": .35},
    {"id": "frio", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["RS"], "cor": AZC, "alfa": .4},
    {"id": "hoje", "ini": ini("f7"), "fim": em("f7", "quinta") + .3, "ufs": TEMP, "cor": AMA, "alfa": .35},
    {"id": "quinta", "ini": em("f7", "quinta"), "fim": ini("f8") + .3, "ufs": QUI, "cor": LAR, "alfa": .35},
    {"id": "volba", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["BA"], "cor": AZU, "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
CRU = {(e["uf"], e["cidade"], e["nomeestacao"]): e for e in json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())}
acc = lambda u, c, e, k="acc24hr": CRU[(u, c, e)][k]
VDC = [acc("BA", "VITÓRIA DA CONQUISTA", e) for e in ("Barcelar", "Recreio", "Patagônia", "Centro")]
assert VDC == [54.39, 54.3, 45.8, 45.68] and min(VDC) > 45, VDC                                       # "4 pluviômetros passaram de 45"
assert acc("GO", "FORMOSA", "Av. Maestro Joaquim de Abreu") == 69 and acc("GO", "FORMOSA", "Av. Maestro Joaquim de Abreu", "acc3hr") == 69   # "69 em 3 horas"
assert acc("GO", "FORMOSA", "Parque da Colina", "acc3hr") == 50.2
# sensores isolados (vizinhos da cidade bem abaixo ou sem leitura), fora das somas
DESC = {("MG", "VISCONDE DO RIO BRANCO", "Rio Xopoto"): 146.2, ("MG", "ARINOS", "G2-310450202A"): 95,
        ("BA", "JACOBINA", "JACOBINA"): 86.6, ("BA", "SALVADOR", "Doron"): 48.2}
assert {k: acc(*k) for k in DESC} == DESC
assert acc("MG", "VISCONDE DO RIO BRANCO", "Centro") == "-" and acc("MG", "ARINOS", "G2-310450201A") == 8.6 and acc("BA", "JACOBINA", "Feliz Tomaz") == 16
SOMA = CM["soma_por_uf"]
assert CM["soma_mm_estacoes"] == 6971.5 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 6971.5) < .5
NEST = sum(d["estacoes"] for d in SOMA.values()) - len(DESC)
SEMV = {u: d["soma_mm"] - sum(v for k, v in DESC.items() if k[0] == u) for u, d in SOMA.items()}
BRASIL = sum(SEMV.values())
assert 6500 < BRASIL < 6600, BRASIL                            # "mais de 6.500" sem os 4 sensores (6.595,5)
assert 3500 < SEMV["BA"] < 3560 and SEMV["BA"] > BRASIL / 2, SEMV["BA"]   # "mais de 3.500 só na Bahia", "mais da metade"
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["BA", "MG", "GO", "SP", "RJ"], RK

# ---------------------------------------------------------------- NOAA METAR: fumaça em Santarém, rajada em São José dos Campos, calor, frio no RS
MT = json.loads((B / "noaa_metar_brasil_24h.json").read_text())
FU = [o for o in MT if o["icaoId"] == "SBSN" and " 3000 FU " in o["rawOb"]]
assert len(FU) == 4 and min(o["reportTime"] for o in FU).startswith("2026-10-27T07"), [o["rawOb"] for o in FU]   # "fumaça e 3 km"
SJC = max((o for o in MT if o["icaoId"] == "SBSJ" and o.get("wgst")), key=lambda o: o["wgst"])
assert SJC["wgst"] == 29 and SJC["reportTime"].startswith("2026-10-27T20:00"), SJC["rawOb"]
RAJ = round(29 * 1.852)
assert RAJ == 54                                                 # "54 km/h"
for icao, tt in (("SBTE", 39), ("SBBV", 38), ("SBSN", 37)):
    o = max((o for o in MT if o["icaoId"] == icao and o.get("temp") is not None), key=lambda o: o["temp"])
    assert o["temp"] == tt and o["reportTime"].startswith("2026-10-27"), o["rawOb"]
for icao in ("SBCO", "SBSM", "SBNM"):
    o = min((o for o in MT if o["icaoId"] == icao and o.get("temp") is not None and o["reportTime"] >= "2026-10-27T08:30"), key=lambda o: o["temp"])
    assert o["temp"] == 9 and o["reportTime"].startswith("2026-10-27T09:00"), o["rawOb"]   # "9 graus" às 6h

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-28" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qua", "qui", "sex", "sáb", "dom", "seg", "ter"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 686.0   # "mais de 680"
TOP = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP["dia"], TOP["soma_chuva_mm"]) == ("2026-10-30", 139.4), TOP                                          # "sexta"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "CO" and P7["soma_7d_por_regiao_mm"]["CO"] == 227.5
assert P7["acumulado_7d_top"][0] == ["Goiânia", 78.7]
PICO = max(P7["por_dia"], key=lambda d: d["tmax_pico"][0])
assert PICO["tmax_pico"] == [39.3, "Boa Vista"] and PICO["dia"] == "2026-10-29"                                  # "39 graus"

pinos = [
    {"nome": "Santarém (PA)", "sub": "fumaça · 3 km de visibilidade", "lon": -54.71, "lat": -2.44, "ini": em("f2", "Santarém"), "fim": ini("f3"), "h": 75},
    {"nome": "Uruará (PA)", "sub": f"{ref_mun['URUARÁ']} focos", "lon": -53.74, "lat": -3.72, "ini": em("f2", "902") + .4, "fim": ini("f3"), "h": 20},
    {"nome": "Portel (PA)", "sub": f"{ref_mun['PORTEL']} focos", "lon": -50.82, "lat": -1.94, "ini": em("f2", "902") + .8, "fim": ini("f3"), "h": 40},
    {"nome": "Vitória da Conquista (BA)", "sub": "4 pluviômetros acima de 45 mm", "lon": -40.84, "lat": -14.86, "ini": em("f3", "Vitória"), "fim": ini("f4"), "h": 40},
    {"nome": "Formosa (GO)", "sub": "69 mm em 3 h", "lon": -47.33, "lat": -15.54, "ini": em("f4", "Formosa"), "fim": em("f4", "São"), "h": 40},
    {"nome": "São José dos Campos (SP)", "sub": f"rajada de {RAJ} km/h", "lon": -45.89, "lat": -23.18, "ini": em("f4", "José"), "fim": ini("f5"), "h": 40},
    {"nome": "Teresina (PI)", "sub": "39 °C", "lon": -42.80, "lat": -5.09, "ini": em("f5", "Teresina"), "fim": ini("f6"), "h": 40},
    {"nome": "Boa Vista (RR)", "sub": "38 °C", "lon": -60.67, "lat": 2.82, "ini": em("f5", "Boa"), "fim": ini("f6"), "h": 40},
    {"nome": "Santarém (PA)", "sub": "37 °C", "lon": -54.71, "lat": -2.44, "ini": em("f5", "Santarém"), "fim": ini("f6"), "h": 60},
    {"nome": "Santo Ângelo (RS)", "sub": "9 °C às 6h", "lon": -54.26, "lat": -28.30, "ini": em("f6", "Ângelo"), "fim": ini("f7"), "h": 60},
    {"nome": "Santa Maria (RS)", "sub": "9 °C às 6h", "lon": -53.81, "lat": -29.69, "ini": em("f6", "Maria"), "fim": ini("f7"), "h": 20},
    {"nome": "Canoas (RS)", "sub": "9 °C às 6h", "lon": -51.18, "lat": -29.92, "ini": em("f6", "Canoas"), "fim": ini("f7"), "h": 40},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🔥 902 focos no Pará · 🌧️ Bahia: mais da metade da chuva somada</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "PARÁ · FOGO EM 27/10",
     "contador": {"de": 0, "ate": ref_uf["PARÁ"], "dec": 0, "ini": em("f2", "902") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": f"FOCOS NO PARÁ · DE {ref:,} NO BRASIL".replace(",", ".")},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f2", "1.331") + .3, "dur": 1.2},
     "itens": [{"t": em("f2", "Santarém"), "txt": "Aeroporto de Santarém: fumaça e 3 km de visibilidade de 4h a 7h"}],
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência (INPE)", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "BAHIA · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 54.4, "dec": 1, "ini": em("f3", "45") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM VITÓRIA DA CONQUISTA (BA)"},
     "itens": [{"t": em("f3", "45") + .3, "txt": "Barcelar 54,4 · Recreio 54,3 · Patagônia 45,8 · Centro 45,7 mm"},
               {"t": em("f3", "45") + 1.0, "txt": "Camacan: 54,8 mm · alerta de acumulado de chuva em 116 cidades da BA"}],
     "l": "CEMADEN, leituras até 28/10 5h20", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "GOIÁS E SÃO PAULO · CHUVA E VENTO",
     "contador": {"de": 0, "ate": 69, "dec": 0, "ini": em("f4", "69") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM 3 H EM FORMOSA (GO)"},
     "itens": [{"t": em("f4", "horas"), "txt": "Outro pluviômetro de Formosa: 50,2 mm em 3 h"},
               {"t": em("f4", "rajada"), "txt": f"São José dos Campos (SP): rajada de {RAJ} km/h às 17h de terça"}],
     "l": "CEMADEN · aeroporto de São José dos Campos (METAR)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "CALOR · MÁXIMAS DE TERÇA, 27/10",
     "contador": {"de": 0, "ate": 39, "dec": 0, "ini": em("f5", "39") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "°C EM TERESINA (PI)"},
     "itens": [{"t": em("f5", "38"), "txt": "Boa Vista (RR): 38 °C"}, {"t": em("f5", "37"), "txt": "Santarém (PA): 37 °C, no meio da fumaça"}],
     "l": "temperatura nos aeroportos (METAR)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SUL · MADRUGADA FRIA",
     "contador": {"de": 0, "ate": 9, "dec": 0, "ini": em("f6", "9") - 1.0, "dur": 1.0, "cor": "#96d2ff", "unid": "°C ÀS 6H DE TERÇA, NO RS"},
     "itens": [{"t": em("f6", "9") + .4, "txt": "Canoas, Santa Maria e Santo Ângelo: 9 °C"}],
     "l": "temperatura nos aeroportos (METAR)", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA AMARELO DE TEMPESTADE",
     "contador": {"de": 0, "ate": HOJE_N, "dec": 0, "ini": em("f7", "1.861") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES · SP 409 · GO 246 · PR 188"},
     "itens": [{"t": em("f7", "cidades") + .3, "txt": "Até 50 mm no dia, vento de 40 a 60 km/h e granizo"},
               {"t": em("f7", "quinta"), "txt": "Quinta (29): 2.777 cidades · SP 645 · MG 536 · PR 399"}],
     "l": "aviso do INMET · sexta (30): 2.430 cidades · é aviso, pode mudar", "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · sexta 30/10: 139,4 mm somados · Centro-Oeste 227,5 mm na semana · Goiânia 78,7 mm · Boa Vista até 39,3 °C na quinta", "borda": "rgba(251,146,60,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f9", "6.500") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM NO BRASIL · {NEST:,} PLUVIÔMETROS".replace(",", ".")},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "3.500") + .1, "dur": 1.2},
     "itens": [{"t": em("f9", "680"), "txt": "7 dias nas capitais: 686 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · a BA soma muito por ter muitos pluviômetros", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 27/10 5h a 28/10 5h · <b>INPE</b> · <b>CEMADEN</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>INPE</b>: focos de 27/10 (AQUA tarde, satélite de referência) · <b>NOAA</b>: METAR de Santarém (27/10)"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>CEMADEN</b>: pluviômetros da BA, chuva em 24 h até 28/10 5h20 · <b>INMET</b>: aviso de acumulado"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>CEMADEN</b>: pluviômetros de Formosa · <b>NOAA</b>: METAR de São José dos Campos (29 nós às 17h de 27/10)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>NOAA</b>: METAR de Teresina, Boa Vista e Santarém (27/10)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>NOAA</b>: METAR de Canoas, Santa Maria e Santo Ângelo (27/10 6h)"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: avisos amarelos de tempestade de 28/10 (1.861 municípios), 29/10 (2.777) e 30/10 (2.430) · é aviso, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (28/10 a 3/11) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST:,} pluviômetros; sem 4 sensores isolados) · previsão <b>Open-Meteo</b>: 686 mm somados nas capitais em 7 dias".replace(",", ".", 1)},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff",
         "tempestade": "#ff8c1a", "graus": "#ff2a1f", "rajada": "#ff8c1a", "kmh": "#ff8c1a", "km": "#ff8c1a",
         "fogo": "#ff2a1f", "focos": "#ff2a1f", "fumaca": "#ff8c1a", "calor": "#ff2a1f",
         "amarelo": AM,
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "para", "bahia", "goias", "formosa", "vitoria", "conquista", "santarem", "sao", "jose", "campos", "teresina", "boa", "vista",
         "canoas", "santa", "maria", "santo", "angelo", "centrooeste", "capitais", "brasil", "hoje", "quarta", "quinta", "sexta",
         "inemaclub", "cidade", "regiao", "pais", "aeroporto"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:;" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · CLIMA 24 H", "selo": "INPE · CEMADEN · INMET · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · "
      f"amarelo {TEMP} · quinta {QUI} · fogo {len(fogo)} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
