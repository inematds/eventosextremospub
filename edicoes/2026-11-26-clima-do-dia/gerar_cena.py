#!/usr/bin/env python3
"""Clima do DIA 26/11/2026. Boletim como fonte da previsão; --canto usa tempos do avatar."""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "26/11/2026"
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

# Chuvas intensas do INMET em 26/11. O mapa pinta estados com municípios sob aviso.
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
avisos = {a["id"]: a for a in AV["hoje"]}
UFCOD = {"11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO",
         "21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL",
         "28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP","41":"PR",
         "42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF"}
codigos = {}
for aid, quantidade in [(56508, 2219), (56510, 738)]:
    aviso = avisos[aid]
    assert aviso["descricao"] == "Chuvas Intensas"
    assert aviso["inicio"].startswith("2026-11-26")
    codigos[aid] = set(aviso["geocodes"].split(","))
    assert len(codigos[aid]) == quantidade
municipios = codigos[56508] | codigos[56510]
assert len(municipios) == 2219
ufs = {UFCOD[c[:2]] for c in municipios}
ufs_perigo = {UFCOD[c[:2]] for c in codigos[56510]}

# A câmera chega antes do assunto e faz o movimento principal dentro de cada fala.
regioes = [
    (-42.2, -21.5, 4.05, 0), (-53.9, -14.0, 3.55, 0),
    (-44.7, -22.15, 4.65, 8), (-59.0, -10.8, 3.72, 6),
    (-42.6, -8.3, 4.0, 6), (-51.3, -29.9, 4.60, 10),
    (-47.6, -23.5, 4.48, 10), (-43.35, -21.75, 5.18, 54),
    (-52.4, -14.3, 3.04, 0), (-52.4, -14.3, 3.04, 0),
    (-52.4, -14.3, 3.04, 0),
]
camera = []

def chave(t, loc, bearing, zoom_extra=0):
    lon, lat, zoom, pitch = loc
    camera.append(dict(t=t, lon=lon, lat=lat, zoom=zoom + zoom_extra, pitch=pitch, bearing=bearing))

def fim_mapa(fid):
    return min(fim(fid) - .1, FALA[fid]["palavras"][-1]["f"] + .1)

for i, loc in enumerate(regioes, 1):
    fid = f"f{i}"
    inicio = 0 if i == 1 else ini(fid) + .16
    ultima = max(inicio + .25, fim_mapa(fid) - .5)
    giro0, giro1 = (-14, 16) if i == 8 else (-2, 4)
    chave(inicio, loc, giro0)
    if i == 6:
        mudar = em(fid, "sexta")
        chave(max(inicio + .1, mudar - .55), loc, giro1)
        chave(ultima, (-50.8, -28.75, 4.6, 10), giro1)
    elif i == 8:
        mudar = em(fid, "domingo", 2)
        depois = (-43.40, -22.70, 4.75, 13)
        chave(max(inicio + .1, mudar - .2), loc, giro1, .06)
        chave(max(mudar + .35, ultima), depois, 5)
    else:
        chave(ultima, loc, giro1, .07 if i < 10 else 0)
chave(DUR, regioes[-1], 4)
assert all(a["t"] < b["t"] for a, b in zip(camera, camera[1:]))

from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
BONS = []
for i in range(len(TS)):
    with Image.open(AQUI / f"sat/web/ir{i:02d}.jpg") as img:
        if 90 < ImageStat.Stat(img.convert("L")).mean[0] < 130:
            BONS.append(i)
assert len(BONS) == 48 and 40 not in BONS

def brt(z):
    return (datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)).strftime("%d/%m %Hh%M")

IR_JANELA = f"{brt(TS[BONS[0]])} a {brt(TS[BONS[-1]])} (Brasília)"
SAT = dict(fundo=dict(src="sat/web/mundo.jpg", bbox=[-180,-60,180,75], tint=[170,170,175]),
           base="sat/web/geocolor-borda.png", bbox=[-76,-35,-33,7], tint=[170,170,175],
           ir=dict(frames=[f"sat/web/ir{i:02d}-borda.png" for i in BONS],
                   tempos=[brt(TS[i]) for i in BONS], ini=ini("f2"), fim=fim("f2"),
                   dur=fim("f2")-ini("f2"), alfa=.92, rotulo="GOES-19 · INFRAVERMELHO"))

CORTE_CAPA = 2
telas = [
    dict(src="capa-dia/abertura.png", ini=0, fim=CORTE_CAPA, fade=0, zoom=0),
    dict(src="capa-dia/granizo.png", ini=em("f7", "granizo"), fim=fim("f7"),
         fade=0, zoom=.035, selo="ILUSTRAÇÃO"),
]
estados = [
    dict(id="inmet-potencial", ini=CORTE_CAPA, fim=fim("f3"), ufs=sorted(ufs),
         cor=[241, 199, 44], alfa=.24),
    dict(id="inmet-perigo", ini=CORTE_CAPA, fim=fim("f3"), ufs=sorted(ufs_perigo),
         cor=LAR, alfa=.34),
    dict(id="norte-oeste", ini=ini("f4"), fim=fim("f4"), ufs=["AC","AM","RO","MT"],
         cor=AZUL, alfa=.31),
    dict(id="calor", ini=ini("f5"), fim=fim("f5"), ufs=["PI"], cor=LAR, alfa=.34),
    dict(id="sul-frio", ini=ini("f6"), fim=fim("f6"), ufs=["RS","SC"],
         cor=AZUL, alfa=.29),
    dict(id="sabado", ini=ini("f7"), fim=em("f7","granizo"), ufs=["SP","SC"],
         cor=AZUL, alfa=.31),
    dict(id="chuva-brasil", ini=ini("f9"), fim=fim("f9"),
         ufs=["AC","AM","RO","MT","MS","GO","MG","SP","RJ","ES","PR","SC","RS"],
         cor=AZUL, alfa=.18),
    dict(id="tendencia-sudeste", ini=ini("f9"), fim=fim("f9"), ufs=["MG","RJ"],
         cor=AZUL, alfa=.51),
]

# Complemento quantitativo: pontos da grade nas capitais, acumulado de quinta a domingo.
om = json.loads((B / "openmeteo_capitais_3d.json").read_text())
capitais = [("São Paulo",-46.64,-23.55), ("Belo Horizonte",-43.94,-19.92),
            ("Rio de Janeiro",-43.17,-22.91), ("Vitória",-40.31,-20.32)]
col = []
for nome, lon, lat in capitais:
    ponto = min(om, key=lambda d: (d["longitude"]-lon)**2 + (d["latitude"]-lat)**2)
    diaria = ponto["daily"]
    assert diaria["time"][:4] == [f"2026-11-{d}" for d in range(26,30)]
    col.append(dict(id=nome, p=[lon, lat], v=round(sum(diaria["precipitation_sum"][:4]), 1),
                    cor=[94, 200, 255] if nome != "Vitória" else [250, 204, 21]))
assert col[-1]["v"] == 74
rio_dom = em("f8", "domingo", 2)
OM = "Open-Meteo · previsão de 26 a 29/11"
colunas = [dict(id="chuva-ate-domingo", ini=ini("f8"), fim=rio_dom, dados=col, cor=AZUL,
                escala=4100, raio=29000, varredura=.2, ordem={c["id"]:i for i,c in enumerate(col)})]

pinos = []
def pin(fid, palavra, nome, sub, lon, lat, fim_pin=None, h=78):
    instante = em(fid, palavra)
    fim_pin = fim(fid) if fim_pin is None else fim_pin
    assert instante < fim_pin
    pinos.append(dict(nome=nome, sub=sub, lon=lon, lat=lat, ini=instante, fim=fim_pin, h=h))

pin("f1", "Rio", "Rio de Janeiro", "RISCO DE CHUVA FORTE", -43.17,-22.91, em("f1","capixaba"))
pin("f1", "capixaba", "Sul capixaba", "RISCO DE CHUVA FORTE", -41.11,-20.85)
pin("f3", "Serrana", "Região Serrana", "RIO DE JANEIRO", -43.00,-22.36, em("f3","Minas"))
pin("f3", "Minas", "Centro-sul de Minas", "PANCADAS", -44.18,-21.27, em("f3","litoral"))
pin("f3", "litoral", "Litoral paulista", "PANCADAS", -46.33,-23.96)
pin("f4", "oeste", "Oeste do Amazonas", "TROVOADAS", -68.0,-6.0, em("f4","Rondônia"))
pin("f4", "Rondônia", "Rondônia", "TROVOADAS", -63.9,-8.76, em("f4","Mato"))
pin("f4", "Mato", "Mato Grosso", "CHUVA OBSERVADA", -56.1,-12.65)
pin("f5", "Piauí", "Piauí", "MÁXIMA PREVISTA", -42.6,-8.3)
pin("f6", "Pinheiro", "Pinheiro Machado", "RS · MÍNIMA OBSERVADA", -53.38,-31.58, em("f6","sexta"))
pin("f6", "gear", "Serra do Sul", "TOPO DA SERRA · SEXTA", -50.33,-28.25)
pin("f7", "Paulo", "São Paulo", "SÁBADO · CHUVA FORTE", -46.64,-23.55, em("f7","Santa"))
pin("f7", "Catarina", "Santa Catarina", "RISCO LOCALIZADO", -50.9,-27.05, em("f7","granizo"))
pin("f8", "74", "Vitória", "74 mm previstos", -40.31,-20.32, rio_dom)
pin("f8", "Grande", "Grande Rio", "DOMINGO · CHUVA FORTE", -43.25,-22.79)
pin("f9", "Minas", "Minas Gerais", "TENDÊNCIA DE MUITA CHUVA", -44.1,-19.2, em("f9","serra"))
pin("f9", "serra", "Serra fluminense", "TENDÊNCIA DE MUITA CHUVA", -43.0,-22.35)

paineis = []
def painel(fid, k, linhas, inicio=None, fim_painel=None, l=MET):
    paineis.append(dict(ini=max(CORTE_CAPA, ini(fid)) if inicio is None else inicio,
                        fim=fim(fid) if fim_painel is None else fim_painel,
                        k=k, itens=[dict(t=em(fid,pal),txt=txt) for pal,txt in linhas],
                        l=l, borda="rgba(60,150,255,.8)"))

def contador(fid, palavra, ate, unid, cor="#ff8c1a"):
    paineis[-1]["contador"] = dict(de=0, ate=ate, ini=em(fid,palavra)-1, dur=1, dec=0, cor=cor, unid=unid)

painel("f1","SUDESTE · QUINTA",[("forte","CHUVA FORTE"),("Rio","RIO E SUL CAPIXABA")])
painel("f2","BRASIL · QUINTA",[("instabilidade","FAIXA DE INSTABILIDADE"),("pancadas","CENTRO-OESTE AO SUDESTE")])
painel("f3","SUDESTE · QUINTA",[("Serrana","ATENÇÃO NA SERRA"),("Minas","PANCADAS EM MG E SP")])
painel("f4","NORTE E CENTRO-OESTE",[("trovoada","TROVOADAS NA AMAZÔNIA")],fim_painel=em("f4","Mato"))
painel("f4","MATO GROSSO · MANHÃ",[],inicio=em("f4","Mato"))
contador("f4","50",50,"mm · ACIMA DE","#5ec8ff")
painel("f5","NORDESTE · QUINTA",[("chove","POUCA CHUVA")],fim_painel=em("f5","Piauí"))
painel("f5","PIAUÍ · QUINTA",[],inicio=em("f5","Piauí"))
contador("f5","40",40,"°C · PODE PASSAR")
painel("f6","PINHEIRO MACHADO · RS",[],fim_painel=em("f6","sexta"))
contador("f6","4",4,"°C · REGISTRADOS","#96d2ff")
painel("f6","TOPO DA SERRA · SEXTA",[("gear","RISCO DE GEADA"),("topo","2 A 5 °C PREVISTOS")],inicio=em("f6","sexta"))
painel("f7","SÁBADO",[("Paulo","CHUVA FORTE EM SP"),("granizo","GRANIZO PONTUAL EM SC")])
painel("f8","VITÓRIA · ATÉ DOMINGO",[("modelo","ACUMULADO PREVISTO")],fim_painel=rio_dom,l=OM)
contador("f8","74",74,"mm","#5ec8ff")
painel("f8","GRANDE RIO · DOMINGO",[("forte","CHUVA PODE VOLTAR FORTE")],inicio=rio_dom)
painel("f9","BRASIL · TENDÊNCIA",[("chuva","ATENÇÃO À CHUVA"),("Minas","MINAS E SERRA FLUMINENSE")],fim_painel=fim_mapa("f9")+.55)
painel("f10","COMENTA AQUI",[("onde","DE ONDE VOCÊ É?"),("tempo","COMO ESTÁ AÍ?")])
cta = dict(ini=ini("f11"),fim=DUR,a="APRENDA IA",b="inema.club")
club = dict(ini=em("f11","inema"),fim=DUR,a="inema.club",b="aprenda sobre inteligência artificial")

INMET = "INMET · municípios sob aviso de chuvas intensas, por estado"
fontes = [
    dict(ini=CORTE_CAPA,fim=ini("f2"),html=MET+"<br>"+INMET),
    dict(ini=ini("f2"),fim=fim("f2"),html="NOAA / GOES-19 observado · "+IR_JANELA+"<br>"+INMET),
    dict(ini=ini("f3"),fim=fim("f3"),html=MET+"<br>"+INMET),
    dict(ini=ini("f4"),fim=fim("f7"),html=MET),
    dict(ini=ini("f8"),fim=rio_dom,html=OM+" · acumulados previstos por ponto"),
    dict(ini=rio_dom,fim=fim("f8"),html=MET+" · previsão de domingo"),
    dict(ini=ini("f9"),fim=fim_mapa("f9")+.55,html=MET+" · tendência para os próximos dias"),
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
'marca':'INEMA · CLIMA DO DIA','selo':'26/11 · Meteorologia', 'camera':camera,'sat':SAT,'colunas':colunas,'telas':telas,'estados':estados,'pinos':pinos,'paineis':paineis,'cta':cta,'club':club,'fontes':fontes,'legenda':legenda}
# Ajuste local de composição: capa limpa durante os dois segundos iniciais.
# O motor compartilhado permanece intacto; --canto recebe o mesmo comportamento.
AJUSTE = """
window.addEventListener('load',()=>{const original=window.render;window.render=async function(t){await original(t);for(const id of ['topo','leg']) document.getElementById(id).style.opacity=t<2?'0':'1';};});
"""
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';'+AJUSTE)
print(f'cena.js ok · {DUR}s · {len(BONS)} quadros IR · {len(municipios)} municípios INMET · {len(col)} colunas')
