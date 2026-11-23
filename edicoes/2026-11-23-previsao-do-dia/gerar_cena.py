#!/usr/bin/env python3
"""Previsão do Dia 23/11/2026. Gera cena.js; --canto usa avatar/tempos.json.
Fontes e rastreabilidade em pesquisa/boletim.md. TEMPOS=tempos.json permite validar --canto antes do avatar."""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "23/11/2026"
MET = "Meteorologia · " + DATA
OM = "<b>Open-Meteo</b>, previsão nas capitais"
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
LAR, AMA, VERM, AZUL, FRIO = [255, 140, 26], [250, 204, 21], [255, 42, 31], [60, 150, 255], [150, 210, 255]

# Câmeras por região e por dia da previsão.
K=lambda t,r,pitch=0,bearing=0: {"t":t,**r,"pitch":pitch,"bearing":bearing}
SUL={"lon":-52.5,"lat":-27.4,"zoom":5.8}
SC={"lon":-52.3,"lat":-27.0,"zoom":6.15}
PR={"lon":-53.0,"lat":-25.5,"zoom":6.0}
BR={"lon":-51,"lat":-19,"zoom":4.5}
ES={"lon":-42,"lat":-20,"zoom":5.1}
CAPA=2.2

camera=[K(0,SUL,55,-15),K(CAPA,SUL,55,-15)]
for fid,r,p,b in [("f1",SUL,55,-15),("f2",SUL,15,-8),("f3",PR,15,-8),("f4",BR,0,0),("f5",SC,20,-10),("f6",BR,0,0),("f7",SUL,20,-10),("f8",SUL,55,-15),("f9",SUL,15,0),("f10",BR,0,0),("f11",BR,0,0)]:
 if fid!="f1":camera.append(K(ini(fid)+.7,r,p,b))
 camera.append(K(fim(fid)-.1,r,p,b+18 if p else b))
camera.sort(key=lambda x:x["t"])
assert all(a["t"]<b["t"] for a,b in zip(camera,camera[1:]))
from PIL import Image,ImageStat
TS=json.loads((AQUI/"sat/web/ir_tempos.json").read_text())
luz=lambda i:ImageStat.Stat(Image.open(AQUI/f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS=[i for i in range(len(TS)) if 90<luz(i)<130]
assert len(BONS)>=20,BONS
def brt(z):
 d=datetime.strptime(z,"%Y-%m-%dT%H:%M:%SZ")-timedelta(hours=3)
 return f"{d:%d/%m %Hh%M}"
IR_DE,IR_ATE=brt(TS[BONS[0]]),brt(TS[BONS[-1]])
SAT={"fundo":{"src":"sat/web/mundo.jpg","bbox":[-180,-60,180,75],"tint":[170,170,175]},
 "base":"sat/web/geocolor-borda.png","bbox":[-76,-35,-33,7],"tint":[170,170,175],
 "ir":{"frames":[f"sat/web/ir{i:02d}-borda.png" for i in BONS],"tempos":[brt(TS[i]) for i in BONS],"ini":ini("f2"),"fim":fim("f2"),"dur":fim("f2")-ini("f2"),"alfa":.9,"rotulo":"GOES-19 · IR observado"}}
imagens=[]
rios=[]
# Colunas são referências do intervalo REGIONAL, não previsão municipal.
colunas=[{"id":"limiar-domingo","ini":CAPA,"fim":fim("f1"),"cor":AZUL,"escala":1100,"raio":24000,"varredura":0,"dados":[{"id":"limiar","p":[-53.2,-27.0],"v":200}]},
 {"id":"intervalo-quinta","ini":ini("f8"),"fim":fim("f8"),"cor":AZUL,"escala":1100,"raio":18000,"varredura":0,"dados":[{"id":"a","p":[-53.5,-27.5],"v":100},{"id":"b","p":[-52.8,-26.5],"v":150}]}]
telas=[{"src":"capa-dia/abertura.png","ini":0,"fim":CAPA,"fade":0,"zoom":.015,"selo":"ilustração · previsão"}]
UF={"11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO","21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL","28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP","41":"PR","42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF"}
AV=json.loads((B/"inmet_avisos_ativos.json").read_text())
aviso={int(a["id"]):a for a in AV["hoje"]}
geo=lambda i:set(filter(None,aviso[i]["geocodes"].split(",")))
assert len(geo(56484))==356
assert len(geo(56489))==1767
assert aviso[56484]["inicio"].startswith("2026-11-23") and aviso[56484]["severidade"]=="Perigo"
assert aviso[56489]["fim"].startswith("2026-11-23")
estados=[{"id":"laranja-sul","ini":ini("f3"),"fim":fim("f3"),"ufs":sorted({UF[c[:2]] for c in geo(56484)}),"cor":LAR,"alfa":.22},
 {"id":"amarelo-brasil","ini":ini("f4"),"fim":fim("f4"),"ufs":sorted({UF[c[:2]] for c in geo(56489)}),"cor":AMA,"alfa":.18}]
def pin(nome,sub,lon,lat,fid,h=40):
 return {"nome":nome,"sub":sub,"lon":lon,"lat":lat,"ini":ini(fid)+.8,"fim":fim(fid),"h":h}
pinos=[pin("Oeste do Sul","acumulado regional · até 29/11",-53.2,-27,"f1",20),pin("Paraná","pancadas previstas · hoje",-52.2,-24.5,"f3",20),pin("Norte gaúcho","chuva forte pode chegar terça",-52.5,-27.8,"f5",20),pin("Oeste de SC","risco de temporais · terça",-53,-26.6,"f5",20),pin("Oeste do Sul","100–150 mm previstos até quinta",-53.2,-27,"f8",20),pin("SC / PR","pancadas · sexta e fim de semana",-51.8,-26.1,"f9",20)]
def conta(ate,fid,palavra,unid,cor="#ff8c1a"):
 t=em(fid,palavra)
 return {"de":0,"ate":ate,"dec":0,"ini":t-1,"dur":1,"cor":cor,"unid":unid}
hero=[]
def painel(fid,k,itens,l):
 return {"ini":ini(fid),"fim":fim(fid),"k":k,"itens":[{"t":ini(fid),"txt":x} for x in itens],"l":l}
paineis=[
 {"ini":CAPA,"fim":fim("f1"),"k":"ATÉ DOMINGO 29 · PREVISÃO","contador":conta(200,"f1","200","MM · PODE PASSAR"),"l":"Oeste do Sul · limiar regional, sem cidade específica"},
 painel("f2","BAIXA PRESSÃO · PREVISÃO",["Chuva deve se intensificar","Umidade vem da Amazônia"],"IR observado: "+IR_DE+" a "+IR_ATE),
 painel("f3","HOJE 23 · PREVISÃO",["PR: tarde e noite","SC / norte RS: irregular"],"Pintura parcial: INMET 56484 · válido 23/11"),
 painel("f4","HOJE · PANCADAS PREVISTAS",["SP / MG / GO / MT / MS","Distribuição irregular"],"Pintura parcial: INMET 56489 · válido 23/11"),
 painel("f5","TERÇA 24 · ATENÇÃO",["Norte RS · oeste/meio-oeste SC","Chuva forte e temporais"],"Risco previsto · acompanhe avisos locais"),
 painel("f6","RISCO PREVISTO",["Acompanhe os avisos locais","PR / Sudeste / Centro-Oeste"],"Tempestades podem atingir partes dessas regiões"),
 painel("f7","QUARTA 25 · PREVISÃO",["Instabilidade deve ganhar força","Temporais localizados no Sul"],"Risco regional · não é certeza por cidade"),
 {"ini":ini("f8"),"fim":fim("f8"),"k":"ATÉ QUINTA 26 · PREVISÃO","contador":conta(150,"f8","150","MM · ATÉ QUINTA"),"l":"100–150 mm · oeste do Sul · intervalo regional"},
 painel("f9","SEXTA E FIM DE SEMANA",["SC / PR: pancadas à tarde","Calor deve continuar"],"Previsão · acumulado pode passar de 200 mm até 29/11"),
 {"ini":ini("f10"),"fim":fim("f10"),"k":"COMENTA AQUI","itens":[{"t":em("f10","onde"),"txt":"DE ONDE VOCÊ É?"},{"t":em("f10","tempo"),"txt":"COMO ESTÁ AÍ?"}]}]
for p in paineis:
 p["borda"]="rgba(94,200,255,.8)"
 assert p["ini"]<p["fim"]
 if p.get("contador"):
  c=p["contador"];assert c["ini"]+c["dur"]<=p["fim"]
for a,b in zip(paineis,paineis[1:]): assert a["fim"]<=b["ini"]
cta={"img":True,"ini":ini("f11"),"fim":DUR,"a":"APRENDA IA","b":"inema.club"}
club={"ini":em("f11","inema"),"fim":DUR,"a":"inema.club","b":"aprenda de graça · inteligência artificial"}
GOES=f"GOES-19 / NOAA via NASA GIBS · observado {IR_DE} a {IR_ATE}"
fontes=[{"ini":0,"fim":ini("f2"),"html":MET},
 {"ini":ini("f2"),"fim":fim("f2"),"html":MET+" · "+GOES},
 {"ini":ini("f3"),"fim":fim("f4"),"html":MET+" · pintura: INMET 56484 / 56489 (parcial)"},
 {"ini":ini("f5"),"fim":DUR,"html":MET}]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "pancadas": "#5ec8ff", "chove": "#5ec8ff", "milimetros": "#5ec8ff", "umidade": "#5ec8ff", "oceano": "#5ec8ff",
         "granizo": "#ff2a1f", "tempestade": "#ff8c1a", "temporal": "#ff8c1a", "temporais": "#ff8c1a", "ciclone": "#ff8c1a", "ciclones": "#ff8c1a",
         "bomba": "#ff2a1f", "alerta": "#ff2a1f", "atencao": "#ff2a1f", "risco": "#ff2a1f", "dispara": "#ff2a1f",
         "calor": "#ff2a1f", "quente": "#ff2a1f", "verao": "#ff8c1a", "abafamento": "#ff2a1f", "graus": "#ff2a1f", "sol": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "mato", "grosso", "sao", "paulo", "oeste", "nordeste", "piaui", "ceara", "pernambuco", "teresina", "brasil",
         "campanha", "extremo", "gaucho", "palmas", "belo", "horizonte", "hoje", "noite", "sabado", "domingo", "segunda", "terca",
         "quarta", "sexta", "inemaclub", "onde"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        prox = t["palavras"][i + 1]["w"] if i + 1 < len(t["palavras"]) else ""
        longo = sum(len(b["w"]) + 1 for b in bloco) + len(prox) > 20   # "marcaram 500 milímetros" passava da borda
        if len(bloco) == 3 or longo or w[-1:] in ".?!,:;" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo":640 if CANTO else 820,
     "padding_topo":560,"duracao":DUR,"marca":"INEMA · PREVISÃO DO DIA","selo":"23/11/2026",
     "camera":camera,"sat":SAT,"imagens":imagens,"colunas":colunas,"rios":rios,"telas":telas,"estados":estados,"pinos":pinos,
     "hero":hero,"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js ok · duração {DUR} · IR {len(BONS)}/{len(TS)} ({IR_DE} a {IR_ATE}) · layout {C['layout']}")
