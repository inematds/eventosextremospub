#!/usr/bin/env python3
"""Monta cena.js da "Previsão do dia" de 15/11/2026 a partir de tempos.json (palavras da narração),
da previsão do dia (pesquisa/boletim.md), do timelapse do GOES-19 (NASA GIBS), dos avisos do INMET
e da previsão Open-Meteo das capitais (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>
Visual: capa Codex de chuva pontual acima de 300 mm até 30/11; temporais SC/PR,
calor nas três regiões, avisos INMET de 15–17/11, gráfico 15–21/11,
baixa pressão, frente fria condicional e colunas das faixas projetadas até 30/11.
Teste do --canto sem avatar: TEMPOS=tempos.json python3 gerar_cena.py --canto"""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "15/11/2026"
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

# ---------------------------------------------------------------- câmera: uma composição por fala
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
SUL = {"lon": -52.6, "lat": -27.0, "zoom": 5.95}
BR = {"lon": -50, "lat": -16, "zoom": 5.2}
SC = {"lon": -51.7, "lat": -26.7, "zoom": 6.0}
SECO = {"lon": -49.5, "lat": -19.5, "zoom": 5.4}
if CANTO:
 SUL["zoom"] += .4  # mantém o limite sul do raster fora da área livre
 SC["zoom"] += .3
CAPA = 2.2
GRAN = em("f3", "granizo")
GFIM = fim("f3")
camera = [K(0,SUL), K(CAPA,SUL), K(fim("f1")-.2,SUL,15,8)]
for fid,reg,pitch,bearing in [
 ("f2",BR,0,0),("f3",SC,0,0),("f4",BR,0,0),("f5",SECO,10,8),
 ("f6",BR,0,0),("f7",BR,0,0),("f8",SUL,25,-10),("f9",SUL,12,4),
 ("f10",SUL,55,-20),("f11",BR,0,0),("f12",BR,0,0)]:
 camera += [K(ini(fid)+.85,reg,pitch,bearing), K(fim(fid)-.1,reg,pitch,bearing+12 if fid=="f10" else bearing)]
camera.sort(key=lambda k:k["t"])
assert all(a["t"]<b["t"] for a,b in zip(camera,camera[1:]))

# ---------------------------------------------------------------- satélite OBSERVADO, nunca projeção
from PIL import Image, ImageStat
TS=json.loads((AQUI/"sat/web/ir_tempos.json").read_text())
luz=lambda i:ImageStat.Stat(Image.open(AQUI/f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS=[i for i in range(len(TS)) if 90<luz(i)<130]
assert len(BONS)>=20,BONS
DIAS=["seg","ter","qua","qui","sex","sáb","dom"]
def brt(z):
 d=datetime.strptime(z,"%Y-%m-%dT%H:%M:%SZ")-timedelta(hours=3)
 return f"{d:%d/%m %Hh%M}"
IR_DE,IR_ATE=brt(TS[BONS[0]]),brt(TS[BONS[-1]])
SAT={"fundo":{"src":"sat/web/mundo.jpg","bbox":[-180,-60,180,75],"tint":[170,170,175]},
 "base":"sat/web/geocolor.jpg","bbox":[-76,-35,-33,7],"tint":[170,170,175],
 "ir":{"frames":[f"sat/web/ir{i:02d}.jpg" for i in BONS],"tempos":[brt(TS[i]) for i in BONS],
       "ini":ini("f2"),"fim":fim("f2"),"dur":fim("f2")-ini("f2"),"alfa":.9,"rotulo":"GOES-19 · observado 24 h"}}
imagens=[]
rios=[]
telas=[{"src":"capa-dia/abertura.png","ini":0,"fim":CAPA,"fade":0,"zoom":.015,"selo":"ilustração"},
       {"src":"capa-dia/granizo.png","ini":GRAN,"fim":GFIM,"fade":.12,"zoom":.025,"selo":"ilustração"}]

# ---------------------------------------------------------------- avisos: abrangência parcial por UF
UF={"11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO","21":"MA","22":"PI","23":"CE",
    "24":"RN","25":"PB","26":"PE","27":"AL","28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP",
    "41":"PR","42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF"}
AV=json.loads((B/"inmet_avisos_ativos.json").read_text())
aviso={int(a["id"]):a for g in ("hoje","futuro") for a in AV.get(g,[])}
geo=lambda i:set(c for c in aviso[i]["geocodes"].split(",") if c)
ufs_av=lambda i:sorted({UF[c[:2]] for c in geo(i)})
for aid,total,dia in [(56412,2438,"2026-11-15"),(56415,2938,"2026-11-16"),(56419,300,"2026-11-17")]:
 assert len(geo(aid))==total,(aid,len(geo(aid)))
 assert aviso[aid]["descricao"]=="Tempestade" and aviso[aid]["inicio"].startswith(dia)
assert sum(c.startswith("31") for c in geo(56415))==853
assert sum(c.startswith("35") for c in geo(56415))==586
HOJE,SEG,TER=ufs_av(56412),ufs_av(56415),ufs_av(56419)
estados=[
 {"id":"hoje","ini":ini("f3"),"fim":GRAN,"ufs":[u for u in HOJE if u in ["SC","PR"]],"cor":LAR,"alfa":.35},
 {"id":"segunda","ini":ini("f6"),"fim":ini("f7"),"ufs":SEG,"cor":LAR,"alfa":.35},
 {"id":"terca","ini":ini("f7"),"fim":ini("f8"),"ufs":TER,"cor":LAR,"alfa":.35}]

# ---------------------------------------------------------------- projeção regional mensal, SEM valores inventados por cidade
# Três colunas com as referências 100 / 150 / 300 mm citadas pela fonte (04:38–04:49).
# Coordenadas só organizam o diagrama no oeste do Sul; não são previsão pontual de município.
COLINI=ini("f10")+.15
colunas=[{"id":"faixas30","ini":COLINI,"fim":ini("f11"),"raio":26000,"escala":750,
 "dados":[{"id":0,"p":[-54.4,-28.0],"v":100,"cor":AZUL},
          {"id":1,"p":[-52.6,-27.0],"v":150,"cor":[94,200,255]},
          {"id":2,"p":[-51.6,-25.3],"v":300,"cor":LAR}],"ordem":{},"varredura":1}]

def pin(nome,sub,lon,lat,fid,palavra=None,h=100,ate=None):
 return {"nome":nome,"sub":sub,"lon":lon,"lat":lat,"ini":em(fid,palavra) if palavra else ini(fid)+1,"fim":ate or fim(fid),"h":h}
pinos=[
 pin("Oeste do Sul","pico pontual pode passar de 300 mm até 30/11",-52.6,-27.6,"f1",ate=ini("f2")),
 pin("Oeste catarinense","risco localizado · restante de 15/11",-52.6,-27.1,"f3",ate=GRAN),
 pin("Sudeste e Centro-Oeste","temporais podem vir mais fortes em 16/11",-49.5,-19.5,"f5",h=80),
 pin("Oeste do Sul","baixa + umidade · 18 para 19/11",-52.6,-27.6,"f8",h=100),
 pin("Frente fria possível","20–22/11 · se confirmar",-52.6,-27.6,"f9",h=100),
 pin("Faixas regionais até 30/11","100–150 mm; picos podem passar de 300 mm",-52.6,-27.6,"f10",h=70)]

pinos[0]["ini"] = CAPA + .3
if CANTO:
 pinos[0].update(lon=-54.0, lat=-29.5, h=65)

# ---------------------------------------------------------------- contadores sincronizados na palavra, duração fixa 1 s

def conta(ate,fid,palavra,unid,cor="#5ec8ff"):
 t=em(fid,palavra)
 return {"de":0,"ate":ate,"dec":0,"ini":t-1.0,"dur":1.0,"cor":cor,"unid":unid}
hero=[{"ini":CAPA,"fim":ini("f2"),"html":
 f'<div style="font:400 116px/1 \'Archivo Black\';margin-bottom:12px">{DATA}</div>'
 '<div class="dt">PREVISÃO DO DIA</div><div class="t1" style="font-size:88px;color:#FACC15">PODE PASSAR DE 300 MM</div>'
 '<div class="t4">Pontos do oeste do Sul<br>até 30/11 · previsão pontual</div>'}]
P7=json.loads((B/"previsao7d.json").read_text())
assert P7["dias"][0]=="2026-11-15" and P7["dias"][-1]=="2026-11-21"
ROTD=[DIAS[datetime.strptime(d,"%Y-%m-%d").weekday()] for d in P7["dias"]]
series=[{"nome":nome,"cor":cor,"v":[d["por_regiao_mm"][r] for d in P7["por_dia"]]}
        for r,nome,cor in [("S","Sul","#5ec8ff"),("SE","Sudeste","#3c96ff"),("CO","Centro-Oeste","#FACC15")]]
F10P=min(em("f10","picos"), em("f10","300")-1.0)
paineis=[
 {"ini":ini("f2"),"fim":ini("f3"),"k":"O QUE ALIMENTA O RISCO · PREVISÃO",
  "itens":[{"t":em("f2","Calor"),"txt":"Calor + umidade"},{"t":em("f2","pressão"),"txt":"Pressão em queda"}],"l":"Satélite abaixo: observação das últimas 24 h"},
 {"ini":ini("f3"),"fim":GRAN,"k":"DOMINGO · RESTANTE DE 15/11",
  "itens":[{"t":em("f3","oeste"),"txt":"Oeste de SC / sul do PR"},{"t":em("f3","pancadas"),"txt":"Pancadas ainda possíveis"}],"l":"Risco localizado · previsão meteorológica"},
 {"ini":ini("f4"),"fim":ini("f5"),"k":"SEGUNDA A SEXTA · PREVISÃO",
  "contador":conta(30,"f4","30","°C","#ff2a1f"),"l":"Temperaturas próximas ou acima de 30 °C · Sul, Sudeste e Centro-Oeste"},
 {"ini":ini("f5"),"fim":ini("f6"),"k":"SEGUNDA, 16/11 · PREVISÃO",
  "itens":[{"t":em("f5","Sul"),"txt":"Sul: pancadas isoladas"},{"t":em("f5","Sudeste"),"txt":"SE / CO: risco de temporais"}]},
 {"ini":ini("f6"),"fim":ini("f7"),"k":"BRASIL · AVISO PARA 16/11",
  "contador":conta(2938,"f6","2.938","CIDADES","#ff8c1a"),"l":"INMET · aviso 56415 de tempestade; Cor nas UFs = abrangência parcial"},
 {"ini":ini("f7"),"fim":ini("f8"),"k":"17–18/11 · TEMPORAIS À TARDE / NOITE",
  "grafico":{"rotulos":ROTD,"series":series,"previsto_a_partir":0,"ini":ini("f7")+.2,"dur":1.3},
  "l":"Gráfico: chuva 15–21/11 somada nas capitais de cada região (mm) · não é média regional"},
 {"ini":ini("f8"),"fim":ini("f9"),"k":"18 PARA 19/11 · OESTE DO SUL",
  "itens":[{"t":em("f8","baixa"),"txt":"Baixa pressão"},{"t":em("f8","Amazônia"),"txt":"Umidade da Amazônia"}],"l":"Tempestades podem ganhar força"},
 {"ini":ini("f9"),"fim":ini("f10"),"k":"20–22/11 · ATENÇÃO AO SUL",
  "itens":[{"t":em("f9","frente"),"txt":"Frente fria possível"},{"t":em("f9","severo"),"txt":"Potencial de tempo severo"}],"l":"Previsão condicionada à confirmação do sistema"},
 {"ini":ini("f10"),"fim":F10P,"k":"ATÉ 30/11 · FAIXA REGIONAL",
  "contador":conta(150,"f10","150","MM"),"l":"100 a 150 mm no oeste do Sul (previsão); Colunas = faixas; posições indicativas"},
 {"ini":F10P,"fim":ini("f11"),"k":"ATÉ 30/11 · PICO PONTUAL",
  "contador":conta(300,"f10","300","MM +","#ff8c1a"),"l":"Pode passar de 300 mm em pontos da região. Não é acumulado de um dia."},
 {"ini":ini("f11"),"fim":ini("f12"),"k":"COMENTA AQUI",
  "itens":[{"t":em("f11","onde"),"txt":"DE ONDE VOCÊ É?"},{"t":em("f11","tempo"),"txt":"COMO ESTÁ AÍ?"}]}]
for p in paineis:
 p["borda"]="rgba(94,200,255,.8)"
 assert p["ini"]<p["fim"],p["k"]
 if p.get("contador"):
  c=p["contador"]
  assert p["ini"]<=c["ini"] and c["ini"]+c["dur"]<=p["fim"],(p["k"],c)
for a,b in zip(paineis,paineis[1:]):
 assert a["fim"]<=b["ini"],(a["k"],b["k"])
cta={"ini":ini("f12"),"fim":DUR,"a":"APRENDA IA","b":"inema.club"}
club={"ini":em("f12","inema"),"fim":DUR,"a":"inema.club","b":"aprenda de graça · inteligência artificial"}
GOES=f"GOES-19 / NOAA via NASA GIBS · observado {IR_DE} a {IR_ATE}"
fontes=[{"ini":0,"fim":ini("f2"),"html":MET+" · ilustração"},
 {"ini":ini("f2"),"fim":ini("f3"),"html":MET+" · "+GOES},
 {"ini":ini("f3"),"fim":ini("f4"),"html":MET+" · granizo: ilustração"},
 {"ini":ini("f4"),"fim":ini("f6"),"html":MET},
 {"ini":ini("f6"),"fim":ini("f7"),"html":"INMET · aviso 56415 · 16/11 · 2.938 municípios"},
 {"ini":ini("f7"),"fim":ini("f8"),"html":MET+" · gráfico Open-Meteo 15–21/11 · INMET 56419 (17/11)"},
 {"ini":ini("f8"),"fim":DUR,"html":MET}]

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
     "padding_topo":0,"duracao":DUR,"marca":"INEMA · PREVISÃO DO DIA","selo":"15/11 · INMET",
     "camera":camera,"sat":SAT,"imagens":imagens,"colunas":colunas,"rios":rios,"telas":telas,"estados":estados,"pinos":pinos,
     "hero":hero,"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js ok · duração {DUR} · IR {len(BONS)}/{len(TS)} ({IR_DE} a {IR_ATE}) · INMET 56415: {len(geo(56415))} cidades · layout {C['layout']}")
