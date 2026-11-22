#!/usr/bin/env python3
"""Previsão do Dia 22/11/2026. Gera cena.js; --canto usa avatar/tempos.json.
Fontes e rastreabilidade em pesquisa/boletim.md. TEMPOS=tempos.json permite validar --canto antes do avatar."""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "22/11/2026"
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
VENTO=em("f5","vendaval")
camera=[K(0,SC),K(CAPA,SC)]
for fid,r,p,b in [("f1",SC,0,0),("f2",SUL,15,-8),("f3",SC,15,-8),("f4",PR,15,0),("f5",SUL,0,0),("f6",BR,0,0),("f7",SUL,20,-10),("f8",SUL,55,-15),("f9",ES,0,0),("f10",BR,0,0),("f11",BR,0,0)]:
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
 "ir":{"frames":[f"sat/web/ir{i:02d}-borda.png" for i in BONS],"tempos":[brt(TS[i]) for i in BONS],"ini":ini("f2"),"fim":fim("f2"),"dur":fim("f2")-ini("f2"),"alfa":.9,"rotulo":"GOES-19 · observado 24 h"}}
imagens=[]
rios=[]
# Duas colunas mostram extremos do intervalo REGIONAL, sem leitura por município.
colunas=[{"id":"acumulado-regional","ini":ini("f8"),"fim":em("f8","Espírito"),"cor":AZUL,"escala":1100,"raio":18000,"varredura":0,"dados":[{"id":"a","p":[-53.5,-27.5],"v":250},{"id":"b","p":[-52.8,-26.5],"v":320}]}]
telas=[{"src":"capa-dia/abertura.png","ini":0,"fim":CAPA,"fade":0,"zoom":.015,"selo":"ilustração · risco previsto"},
 {"src":"capa-dia/vendaval.png","ini":VENTO,"fim":fim("f5"),"fade":.12,"zoom":.025,"selo":"ilustração · risco previsto"}]
UF={"11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO","21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL","28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP","41":"PR","42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF"}
AV=json.loads((B/"inmet_avisos_ativos.json").read_text())
aviso={int(a["id"]):a for a in AV["hoje"]}
geo=lambda i:set(filter(None,aviso[i]["geocodes"].split(",")))
assert len(geo(56477))==655
assert len(geo(56475))==3717
assert aviso[56477]["inicio"].startswith("2026-11-22") and aviso[56477]["severidade"]=="Perigo"
assert aviso[56475]["fim"].startswith("2026-11-22")
estados=[{"id":"laranja-sul","ini":CAPA,"fim":ini("f5"),"ufs":sorted({UF[c[:2]] for c in geo(56477)}),"cor":LAR,"alfa":.22},
 {"id":"amarelo-brasil","ini":ini("f6"),"fim":fim("f6"),"ufs":sorted({UF[c[:2]] for c in geo(56475)}),"cor":AMA,"alfa":.18}]
def pin(nome,sub,lon,lat,fid,h=40):
 return {"nome":nome,"sub":sub,"lon":lon,"lat":lat,"ini":ini(fid)+.8,"fim":fim(fid),"h":h}
pinos=[pin("Oeste de SC","rajadas fortes previstas hoje",-52.7,-27,"f1"),pin("Santa Catarina","oeste / meio-oeste / Serra / sul",-51.3,-27.4,"f3"),pin("Oeste / SO do PR","chuva deve avançar",-53,-25.5,"f4"),pin("Oeste do Sul","novos temporais · terça",-53,-27,"f7"),pin("Espírito Santo","chuva forte prevista até 26/11",-40.6,-19.8,"f9")]
def conta(ate,fid,palavra,unid,cor="#ff8c1a"):
 t=em(fid,palavra)
 return {"de":0,"ate":ate,"dec":0,"ini":t-1,"dur":1,"cor":cor,"unid":unid}
hero=[]
def painel(fid,k,itens,l):
 return {"ini":ini(fid),"fim":fim(fid),"k":k,"itens":[{"t":ini(fid),"txt":x} for x in itens],"l":l}
paineis=[
 {"ini":CAPA,"fim":fim("f1"),"k":"HOJE · OESTE DE SC","contador":conta(100,"f1","100","KM/H"),"l":"Rajadas podem superar esse valor · previsão"},
 painel("f2","COMO O RISCO SE FORMA",["Umidade da Amazônia","Perturbação dos Andes"],"IR observado: "+IR_DE+" a "+IR_ATE),
 painel("f3","DOMINGO 22 · PREVISÃO",["Oeste / meio-oeste de SC","Serra e sul: atenção"],"INMET 56477 · pintura parcial · aviso hoje"),
 painel("f4","HOJE · CHUVA AVANÇA",["Oeste / sudoeste do PR","Noroeste gaúcho: risco"],"INMET 56477 · abrangência parcial"),
 {**painel("f5","RISCO DE TEMPO SEVERO",["Acompanhe avisos locais"],"Previsão regional, sem cidade certa"),"fim":VENTO},
 painel("f6","SEGUNDA 23 · PREVISÃO",["RS: tempo mais seco","PR / SP / MG / GO / MT / MS"],"Pintura: INMET 56475 vigente hoje · previsão de amanhã: Meteorologia"),
 painel("f7","TERÇA 24 · PREVISÃO",["Oeste SC · NO RS · SO PR","Novos temporais e vendavais"],"Risco previsto, localizado"),
 {"ini":ini("f8"),"fim":fim("f8"),"k":"ATÉ QUINTA 26 · PREVISÃO","contador":conta(320,"f8","320","MM PONTUAIS"),"l":"250–320 mm · oeste do Sul · intervalo regional, sem cidade específica; ES também exige atenção"},
 painel("f9","QUINTA 26 · PREVISÃO",["PR / parte de SC / SE / CO","RS: chuva deve enfraquecer"],"ES: chuva forte pode persistir até 26/11"),
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
 {"ini":ini("f3"),"fim":fim("f4"),"html":MET+" · pintura: INMET 56477 (parcial)"},
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
     "padding_topo":560,"duracao":DUR,"marca":"INEMA · PREVISÃO DO DIA","selo":"22/11/2026",
     "camera":camera,"sat":SAT,"imagens":imagens,"colunas":colunas,"rios":rios,"telas":telas,"estados":estados,"pinos":pinos,
     "hero":hero,"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js ok · duração {DUR} · IR {len(BONS)}/{len(TS)} ({IR_DE} a {IR_ATE}) · layout {C['layout']}")
