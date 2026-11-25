#!/usr/bin/env python3
"""Clima do DIA 25/11/2026. Boletim como fonte da previsão; --canto usa tempos do avatar."""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "25/11/2026"
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
        if n(palavra) == n(p["w"]) or (len(n(palavra)) > 3 and n(palavra) in n(p["w"])):
            achou += 1
            if achou == k:
                return p["t"]
    raise KeyError(f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in FALA[fid]["palavras"]))


ini = lambda fid: FALA[fid]["ini"]
fim = lambda fid: FALA[fid]["fim"]
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
LAR, AZUL = [255, 140, 26], [60, 150, 255]

# Abrangência estadual dos avisos atuais de tempestade do INMET.
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
avisos = {a["id"]: a for a in AV["hoje"]}
UFCOD = {"11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO",
         "21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL",
         "28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP","41":"PR",
         "42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF"}
municipios = set()
for aid, quantidade in [(56499, 3111), (56501, 1351)]:
    aviso = avisos[aid]
    assert aviso["descricao"] == "Tempestade" and aviso["inicio"].startswith("2026-11-25")
    codigos = set(aviso["geocodes"].split(","))
    assert len(codigos) == quantidade
    municipios.update(codigos)
assert len(municipios) == 3111
ufs = {UFCOD[c[:2]] for c in municipios}

regioes = [(-42.6,-7.6,4.25,10), (-52.5,-13,3.05,0), (-51.8,-25.2,4.7,24),
           (-49.6,-20.8,4.15,13), (-65.5,-8.7,4.0,13), (-45.4,-23,4.65,15),
           (-49.86,-28.29,5.45,27), (-64.7,-6.5,3.75,55), (-51.4,-26,4.55,20),
           (-53,-14,3.1,0), (-53,-14,3.05,0)]
camera = []
for i, (lon, lat, zoom, pitch) in enumerate(regioes, 1):
    fid = f"f{i}"
    giro = (-13, 18) if i == 8 else (-4, 6)
    entrada = 0 if i == 1 else ini(fid) + .25
    chegada = min(fim(fid) - .12, FALA[fid]["palavras"][-1]["f"] + .12)
    if i == 9:
        transicao = em(fid, "Nordeste")
        camera.extend([dict(t=entrada, lon=lon, lat=lat, zoom=zoom, pitch=pitch, bearing=-4),
                       dict(t=transicao-1.35, lon=lon, lat=lat, zoom=zoom, pitch=pitch, bearing=0),
                       dict(t=transicao+.15, lon=-43, lat=-8.5, zoom=4.1, pitch=10, bearing=4),
                       dict(t=chegada, lon=-43, lat=-8.5, zoom=4.16, pitch=10, bearing=7)])
        continue
    camera.extend([dict(t=entrada, lon=lon, lat=lat, zoom=zoom, pitch=pitch, bearing=giro[0]),
                   dict(t=chegada, lon=lon, lat=lat, zoom=zoom + .06, pitch=pitch, bearing=giro[1])])
camera.append({**camera[-1], "t": DUR})
assert all(a["t"] < b["t"] for a, b in zip(camera, camera[1:]))

from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
BONS = []
for i in range(len(TS)):
    with Image.open(AQUI / f"sat/web/ir{i:02d}.jpg") as img:
        if 90 < ImageStat.Stat(img.convert("L")).mean[0] < 130:
            BONS.append(i)
assert len(BONS) == 45

def brt(z):
    return (datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)).strftime("%d/%m %Hh%M")

SAT = dict(fundo=dict(src="sat/web/mundo.jpg", bbox=[-180,-60,180,75], tint=[170,170,175]),
           base="sat/web/geocolor-borda.png", bbox=[-76,-35,-33,7], tint=[170,170,175],
           ir=dict(frames=[f"sat/web/ir{i:02d}-borda.png" for i in BONS],
                   tempos=[brt(TS[i]) for i in BONS], ini=ini("f2"), fim=fim("f2"),
                   dur=fim("f2")-ini("f2"), alfa=.92, rotulo="GOES-19 · TOPOS FRIOS"))

telas = [dict(src="capa-dia/abertura.png", ini=0, fim=2, fade=0, zoom=0)]
estados = []
for i, estados_em_foco in [(3, ["PR", "SC"]), (4, ["MS", "GO", "MG", "SP", "RJ", "ES"]),
                          (5, ["AC", "AM", "RO"])]:
    fid = f"f{i}"
    estados.append(dict(id=f"inmet-{fid}", ini=ini(fid), fim=fim(fid), ufs=sorted(ufs.intersection(estados_em_foco)),
                        cor=LAR, alfa=.27))

# Colunas nas capitais são a previsão complementar, na janela do boletim.
om = json.loads((B / "openmeteo_capitais_3d.json").read_text())
capitais = [("Rio Branco",-67.81,-9.97), ("Porto Velho",-63.90,-8.76), ("Manaus",-60.02,-3.12)]
col = []
for nome, lon, lat in capitais:
    ponto = min(om, key=lambda d: (d["longitude"]-lon)**2 + (d["latitude"]-lat)**2)
    diaria = ponto["daily"]
    assert diaria["time"][:5] == [f"2026-11-{d}" for d in range(25,30)]
    col.append(dict(id=nome, p=[lon, lat], v=round(sum(diaria["precipitation_sum"][:5]), 1)))
colunas = [dict(id="chuva-ate-domingo", ini=ini("f8"), fim=fim("f8"), dados=col, cor=AZUL,
                escala=4800, raio=42000, varredura=.22, ordem={c["id"]:i for i,c in enumerate(col)})]

pinos = []
def pin(fid, palavra, nome, sub, lon, lat, fim_pin=None):
    pinos.append(dict(nome=nome, sub=sub, lon=lon, lat=lat, ini=em(fid, palavra), fim=fim_pin or fim(fid), h=100))

pin("f1", "Piauí", "Piauí", "HOJE · calor intenso", -42.6,-7.6)
pin("f3", "Paraná", "Oeste do Paraná", "HOJE · risco de chuva forte", -53.5,-24.55)
pin("f4", "Grosso", "Mato Grosso do Sul", "HOJE · pancadas", -54.7,-20.45, em("f4","Paulo"))
pin("f4", "Paulo", "São Paulo", "HOJE · áreas de chuva", -46.64,-23.55, em("f4","Janeiro"))
pin("f4", "Janeiro", "Rio de Janeiro", "HOJE · áreas de chuva", -43.17,-22.91)
pin("f5", "Porto", "Porto Velho", "HOJE · pode chover forte", -63.90,-8.76)
pin("f6", "Paulo", "São Paulo", "QUINTA · queda de temperatura", -46.64,-23.55, em("f6","Rio"))
pin("f6", "Rio", "Rio de Janeiro", "QUINTA · queda de temperatura", -43.17,-22.91)
pin("f7", "Joaquim", "São Joaquim", "SEXTA · chance de geada", -49.93,-28.29)
for j, c in enumerate(col):
    a = ini("f8") + .75 + j*(fim("f8")-ini("f8")-.75)/3
    b = ini("f8") + .75 + (j+1)*(fim("f8")-ini("f8")-.75)/3
    pinos.append(dict(nome=c["id"], sub=f"{c['v']:.1f} mm previstos".replace(".",","),
                      lon=c["p"][0], lat=c["p"][1], ini=a, fim=b, h=140))
pin("f9", "Paraná", "Paraná e Santa Catarina", "ATÉ DOMINGO · chuva ganha força", -51.4,-26, em("f9","Nordeste")-1.15)
pin("f9", "Nordeste", "Nordeste", "ATÉ DOMINGO · pouca chuva", -43,-8.5)

paineis = []
def painel(fid, k, linhas, inicio=None, fim_painel=None, l=MET):
    paineis.append(dict(ini=max(2, ini(fid)) if inicio is None else inicio,
                        fim=fim(fid) if fim_painel is None else fim_painel,
                        k=k, itens=[dict(t=em(fid,pal),txt=txt) for pal,txt in linhas],
                        l=l, borda="rgba(60,150,255,.8)"))

def contador(fid, palavra, ate, unid, cor="#ff8c1a"):
    paineis[-1]["contador"] = dict(de=0, ate=ate, ini=em(fid,palavra)-1, dur=1, dec=0, cor=cor, unid=unid)

painel("f1","PIAUÍ · HOJE",[])
contador("f1","40",40,"°C · PODE PASSAR DE")
painel("f2","BRASIL · HOJE",[("faixa","FAIXA DE INSTABILIDADE"),("Paraná","CENTRO-OESTE · SUL · SUDESTE")])
painel("f3","OESTE DO PARANÁ · HOJE",[("forte","RISCO DE CHUVA FORTE")])
contador("f3","20",20,"mm · PODE PASSAR DE","#5ec8ff")
painel("f4","CENTRO-OESTE E SUDESTE · HOJE",[("Sul","CHUVA EM MS"),("Paulo","SP, MG E RJ")])
painel("f5","NORTE · HOJE",[("Amazonas","PANCADAS EM AM, AC E RO"),("Porto","PORTO VELHO · CHUVA FORTE")])
painel("f6","SÃO PAULO · QUINTA",[],fim_painel=em("f6","Rio")-.35)
contador("f6","22",22,"°C · ATÉ","#96d2ff")
painel("f6","RIO DE JANEIRO · QUINTA",[],inicio=em("f6","Rio")-.35)
contador("f6","30",30,"°C · ABAIXO DE","#96d2ff")
painel("f7","SÃO JOAQUIM · SEXTA",[("geada","POSSIBILIDADE DE GEADA"),("2","MÍNIMA PREVISTA · 2 A 5 °C")])
contador("f7","5",5,"°C · ATÉ","#96d2ff")
painel("f8","OESTE DA AMAZÔNIA · ATÉ DOMINGO",[("45","FAIXAS DE 45 A 100 MM")],
       l=MET+"<br>Colunas: Open-Meteo · 25–29/11")
contador("f8","100",100,"mm · ATÉ","#5ec8ff")
painel("f9","FIM DE SEMANA",[("Paraná","PR / SC · MAIS CHUVA"),("Nordeste","NORDESTE · POUCA CHUVA")])
painel("f10","COMENTA AQUI",[("onde","DE ONDE VOCÊ É?"),("tempo","COMO ESTÁ AÍ?")])
cta = dict(ini=ini("f11"),fim=DUR,a="APRENDA IA",b="inema.club")
club = dict(ini=em("f11","inema"),fim=DUR,a="inema.club",b="aprenda sobre inteligência artificial")

fontes = [
    dict(ini=2,fim=ini("f2"),html=MET+" · máxima prevista"),
    dict(ini=ini("f2"),fim=fim("f2"),html="NOAA / GOES-19 observado · "+brt(TS[BONS[0]])+" a "+brt(TS[BONS[-1]])),
    dict(ini=ini("f3"),fim=fim("f5"),html=MET+" · cor: estados com municípios sob aviso de tempestade do INMET"),
    dict(ini=ini("f6"),fim=fim("f7"),html=MET+" · temperatura prevista"),
    dict(ini=ini("f8"),fim=fim("f8"),html=MET+" · acumulado previsto · colunas: Open-Meteo"),
    dict(ini=ini("f9"),fim=fim("f9"),html=MET+" · previsão para o fim de semana"),
]
# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "umidade": "#5ec8ff", "pancadas": "#5ec8ff", "pancadao": "#5ec8ff", "toro": "#5ec8ff",
         "frio": "#96d2ff", "amanhecer": "#96d2ff", "graus": "#ff2a1f", "granizo": "#ff2a1f", "tempestade": "#ff2a1f", "sobe": "#ff2a1f",
         "alerta": "#ff8c1a", "vento": "#ff8c1a", "calor": "#ff8c1a", "acima": "#ff2a1f", "abaixo": "#ff8c1a", "baixa": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "sao", "paulo", "minas", "brasil", "nordeste", "piaui", "serra", "curitiba", "porto", "alegre", "oeste", "paulista",
         "rio", "sertao", "maranhao", "pernambuco", "paraiba", "bahia", "amazonia", "pais", "inemaclub", "onde"}
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

C = {'layout':'canto' if CANTO else 'avatar' if AVATAR else 'cheio','padding_baixo':640 if CANTO else 820,'padding_topo':290,'duracao':DUR,
'marca':'INEMA · CLIMA DO DIA','selo':'25/11 · Meteorologia', 'camera':camera,'sat':SAT,'colunas':colunas,'telas':telas,'estados':estados,'pinos':pinos,'paineis':paineis,'cta':cta,'club':club,'fontes':fontes,'legenda':legenda}
# Ajuste local de composição: capa limpa durante os dois segundos iniciais.
# O motor compartilhado permanece intacto; --canto recebe o mesmo comportamento.
AJUSTE = """
window.addEventListener('load',()=>{const original=window.render;window.render=async function(t){await original(t);for(const id of ['topo','leg']) document.getElementById(id).style.opacity=t<2?'0':'1';};});
"""
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';'+AJUSTE)
print(f'cena.js ok · {DUR}s · {len(BONS)} quadros IR · {len(municipios)} municípios INMET · {len(col)} colunas')
