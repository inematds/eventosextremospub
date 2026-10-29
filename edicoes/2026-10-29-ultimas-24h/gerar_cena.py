#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 29/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "29/10/2026"
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
SSA = {"lon": -38.6, "lat": -11.9, "zoom": 7.0}      # Salvador (BA)
ROC = {"lon": -60.5, "lat": -12.4, "zoom": 7.0}      # Colorado do Oeste (RO)
MAC = {"lon": -43.3, "lat": -5.0, "zoom": 6.6}       # Parnarama (MA)
GOC = {"lon": -49.25, "lat": -16.6, "zoom": 7.0}     # Goiânia (GO)
PAC = {"lon": -56.5, "lat": -1.0, "zoom": 5.3}       # fogo no Pará, fumaça em Santarém e Manaus
NNE = {"lon": -49.5, "lat": -4.5, "zoom": 5.0}       # calor: Teresina, Santarém, Itaituba
CWB = {"lon": -49.3, "lat": -25.4, "zoom": 7.0}      # frio: Curitiba
HOJ = {"lon": -47.5, "lat": -14.0, "zoom": 4.6}      # alerta laranja (MG, SP, GO, RJ)
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
VOL = {"lon": -41.5, "lat": -13.0, "zoom": 5.4}      # Bahia (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, SSA, 34, -6), K(fim("f2") - .2, {**SSA, "zoom": 7.1}, 36, 4),
    K(ini("f3") + 1.0, ROC, 34, -4), K(fim("f3") - .2, {**ROC, "zoom": 7.1}, 36, 2),
    K(ini("f4") + 1.0, MAC, 34, 0), K(em("f4", "Goiânia") - .2, {**MAC, "zoom": 6.7}, 36, 2),
    K(em("f4", "Goiânia") + 1.0, GOC, 34, 0), K(fim("f4") - .2, {**GOC, "zoom": 7.1}, 36, 4),
    K(ini("f5") + 1.0, PAC, 30, -4), K(fim("f5") - .2, {**PAC, "zoom": 5.4}, 32, 2),
    K(ini("f6") + 1.0, NNE, 26, 0), K(em("f6", "Curitiba") - .2, {**NNE, "zoom": 5.1}, 28, 4),
    K(em("f6", "Curitiba") + 1.0, CWB, 30, 0), K(fim("f6") - .2, {**CWB, "zoom": 7.1}, 32, 2),
    K(ini("f7") + 1.0, HOJ, 16, 0), K(fim("f7") - .2, {**HOJ, "zoom": 4.8}, 18, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f9") + 1.0, VOL, 10, 0), K(fim("f9") - .2, {**VOL, "zoom": 5.5}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-28T08") and TS[-1].startswith("2026-10-29T08"), (TS[0], TS[-1])
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

# ---------------------------------------------------------------- INPE: focos de 28/10 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
# o CSV de 29/10 é parcial (0 focos AQUA): não usado
grade, ref, ref_uf, ref_mun = {}, 0, {}, {}
with open(B / "inpe_focos_diario_br_20261028.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-28"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
            if uf == "PARÁ":
                ref_mun[r["municipio"].strip()] = ref_mun.get(r["municipio"].strip(), 0) + 1
assert (ref, ref_uf["PARÁ"]) == (502, 257), (ref, ref_uf["PARÁ"])          # "257 dos 502 focos"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["PARÁ", "RORAIMA", "AMAZONAS", "CEARÁ", "PERNAMBUCO"], RKF
assert (ref_mun["PLACAS"], ref_mun["SANTARÉM"]) == (33, 29), ref_mun
SIGLA = {"PARÁ": "PA", "RORAIMA": "RR", "AMAZONAS": "AM", "CEARÁ": "CE", "PERNAMBUCO": "PE"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f5"), "fim": ini("f6") + .3, "dados": fogo, "dur": 2.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET (hoje: laranja de chuvas intensas)
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
assert {a["severidade"] for a in aviso.values()} == {"Perigo Potencial", "Perigo"}, "apareceu vermelho: rever a fala f7"
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
conta = lambda i, ufs: [sum(UF[c[:2]] == u for c in geo(i)) for u in ufs]
# laranja hoje 29/10: 56207 (918: MG 352, SP 342, GO 160, RJ 43 …), 50 a 100 mm/dia, vento 60 a 100 km/h; inclui Goiânia e São Paulo
assert aviso[56207]["descricao"] == "Chuvas Intensas" and aviso[56207]["severidade"] == "Perigo" and aviso[56207]["inicio"].startswith("2026-10-29")
LAR_N = len(geo(56207))
assert LAR_N == 918 and conta(56207, ["MG", "SP", "GO", "RJ"]) == [352, 342, 160, 43], LAR_N
RISCO = " ".join(aviso[56207]["riscos"])
assert "50 e 100 mm/dia" in RISCO and "30 e 60 mm/h" in RISCO and "60-100 km/h" in RISCO
assert {"5208707", "3550308"} <= {c[:7] for c in geo(56207)}        # Goiânia e São Paulo
LARU = ufs_av(56207, 40)
# amarelo hoje 29/10: 56206 (2.338)
assert aviso[56206]["severidade"] == "Perigo Potencial" and aviso[56206]["inicio"].startswith("2026-10-29")
AMA_N = len(geo(56206))
assert AMA_N == 2338, AMA_N
AMAU = ufs_av(56206, 40)
# sexta 30/10: dois amarelos (56209: 1.670; 56210: 945), com sobreposição: não somar
assert len(geo(56209)) == 1670 and len(geo(56210)) == 945 and aviso[56210]["inicio"].startswith("2026-10-30")
assert len(geo(56196)) == 116 and aviso[56196]["descricao"] == "Acumulado de Chuva" and "2927408" in {c[:7] for c in geo(56196)}   # Salvador
estados = [
    {"id": "f1", "ini": CAPA, "fim": ini("f2") + .3, "ufs": LARU, "cor": LAR, "alfa": .4},
    {"id": "f1ba", "ini": em("f1", "Salvador"), "fim": ini("f2") + .3, "ufs": ["BA"], "cor": AZU, "alfa": .4},
    {"id": "ba", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["BA"], "cor": AZU, "alfa": .35},
    {"id": "ro", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["RO"], "cor": AZU, "alfa": .35},
    {"id": "ma", "ini": ini("f4"), "fim": em("f4", "Goiânia") + .3, "ufs": ["MA"], "cor": AZU, "alfa": .35},
    {"id": "go", "ini": em("f4", "Goiânia"), "fim": ini("f5") + .3, "ufs": ["GO"], "cor": AZU, "alfa": .35},
    {"id": "pa", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["PA"], "cor": LAR, "alfa": .35},
    {"id": "calor", "ini": ini("f6"), "fim": em("f6", "Curitiba") + .3, "ufs": ["PI", "PA"], "cor": VERM, "alfa": .35},
    {"id": "frio", "ini": em("f6", "Curitiba"), "fim": ini("f7") + .3, "ufs": ["PR"], "cor": AZC, "alfa": .4},
    {"id": "laranja", "ini": ini("f7"), "fim": em("f7", "amarelo") + .3, "ufs": LARU, "cor": LAR, "alfa": .45},
    {"id": "amarelo", "ini": em("f7", "amarelo"), "fim": ini("f8") + .3, "ufs": AMAU, "cor": AMA, "alfa": .35},
    {"id": "volba", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["BA"], "cor": AZU, "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
CRU = {(e["uf"], e["cidade"], e["nomeestacao"]): e for e in json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())}
acc = lambda u, c, e, k="acc24hr": CRU[(u, c, e)][k]
SSA3 = [acc("BA", "SALVADOR", e) for e in ("Matatu", "Federação", "Engenho Velho de Brotas")]
assert SSA3 == [58.89, 58.35, 58.2] and min(SSA3) > 58, SSA3                                          # "3 pluviômetros passaram de 58"
assert acc("BA", "SALVADOR", "Centro") == 45.27
COL = sorted((acc("RO", "COLORADO DO OESTE", f"G2-11000640{i}A") for i in (1, 2, 3)), reverse=True)
assert COL == [81.6, 70.4, 68.2], COL                                                                  # "de 68 a quase 82"
assert acc("MA", "PARNARAMA", "Prefeitura Municipal") == 50 and acc("MA", "PARNARAMA", "Prefeitura Municipal", "acc3hr") == 50   # "50 em 3 horas"
assert acc("MA", "BURITI BRAVO", "G2-210230903A") == 59 and acc("MA", "BURITI BRAVO", "G2-210230903A", "acc3hr") == 31.2
assert acc("GO", "GOIÂNIA", "Jardim Curitiba") == 53.6 and acc("GO", "GOIÂNIA", "Vila Jardim Pompeia") == 42.2   # "passou de 53"
# sensores isolados (vizinhos secos ou sem leitura), fora das somas e da fala
DESC = {("MG", "VISCONDE DO RIO BRANCO", "Rio Xopoto"): 121.6, ("SP", "SERTÃOZINHO", "G2-355170202A"): 83.2}
assert {k: acc(*k) for k in DESC} == DESC
assert acc("MG", "VISCONDE DO RIO BRANCO", "Centro") == "-" and acc("MG", "SENADOR FIRMINO", "G2-316570101A") == 0.2
assert acc("SP", "SERTÃOZINHO", "G2-355170205A") == 0.4 and acc("SP", "SERTÃOZINHO", "G2-355170204A") == 0.6
SOMA = CM["soma_por_uf"]
assert CM["soma_mm_estacoes"] == 6180.0 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 6180.0) < .5
NEST = sum(d["estacoes"] for d in SOMA.values()) - len(DESC)
SEMV = {u: d["soma_mm"] - sum(v for k, v in DESC.items() if k[0] == u) for u, d in SOMA.items()}
BRASIL = sum(SEMV.values())
assert 5900 < BRASIL < 6000, BRASIL                            # "quase 6.000" sem os 2 sensores (5.975,4)
assert 1600 < SEMV["BA"] < 1700, SEMV["BA"]                    # "mais de 1.600 na Bahia"
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["BA", "MA", "GO", "SP", "RO"], RK

# ---------------------------------------------------------------- NOAA METAR: chuva forte em Salvador, fumaça, calor, frio
MT = json.loads((B / "noaa_metar_brasil_24h.json").read_text())
SV = [o for o in MT if o["icaoId"] == "SBSV" and " 1000 " in o["rawOb"] and "+RA" in o["rawOb"]]
assert len(SV) == 1 and SV[0]["reportTime"].startswith("2026-10-28T12:06"), [o["rawOb"] for o in SV]   # "1 km" às 9h06
assert any(o["icaoId"] == "SBSN" and " 3000 FU " in o["rawOb"] and o["reportTime"].startswith("2026-10-28T12") for o in MT)   # Santarém 3 km às 9h
assert any(o["icaoId"] == "SBEG" and " 4000 FU " in o["rawOb"] for o in MT)                                                   # Manaus 4 km
for icao in ("SBTE", "SBSN", "SBIH"):
    o = max((o for o in MT if o["icaoId"] == icao and o.get("temp") is not None), key=lambda o: o["temp"])
    assert o["temp"] == 38 and o["reportTime"].startswith("2026-10-28"), o["rawOb"]                   # "38 graus"
CT = [o for o in MT if o["icaoId"] == "SBCT" and o.get("temp") is not None]
assert min(o["temp"] for o in CT) == 12 and any(o["temp"] == 12 and o["reportTime"].startswith("2026-10-28T08:00") for o in CT)   # "12 graus" às 5h

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-29" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qui", "sex", "sáb", "dom", "seg", "ter", "qua"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 750.7   # "mais de 750"
TOP = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP["dia"], TOP["soma_chuva_mm"]) == ("2026-10-30", 143.3), TOP                                          # "sexta"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "SE" and P7["soma_7d_por_regiao_mm"]["SE"] == 236.9
assert P7["acumulado_7d_top"][0] == ["Belo Horizonte", 107.6]                                                    # "BH passa de 100"
PICO = max(P7["por_dia"], key=lambda d: d["tmax_pico"][0])
assert PICO["tmax_pico"] == [39.9, "Teresina"] and PICO["dia"] == "2026-11-04"                                   # "perto de 40 graus"

pinos = [
    {"nome": "Salvador (BA)", "sub": "3 pluviômetros acima de 58 mm", "lon": -38.50, "lat": -12.97, "ini": em("f2", "Salvador"), "fim": ini("f3"), "h": 40},
    {"nome": "Colorado do Oeste (RO)", "sub": "68 a 81,6 mm em 24 h", "lon": -60.55, "lat": -13.12, "ini": em("f3", "Colorado"), "fim": ini("f4"), "h": 40},
    {"nome": "Parnarama (MA)", "sub": "50 mm em 3 h", "lon": -43.10, "lat": -5.68, "ini": em("f4", "Parnarama"), "fim": em("f4", "Goiânia"), "h": 40},
    {"nome": "Goiânia (GO)", "sub": "53,6 mm", "lon": -49.25, "lat": -16.68, "ini": em("f4", "Goiânia"), "fim": ini("f5"), "h": 40},
    {"nome": "Santarém (PA)", "sub": "fumaça · 3 km de visibilidade", "lon": -54.71, "lat": -2.44, "ini": em("f5", "Santarém"), "fim": ini("f6"), "h": 60},
    {"nome": "Manaus (AM)", "sub": "fumaça · 4 km de visibilidade", "lon": -60.02, "lat": -3.12, "ini": em("f5", "Manaus"), "fim": ini("f6"), "h": 30},
    {"nome": "Placas (PA)", "sub": f"{ref_mun['PLACAS']} focos", "lon": -54.21, "lat": -3.87, "ini": em("f5", "257") + .4, "fim": ini("f6"), "h": 20},
    {"nome": "Teresina (PI)", "sub": "38 °C", "lon": -42.80, "lat": -5.09, "ini": em("f6", "Teresina"), "fim": em("f6", "Curitiba"), "h": 40},
    {"nome": "Santarém (PA)", "sub": "38 °C", "lon": -54.71, "lat": -2.44, "ini": em("f6", "Santarém"), "fim": em("f6", "Curitiba"), "h": 60},
    {"nome": "Itaituba (PA)", "sub": "38 °C", "lon": -55.98, "lat": -4.28, "ini": em("f6", "Itaituba"), "fim": em("f6", "Curitiba"), "h": 20},
    {"nome": "Curitiba (PR)", "sub": "12 °C às 5h", "lon": -49.27, "lat": -25.43, "ini": em("f6", "Curitiba"), "fim": ini("f7"), "h": 40},
    {"nome": "Goiânia (GO)", "sub": "alerta laranja", "lon": -49.25, "lat": -16.68, "ini": em("f7", "laranja") + .3, "fim": em("f7", "amarelo"), "h": 15},
    {"nome": "São Paulo (SP)", "sub": "alerta laranja", "lon": -46.63, "lat": -23.55, "ini": em("f7", "laranja") + .6, "fim": em("f7", "amarelo"), "h": 40},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🟠 Alerta laranja em 918 cidades · 🌧️ Salvador: quase 60 mm</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "SALVADOR · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 58.9, "dec": 1, "ini": em("f2", "58") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM NO PLUVIÔMETRO DO MATATU"},
     "itens": [{"t": em("f2", "58") + .3, "txt": "Matatu 58,9 · Federação 58,4 · Engenho Velho de Brotas 58,2 · Centro 45,3 mm"},
               {"t": em("f2", "aeroporto"), "txt": "Aeroporto de Salvador: chuva forte e 1 km de visibilidade às 9h de quarta"}],
     "l": "CEMADEN, leituras até 29/10 5h20 · aeroporto (METAR)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "RONDÔNIA · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 81.6, "dec": 1, "ini": em("f3", "82") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM COLORADO DO OESTE (RO)"},
     "itens": [{"t": em("f3", "82") + .3, "txt": "Os 3 pluviômetros da cidade: 81,6 · 70,4 · 68,2 mm"}],
     "l": "CEMADEN, leituras até 29/10 5h10", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "MARANHÃO E GOIÁS · CHUVA FORTE",
     "contador": {"de": 0, "ate": 50, "dec": 0, "ini": em("f4", "50") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM 3 H EM PARNARAMA (MA)"},
     "itens": [{"t": em("f4", "horas"), "txt": "Buriti Bravo (MA): 59 mm, 31,2 em 3 h"},
               {"t": em("f4", "Goiânia"), "txt": "Goiânia (GO): 53,6 mm no Jardim Curitiba, 42,2 no Jardim Pompeia"}],
     "l": "CEMADEN, leituras até 29/10 5h20", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "PARÁ · FOGO EM 28/10",
     "contador": {"de": 0, "ate": ref_uf["PARÁ"], "dec": 0, "ini": em("f5", "257") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": f"FOCOS NO PARÁ · DE {ref} NO BRASIL"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f5", "502") + .3, "dur": 1.2},
     "itens": [{"t": em("f5", "Santarém"), "txt": "Fumaça: Santarém com 3 km de visibilidade · Manaus com 4 km"}],
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência (INPE)", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "CALOR E FRIO · QUARTA, 28/10",
     "contador": {"de": 0, "ate": 38, "dec": 0, "ini": em("f6", "38") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "°C EM TERESINA, SANTARÉM E ITAITUBA"},
     "itens": [{"t": em("f6", "Curitiba"), "txt": "Curitiba (PR): 12 °C às 5h"}],
     "l": "temperatura nos aeroportos (METAR)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA LARANJA DE CHUVAS INTENSAS",
     "contador": {"de": 0, "ate": LAR_N, "dec": 0, "ini": em("f7", "918") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES · MG 352 · SP 342 · GO 160 · RJ 43"},
     "itens": [{"t": em("f7", "dia"), "txt": "50 a 100 mm no dia ou 30 a 60 mm por hora"},
               {"t": em("f7", "km/h"), "txt": "Vento de 60 a 100 km/h · Goiânia e São Paulo no laranja"},
               {"t": em("f7", "amarelo"), "txt": "Amarelo: 2.338 cidades · sexta (30): amarelo de MG ao RS"}],
     "l": "aviso do INMET · é aviso, pode mudar", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · sexta 30/10: 143,3 mm somados · Sudeste 236,9 mm na semana · Belo Horizonte 107,6 mm · Teresina até 39,9 °C em 4/11", "borda": "rgba(244,114,182,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f9", "6.000") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM NO BRASIL · {NEST:,} PLUVIÔMETROS".replace(",", ".")},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "1.600") + .1, "dur": 1.2},
     "itens": [{"t": em("f9", "750"), "txt": "7 dias nas capitais: 750,7 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · a BA soma muito por ter muitos pluviômetros", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 28/10 5h a 29/10 5h · <b>INMET</b> · <b>CEMADEN</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>CEMADEN</b>: pluviômetros de Salvador, chuva em 24 h até 29/10 5h20 · <b>NOAA</b>: METAR do aeroporto (28/10 9h06)"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>CEMADEN</b>: pluviômetros de Colorado do Oeste (RO), chuva em 24 h até 29/10"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>CEMADEN</b>: pluviômetros de Parnarama, Buriti Bravo (MA) e Goiânia (GO)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INPE</b>: focos de 28/10 (AQUA tarde, satélite de referência) · <b>NOAA</b>: METAR de Santarém e Manaus (28/10)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>NOAA</b>: METAR de Teresina, Santarém, Itaituba e Curitiba (28/10)"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: aviso laranja de chuvas intensas de 29/10 (918 municípios) e amarelo (2.338) · é aviso, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (29/10 a 4/11) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST:,} pluviômetros; sem 2 sensores isolados) · previsão <b>Open-Meteo</b>: 750,7 mm somados nas capitais em 7 dias".replace(",", ".", 1)},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff",
         "laranja": "#ff8c1a", "vento": "#ff8c1a", "kmh": "#ff8c1a", "km": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "fumaca": "#ff8c1a", "calor": "#ff2a1f",
         "amarelo": AM,
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"salvador", "aeroporto", "rondonia", "colorado", "oeste", "maranhao", "parnarama", "goiania", "para", "santarem", "manaus",
         "teresina", "itaituba", "curitiba", "sudeste", "belo", "horizonte", "bahia", "capitais", "brasil", "hoje", "quinta", "sexta",
         "inemaclub", "cidade", "regiao", "cidades"}
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
     "marca": "INEMA · CLIMA 24 H", "selo": "INMET · CEMADEN · INPE · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · "
      f"laranja {LARU} · amarelo {AMAU} · fogo {len(fogo)} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
