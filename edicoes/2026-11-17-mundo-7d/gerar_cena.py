#!/usr/bin/env python3
"""Clima no Mundo 17/11/2026. Adaptado do modelo 15/11: mapa 9:16, imagens por evento, zoom <=3,2. --canto usa avatar/tempos.json."""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "17/11/2026"
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

CAPA = 3.2
K = lambda t, r: {"t": round(t,3), **r, "pitch": 0, "bearing": 0}
MUNDO = {"lon": 5, "lat": 15, "zoom": 1.25}
LOCAIS = {
    "tailandia": {"lon":100.57,"lat":14.35,"zoom":3.2},
    "eua": {"lon":-98,"lat":36,"zoom":2.5},
    "gaza": {"lon":34.35,"lat":31.40,"zoom":3.2},
    "somalia": {"lon":45.50,"lat":2.78,"zoom":3.0},
    "madeira": {"lon":-16.93,"lat":32.73,"zoom":3.2},
    "sul": {"lon":99.2,"lat":8,"zoom":3.0},
}
camera=[K(0,MUNDO),K(CAPA,LOCAIS["tailandia"]),K(em("f1","Gaza")-.6,LOCAIS["tailandia"]),K(em("f1","Gaza")+.6,LOCAIS["gaza"])]
eventos=[("f2","tailandia","Ayutthaya · Tailândia","corte de domingo · 15/11"),
         ("f3","eua","Estados Unidos","seca · dados 10/11 · publicado 12/11"),
         ("f4","gaza","Faixa de Gaza","estimativa · chuvas desde 6/11"),
         ("f5","somalia","Jowhar · Somália","alagamentos ativos · boletim 11–17/11"),
         ("f6","madeira","Chão do Areeiro · Portugal","recorde nacional · medição até 11/11")]
SAT={"base":"../2026-10-12-mundo-clima/sat/web/mundo.jpg","bbox":[-180,-60,180,75],"tint":[200,200,200]}
telas=[{"src":"imgs/capa.png","ini":0,"fim":CAPA,"fade":.25,"zoom":.035,"selo":"ILUSTRAÇÃO"},
       {"src":"imgs/tailandia.png","ini":CAPA,"fim":em("f1","Gaza")-.3,"fade":.25,"zoom":.035,"selo":"ILUSTRAÇÃO"},
       {"src":"imgs/gaza.png","ini":em("f1","Gaza")+.6,"fim":fim("f1"),"fade":.25,"zoom":.035,"selo":"ILUSTRAÇÃO"}]
pinos=[]
for fid,local,nome,sub in eventos:
    a,b=ini(fid),fim(fid)
    camera += [K(a+.7,LOCAIS[local]),K(b-.25,LOCAIS[local])]
    telas.append({"src":f"imgs/{local}.png","ini":a+1.6,"fim":b-.3,"fade":.3,"zoom":.035,"selo":"ILUSTRAÇÃO"})
    pinos.append({"nome":nome,"sub":sub,"lon":LOCAIS[local]["lon"],"lat":LOCAIS[local]["lat"],"ini":a+.15,"fim":a+1.55,"h":90})
camera += [K(ini("f7")+.7,MUNDO),K(ini("f8")+.7,LOCAIS["sul"]),K(fim("f8")-.2,LOCAIS["sul"]),K(ini("f9")+.8,MUNDO),K(DUR,{**MUNDO,"lon":10,"zoom":1.4})]
camera.sort(key=lambda x:x["t"])
assert max(x["zoom"] for x in camera)<=3.2
pinos.append({"nome":"Sul da Tailândia","sub":"PREVISÃO · 18–22/11","lon":99.2,"lat":8,"ini":ini("f8")+.8,"fim":fim("f8"),"h":85})
imagens=[]
pontos=[]
hero=[{"ini":0,"fim":em("f1","Gaza")-.3,"html":
       '<div class="dt">17/11/2026</div><div class="t1" style="font-size:112px">TAILÂNDIA</div><div class="t2" style="font-size:130px">121,4 MIL</div><div class="t4">pessoas ainda atingidas<br>89 vítimas desde setembro<br>AHA/DDPM · corte 15/11<br><span style="font:800 24px Inter;letter-spacing:1px">ILUSTRAÇÃO</span></div>'}]
cont=lambda fid,pal,ate,dec,cor,unid: {"de":0,"ate":ate,"dec":dec,"ini":em(fid,pal)-1.,"dur":1.,"cor":cor,"unid":unid}
it=lambda fid,pal,txt:{"t":em(fid,pal),"txt":txt}
paineis=[
 {"ini":em("f1","Gaza")-.3,"fim":fim("f1"),"k":"GAZA · ESTIMATIVA · OCHA 13/11","contador":cont("f1","226",226,0,"#5ec8ff","MIL POSSIVELMENTE ATINGIDOS"),"l":"Chuvas desde 6/11 · alertas até 9/11"},
 {"ini":ini("f2"),"fim":fim("f2"),"k":"TAILÂNDIA · BALANÇO DE DOMINGO","contador":{"de":0,"ate":121.4,"dec":1,"ini":ini("f2")-.9,"dur":.9,"cor":"#5ec8ff","unid":"MIL PESSOAS AINDA ATINGIDAS"},"l":"5 províncias · 89 vítimas desde setembro · AHA/DDPM"},
 {"ini":ini("f3"),"fim":fim("f3"),"k":"ESTADOS UNIDOS · SECA PERSISTENTE","contador":cont("f3","84,6",84.6,1,"#ff8c1a","MILHÕES NAS ÁREAS EM SECA"),"l":"NOAA/NIDIS · dados 10/11 · publicado 12/11"},
 {"ini":ini("f4"),"fim":fim("f4"),"k":"GAZA · ESTIMATIVA DIVULGADA 13/11","contador":{"de":0,"ate":226,"dec":0,"ini":ini("f4")-.9,"dur":.9,"cor":"#5ec8ff","unid":"MIL POSSIVELMENTE ATINGIDOS"},"l":"OCHA · alertas 6–9/11 · não é balanço fechado"},
 {"ini":ini("f5"),"fim":fim("f5"),"k":"SOMÁLIA · ACUMULADO DE OUTUBRO","contador":cont("f5","170",170,0,"#5ec8ff","MIL ATINGIDOS · QUASE"),"l":"OCHA 12/11 · alagamentos persistentes: FAO 11–17/11"},
 {"ini":ini("f6"),"fim":fim("f6"),"k":"MADEIRA · CHÃO DO AREEIRO · IPMA","contador":cont("f6","502,7",502.7,1,"#5ec8ff","MM DIÁRIOS · RECORDE NACIONAL"),"l":"Anterior: 497,5 mm em 6/6/2023 · mesmo posto · provisório"},
 {"ini":ini("f7"),"fim":fim("f7"),"k":"CADA BALANÇO TEM SEU PERÍODO","itens":[it("f7","períodos","Tailândia: desde setembro<br>Somália: acumulado de outubro"),it("f7","somar","Sem somar desastres independentes")]},
 {"ini":ini("f8"),"fim":fim("f8"),"k":"E AGORA? · PREVISÃO TMD 17/11","itens":[it("f8","chuva","Chuva intensa · sul da Tailândia"),it("f8","quarta","18–22/11 · quarta a domingo"),it("f8","risco","Risco de novas enchentes")],"l":"Aviso 313/2026 · previsão, não impacto observado"},
 {"ini":ini("f9"),"fim":fim("f9"),"k":"COMENTA AQUI","itens":[it("f9","região","De que região você é?"),it("f9","cidade","E de que cidade?")]}
]
cta={"ini":ini("f10"),"fim":DUR,"a":"APRENDA IA","b":"inema.club"}
club={"ini":em("f10","inema"),"fim":DUR,"a":"inema.club","b":"APRENDA IA · DE GRAÇA"}
fontes=[
 {"ini":0,"fim":fim("f1"),"html":"AHA/DDPM: corte 15/11 · OCHA 13/11: Gaza estimativa"},
 {"ini":ini("f2"),"fim":fim("f2"),"html":"AHA Centre · DDPM · 15/11 18h UTC+7 · publicado 16/11"},
 {"ini":ini("f3"),"fim":fim("f3"),"html":"NOAA/NIDIS · Drought.gov · publicado 12/11 · dados 10/11"},
 {"ini":ini("f4"),"fim":fim("f4"),"html":"OCHA OPT · 13/11 · estimativa: alertas até 9/11"},
 {"ini":ini("f5"),"fim":fim("f5"),"html":"OCHA ROSEA 12/11 · FAO-SWALIM/SODMA 11–17/11"},
 {"ini":ini("f6"),"fim":fim("f6"),"html":"IPMA 11/11 · 09 UTC 10/11 a 09 UTC 11/11 · provisório"},
 {"ini":ini("f7"),"fim":fim("f7"),"html":"Períodos e URLs completos: pesquisa/noticias.md"},
 {"ini":ini("f8"),"fim":fim("f8"),"html":"TMD · aviso 313/2026 de 17/11 · PREVISÃO 18–22/11"},
 {"ini":ini("f9"),"fim":DUR,"html":"INEMA · inema.club · NASA Blue Marble · imagens: ilustração"}]
AM="#FACC15"
CORES={"vitimas":"#ff8c1a","recorde":"#5ec8ff","atingidas":"#5ec8ff","atingidos":"#5ec8ff","calor":"#ff8c1a","chuvas":"#5ec8ff","estimativa":"#ff8c1a","possivelmente":"#ff8c1a"}
LUGAR={"eua","estados","unidos","gaza","somalia","jowhar","madeira","portugal","tailandia","ayutthaya","inema","inemaclub","regiao","cidade"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        nxt = len(t["palavras"][i + 1]["w"]) if i + 1 < len(t["palavras"]) else 0
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1 or sum(len(b["w"]) + 1 for b in bloco) + nxt > 18:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C={"layout":"canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo":640 if CANTO else 820,
   "duracao":DUR,"padding_topo":0 if AVATAR else 560,"marca":"INEMA · CLIMA NO MUNDO","selo":"NOAA · ONU · IPMA · 17/11",
   "camera":camera,"sat":SAT,"telas":telas,"imagens":imagens,"pontos":pontos,"pinos":pinos,"hero":hero,
   "paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js: {DUR}s, {len(legenda)} blocos, zoom máximo {max(x['zoom'] for x in camera)}, {len(telas)} imagens")
