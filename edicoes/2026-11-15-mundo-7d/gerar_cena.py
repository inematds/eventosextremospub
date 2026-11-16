#!/usr/bin/env python3
"""Clima no Mundo 15/11/2026. Adaptado do modelo 14/11: mapa 9:16, imagens por evento, zoom <=3,2. --canto usa avatar/tempos.json."""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "15/11/2026"
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
MUNDO = {"lon": 35, "lat": 15, "zoom": 1.25}
LOCAIS = {
    "gaza": {"lon": 34.35, "lat": 31.40, "zoom": 3.2},
    "tailandia": {"lon": 100.3, "lat": 14.4, "zoom": 3.0},
    "somalia": {"lon": 45.50, "lat": 2.78, "zoom": 3.0},
    "madeira": {"lon": -16.93, "lat": 32.73, "zoom": 3.2},
    "weipa": {"lon": 141.87, "lat": -12.63, "zoom": 3.0},
    "bengala": {"lon": 86.5, "lat": 11.0, "zoom": 2.7},
}
camera=[K(0,MUNDO),K(CAPA,LOCAIS["gaza"]), K(em("f1","Tailândia")-.6,LOCAIS["gaza"]),K(em("f1","Tailândia")+.7,LOCAIS["tailandia"])]
eventos=[("f2","gaza","Faixa de Gaza","estimativa · 6 a 9/11"),
         ("f3","tailandia","Planície central · Tailândia","enchentes desde setembro"),
         ("f4","somalia","Jowhar · Somália","alagamentos ainda ativos em 11/11"),
         ("f5","madeira","Chão do Areeiro · Madeira","recorde nacional de chuva diária"),
         ("f6","weipa","Weipa Aero · Austrália","recorde de novembro · estação 027045")]
SAT={"base":"../2026-10-12-mundo-clima/sat/web/mundo.jpg","bbox":[-180,-60,180,75],"tint":[200,200,200]}
telas=[{"src":"imgs/capa.png","ini":0,"fim":CAPA,"fade":.25,"zoom":.035,"selo":"ILUSTRAÇÃO"}]
pinos=[]
for fid,local,nome,sub in eventos:
    a,b=ini(fid),fim(fid)
    camera += [K(a+.7,LOCAIS[local]),K(b-.25,LOCAIS[local])]
    # O mapa liga países; a imagem de impacto ocupa a fala após 1,6 s.
    telas.append({"src":f"imgs/{local}.png","ini":a+1.6,"fim":b-.3,"fade":.3,"zoom":.035,"selo":"ILUSTRAÇÃO"})
    pinos.append({"nome":nome,"sub":sub,"lon":LOCAIS[local]["lon"],"lat":LOCAIS[local]["lat"],"ini":a+.15,"fim":a+1.55,"h":90})
camera += [K(ini("f7")+.7,MUNDO),K(ini("f8")+.7,LOCAIS["bengala"]),K(fim("f8")-.2,LOCAIS["bengala"]),K(ini("f9")+.8,MUNDO),K(DUR,{**MUNDO,"lon":10,"zoom":1.4})]
camera.sort(key=lambda x:x["t"])
assert max(x["zoom"] for x in camera)<=3.2
pinos.append({"nome":"Golfo de Bengala","sub":"PREVISÃO · ciclone em 16/11","lon":86.5,"lat":11.,"ini":ini("f8")+.8,"fim":fim("f8"),"h":85})
imagens=[]
pontos=[]
hero=[{"ini":0,"fim":em("f1","Tailândia")-.4,"html":
       '<div class="dt">15/11/2026</div><div class="t1">GAZA</div><div class="t2">226 MIL</div><div class="t4">estimativa de pessoas possivelmente atingidas<br>balanço da semana · OCHA, 13/11<br><span style="font:800 22px Inter;letter-spacing:1px">ILUSTRAÇÃO</span></div>'}]
cont=lambda fid,pal,ate,dec,cor,unid: {"de":0,"ate":ate,"dec":dec,"ini":em(fid,pal)-1.,"dur":1.,"cor":cor,"unid":unid}
it=lambda fid,pal,txt:{"t":em(fid,pal),"txt":txt}
paineis=[
 {"ini":em("f1","Tailândia")-.4,"fim":fim("f1"),"k":"TAILÂNDIA · DESDE SETEMBRO","contador":cont("f1","88",88,0,"#ff8c1a","VÍTIMAS · ACUMULADO"),"l":"AHA / DDPM · balanço publicado em 9/11"},
 {"ini":ini("f2"),"fim":fim("f2"),"k":"GAZA · CHUVAS DESDE 6/11","contador":cont("f2","46",46,0,"#5ec8ff","MIL FAMÍLIAS · ESTIMATIVA"),"l":"Possivelmente atingidas · dados até 9/11 · OCHA, 13/11"},
 {"ini":ini("f3"),"fim":em("f3","88")-1.,"k":"TAILÂNDIA · BALANÇO PUBLICADO 9/11","contador":cont("f3","162.800",162.8,1,"#5ec8ff","MIL PESSOAS AINDA ATINGIDAS"),"l":"7 províncias · corte de 8/11 · não são impactos só desta semana"},
 {"ini":em("f3","88")-1.,"fim":fim("f3"),"k":"TAILÂNDIA · DESDE SETEMBRO","contador":cont("f3","88",88,0,"#ff8c1a","VÍTIMAS · ACUMULADO"),"l":"DDPM via AHA Centre · publicação em 9/11"},
 {"ini":ini("f4"),"fim":fim("f4"),"k":"SOMÁLIA · BALANÇO DE OUTUBRO","contador":cont("f4","170",170,0,"#5ec8ff","MIL ATINGIDOS · QUASE"),"l":"OCHA, 12/11 · Jowhar ainda alagada: FAO, 11/11"},
 {"ini":ini("f5"),"fim":fim("f5"),"k":"MADEIRA · 10–11/11 · IPMA","contador":cont("f5","502,7",502.7,1,"#5ec8ff","MM EM 24 H · RECORDE NACIONAL"),"l":"Anterior: 497,5 mm em 6/6/2023 · mesmo posto · dados provisórios"},
 {"ini":ini("f6"),"fim":fim("f6"),"k":"WEIPA AERO · TERÇA, 10/11","contador":cont("f6","39,9",39.9,1,"#ff8c1a","°C · RECORDE DE NOVEMBRO"),"l":"Anterior ao episódio: 39,6 °C em 2024 · estação 027045"},
 {"ini":ini("f7"),"fim":fim("f7"),"k":"CADA BALANÇO TEM SEU PERÍODO","itens":[it("f7","acumulados","Gaza: estimativa de 6–9/11"),it("f7","semana","Tailândia: desde setembro<br>Somália: acumulado de outubro")]},
 {"ini":ini("f8"),"fim":fim("f8"),"k":"E AGORA? · PREVISÃO · IMD, 15/11","itens":[it("f8","tempestade","Tempestade ciclônica prevista"),it("f8","Bengala","Golfo de Bengala"),it("f8","segunda","Segunda · 16/11")],"l":"Previsão oficial · não é impacto já ocorrido"},
 {"ini":ini("f9"),"fim":fim("f9"),"k":"COMENTA AQUI","itens":[it("f9","região","De que região você é?"),it("f9","cidade","E de que cidade?")]}
]
cta={"ini":ini("f10"),"fim":DUR,"a":"APRENDA IA","b":"inema.club"}
club={"ini":em("f10","inema"),"fim":DUR,"a":"inema.club","b":"APRENDA IA · DE GRAÇA"}
fontes=[
 {"ini":0,"fim":fim("f1"),"html":"OCHA, 13/11 · AHA/DDPM, 9/11 · estimativa Gaza e acumulado Tailândia"},
 {"ini":ini("f2"),"fim":fim("f2"),"html":"OCHA OPT · relatório 13/11/2026 · estimativa por alertas até 9/11"},
 {"ini":ini("f3"),"fim":fim("f3"),"html":"AHA Centre / DDPM · publicado 9/11 · balanço até 8/11/2026"},
 {"ini":ini("f4"),"fim":fim("f4"),"html":"OCHA ROSEA, 12/11 · FAO-SWALIM/SODMA, 11/11/2026"},
 {"ini":ini("f5"),"fim":fim("f5"),"html":"IPMA · Chão do Areeiro · 09 UTC 10/11 a 09 UTC 11/11/2026"},
 {"ini":ini("f6"),"fim":fim("f6"),"html":"BOM · observações 10/11/2026 e arquivo 19/11/2024 · ABC, 14/11"},
 {"ini":ini("f7"),"fim":fim("f7"),"html":"Períodos: OCHA OPT · AHA/DDPM · OCHA ROSEA · pesquisa/noticias.md"},
 {"ini":ini("f8"),"fim":fim("f8"),"html":"IMD / RSMC New Delhi · outlook 00 UTC, 15/11/2026 · previsão"},
 {"ini":ini("f9"),"fim":DUR,"html":"INEMA · inema.club · mapa: NASA Blue Marble · imagens: ilustração"},
]
AM="#FACC15"
CORES={"vitimas":"#ff8c1a","recorde":"#5ec8ff","atingidas":"#5ec8ff","atingidos":"#5ec8ff","calor":"#ff8c1a","chuvas":"#5ec8ff","estimativa":"#ff8c1a","possivelmente":"#ff8c1a"}
LUGAR={"gaza","tailandia","somalia","jowhar","madeira","portugal","weipa","australia","bengala","inema","inemaclub","regiao","cidade"}
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
   "duracao":DUR,"padding_topo":0 if AVATAR else 560,"marca":"INEMA · CLIMA NO MUNDO","selo":"ONU · BOM · IPMA · 15/11",
   "camera":camera,"sat":SAT,"telas":telas,"imagens":imagens,"pontos":pontos,"pinos":pinos,"hero":hero,
   "paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js: {DUR}s, {len(legenda)} blocos, zoom máximo {max(x['zoom'] for x in camera)}, {len(telas)} imagens")
